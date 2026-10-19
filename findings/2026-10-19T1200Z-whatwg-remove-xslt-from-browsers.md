# Removing XSLT from browsers: Chrome turns it off on November 17, 2026 (whatwg/html#11523)

- Source: https://github.com/whatwg/html/issues/11523 "Should we remove XSLT from the web platform?" Opened 2025-08-01 by a Chrome engineer (mfreed7), open, 77 comments, 145 reactions on the post, labels "removal/deprecation" and "stage: 3". Last comment 2026-10-19.
- Chrome's own plan: https://developer.chrome.com/docs/web-platform/deprecating-xslt (published 2025-10-29, read 2026-10-19).
- Blink's approval thread: https://www.mail-archive.com/blink-dev@chromium.org/msg15924.html (a status update dated 2026-02-23).
- Spec change "Mark XSLT deprecated": https://github.com/whatwg/html/pull/12805 (merged 2026-08-25, by the API). A separate PR to remove mentions of XSLT from the HTML spec, https://github.com/whatwg/html/pull/11563, is still open.

## What is changing
XSLT is a way for a browser to turn an XML file into a web page, using a stylesheet. Two browser features use it: the `XSLTProcessor` JavaScript class and the XSLT processing instruction in an XML file. The opener argues the libraries behind it are old C and C++ code that is a security risk for a feature that few sites use.

## Chrome's timeline (from the Chrome page above)
- Console warnings began in Chrome 142 (October 2025). Official deprecation in Chrome 143.
- XSLT disabled by default in Canary, Dev and Beta from Chrome 145. An enterprise policy came in Chrome 146. An origin trial, which lets a site keep using it past the removal date, goes live in Chrome 152 (2026-08-25).
- Chrome 158, planned for 2026-11-17: XSLT stops working in Stable for everyone except origin trial and enterprise policy participants.
- Chrome 176 (2027-08-17): origin trial and enterprise policy stop working, and XSLT is off for everyone.
- The page says the Firefox and WebKit projects have "indicated plans" to remove XSLT too. In the thread a WebKit member (annevk, 2025-08-04) wrote that WebKit is "cautiously supportive" and would wait for one implementation to fully remove it.
- Dates here are Chrome's stated plan from 2025. I did not check whether they have been revised, though the Chrome page was the primary source and several recent blog posts repeat the November 17 date.

## What worried people in the thread
- Many comments object. They say XSLT works with JavaScript off, is used for XML publishing, digital publishing and intranets, and that the fix should be a memory-safe implementation and not removal.
- A common use is making RSS and podcast feeds readable when someone opens the feed URL in a browser. The Chrome engineer's answer is a JavaScript polyfill, a script you add to the XML, and HTML alternatives. A commenter notes some feed readers also ask for HTML, which complicates serving one thing to browsers. The polyfill repository exists (https://github.com/mfreed7/xslt_polyfill, not archived at checking time).
- A WHATWG editor (zcorpan) measured use in the HTTP Archive crawl. In 2025 he found 357 of about 23 million desktop pages used the processing instruction. On 2026-10-19 he posted a repeat with a 2026-09-01 crawl: the processing instruction on 632 pages (about 0.001% of desktop and 0.0015% of mobile pages), `XSLTProcessor` on 2,418. He loaded a sample of 200 in Chrome Canary 158 with XSLT on and off and reports 12 broken and 85 "worse" (mostly sitemaps and feeds), and none of the top 100,000 hits breaking. His comment says the analysis was done with the Claude AI tool, and shows the data and scripts at https://github.com/zcorpan/xslt-compat-11523. I did not rerun or check his numbers.
- The same comment says Microsoft documents that its RD Web Access breaks without XSLT (a knowledge base article number is given). I did not look it up.

## What can be said
- By Chrome's own page, this is going ahead on the stated dates, with an escape hatch until August 2027 through the origin trial and enterprise policy. The thread's objections have not changed that plan, as far as the sources I read show.
- If you publish XML with a stylesheet (feeds, sitemaps, internal portals), what changes is that browsers would show the raw XML. Crawlers and feed readers are not affected, per the commenters. Check the Chrome page for the migration steps.

## Honest limits
- I did not test any page in Chrome Canary or the polyfill.
- I read about a third of the thread in detail, focusing on members and the most-reacted comments.
- I did not verify Firefox's plans, or the Microsoft claim.
