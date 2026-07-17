# DOCX V3 Numeric Precision Report

## 1. Policy

Main-text metrics use at most three decimal places, percentages use two decimal places, and explicit alpha assignments use two decimal places. Main-text values are rounded for readability. Full precision remains available in the registered evidence files and build reports.

## 2. Global Numeric Scan

| Category | Original pattern count | Normalised count | Notes |
|---|---:|---:|---|
| percentage | 4 | 4 | Presentation-layer normalisation only |
| metric/general decimal | 202 | 202 | Presentation-layer normalisation only |
| alpha | 34 | 34 | Presentation-layer normalisation only |
| Table 5.1 percentage fields | 24 | 24 | Rounded to two decimals during table simplification |

## 3. Representative Changes

| Location | Original | V3 presentation | Reason |
|---|---|---|---|
| Source line 69 | `alpha=0` | `alpha=0.00` | alpha policy |
| Source line 578 | `0.0062` | `0.006` | metric/general decimal policy |
| Source line 578 | `0.0219` | `0.022` | metric/general decimal policy |
| Source line 578 | `0.4655` | `0.466` | metric/general decimal policy |
| Source line 578 | `0.9627` | `0.963` | metric/general decimal policy |
| Source line 578 | `alpha=0` | `alpha=0.00` | alpha policy |
| Source line 578 | `alpha=1` | `alpha=1.00` | alpha policy |
| Source line 596 | `alpha=0` | `alpha=0.00` | alpha policy |
| Source line 664 | `alpha=1` | `alpha=1.00` | alpha policy |
| Source line 666 | `alpha=0` | `alpha=0.00` | alpha policy |
| Source line 674 | `alpha=1` | `alpha=1.00` | alpha policy |
| Source line 676 | `alpha=0` | `alpha=0.00` | alpha policy |

## 4. Values Not Changed

| Pattern | Reason |
|---|---|
| Integer IDs, years, row counts, dataset sizes, and top-k values | These are identifiers or counts rather than presentation decimals. |
| DOI, URL, citation key, file name, and evidence path tokens | Protected from numeric rewriting. |
| Values already within policy | No presentation change required. |

## 5. Risks and Safeguards

- Source Markdown, BibTeX, and evidence files were not modified.
- Rounding occurs only in the V3 intermediate manuscript and DOCX.
- Long decimal values remaining in main text: 0.
- Values with more than 3 decimal places in prose/tables: 0, excluding protected DOI/path/file-name tokens.
