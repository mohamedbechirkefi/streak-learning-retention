<!-- SPDX-License-Identifier: LicenseRef-STREAK-NC-Research-1.0 -->
# Test fixtures

`duolingo_synthetic.csv` is invented: twelve rows in the schema of the Duolingo half-life regression traces (Settles and Meeder 2016), with made-up user ids (`synthU01` to `synthU10`), languages (`xx`, `yy`) and lexemes. It contains no real row. It exercises every validation and exclusion path of `streak.duolingo.ingest`; the expected counts are asserted in `tests/test_duolingo.py`.
