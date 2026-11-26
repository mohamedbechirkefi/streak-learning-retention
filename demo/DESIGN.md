<!-- SPDX-License-Identifier: LicenseRef-STREAK-NC-Research-1.0 -->
# Design plan: the STREAK demo page

Owner request of 2026-11-26: every lab demo gets its own brand, motion and premium UI. This plan replaces the shared editorial look of the earlier page.

## Subject, audience, job

- **Subject.** Activity streaks against retention. The vernacular is two school objects that measure different things: the habit calendar on the fridge (a square filled for every day practised, the streak as an unbroken run) and the teacher's grade book (one row per item, a mark when it was tested, the grade that matters weeks later). The study's finding lives exactly between them: a calendar can be full while the grade book is thin.
- **Audience.** A curious technical reader; an admissions committee skimming for rigour; a researcher who wants every estimate, interval, assumption and limitation.
- **Primary job.** Say the question and the answer in one sentence, show the key result as a grade book (attendance against the grade 30 days later), then give the evidence, the playground, the limitations and the way to reproduce.

## Colour (light only: the brand is daylight on a school desk)

| Name | Hex | Role |
|---|---|---|
| Window white | `#FFFDF7` | page ground: sunlit paper, nearly white, not cream |
| Marigold | `#F2A900` | the streak: filled calendar days, the logo, the hero fill; never text |
| Grade-book green | `#17624A` | headings, links, the primary button, the A1 Fixed ink |
| Pencil lead | `#29262F` | body text (secondary text `#5A5560`) |
| Ruling sage | `#CFE2D6` | ruled lines of the grade book and chart grids; decoration only |
| Red pen | `#B4233A` | the teacher's correction: the fade annotation, the focus ring, negative-result marks |

Supporting tints: butter `#FFF2CC` (the hero desk and highlighted rows), sage wash `#EEF5F0` (table header bands). Arm colours for data marks: A0 graphite `#7C7782`, A1 grade-book green `#17624A`, A2 marigold-dark `#B07800` (3:1 against white for marks; the bright marigold stays decorative), A3 slate blue `#2F62A8`. Every arm also keeps a marker shape and a dash pattern, so colour never carries meaning alone.

## Type

- **Bricolage Grotesque** (variable, optical size 12 to 96, weights 500 to 800; OFL): the wordmark, headings and the big figures. A grotesque with ink traps and a slightly hand-cut warmth, like the stencil numerals of a classroom wall calendar. Its optical-size axis lets the hero headline tighten at display size.
- **Nunito Sans** (variable, 400 to 700, roman and italic; OFL): body, tables, controls, chart labels. A humanist sans with softened terminals, the friendly worksheet voice of a classroom without the toy look of a rounded display face. Its figures are tabular by default, so every column of numbers aligns.

Scale (ratio about 1.25): 14 px chart labels, 15 px meta, 17 px body, 21 px lede, 26 px h3 and report-card figures, 34 px h2, clamp(36 px, 5.4vw, 64 px) hero. Prose capped at 66 characters.

## Layout concept

Left-aligned, one 74 rem column, prose at 40 rem. The sticky bar carries the lockup and the section links with a marigold indicator that slides to the section being read.

```
+--------------------------------------------------------------------------+
| [mark] Streak    Answer  Report card  Evidence  Results  Playground ...  |  sticky bar
+--------------------------------------------------------------------------+
| When can activity streaks diverge       | Illustration, not study data   |
| from knowledge retention in a           | calendar  [#][#][#][#] ... 28  |  day squares fill
| learning model?                         | items     [x][x][ ][x] ...     |  ticks land on 3 rows
|                                         |           [ ][ ][ ][ ] ...     |  unpractised rows fade
| Answer sentence (bold lede)             | "a full calendar,              |
| status line, author line                |  a thin grade book"            |
+-----------------------------------------+--------------------------------+
| REPORT CARD (key result, a grade book):                                  |
| policy    | days practised (56 squares)       | streak | R30 bar + CI    |
| A1 Fixed  | ##########............            | 1.88   | ======== 0.7931 |
| A2 Streak | ####################....          | 16.24  | ====     0.4863 |
| three margin notes with the measured EXP-001 figures                     |
+--------------------------------------------------------------------------+
| Evidence: streak vs recall [Active days | Longest streak] segmented      |
| Memory curves (model) | Real data test (negative)                        |
| Published results: one ruled grade-book sheet per experiment             |
| Playground (a dashed desk tray) | Assumptions | Method and limitations  |
| Reproduce (commands) | Footer: links, licence, AI use, font credits      |
+--------------------------------------------------------------------------+
```

