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

1. Publication of any kind (push, release, tag, preprint, articles, demo hosting) is not approved; it needs the owner's explicit approval under G-PUBLIC (OD-5; owner-approvals-2026-11-25e).
2. The owner has not yet signed off this checklist, and only the owner can tick its boxes (owner-approvals-2026-11-25e).
3. The three frozen EXP protocols (`research/experiments/EXP-001/protocol.md`, `EXP-002/protocol.md` and `EXP-003/protocol.md`, line 8 each) still say "frozen (owner-approved 2026-11-24), not yet run" although all three experiments have run; they were not edited because they are frozen with recorded hashes, and the owner decides whether to leave them, add a note outside the frozen files, or accept a hash change (D-025; owner-approvals-2026-11-25e lists this "STREAK 'not yet run' protocol note" as open).
4. The repository URL and the demo URL are owner-only facts that do not exist yet; they are placeholders until the owner publishes (owner-approvals-2026-11-25e).
5. The author line, affiliation (none), funding (none) and competing interests (none) were decided by the owner (OD-4, D-021); the owner confirms that they still hold before any publication (owner-approvals-2026-11-25e lists these as owner-only facts).
6. The manuscript title is the one approved on 2026-11-25 (D-021); no other title is proposed.
7. The `CITATION.cff` version reads `0.1.0-rc1` and `date-released` was removed (coordinator default under owner-approvals-2026-11-25e, D-026); re-adding a release date and choosing the final version number are part of the owner's publication step.
8. The article drafts in `articles/` were written in M5 and have not yet been read by the owner (progress.md, M5 entry).
9. The owner's review of the evidence audit is still open (`research/publication/claims_audit.md`, section 5, last box).
10. The SESOI of 0.02 is labelled "Planning proposal, owner to confirm" in the frozen `research/protocol.md` (line 66); the owner froze the protocol with this value (OD-1), so this is recorded as confirmed by the freeze unless the owner says otherwise.
11. Risk R-5 stays open: the model's time scale is not validated by real data (the held-out test was negative); the owner decides whether the manuscript's limitations wording suffices for publication.

### Remaining owner placeholders (file and line)

| File | Line | Placeholder |
|---|---|---|
| `research/paper/manuscript.md` | 252 | public repository URL |
| `research/paper/manuscript.tex` | 845 | public repository URL (generated from the manuscript) |
| `README.md` | 64 | demo URL |
| `README.md` | 80 | repository URL |
| `CITATION.cff` | 6 | repository URL (in `message`) |
| `demo/README.md` | 28 | demo URL |
| `articles/medium.md` | 50 | repository URL |
| `articles/medium.md` | 51 | demo URL |
| `articles/linkedin.md` | 12 | repository URL |
| `articles/linkedin.md` | 13 | demo URL |

The PDFs (`manuscript.pdf`) carry the same repository-URL placeholder as their source.
