# SEP Wording and Trend Preservation Report

## 1. Scope

This Mini Batch freezes conservative SEP wording and preserves the result-level value of the registered SEP-oriented trends. It does not revalidate the SEP matrix, search for historical caches, run experiments, alter values, add metrics, or render figures. Batch 1C files remain unchanged.

## 2. Frozen SEP Position

The dissertation uses the following position consistently in the revised Chapter 3-5 copies, formula inventory, tables, and captions:

> SEP is a repository-specific bridge-entity score.

> SEP follows the XRecSys-style explanation-metric setting but is interpreted here through the implemented repository metric pipeline.

SEP is used as an operational explanation-side metric rather than as direct evidence of user-perceived serendipity. The dissertation does not independently validate the semantic direction of SEP against user perception or external serendipity judgments.

## 3. Chapter 3 Wording Freeze

The abstract formula remains

\[
\mathrm{SEP}(p_{u,i})
=
\sigma_d(b(p_{u,i})),
\quad
\sigma_d(\cdot) \in [0,1].
\]

The revised explanation defines \(\sigma_d\) as the repository-specific bridge-entity score used by the implemented SEP metric. Current-generator and historical-cache discussion has been removed from the main Chapter 3 body. The historical artifact caveat remains in limitations and status documentation.

## 4. Chapter 4 Trend Preservation

Chapter 4.5 remains a dedicated SEP-oriented result section. Its existing LastFM and ML-1M values and comparisons are unchanged. The revised prose makes three result-level points:

1. SEP-oriented results describe movement along the implemented SEP objective.
2. Several models show substantial SEP movement while paired sweep NDCG changes at different rates.
3. The SEP curves are useful for analysing framework controllability under an explanation-side objective.

The SEP-oriented sweep provides one of the clearest empirical trade-off profiles in the alpha-sweep results. This statement concerns the visual and descriptive pattern in the registered curves, not statistical significance or overall explanation superiority.

## 5. Figure Placement

Figure 4.5 is frozen as main-text Chapter 4.5 evidence. It is no longer described as optional or an appendix candidate. Its source paths and experimental content are unchanged.

The frozen decision is:

> SEP-NDCG trade-off curve should remain in the main Chapter 4 evidence stream because it provides a visually clear example of implemented objective movement under the alpha-sweep design.

## 6. Chapter 5 Boundary

Chapter 5 states that SEP is adopted as an implemented explanation-side metric rather than independently validated as a user-perceived serendipity construct. It also preserves that LIR / SEP / ETD exact implementation is repository-specific. No SEP trend is converted into a causal mechanism claim.

## 7. Formula, Table, and Caption Updates

The SEP formula-inventory row now uses “repository-specific bridge-entity score following XRecSys-style metric setting,” with confidence “implemented metric available; semantic direction conservatively bounded.” The caveat records that the historical cached SEP matrix is unavailable and that no direct user-perceived serendipity claim is made.

Table notes and captions use “SEP denotes the implemented repository-specific bridge-entity score.” Figure 4.5 explicitly identifies paired NDCG as alpha-sweep evidence rather than strict NDCG@10 and retains the analytical value of movement along the implemented SEP objective.

## 8. Single-Example Trace Notation

The new isolated copy `SINGLE_EXAMPLE_TRACE_SEP_TREND.md` changes the schematic top-k position from `i*` to `j*`. All other abstract placeholders remain unchanged, and no real identifier is introduced.

| Field | Frozen placeholder |
| --- | --- |
| canonical uid | `u*` |
| recommended pid | `recommended_item*` |
| top-k position | `j*` |

## 9. Removed or Avoided Wording

The revised outputs do not claim that:

- higher SEP always means a lower-degree bridge entity;
- higher SEP proves greater rarity or serendipity;
- SEP directly measures user-perceived serendipity;
- SEP improvement means explanation-quality improvement; or
- SEP direction is fully verified from historical cached matrices.

## 10. Remaining Caveat

The historical cached SEP matrix is not available in the current evidence package. This Mini Batch freezes conservative semantic wording rather than closing historical artifact provenance. No direct user-perceived serendipity, novelty, usefulness, surprise, or explanation-quality claim is supported.
