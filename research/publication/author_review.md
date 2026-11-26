<!-- SPDX-License-Identifier: LicenseRef-STREAK-NC-Research-1.0 -->
# Owner review checklist

To be completed by the owner. The AI does not tick these boxes.

- [ ] Research question, hypotheses, primary metric and baseline approved.
- [ ] Protocol and EXP protocols frozen (hash recorded in the registry).
- [ ] Authorship and metadata approved (no invented affiliation, funding or endorsement).
- [ ] AI-assistance disclosure reviewed and accurate.
- [ ] Claims register reviewed.
- [ ] Limitations and ethics sections reviewed.
- [ ] Licence statements reviewed.
- [ ] Publication (repository push, release, preprint, articles) explicitly approved, or declined.

## Prepared for the owner (M6, 2026-11-25)

No box above was ticked by an agent in any milestone (checked in M5, D-025, and again in M6), so nothing was unticked. The boxes are the owner's.

### What to read for each item

| Item | What to read |
|---|---|
| Research question, hypotheses, primary metric and baseline | `research/protocol.md` sections 1 to 6 (question, H0/H1, R30, A1 Fixed, SESOI 0.02); manuscript section 1.3 (`research/paper/manuscript.pdf`, pages 1 and 2). |
| Protocol and EXP protocols frozen | `research/freeze_record.md` and `research/freeze.json` (hashes); supplementary section S1 (`research/paper/supplementary.pdf`, page 1, protocol hash list). |
| Authorship and metadata | `CITATION.cff` (author, title, version 0.1.0-rc1, no release date); manuscript front matter and section "Funding, competing interests and AI assistance" (`manuscript.pdf`, pages 1 and 11); decision D-021. |
| AI-assistance disclosure | Manuscript section "Funding, competing interests and AI assistance" (`manuscript.pdf`, page 11); `README.md` section Citation; `CITATION.cff` message. |
| Claims register | `research/claims_register.csv` (25 claims mapped in `artifact_manifest.json`); `research/publication/claims_audit.md` sections 1 to 6. |
| Limitations and ethics | Manuscript sections 7 and 8 (`manuscript.pdf`, pages 10 and 11); `research/limitations.md`. |
| Licence statements | `LICENSE`, `NOTICE.md`, `README.md` section Licence; `research/publication/dependency_licences.md` (one flag for information: pandoc, GPL-2.0-or-later, external build tool). |
| Publication | `research/publication/release_checklist.md`; `research/publication/reproducibility_report.md`; the articles `articles/medium.md` and `articles/linkedin.md` (drafts, not yet read by the owner). |

### Open decisions for this repository

1. Publication (updated 2026-11-26): the repository was pushed on 2026-11-25 and is public, and the owner approved hosting the demo on Cloudflare Workers (owner, 2026-11-26, decision sheet, B2). The release, tag, DOI or preprint and the posting of the articles are not approved yet (B15, B18).
2. The owner has not yet signed off this checklist, and only the owner can tick its boxes (owner-approvals-2026-11-25e).
3. (Answered 2026-11-26, B12: leave the frozen files; README sentence added.) The three frozen EXP protocols (`research/experiments/EXP-001/protocol.md`, `EXP-002/protocol.md` and `EXP-003/protocol.md`, line 8 each) still say "frozen (owner-approved 2026-11-24), not yet run" although all three experiments have run; they were not edited because they are frozen with recorded hashes, and the owner decides whether to leave them, add a note outside the frozen files, or accept a hash change (D-025; owner-approvals-2026-11-25e lists this "STREAK 'not yet run' protocol note" as open).
4. Repository and demo URLs (updated 2026-11-26): filled with https://github.com/mohamedbechirkefi/streak-learning-retention and https://streak-learning-retention.kefimohamedbechir.workers.dev (owner, 2026-11-26, decision sheet, B1 and B2).
5. Author line and statements (updated 2026-11-26): "Mohamed Bechir Kefi, independent researcher", "No funding was received." and "The author declares no competing interests." (owner, 2026-11-26, decision sheet, B3 and B4; the affiliation replaces "none" of OD-4, D-021).
6. The manuscript title is the one approved on 2026-11-25 (D-021); no other title is proposed.
7. The `CITATION.cff` version reads `0.1.0-rc1` and `date-released` was removed (coordinator default under owner-approvals-2026-11-25e, D-026); re-adding a release date and choosing the final version number are part of the owner's publication step.
8. The article drafts in `articles/` were written in M5 and have not yet been read by the owner (progress.md, M5 entry).
9. The owner's review of the evidence audit is still open (`research/publication/claims_audit.md`, section 5, last box).
10. The SESOI of 0.02 is labelled "Planning proposal, owner to confirm" in the frozen `research/protocol.md` (line 66); the owner froze the protocol with this value (OD-1), so this is recorded as confirmed by the freeze unless the owner says otherwise.
11. Risk R-5 stays open: the model's time scale is not validated by real data (the held-out test was negative); the owner decides whether the manuscript's limitations wording suffices for publication.