Panels are sheets of a grade book: white paper on the window-white desk, a sage ruling, a thin red margin line on the left of the sheet only where the sheet holds results (the teacher's margin). Corner radius is small on sheets (6 px) and larger on controls (10 px), so hierarchy reads from shape.

## Motion

- **One orchestrated hero moment (about 2.8 s, once on load).** A 28-day habit calendar fills square by square in marigold (35 ms stagger, 220 ms strong ease-out, transform and opacity). With each day a pencil tick lands in the grade book underneath, always on the same three easy rows. When the calendar is full, the five rows that were never reviewed fade (opacity 1 to 0.22, 70 ms stagger) and a red-pen bracket marks them. Labelled visibly "Illustration, not study data"; it shows no number except the day labels 1 and 28, which are a real sequence.
- **Answers to the visitor.** The section indicator in the sticky bar slides (transform, 260 ms). The segmented control's thumb slides between "Active days" and "Longest streak" (220 ms). Charts reveal once when scrolled into view: lines draw left to right with a `clip-path` wipe (700 ms), marks fade in with a 40 ms stagger. Report-card strips grow from the left (scaleX, 600 ms) once. Sandbox: the Run button presses (scale 0.97, 120 ms), progress fills, the result sheet enters with `@starting-style` (opacity and 8 px rise, 260 ms), and the timeline bars grow from the baseline with a 6 ms per-day stagger.
- **Rules.** Transform, opacity and clip-path only; `cubic-bezier(0.23, 1, 0.32, 1)` for entrances, `cubic-bezier(0.77, 0, 0.175, 1)` for indicators that move on screen. Hover motion only under `(hover: hover) and (pointer: fine)`. Under reduced motion everything is shown in its final state with no transform; nothing loops.

## The one memorable thing

The hero grade book: a calendar that fills completely while most of the grade book fades. It is the study's mechanism in one picture (a streak counts days, retention depends on which items are practised), and it reappears as the report card, where attendance and the grade sit side by side.

## Review against the brief and the generated-page tells

| Check | First draft | Revision |
|---|---|---|
| Cream plus terracotta | warm ground `#FBF6EA` with a clay-orange streak colour | ground moved to near-white `#FFFDF7`, streak colour is marigold, the only red is a cool crimson pen used for corrections and focus |
| Serif display on warm ground | an old-style serif for headings, as in the old page | grotesque display (Bricolage Grotesque); no serif anywhere |
| All-caps tracked eyebrows | evidence labels as uppercase chips above every heading | labels kept (they carry the evidence class, a test of honesty) but set in sentence case, as a coloured tab on the sheet margin, not as an eyebrow |
| Mono data labels | none planned | none: all figures in Nunito Sans, whose figures are tabular by default |
| 01/02/03 markers | experiments numbered in the margin | removed; EXP ids are real identifiers and stay in the heading |
| Identical rounded SaaS cards | the three key facts as three cards | they became margin notes under the report card, separated by rules, not boxes |
| Fade-up on every section | scroll reveals on all sections | only charts and the report card reveal, because their drawing shows the data; text never animates |
| Body face with slashed zeros | Atkinson Hyperlegible Next for body text | first screenshot: its slashed zero made every table read like monospace code (a generated-page tell); replaced by Nunito Sans, tabular by default and with a plain zero |
| Generic big-number hero | a large "-0.3068" in the hero | removed from the hero; the hero is the illustration and the sentence, the number lives in the report card with its interval |
| UI-UX search output | claymorphism, amber plus emerald, Baloo 2 with Comic Neue | rejected as a children's-app look; kept only the warm daylight light theme and the 44 px touch targets |

Against the other demos: MEMORY (cool sea-glass paper, ink blue, a slab serif, index cards in boxes) is the closest subject; STREAK stays warm, sans-serif, and is built from day squares and grade-book rows rather than cards and curves. FARE, SCROLL and TOKEN use dark or instrument looks; STREAK is the only daylight calendar.
