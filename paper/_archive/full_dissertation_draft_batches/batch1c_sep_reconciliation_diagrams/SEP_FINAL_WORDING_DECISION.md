# SEP Final Wording Decision

## 1. Decision

The accessible implementation does not support the claim that higher SEP means a lower-degree bridge entity. The guide wording appears stale relative to the current generator and the XRecSys README. Historical matrix artifacts are unavailable, so the final interpretation remains bounded pending manual artifact verification.

The Batch 1C wording decision is:

> SEP is a repository-specific degree-derived bridge-entity score.

## 2. Allowed Wording

- “SEP is a repository-specific degree-derived bridge-entity score.”
- “The SEP value is retrieved from the bridge entity at the penultimate path position.”
- “The accessible SEP optimiser favours larger stored SEP matrix values.”
- “The registered SEP endpoints show movement in the repository-specific score under the SEP-oriented sweep.”
- “The accessible generator is rank-weighted after ascending degree sorting, but the exact historical cached matrices require manual verification.”
- “SEP is reported as a computational path property and not as user-perceived explanation quality.”

## 3. Wording to Avoid

- “higher SEP always means lower-degree bridge entity”
- “SEP proves greater rarity”
- “SEP proves greater serendipity, novelty, unexpectedness, usefulness, or explanation quality”
- “the registered historical SEP matrix was verified from its primary cache”
- “guide and implementation are fully reconciled”

The following wording is not allowed unless the original matrix and generator provenance are recovered and shown to implement it:

> SEP operationalises bridge-entity rarity, with lower-degree bridge entities receiving higher weights under the repository implementation.

## 4. Required Updates to Chapter 3

1. Replace “serendipity of the bridge entity” and “bridge-entity rarity” with “repository-specific degree-derived bridge-entity score”.
2. Retain the verified bridge-anchor lookup \(b(p)=e_{L-1}\) and the abstract lookup \(\mathrm{SEP}(p)=\sigma_d(b(p))\).
3. State that \(\sigma_d\)'s exact historical matrix content requires manual verification.
4. State that the accessible generator assigns increasing rank-based EMA weights after ascending degree sorting.
5. Add the metric-anchor schematic with the downgraded SEP wording.

## 5. Required Updates to Chapter 4

1. Retain every registered SEP endpoint and sweep value unchanged.
2. Describe endpoint changes as SEP-score movement rather than rarity or serendipity gains.
3. Replace claims about favouring rarer bridge entities with claims about favouring larger repository-specific SEP weights.
4. Preserve result-level interpretation and avoid causal or user-facing conclusions.
5. Keep the historical-matrix verification caveat visible in Sections 4.3 and 4.5.

## 6. Required Updates to Tables / Captions

1. Define SEP as a repository-specific degree-derived bridge-entity score.
2. Mark the bridge anchor and runtime lookup as verified.
3. Mark the historical matrix direction as requiring manual verification.
4. Avoid “rarity-oriented” and “serendipity-oriented” in figure captions unless explicitly attributed to stale guide semantics.
5. Preserve strict-accuracy, alpha-sweep, ablation, and boundary-case separation.

## 7. Remaining Caveat

The current generator and optimiser direction are statically traceable, but the cached `sep_matrix.pkl` files used by the registered historical sweeps are unavailable. Batch 1C therefore resolves the safe dissertation wording but does not close historical matrix provenance. Final wording freeze requires the checklist in `SEP_RECONCILIATION_REPORT.md`.
