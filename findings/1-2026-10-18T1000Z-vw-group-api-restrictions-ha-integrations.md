# Volkswagen Group vehicle data: third-party integrations lost access in May 2026 (Home Assistant issue #977)

- Source: https://github.com/robinostlund/homeassistant-volkswagencarnet/issues/977 "Volkswagen API access restrictions, EU Data Act concerns, and impact on existing integrations" (open, opened 2026-05-29 by janmisek, 455 comments, label enhancement, updated 2026-10-18)
- Checked by GitHub API on 2026-10-18: the GitHub account https://github.com/VWGroupDatahub (type User, created 2026-09-14, 5 public repos, bio says it is "Contribution by an employee of Volkswagen Group Info Services AG. This is not an official product and does not constitute any support, service, or warranty") and 8 closed pull requests it authored, listed below.
- Not verified: the European Parliament pages quoted by commenters (https://www.europarl.europa.eu/doceo/document/E-10-2026-002465-ASW_EN.html). My fetch of the answer page timed out and returned nothing, so everything about it below is a commenter's account.

## What the thread says happened
The opening post says that around May 2026 Volkswagen Group restricted API access, and that community integrations (the Home Assistant integration this repo hosts, and evcc) lost access to data such as battery state of charge, charging status, mileage and climate controls. The author's reading is that access is now limited to approved commercial partners, and that it may affect Skoda, SEAT and Cupra too. This is the author's reading of what he saw, not a Volkswagen statement. The post says the thread is for policy discussion, not troubleshooting, and links an EU petition and complaint forms for German and Finnish residents.

## Replacement path and what the company's engineers did on GitHub
- Comments describe an "EU Data Act" portal that delivers a ZIP of vehicle data every 15 minutes, and community integrations named in the thread (for example HA_VAG-EU-Data-Act and hass-vw-eu-data-act) that read it. I did not test any of these.
- One commenter measured that a ZIP delivered on 2026-10-16 contained a state-of-charge value timestamped about five hours earlier than the value the VW app showed. This is one comment's measurement and I could not reproduce it.
- The VWGroupDatahub account has authored 8 pull requests across community repos between 2026-09-25 and 2026-10-06, all now closed. Titles include "Remove Probing from VW Portal", "Remove not needed priming call from code", "EUDA: change login flow to speedup login", "Change to health endpoint instead of calling root page" and "refactor: Speed up EUDA login and set custom User Agent". One commenter argues these change nothing for users except load reduction and identifying who is calling. That is his interpretation. I did not review the code.

## What users say about contacting the company
Several commenters report that customer care replies are templated, that formal GDPR and Data Act requests got acknowledgements, and one says a reply on 2026-10-12 repeated text sent in June. These are unverified accounts of private correspondence. One commenter says the European Commission answered a written parliamentary question (E-002465/2026) on 2026-08-31 and that the answer did not find a breach and says it will "closely monitor". I could not check that wording.

## What this finding does not say
- It does not say Volkswagen is in breach of any law. That question is for regulators, and the thread itself says no authority has acted so far.
- It does not give legal advice, and I do not recommend any complaint route. Commenters list some (national regulators, data protection authorities, press). Rules differ per country.
- I do not say the restriction is intentional or permanent, or that a particular integration is safe or unsafe to use. Anyone running a third-party integration with their account credentials should judge that themselves.

## Honest limits
- 455 comments is too many to read in full. I read the opening post and roughly the most recent 30 to 40 comments, and the 8 pull-request titles. Earlier months are not covered.
- Most statements about company behaviour come from users and are unverified. I could not confirm the European Parliament pages or the company notice commenters quote.
- I did not run any integration or measure any data.
