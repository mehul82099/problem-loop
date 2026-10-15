#!/usr/bin/env python3
"""problem-loop: a five-stage agent pipeline that runs once per cycle.

Research -> Discussion -> Conclusion -> Action -> Publisher

Each stage is a small class with one method that takes the previous stage's
output and returns its own. State is plain dataclasses, so every stage can be
tested alone and every hand-off is visible in the cycle log.

Stdlib only. No LLM is called. Discussion uses explicit scoring rules, and
the log says so. A model can be plugged in by replacing a stage class.
"""
from __future__ import annotations

import argparse
import dataclasses
import datetime as dt
import json
import re
import subprocess
import sys
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Callable, Dict, List, Optional

__version__ = "0.1.0"
USER_AGENT = "problem-loop/0.1 (+https://github.com/mehul82099/problem-loop)"

Fetch = Callable[[str], dict]


def http_json(url: str, timeout: float = 15.0) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310 - https URLs we build
        return json.loads(resp.read().decode("utf-8"))


@dataclasses.dataclass
class Candidate:
    title: str
    url: str
    source: str  # "hn" | "github" | "stackexchange"
    points: int = 0
    comments: int = 0
    snippet: str = ""


@dataclasses.dataclass
class Vote:
    role: str
    score: float  # 0..10
    reason: str


@dataclasses.dataclass
class Discussion:
    candidate: Candidate
    votes: List[Vote]

    @property
    def total(self) -> float:
        return round(sum(v.score for v in self.votes), 2)

    @property
    def vetoed(self) -> bool:
        return any(v.score == 0 for v in self.votes)


@dataclasses.dataclass
class Conclusion:
    chosen: Optional[Discussion]
    reason: str
    rejected: List[str]


@dataclasses.dataclass
class Finding:
    slug: str
    filename: str
    markdown: str
    sources: List[str]


# ---------------------------------------------------------------- Research

PROBLEM_WORDS = re.compile(
    r"\b(bug|broken|fails?|failing|can'?t|cannot|unable|wrong|annoying|painful|"
    r"how do (i|you)|why (does|is|do)|crash(es|ing)?|slow|confusing|workaround)\b",
    re.I,
)


class Research:
    """Collect candidate problems from public, keyless APIs."""

    def __init__(self, fetch: Fetch = http_json, per_source: int = 15):
        self.fetch = fetch
        self.per_source = per_source

    def run(self) -> List[Candidate]:
        out: List[Candidate] = []
        for name, fn in (("hn", self._hn), ("github", self._github), ("stackexchange", self._se)):
            try:
                out.extend(fn())
            except Exception as exc:  # one dead source must not stop the cycle
                print(f"[research] {name} failed: {exc}", file=sys.stderr)
        return out

    def _hn(self) -> List[Candidate]:
        q = urllib.parse.urlencode({"tags": "ask_hn", "hitsPerPage": self.per_source, "query": "how do you handle"})
        data = self.fetch(f"https://hn.algolia.com/api/v1/search_by_date?{q}")
        return [
            Candidate(
                title=h.get("title") or "",
                url=f"https://news.ycombinator.com/item?id={h['objectID']}",
                source="hn",
                points=h.get("points") or 0,
                comments=h.get("num_comments") or 0,
                snippet=(h.get("story_text") or "")[:300],
            )
            for h in data.get("hits", [])
            if h.get("title")
        ]

    def _github(self) -> List[Candidate]:
        q = urllib.parse.urlencode(
            {"q": "is:issue is:open label:\"help wanted\" comments:>5", "sort": "reactions", "per_page": self.per_source}
        )
        data = self.fetch(f"https://api.github.com/search/issues?{q}")
        return [
            Candidate(
                title=i.get("title") or "",
                url=i["html_url"],
                source="github",
                points=(i.get("reactions") or {}).get("total_count", 0),
                comments=i.get("comments") or 0,
                snippet=(i.get("body") or "")[:300],
            )
            for i in data.get("items", [])
        ]

    def _se(self) -> List[Candidate]:
        q = urllib.parse.urlencode(
            {"order": "desc", "sort": "votes", "site": "stackoverflow", "pagesize": self.per_source,
             "filter": "default", "fromdate": int((dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=30)).timestamp())}
        )
        data = self.fetch(f"https://api.stackexchange.com/2.3/questions?{q}")
        return [
            Candidate(
                title=i.get("title") or "",
                url=i["link"],
                source="stackexchange",
                points=i.get("score", 0),
                comments=i.get("answer_count", 0),
            )
            for i in data.get("items", [])
        ]


# -------------------------------------------------------------- Discussion

