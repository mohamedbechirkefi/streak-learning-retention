<!-- SPDX-License-Identifier: LicenseRef-STREAK-NC-Research-1.0 -->
# Claims audit checklist

Status at M0: no claims exist; `research/claims_register.csv` has only its header.

For every claim before release:

- [ ] Each numerical claim maps to a result ID, run IDs, config and figure in `artifact_manifest.json`.
- [ ] Each external claim maps to a source actually opened (`research/literature_review.md`), with verification level stated.
- [ ] Type (observed, inferred, simulated, external), scope and limitations recorded.
- [ ] No claim about real human learning efficacy, proprietary systems or causal human behaviour.
- [ ] Numbers re-audited against raw outputs: denominators, units, precision, uncertainty, sample counts.
- [ ] Second review pass that challenges the preferred hypothesis completed and recorded.
- [ ] Unsupported claims removed or qualified.