### Remaining owner placeholders (file and line)

Updated 2026-11-26: none. The ten repository-URL and demo-URL placeholders listed at M6 were filled (owner, 2026-11-26, decision sheet, B1 and B2), and the PDFs were rebuilt from the changed sources.

## Owner answers recorded (2026-11-26)

Source: owner, 2026-11-26, decision sheet (`labs/_shared/owner-decision-sheet-2026-11-26.md` and `labs/_shared/owner-approvals-2026-11-26.md`, outside this repository). Applied in this repository (D-028). No box above was ticked.

| Id | Answer | Applied here |
|---|---|---|
| A1 | Correct the out-of-date "not pushed / no remote" sentences. | README status, `release_checklist.md`, this file (items 1 and 4), demo status label, article headers ("not yet posted"). Append-only records unchanged. |
| B1 | Repository URL `https://github.com/mohamedbechirkefi/streak-learning-retention`. | README, manuscript (Data and code availability), `CITATION.cff` (`message`, new `repository-code`), articles, demo footer. |
| B2 | Demo hosted on Cloudflare Workers, free plan, at `https://streak-learning-retention.kefimohamedbechir.workers.dev`. | README, `demo/README.md` (Hosting), articles, `demo/wrangler.jsonc` (assets only, `./dist`). Deployment by the coordinator. |
| B3 | Author line "Mohamed Bechir Kefi, independent researcher". | Manuscript front matter (author with affiliation "Independent researcher"), three experiment reports (Authorship row), `CITATION.cff` (`affiliation`), README, Medium draft, demo footer. Frozen `freeze.json` and `freeze_record.md` keep "no affiliation" (C3, frozen). `pyproject.toml` has no authors field. |
| B4 | No funding, no competing interests. | Manuscript: "No funding was received. The author declares no competing interests."; README Citation section. |
| B5 | AI-use statement (SCALE, SCROLL, TOKEN, TRUST). | Not applicable here (approved earlier, D-021). |
| B6, B7 | Manuscript title approved; `CITATION.cff` carries it. | Already the case (title approved 2026-11-25, D-021; `tests/test_citation.py`). |
| B8 | `0.1.0-rc1` becomes `0.1.0` with `date-released` at the release. | Recorded in `release_checklist.md`; `pyproject.toml` keeps `0.2.0`. |
| B9 | Scrub home paths from editable files. | Done; remaining lines listed in `reproducibility_report.md` section 9. |
| B10 | Committed PDFs stay and are attached to a release. | Recorded. |
| B11, B13 | Release-note sentences. | `release_checklist.md`, "Release notes (draft)". |
| B12 | Frozen protocols' "not yet run" status lines stay; README sentence. | README, below the experiment table. |
| B14 | Source-level labels accepted. | Recorded; labels unchanged. |
| R-STREAK-1 | SESOI 0.02 confirmed by the freeze; R-5 limitation wording kept as written. | Recorded (items 10 and 11 above); no text change. |

### Still open

- B15: the owner reads and approves the article drafts before any posting.
- B16: the owner's full-text review of the manuscript, the supplementary material and the reports, then the sign-off of this checklist (all boxes above are the owner's).
- B18: release, tag and any DOI or preprint (zero cost only).
- Freezes: no freeze is pending in this repository (protocol 1.0 and EXP-001 to EXP-003 were frozen by the owner on 2026-11-24).
- The owner's review of the evidence audit (`claims_audit.md`, section 5, last box).
