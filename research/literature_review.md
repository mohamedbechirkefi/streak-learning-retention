<!-- SPDX-License-Identifier: LicenseRef-STREAK-NC-Research-1.0 -->
# Literature review (M0 source audit, not a systematic review)

Status: initial source audit, 2026-11-24. This is **not** a systematic review: no documented search protocol, inclusion criteria or screening was followed. Searches were ad hoc web searches. Full synthesis is an M1 task.

Verification levels used below:

- **Metadata verified:** bibliographic metadata (title, authors, venue, volume, pages, year, DOI) read from the Crossref API or the publisher landing page on the access date. The full text was **not** read unless stated.
- **Page read:** the stated web page was opened and the cited content read.
- **Unverified:** not opened; must not be cited as read.

## 1. Sources

| Key | Reference | Verification (accessed 2026-11-24) | Relevance |
|---|---|---|---|
| settles2016 | Settles, B., and Meeder, B. (2016). A Trainable Spaced Repetition Model for Language Learning. Proceedings of the 54th Annual Meeting of the ACL (Volume 1: Long Papers), 1848-1858. doi:10.18653/v1/P16-1174 | Metadata verified (ACL Anthology landing page https://aclanthology.org/P16-1174/ and Crossref). Full text not read. Companion repository https://github.com/duolingo/halflife-regression read (README, MIT licence via GitHub API). | Half-life regression; exponential recall p = 2^(-Δ/h) as used in the default model. The functional form will be checked against the full text in M1 before citing it as the source of the formula. |
| tabibian2019 | Tabibian, B., Upadhyay, U., De, A., Zarezade, A., Schölkopf, B., and Gomez-Rodriguez, M. (2019). Enhancing human learning via spaced repetition optimization. PNAS 116(10), 3988-3993. doi:10.1073/pnas.1815156116 | Metadata verified (Crossref). The PNAS page returned HTTP 403 and the PMC copy (PMC6410796) returned a browser check; full text not read. | Spaced repetition as optimal control; scheduler-design reference. |
| cepeda2006 | Cepeda, N. J., Pashler, H., Vul, E., Wixted, J. T., and Rohrer, D. (2006). Distributed practice in verbal recall tasks: A review and quantitative synthesis. Psychological Bulletin 132(3), 354-380. doi:10.1037/0033-2909.132.3.354 | Metadata verified (Crossref). Full text not read (APA PsycNet page did not load). | Spacing effect; motivates the difficulty-dependent gain and delay choice. Claims about its content are deferred to M1. |
| roediger2006 | Roediger, H. L., and Karpicke, J. D. (2006). Test-Enhanced Learning. Psychological Science 17(3), 249-255. doi:10.1111/j.1467-9280.2006.01693.x | Metadata verified (Crossref). Full text not read. | Retrieval practice (testing effect); motivates modelling reviews as retrieval attempts. |
| murre2015 | Murre, J. M. J., and Dros, J. (2015). Replication and Analysis of Ebbinghaus' Forgetting Curve. PLOS ONE 10(7), e0120644. doi:10.1371/journal.pone.0120644 | Metadata and licence verified (Crossref: CC BY 4.0). Full text not read. | Shape of forgetting curves; exponential versus power-law sensitivity. |
| ye2022 | Ye, J., Su, J., and Cao, Y. (2022). A Stochastic Shortest Path Algorithm for Optimizing Spaced Repetition Scheduling. Proceedings of KDD 2022, 4381-4390. doi:10.1145/3534678.3539081 | Metadata verified (Crossref). Full text not read. | Modern scheduler optimisation; related work. |
| fsrs-wiki | open-spaced-repetition, "The Algorithm" (awesome-fsrs wiki), https://github.com/open-spaced-repetition/awesome-fsrs/wiki/The-Algorithm | Page read. Describes FSRS-7, a weighted mix of two power-law curves R = (1 + f t / S)^(-d); stability S defined as the interval at which R = 90%. Repository fsrs4anki is MIT (GitHub API). | Source for the power-law sensitivity form (STREAK uses a simplified single power-law curve, not FSRS itself). |
| silverman2022 | Silverman, J., and Barasch, A. (2022, online; issue 2023). On or Off Track: How (Broken) Streaks Affect Consumer Decisions. Journal of Consumer Research 49(6), 1095-1117. doi:10.1093/jcr/ucac029 | Metadata and abstract read on the University of Delaware repository record (https://udspace.udel.edu/items/42ce576b-8e1f-429a-8541-e29e48dbcfbb) and Crossref. Full text not read. | Streaks as goals in themselves: intact logged streaks increase subsequent engagement relative to broken ones (seven studies, per the abstract). Engagement, not learning outcomes. |

## 2. Unverified leads (not to be cited as read)

- Ebbinghaus (1885), *Über das Gedächtnis*: classic source; not opened.
- Leitner box system, Pimsleur graduated interval recall, SuperMemo SM-2: commonly cited scheduler families; not opened.
- Revisiting half-life regression (PMLR v339, listed in search results at https://proceedings.mlr.press/v339/ilidio26a.html): not opened.
- Literature on gamification and learning outcomes (meta-analyses), and on engagement metrics versus learning: to search in M1.

## 3. Known work and narrow contribution (draft, to be revised in M1)

Known: spacing and retrieval practice improve retention; trainable and optimised spaced-repetition schedulers exist; streaks raise engagement as goals in themselves. Apparent gap, **not yet established by a documented search**: a controlled simulation that holds practice minutes fixed and isolates whether streak-driven scheduling (daily activity plus easy-item selection) can raise activity metrics while retention stays equal or falls, with a timing versus selection decomposition and an explicit test of the model assumption that drives the result. No novelty is claimed until the M1 search is complete.
