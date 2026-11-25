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

## 4. M4 source check (2026-11-25)

Every external statement in the manuscript and the experiment reports was checked against what was actually read. Sources opened on 2026-11-25:

| Key | What was read on 2026-11-25 | Verification level now | What the manuscript may say |
|---|---|---|---|
| settles2016 | Full text, ACL Anthology PDF https://aclanthology.org/P16-1174.pdf (text extracted locally with pypdf; sections 3.3 and 4.1 and Table 2 read). Equation (1): "p = 2^(-Δ/h)", introduced as the Ebbinghaus model in which "memory decays exponentially over time". Section 4.1: "two weeks of Duolingo log data, containing 12.9 million student-word lesson and practice session traces". Table 2 and text: the two HLR variants "are the only two approaches with MAE lower than a baseline constant prediction of the average recall rate in the training data" (constant p̄ = 0.859, MAE 0.175; HLR 0.128; Leitner 0.235; Pimsleur 0.445). | **Full text read (relevant sections)** | The exponential half-life form of the default model; the data source; that in the original evaluation a constant baseline outperformed several established schedulers on MAE. |
| cepeda2006 | Abstract, Europe PMC REST record (PMID 16719566): "839 assessments of distributed practice in 317 experiments located in 184 articles"; "the ISI producing maximal retention increased as retention interval increased". | **Abstract only** | That a quantitative synthesis reported spacing and lag effects and the joint dependence of the optimal interstudy interval on the retention interval. Nothing beyond the abstract. |
| roediger2006 | Abstract, Europe PMC REST record (PMID 16507066): at a 5-minute final test "repeated studying improved recall relative to repeated testing"; "on the delayed tests, prior testing produced substantially greater retention than studying". | **Abstract only** | That testing improved delayed retention relative to restudy in two experiments with prose passages. |
| tabibian2019 | Abstract, Europe PMC REST record (PMID 30670661): for two memory models, "the optimal reviewing schedule is given by the recall probability itself"; a natural experiment on Duolingo data. | **Abstract only** | That optimal-control scheduling (MEMORIZE) reviews according to recall probability. |
| murre2015 | Abstract on the PLOS ONE article page (https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0120644): "a successful replication of Ebbinghaus' classic forgetting curve"; the curve "most probably shows a jump upwards starting at the 24 hour data point". | **Abstract only** (the page holds the full text; only the abstract was read) | That a savings-based replication reproduced the Ebbinghaus curve. Not used for any claim about the best-fitting functional form. |
| silverman2022 | Abstract (read 2026-11-24, University of Delaware repository record). | **Abstract only** | That intact streaks increased subsequent engagement relative to broken ones, as an engagement (not learning) finding. |
| fsrs-wiki | Page read 2026-11-24. | **Page read** | That FSRS uses power-law forgetting curves; the STREAK power-law variant is a simplified single curve, not FSRS. |
| ye2022 | Not opened beyond metadata. | **Metadata only** | Cited only as an example of scheduler optimisation work, with no statement about its content. |

**Correction applied in M4.** Earlier text (EXP protocols and reports) used sentences such as "retrieval practice strengthens memory (Roediger and Karpicke 2006)" and "spacing improves long-term retention (Cepeda et al. 2006)" while only metadata had been verified. These sentences now rest on the abstracts read above and are worded in the manuscript as what those abstracts report. One overstatement remains in the reports: "spacing improves long-term retention (Cepeda et al. 2006)" (EXP-001) and "supports spacing benefits" (EXP-003). The abstract read says that spacing and lag effects were examined and that the optimal interstudy interval grows with the retention interval; it does not state the direction of the spacing effect in the sentences read. Each report receives an M4 audit note qualifying the citation; the frozen protocols are not edited.
