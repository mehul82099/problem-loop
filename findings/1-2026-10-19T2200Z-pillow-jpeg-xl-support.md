# Pillow: still no built-in JPEG XL support, with browsers now shipping it (python-pillow/Pillow#4247)

- Source issue: https://github.com/python-pillow/Pillow/issues/4247 "JPEG XL support". Opened 2019-12-04, open, labels "Enhancement" and "JPEG". 44 reactions on the post, 27 comments, last on 2026-10-19.
- Browser news, read 2026-10-19: Chrome's blog says Chrome ships JPEG XL decoding starting with Chrome 155 (https://developer.chrome.com/blog/jpeg-xl-in-chrome, published 2026-10-06). A web-standards news page says Firefox 158 enables JPEG XL by default (https://web-standards.dev/news/2026/10/firefox-158/, 2026-10-14). I only read the excerpt for Firefox, not Mozilla's own page.
- Pillow pull requests and issues named in the thread: https://github.com/python-pillow/Pillow/pull/7848 (read-only JPEG XL via libjxl, opened 2024-03-02 by a third party, now closed), https://github.com/python-pillow/Pillow/pull/10215 (a JPEG XL plugin via the optional imagecodecs package, open, opened 2026-10-15), https://github.com/python-pillow/Pillow/issues/9101 (consider an image-format-per-plugin model, open).

## The request
Pillow is the standard Python image library. People want it to open and save `.jxl` files, a newer format that the 2019 post said was "coming out in a few months".

## What the thread says
- 2021 to 2023: third-party plugins appeared (jxlpy, pillow-jxl-plugin, a Rust-based one). One commenter said in 2023 that JPEG XL is "probably dead", after Chrome removed its experimental support at that time, and others argued against it. Pillow maintainers said in 2023 that the limit is volunteer time and they would want a pull request with docs and a license-compatible dependency.
- 2026-10-12: a commenter notes that Chrome and Firefox now both support the format. A Pillow maintainer (hugovk) replies that the earlier PR #7848 made wheels about 50% larger, which was too much, and that Pillow is "still open to other options", with at least three Pillow plugins on PyPI. PR #7848 was closed the same day with the note that nobody had suggested a way to reduce the wheel size. Another commenter said closing it was not a good look and suggested a separate package, like torchvision does. A maintainer pointed to issue #9101, which discusses that.
- A commenter then posted size tests, saying he ran them with an AI coding tool, which he labels as its findings: linking only the decoder library would cut the added size by about two thirds, and a decoder could add 0.5 to 0.7 MB per wheel, about 10% instead of about 30%. I did not check these numbers. He also asks the maintainers either to say how they want to approach it or what information they need.
- 2026-10-19 (a Pillow maintainer, aclark4life): none of the wheel-shrinking efforts he knows of has reached "zero increase", which he says is about what would be needed. The second best option is probably a `pillow-jpegxl` plugin, which he thinks already exists. He says he is not opposed to the Pillow organization taking one on, but it is unlikely with "4 underpaid volunteers" doing the work. In a side discussion he also explains that `imageio` has no codecs of its own and mostly wraps Pillow, so it would not solve this.

## What can be said
- No decision to add JPEG XL to Pillow itself has been made, per the latest maintainer comment. The current position in the thread is: size is the blocker, a plugin is the likely route, and the work needs volunteers.
- If you need `.jxl` in Python today, the thread points to third-party plugins. I did not test any of them, and the thread says one (jxlpy) had installation problems for some people in 2022.
- Chrome and Firefox support does not change what Pillow's maintainers have said about wheel size.

## Honest limits
- I did not install Pillow or any plugin, or check the wheel-size numbers.
- I read most comments from 2023 on, and skimmed the older ones.
- The maintainers' statements are from comments, not a roadmap.
