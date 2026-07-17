# DOCX V3 Cohesion and Coherence Report

## 1. Scope

Applied 22 targeted presentation-layer prose revisions. No experimental result, evidence status, citation meaning, chapter boundary, or conclusion direction was changed.

## 2. Chapter-level Changes

| Chapter | Repetition reduced | Cohesion/coherence action | Claim boundary preserved |
|---|---|---|---|
| Chapter 1 | Removed one repeated new-model disclaimer | Preserved background → motivation → objectives → contribution flow | Yes |
| Chapter 2 | Kept synthesis table concise | Retained chapter-end gap and positioning | Yes |
| Chapter 3 | Shortened repeated workflow/boundary reminders | Preserved canonical data → model views → export → validation → metrics → setup flow | Yes |
| Chapter 4 | Replaced repeated strict-vs-sweep warnings with short reminders after the first full statement | Preserved strict accuracy → endpoints → LIR → SEP → ETD → cross-dataset order | Yes |
| Chapter 5 | Shortened repeated Amazon and mechanism caveats | Preserved ablation → mechanism context → interaction → boundary → limitations flow | Yes |
| Chapter 6 | Added one explicit synthesis transition | Preserved objective closure and recommendation derivation | Yes |

## 3. Repeated Phrases Audited

| Phrase / theme | Original issue | V3 treatment |
|---|---|---|
| `does not propose a new recommender model` | 2 occurrences | 1 occurrences; full boundary retained where substantively required |
| `not strict NDCG@10` | 0 occurrences | 0 occurrences; full boundary retained where substantively required |
| `partial boundary case` | 10 occurrences | 8 occurrences; full boundary retained where substantively required |
| `statistical-significance artifact` | 3 occurrences | 2 occurrences; full boundary retained where substantively required |
| `user-study artifact` | 4 occurrences | 4 occurrences; full boundary retained where substantively required |
| `descriptive rather than causal` | 2 occurrences | 1 occurrences; full boundary retained where substantively required |

## 4. Boundary Claims Preserved

| Boundary | Preserved wording strategy |
|---|---|
| SEP semantic scope | First full statement retained; later mentions use operational-score reminders. |
| Strict accuracy versus alpha sweep | Full separation retained in Chapter 3/4; later captions use short reminders. |
| Amazon-Book KGAT | Remains a partial stress test/boundary case with 3 PASS and 3 BLOCKED / N/A rows. |
| Statistical significance and user study | Both missing-artifact caveats remain explicit in Chapters 5 and 6. |
| Causal mechanism | Stronger claims remain limited to registered PGPR/UCPR ablation scope. |

## 5. Risk Check

| Risk | Result | Notes |
|---|---|---|
| Supported caveat removed | PASS | No supported caveat was removed. |
| Unsupported stronger claim introduced | PASS | No unsupported stronger claim was introduced. |
| Chapter transitions obscured | PASS | Chapter transitions remain explicit. |
