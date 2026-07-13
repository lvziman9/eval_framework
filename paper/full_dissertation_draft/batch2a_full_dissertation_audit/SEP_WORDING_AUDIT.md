# SEP Wording Audit

The safe interpretation is deliberately narrow: SEP is a repository-specific bridge-entity score used as an operational explanation-side metric in an XRecSys-style setting. The audit preserves strong empirical trend statements while rejecting unverified semantic direction and user-perceived interpretations.

| Location | Wording found | Risk | Keep / revise | Suggested revision |
| --- | --- | --- | --- | --- |
| Chapter 1, Section 1.1 | "shared entity popularity or serendipity (SEP)" | Medium | Revise | "the repository-specific shared-entity or bridge-entity score (SEP)" |
| Chapter 1, Section 1.1 | A visible path is not automatically "serendipitous" | Low | Keep | This is a general warning, not a claim that SEP directly measures serendipity. |
| Chapter 2, Section 2.3 | "SEP concerns the rarity or serendipity associated with the bridge entity" | High | Revise | "SEP denotes the repository-specific bridge-entity score used by the implemented explanation-metric pipeline." |
| Chapter 3, Section 3.4 | "repository-specific bridge-entity score" and "operational explanation-side metric" | Low | Keep | No change. This is the frozen semantic position. |
| Chapter 3, Section 3.4 | SEP is not "an independently validated measure of user-perceived serendipity" | Low | Keep | No change; retain the explicit exclusion. |
| Chapter 4, Section 4.5 | "movement along the implemented SEP objective" | Low | Keep | No change; this safely describes the observed sweep. |
| Chapter 4, Section 4.5 | SEP provides one of the clearest empirical trade-off profiles | Low | Keep | Keep with model, dataset, endpoint, and paired sweep-NDCG context. |
| Chapter 4, Section 4.5 | SEP movement does not establish perceived surprise, usefulness, or higher explanation quality | Low | Keep | No change; retain the caveat beside the trend claim. |
| Chapter 5, Sections 5.3 and 5.5 | SEP is an implemented explanation-side metric and not an independently validated user construct | Low | Keep | No change. |
| Chapter 6, Section 6.1 | "SEP uses degree-derived serendipity of the bridge entity" | High | Revise | "SEP uses the repository-specific bridge-entity score implemented by the registered metric pipeline." |
| V5 formula inventory and corrected single-example materials | "degree-derived bridge-entity score" appears in explanatory interpretation | Medium | Revise before integration | Prefer "repository-specific bridge-entity score" unless degree provenance is required and separately caveated. |
| Earlier Batch 1C Chapter 3 and table sources | Degree/popularity/serendipity proxy language and historical direction discussion | High if reused | Exclude or revise at source-selection stage | Use V5 frozen wording as the only supervisor-facing source; retain cache-direction uncertainty in provenance notes. |

No audited text should state that higher SEP always means a lower-degree bridge entity, proves rarity, proves serendipity, directly measures user-perceived serendipity, establishes improved explanation quality, or has a direction fully verified from historical cached matrices. The two high-risk full-draft statements must be repaired before Markdown cleanup.
