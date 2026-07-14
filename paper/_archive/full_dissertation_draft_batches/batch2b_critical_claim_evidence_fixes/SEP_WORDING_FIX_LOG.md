# SEP Wording Fix Log

## 1. Scope

The SEP audit covered revised Chapters 1, 2, and 6 using the required search terms: `SEP`, `serendipity`, `rarity`, `novelty`, `surprising`, `usefulness`, `explanation quality`, `degree-derived`, `bridge entity`, and `XRecSys`. Chapters 3–5 were checked to ensure that their frozen operational wording and strong empirical trend statements remained intact.

## 2. Fixes Applied

| Chapter | Issue found | Fix applied | Evidence boundary after fix |
| --- | --- | --- | --- |
| Chapter 1 | SEP was introduced as "shared entity popularity or serendipity," which was broader than the implemented construct. | Replaced the name with "repository-specific bridge-entity score" and stated that SEP is an operational explanation-side metric rather than direct evidence of user-perceived serendipity. | XRecSys remains the conceptual source; exact formulas and data assumptions remain repository-specific. |
| Chapter 2 | SEP was said to concern "rarity or serendipity" under the implementation. | Reframed XRecSys as metric-setting inspiration, defined SEP as the implemented repository-specific bridge-entity score, and stated that the dissertation does not independently validate a user-perceived serendipity construct. | Literature context and repository implementation remain separate evidence sources. |
| Chapter 6 | SEP was described as "degree-derived serendipity of the bridge entity." | Replaced it with the repository-specific bridge-entity score, retained clear movement along the implemented SEP objective, and explicitly excluded direct user-perceived serendipity and explanation-quality interpretations. | The conclusion retains strong operational trend language without strengthening semantic claims. |

## 3. Wording Preserved

Chapter 4 continues to state that the SEP-oriented sweep provides one of the clearest empirical trade-off profiles. It reports movement along the implemented SEP objective and keeps paired sweep NDCG separate from strict NDCG@10. The registered values and trends were not changed.

Chapter 3 continues to define SEP through the implemented repository metric pipeline. Chapter 5 continues to identify the unavailable historical SEP cache and the absence of independent user-perception validation as limitations.

## 4. Verification Result

No revised chapter contains any of the following forbidden statements:

- higher SEP always means a lower-degree bridge entity;
- higher SEP proves rarity, novelty, usefulness, serendipity, or explanation quality;
- SEP directly measures user-perceived serendipity;
- SEP improvement means explanation-quality improvement;
- degree-derived serendipity;
- rarity-oriented SEP.

Generic literature discussion of structural rarity, usefulness, or surprising explanations was retained only where it does not define the implemented SEP metric.