class Discussion_:  # noqa: N801 - name avoids clash with the dataclass
    """Three fixed roles score each candidate. Rules, not a model."""

    def run(self, candidates: List[Candidate], seen: List[str]) -> List[Discussion]:
        seen_urls = set(seen)
        return [Discussion(c, self.vote(c, c.url in seen_urls)) for c in candidates]

    @staticmethod
    def vote(c: Candidate, already_done: bool) -> List[Vote]:
        text = f"{c.title} {c.snippet}"
        demand = min(10.0, (c.points ** 0.5) + (c.comments ** 0.5))
        advocate = Vote("user-advocate", round(demand, 2), f"{c.points} points/reactions, {c.comments} comments/answers")

        has_problem = bool(PROBLEM_WORDS.search(text))
        vague = len(c.title.split()) < 4
        skeptic_score = 0.0 if already_done else (6.0 if has_problem else 2.0) - (3.0 if vague else 0.0)
        skeptic_reason = (
            "already published" if already_done
            else ("states a concrete problem" if has_problem else "no clear problem statement")
            + ("; title too vague" if vague else "")
        )
        skeptic = Vote("skeptic", max(skeptic_score, 0.0 if already_done else 0.5), skeptic_reason)

        small = len(c.title) < 140 and len(text) < 900
        builder = Vote("builder", 6.0 if small else 3.0,
                       "scope looks small enough for one cycle" if small else "scope looks large")
        return [advocate, skeptic, builder]


# -------------------------------------------------------------- Conclusion

class ConclusionAgent:
    def __init__(self, min_total: float = 10.0):
        self.min_total = min_total

    def run(self, talks: List[Discussion]) -> Conclusion:
        ranked = sorted((t for t in talks if not t.vetoed), key=lambda t: t.total, reverse=True)
        rejected = [f"{t.candidate.title} ({t.total})" for t in ranked[1:4]]
        if not ranked or ranked[0].total < self.min_total:
            return Conclusion(None, f"no candidate reached the minimum total of {self.min_total}", rejected)
        top = ranked[0]
        return Conclusion(top, f"highest total {top.total} with no veto", rejected)


# ------------------------------------------------------------------ Action

def slugify(text: str, limit: int = 48) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return s[:limit].rstrip("-") or "finding"


class Action:
    """Turn the decision into a finding document with its sources."""

    def run(self, concl: Conclusion, now: dt.datetime) -> Optional[Finding]:
        if concl.chosen is None:
            return None
        c = concl.chosen.candidate
        slug = slugify(c.title)
        stamp = now.strftime("%Y-%m-%dT%H%MZ")
        votes = "\n".join(f"- **{v.role}**: {v.score} - {v.reason}" for v in concl.chosen.votes)
        rej = "\n".join(f"- {r}" for r in concl.rejected) or "- none"
        md = (
            f"# {c.title}\n\n"
            f"- Cycle: {stamp}\n- Source ({c.source}): {c.url}\n\n"
            f"## Why this was picked\n\n{concl.reason}.\n\n{votes}\n\n"
            f"## Runner-ups\n\n{rej}\n\n"
            "## Status\n\nCandidate problem only. This file records why it was chosen. "
            "It does not claim a solution.\n"
        )
        return Finding(slug, f"findings/{stamp}-{slug}.md", md, [c.url])


# --------------------------------------------------------------- Publisher

class Publisher:
    """Write the finding, update the index, optionally commit and push."""

    def __init__(self, root: Path, push: bool = False):
        self.root = Path(root)
        self.push = push

    def seen(self) -> List[str]:
        idx = self.root / "findings" / "index.json"
        if not idx.exists():
            return []
        return [e["source"] for e in json.loads(idx.read_text())]

    def run(self, finding: Optional[Finding], now: dt.datetime) -> Optional[Path]:
        if finding is None:
            return None
        if not finding.sources:
            raise ValueError("refusing to publish a finding with no source")
        path = self.root / finding.filename
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(finding.markdown, encoding="utf-8")
        idx = self.root / "findings" / "index.json"
        entries = json.loads(idx.read_text()) if idx.exists() else []
        entries.append({"file": finding.filename, "source": finding.sources[0], "at": now.isoformat()})
        idx.write_text(json.dumps(entries, indent=2) + "\n", encoding="utf-8")
        if self.push:
            for cmd in (["git", "add", "-A"], ["git", "commit", "-m", f"finding: {finding.slug}"], ["git", "push"]):
                subprocess.run(cmd, cwd=self.root, check=True)
        return path


# ------------------------------------------------------------------- Cycle

def run_cycle(root: Path, fetch: Fetch = http_json, push: bool = False,
              now: Optional[dt.datetime] = None) -> Dict[str, object]:
    now = now or dt.datetime.now(dt.timezone.utc)
    pub = Publisher(root, push=push)
    cands = Research(fetch).run()
    talks = Discussion_().run(cands, pub.seen())
    concl = ConclusionAgent().run(talks)
    finding = Action().run(concl, now)
    written = pub.run(finding, now)
    return {
        "candidates": len(cands),
        "decision": concl.reason,
        "chosen": concl.chosen.candidate.url if concl.chosen else None,
        "written": str(written) if written else None,
    }


def main(argv: Optional[List[str]] = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--root", default=".", help="repo root to write findings into")
    p.add_argument("--push", action="store_true", help="git add/commit/push after writing")
    p.add_argument("--version", action="version", version=__version__)
    a = p.parse_args(argv)
    print(json.dumps(run_cycle(Path(a.root), push=a.push), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
