# Citation and Provenance TODO

## 1. Must Fix Before Final Submission

- [ ] Task: Recover or formally archive the 12 expected LastFM/ML-1M strict-accuracy JSON artifacts.
  - Affected files: `runs/debug_compare/2026-06-20_native_path_expansion/**/accuracy.json`; final evidence archive; Chapter 4 provenance notes.
  - Reason: All 12 expected primary paths are absent, so primary-artifact verification is incomplete.
  - Evidence: `STRICT_ACCURACY_PROVENANCE_CLOSURE.md`; `reports/tables/canonical_native_path_status_matrix.csv`.
  - Priority: critical

- [ ] Task: Remove the mislabelled `wang2018pgpr` key from the final dissertation bibliography and citation calls.
  - Affected files: final bibliography; future Chapter 1-2 drafts; any Chapter 3-5 citation insertion pass.
  - Reason: arXiv:1811.04540 is KPRN, not PGPR.
  - Evidence: `EXTERNAL_CITATION_AUDIT_VERIFIED.md`; `BIBTEX_VERIFICATION_NOTES.md`.
  - Priority: high

- [ ] Task: Preserve a final immutable citation and evidence snapshot with hashes.
  - Affected files: final evidence manifest; bibliography; canonical status matrix; recovered accuracy JSON files.
  - Reason: The final submission package needs reproducible source identity, not path references alone.
  - Evidence: `STRICT_ACCURACY_PROVENANCE_CLOSURE.md`; `reports/tables/canonical_native_path_artifact_manifest.json`.
  - Priority: high

## 2. Should Fix Before Supervisor Review

- [ ] Task: Manually verify whether PEARLM has a stable final proceedings DOI.
  - Affected files: `BIBTEX_VERIFIED_OR_REQUIRES_CHECK.bib`; future Chapters 1, 2, 3, and 5 citations.
  - Reason: The arXiv record is verified, but a retrieved conference-formatted version retained DOI placeholders.
  - Evidence: arXiv:2310.16452; `BIBTEX_VERIFICATION_NOTES.md`.
  - Priority: medium

- [ ] Task: Manually verify whether the "Measuring Why" survey has a final publisher record.
  - Affected files: `BIBTEX_VERIFIED_OR_REQUIRES_CHECK.bib`; future literature-review text.
  - Reason: Only arXiv:2202.06466 was verified.
  - Evidence: `EXTERNAL_CITATION_AUDIT_VERIFIED.md`; DBLP CoRR record.
  - Priority: low

- [ ] Task: Review future Chapter 1-2 prose for external-literature versus internal-experiment evidence separation.
  - Affected files: future Chapter 1 and Chapter 2 drafts.
  - Reason: Model papers establish background and mechanisms but do not verify this repository's results.
  - Evidence: `CITATION_PROVENANCE_CLOSURE_REPORT.md`; `THESIS_WRITING_TRACEABILITY_LOG.md`.
  - Priority: high

## 3. Safe to Defer as Limitation

- [ ] Task: Add statistical-significance analysis only if an approved artifact becomes available.
  - Affected files: Chapter 4 results; Chapter 5 limitations; Chapter 6 recommendations.
  - Reason: No statistical-significance artifact is registered.
  - Evidence: `UNSUPPORTED_CLAIMS_CHECK.md`; `THESIS_WRITING_TRACEABILITY_LOG.md`.
  - Priority: medium

- [ ] Task: Add user-centred evaluation only as a future study unless an approved user-study artifact is produced.
  - Affected files: Chapter 5 limitations; Chapter 6 recommendations.
  - Reason: No user-study evidence exists in the current package.
  - Evidence: `UNSUPPORTED_CLAIMS_CHECK.md`; `GOAL_5_STATUS.md`.
  - Priority: medium

## 4. Bibliography Cleanup Tasks

- [ ] Task: Convert all in-text citation placeholders to the verified citation keys during the final bibliography pass.
  - Affected files: future integrated dissertation source; `BIBTEX_VERIFIED_OR_REQUIRES_CHECK.bib`.
  - Reason: The current Chapter 3-6 package intentionally preserves citation status rather than inserting final formatted citations.
  - Evidence: `BIBTEX_VERIFICATION_NOTES.md`; `REVISION_TODO.md`.
  - Priority: high

- [ ] Task: Apply the NTU-required bibliography style only after metadata and citation-key review.
  - Affected files: future Word/LaTeX dissertation package.
  - Reason: Formatting before metadata freeze risks propagating the old PGPR/KPRN mismatch.
  - Evidence: `BIBTEX_VERIFICATION_NOTES.md`.
  - Priority: medium

## 5. Provenance Archiving Tasks

- [ ] Task: Archive the exact comparison command showing equality between the canonical CSV and dissertation summary rows.
  - Affected files: future reproducibility appendix or evidence manifest.
  - Reason: The current cross-check passed but is not yet part of an immutable submission archive.
  - Evidence: `STRICT_ACCURACY_PROVENANCE_CLOSURE.md`.
  - Priority: medium

- [ ] Task: Record evaluator version, export hashes, command line, and environment for each recovered accuracy JSON.
  - Affected files: final reproducibility manifest and appendix.
  - Reason: File recovery alone does not establish reproducible lineage.
  - Evidence: `scripts/validation/evaluate_uid_topk.py`; `reports/tables/canonical_export_validation/manifest.json`.
  - Priority: high
