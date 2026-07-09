
# Goal 13: Limitations and Risks

## Current Task

List limitations that must be stated honestly in the dissertation and phrase them as framework boundaries or future work rather than hidden failures.

| Limitation | Why it matters | How dissertation should phrase it | Evidence file path | Suggested future work |
| --- | --- | --- | --- | --- |
| Amazon-Book KGAT is partial, not a complete six-model explanation experiment | Only KGGLM, PEARLM, and PGPR have complete formal rows; UCPR/CAFE/TPRec are blocked. | Frame Amazon as a boundary/stress test for the framework. | reports/tables/canonical_native_path_status_matrix.md; reports/tables/amazon_classic_port_readiness.json | Port UCPR/CAFE safely and resolve TPRec timestamp protocol before formal reporting. |
| Amazon explanation alpha sweeps are N/A | Current docs state no approved timestamp/SEP/ETD denominator exists. | Do not report LIR/SEP/ETD alpha-sweep values for Amazon. | docs/guides/CANONICAL_NATIVE_PATH_COMPLETION_AUDIT_2026-06-27.md; docs/guides/CANONICAL_NATIVE_PATH_HANDOFF_2026-06-27.md | Define an approved timestamp and path-type denominator protocol. |
| Non-path models are excluded from explanation scoring | Post-hoc paths would not faithfully represent the model decision process. | Use non-path models only as accuracy references or appendix context. | `README.md`; docs/guides/NATIVE_PATH_EXPERIMENT_ARCHITECTURE_2026-06-11.md; docs/guides/NATIVE_PATH_MODEL_CANDIDATE_AUDIT_2026-06-21.md | Add only models with auditable native recommendation paths. |
| Strict accuracy and alpha-sweep metric columns have different evidence roles | Status-matrix accuracy values come from per-row accuracy JSON; alpha-sweep CSVs support trade-off analysis. | Keep final accuracy tables separate from explanation trade-off figures. | `reports/tables/canonical_native_path_status_matrix.csv`; canonical trade-off CSV bundles | Document metric provenance in captions and table notes. |
| Short or empty recommendation lists can occur under native-path candidate exhaustion | The framework counts missing slots as non-hits rather than padding with non-path recommendations. | Describe this as faithful native-path evaluation behavior. | docs/guides/CANONICAL_DATASET_STANDARD.md; `scripts/validation/evaluate_uid_topk.py` | Report slot coverage and short-user counts alongside accuracy where relevant. |
| Historical/archive materials are not current source of truth | Older handoffs and duplicate figure folders can conflict with current reports. | Use completion audit, status matrix, validation manifest, and artifact manifest as primary evidence. | docs/guides/CANONICAL_NATIVE_PATH_COMPLETION_AUDIT_2026-06-27.md; reports/tables/canonical_native_path_status_matrix.md; reports/tables/canonical_native_path_artifact_manifest.json | Keep archive material in appendix only when needed for provenance. |
