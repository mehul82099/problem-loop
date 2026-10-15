import datetime as dt
import json
import tempfile
import unittest
from pathlib import Path

import pipeline as p

NOW = dt.datetime(2026, 10, 15, 9, 0, tzinfo=dt.timezone.utc)


def fake_fetch(url: str) -> dict:
    if "algolia" in url:
        return {"hits": [
            {"objectID": "1", "title": "Ask HN: why does my cron job fail silently on reboot?", "points": 80,
             "num_comments": 60, "story_text": "it fails and I cannot tell why"},
            {"objectID": "2", "title": "Hi", "points": 500, "num_comments": 500},
        ]}
    if "api.github.com" in url:
        return {"items": [{"html_url": "https://github.com/o/r/issues/9", "title": "Parser crashes on empty input",
                           "reactions": {"total_count": 4}, "comments": 9, "body": "crashes"}]}
    if "stackexchange" in url:
        raise OSError("down")
    raise AssertionError(url)


class ResearchTests(unittest.TestCase):
    def test_collects_and_survives_dead_source(self):
        got = p.Research(fake_fetch).run()
        self.assertEqual({c.source for c in got}, {"hn", "github"})

    def test_skips_hits_without_title(self):
        got = p.Research(lambda u: {"hits": [{"objectID": "3"}]}).run()
        self.assertEqual(got, [])

    def test_hn_url_is_item_link(self):
        got = [c for c in p.Research(fake_fetch).run() if c.source == "hn"][0]
        self.assertEqual(got.url, "https://news.ycombinator.com/item?id=1")


class DiscussionTests(unittest.TestCase):
    def test_three_roles_vote(self):
        c = p.Candidate("Parser crashes on empty input", "u", "github", 4, 9)
        self.assertEqual([v.role for v in p.Discussion_.vote(c, False)], ["user-advocate", "skeptic", "builder"])

    def test_already_published_is_vetoed(self):
        c = p.Candidate("Parser crashes on empty input", "u", "github", 4, 9)
        d = p.Discussion(c, p.Discussion_.vote(c, True))
        self.assertTrue(d.vetoed)

    def test_vague_title_penalised(self):
        vague = p.Discussion_.vote(p.Candidate("Hi", "u", "hn", 500, 500), False)
        clear = p.Discussion_.vote(p.Candidate("Why does the build fail on tags", "u", "hn", 500, 500), False)
        self.assertLess(vague[1].score, clear[1].score)

    def test_demand_is_capped(self):
        v = p.Discussion_.vote(p.Candidate("x y z w", "u", "hn", 10**6, 10**6), False)[0]
        self.assertEqual(v.score, 10.0)


class ConclusionTests(unittest.TestCase):
    def test_picks_highest_unvetoed(self):
        a = p.Discussion(p.Candidate("a", "ua", "hn"), [p.Vote("r", 9, "")])
        b = p.Discussion(p.Candidate("b", "ub", "hn"), [p.Vote("r", 8, "")] * 2)
        veto = p.Discussion(p.Candidate("c", "uc", "hn"), [p.Vote("r", 10, ""), p.Vote("s", 0, "")])
        out = p.ConclusionAgent(min_total=5).run([a, b, veto])
        self.assertEqual(out.chosen.candidate.url, "ub")

    def test_declines_below_threshold(self):
        a = p.Discussion(p.Candidate("a", "ua", "hn"), [p.Vote("r", 1, "")])
        self.assertIsNone(p.ConclusionAgent(min_total=5).run([a]).chosen)

    def test_empty_input(self):
        self.assertIsNone(p.ConclusionAgent().run([]).chosen)


class ActionTests(unittest.TestCase):
    def test_none_when_no_decision(self):
        self.assertIsNone(p.Action().run(p.Conclusion(None, "x", []), NOW))

    def test_finding_has_source_and_no_solution_claim(self):
        d = p.Discussion(p.Candidate("Parser crashes!", "https://x/1", "github"), [p.Vote("r", 9, "why")])
        f = p.Action().run(p.Conclusion(d, "top", []), NOW)
        self.assertIn("https://x/1", f.markdown)
        self.assertIn("does not claim a solution", f.markdown)
        self.assertEqual(f.filename, "findings/2026-10-15T0900Z-parser-crashes.md")

    def test_slugify_edge_cases(self):
        self.assertEqual(p.slugify("!!!"), "finding")
        self.assertLessEqual(len(p.slugify("a" * 200)), 48)


class PublisherTests(unittest.TestCase):
    def test_refuses_sourceless(self):
        with tempfile.TemporaryDirectory() as t:
            with self.assertRaises(ValueError):
                p.Publisher(Path(t)).run(p.Finding("s", "findings/s.md", "x", []), NOW)

    def test_writes_file_and_index(self):
        with tempfile.TemporaryDirectory() as t:
            pub = p.Publisher(Path(t))
            pub.run(p.Finding("s", "findings/s.md", "x", ["u"]), NOW)
            self.assertEqual(pub.seen(), ["u"])
            self.assertTrue((Path(t) / "findings/s.md").exists())


class CycleTests(unittest.TestCase):
    def test_full_cycle_then_no_repeat(self):
        with tempfile.TemporaryDirectory() as t:
            first = p.run_cycle(Path(t), fake_fetch, now=NOW)
            self.assertIsNotNone(first["written"])
            second = p.run_cycle(Path(t), fake_fetch, now=NOW + dt.timedelta(hours=1))
            self.assertNotEqual(first["chosen"], second["chosen"])
            idx = json.loads((Path(t) / "findings/index.json").read_text())
            self.assertEqual(len({e["source"] for e in idx}), len(idx))


if __name__ == "__main__":
    unittest.main()
