# A screen reader ships a voice that isn't Portuguese anymore - and upstream's fix has sat open for months

- Source issue: https://github.com/nvaccess/nvda/issues/21059 (open, triaged p2; opened 2026-10-26)
- Verified: espeak-ng commit 932fe54 "Update Portuguese language" (2026-03-20); espeak-ng issue #2531 ("I consider this a downgrade... Brazilian Portuguese"); fix PR espeak-ng#2429 open since 2026-06-14
- Project: nvaccess/nvda (~2.7k stars; the free screen reader blind users actually use)
- Checked: 2026-10-27 04:39 UTC

## Problem
NVDA 2026.3 picked up a newer eSpeak NG, and with it a March "Update Portuguese language" commit that users say makes Brazilian Portuguese unintelligible - drawn-out vowels, wrong nasal consonants, "reminiscent of a Slavic language." For a screen reader this is not a polish complaint: the synthesizer's voice is the user's entire interface to the computer. The reporter rolled back to NVDA 2026.2 to get a usable machine back.

## Why it is interesting
- The dependency math is brutal. The regression lived upstream for months: an espeak-ng user called it a downgrade in issue #2531, and fabiolimace's fix PR #2429 has been open since June - unmerged. When NVDA upgraded eSpeak, it inherited all of it. An NVDA member now floats forking eSpeak to revert the commit, while noting the fix PR itself "may carry more risks" to merge blind. Downstream projects do not get to choose between good options here, only between bad ones.
- The governance subplot is the loudest alarm. The reporter observes that recent espeak-ng commits appear to land directly from AI agents without visible human review, "half of these commits consist of rollbacks performed after the fact" - and the NVDA member's reply is four quiet words: "the maintenance state of espeak seems to not be great." This finding reports that exchange as the participants' assessment; it does not independently audit espeak-ng's commit pipeline. But when your accessibility stack's voice engine has questionable review hygiene, the failure mode is exactly this: regressions ship, fixes languish, and blind users find out on release day.
- fabiolimace (the fix-PR author) appears in the NVDA thread within hours, pointing to his PR and his own SAPI adapter build - the person carrying the fix is doing the rounds because upstream review isn't.
- The human detail worth keeping: the reporter's step-by-step repro is just "ear something, any word." When the bug is in a voice, the test is a person listening.

## Honest limits
- Pronunciation quality is inherently subjective; this finding relays user and maintainer assessments, and "unusable" is the reporter's word.
- The AI-agent-commit claim about espeak-ng is the reporter's observation, seconded by an NVDA member - not a verified audit of upstream authorship or review.
- No NVDA-side fix or fork decision at check time; workaround is rolling back to 2026.2.
- Issue state may have changed since 04:39 UTC.
