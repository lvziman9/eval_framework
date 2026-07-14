# Chapter 4 Accuracy–Explainability Trade-off Results

## 4.1 Experimental Scope and Result Organisation

Chapter 3 established which native-path outputs satisfy the common export and validation contract. This chapter uses that admissible evidence to test whether validated native-path recommenders exhibit a universal accuracy leader or a common explanation response. The evidence covers the two complete main datasets, LastFM and ML-1M, and the six implementations that pass the Chapter 3 validation gates on both datasets: PGPR, UCPR, CAFE, TPRec, KGGLM, and PEARLM. This chapter reports empirical results and result-level interpretation. Mechanism-level causal explanation is reserved for Chapter 5.

Two evidence streams remain separate throughout the analysis. Strict accuracy results come from the accessible canonical status matrix and the exactly matching final accuracy summary presented in Table 4.1; the twelve expected row-level primary JSON files remain unavailable. Alpha-sweep results come from the canonical trade-off CSVs and describe changes in LIR, SEP, ETD, and their paired sweep ranking metrics as alpha varies. Alpha-sweep ranking values are not used as substitutes for strict accuracy. All explanation results concern paths produced natively within the recommendation workflow; the main comparison contains no post-hoc explanations.

Amazon-Book KGAT is excluded because the current evidence does not contain a complete six-model alpha-sweep result set. Chapter 5 treats it only as a partial boundary case. The present chapter first establishes the strict accuracy pattern, then examines explanation endpoints and metric-specific trade-offs, and finally compares the resulting profiles across datasets. Ablation and mechanism-level interpretation remain separate and are deferred to Chapter 5. This chapter does not claim statistical significance, user-perceived usefulness, causal mechanism, or universal model superiority.

The Batch 1C alpha-sweep process diagram shows how objective-specific endpoint movement and paired sweep NDCG movement are carried into the result-level analysis. It does not define a universal score function, and its sweep NDCG must not be interpreted as strict NDCG@10.

For an explanation objective \(q\), endpoint movement is summarised by

\[
\Delta q_{m,d}
=
Q_{m,d}^{q}(\alpha=1)
-
Q_{m,d}^{q}(\alpha=0)
\]

and

\[
\Delta \mathrm{NDCG}_{m,d}^{\mathrm{sweep},q}
=
\mathrm{NDCG}_{m,d}^{\mathrm{sweep},q}(\alpha=1)
-
\mathrm{NDCG}_{m,d}^{\mathrm{sweep},q}(\alpha=0).
\]

A positive \(\Delta q\) with negative \(\Delta \mathrm{NDCG}^{\mathrm{sweep}}\) indicates an empirical trade-off under the selected sweep objective. This does not replace strict NDCG@10. The deltas are descriptive endpoint differences, not statistical estimates or tests.

## 4.2 Strict Accuracy Results

The strict results do not identify a universal winner across datasets and metrics. Table 4.1 reports HR@10, NDCG@10, Precision@10, and Recall@10, while Figures 4.1 and 4.2 visualise HR@10 and NDCG@10 for LastFM and ML-1M. This section uses no alpha-sweep evidence.

LastFM divides leadership between two models. UCPR records the highest HR@10 at 0.216416 and the highest Recall@10 at 0.023155. TPRec records the highest NDCG@10 at 0.038981 and the highest Precision@10 at 0.032736. PGPR, CAFE, KGGLM, and PEARLM are lower than these metric-specific leaders on all four measures. The result is therefore a metric-dependent ordering rather than a single LastFM leader.

ML-1M produces a different pattern. CAFE leads all four strict metrics, with HR@10 of 0.554305, NDCG@10 of 0.116655, Precision@10 of 0.107119, and Recall@10 of 0.052024. PGPR is second on HR@10 and NDCG@10, while TPRec is second on Precision@10 and Recall@10. The leading identity thus changes from the split UCPR and TPRec result on LastFM to CAFE on ML-1M. Any assessment of model performance must consequently remain conditional on dataset and metric.

The result-level finding is that there is no universal strict-accuracy winner. Leadership depends first on dataset and then, on LastFM, on the ranking metric being considered. This prevents a single strict ranking from being carried unchanged into the explanation analysis. It also means that a model's strict position cannot be used to predict how far its native paths will move under LIR-, SEP-, or ETD-oriented control: strict accuracy and explanation controllability are different observed properties.

This conclusion applies only to the registered strict evidence stream. The paired NDCG values reported later are generated inside individual alpha sweeps and characterise those trajectories; they are not alternative measurements of the strict NDCG@10 values in Table 4.1. Keeping the two sources separate is necessary even when their metric names appear similar.

## 4.3 Explanation Metric Endpoint Results

The next question is whether explanation behaviour can be reduced to a single dimension or common response pattern. Table 4.2 and Figure 4.3 report alpha=0 and alpha=1 endpoints from the NDCG alpha-sweep summaries for three distinct properties. LIR measures the recency of the linked historical interaction used by a path, SEP is a repository-specific degree-derived bridge-entity score, and ETD measures diversity among explanation path types. Movement in one dimension does not establish overall explanation superiority.

On LastFM, PGPR shows the largest LIR endpoint movement, from 0.0062 to 0.0219. SEP increases for all six models, reaching alpha=1 values from 0.6106 for PEARLM to 0.9890 for CAFE. ETD responses are more varied: TPRec has the largest movement, while PGPR and CAFE also move visibly and KGGLM and PEARLM change only slightly. Table 4.2 retains the complete endpoint set.

ML-1M yields both larger movements and a different ordering in several cases. PGPR and TPRec show large LIR responses, and PGPR, CAFE, and TPRec all approach the upper end of the SEP scale at alpha=1. CAFE records the largest ETD movement, from 0.2902 to 0.8542, followed by visible TPRec and PGPR changes. KGGLM has identical alpha=0 and alpha=1 values for all three metrics, and PEARLM changes only slightly. Explanation-objective controllability is therefore conditional on metric, model, and dataset rather than captured by one endpoint ranking.

The endpoints establish that LIR, SEP, and ETD are non-interchangeable. A model can move strongly on one dimension and moderately or minimally on another, so an endpoint increase cannot be converted into a claim of global explanation superiority. The same restriction applies to flat or restricted responses. Such profiles are informative because they show that the registered sweep exposes little movement for that model-objective-dataset combination; they do not show that the model has poor explanations or reveal why the response is restricted.

These endpoint values are alpha-sweep results rather than strict accuracy results. They describe computational properties of validated native paths, not user-perceived explanation quality. Their conceptual dimensions follow XRecSys, while the exact LIR, SEP, and ETD computations and data assumptions evaluated here remain repository-specific.

## 4.4 LIR-oriented Trade-off Results

The LIR sweep tests how favouring paths linked to more recent historical interactions affects the paired ranking metric. Figure 4.4 plots LIR against the NDCG sweep metric for both datasets. These NDCG values belong to the alpha-sweep evidence stream and are distinct from the strict NDCG@10 results in Section 4.2.

LastFM separates a costly LIR response from more strongly preserved or limited responses. PGPR increases LIR from 0.0062 to 0.0219 while sweep NDCG changes from 0.1130 to 0.0680. UCPR increases LIR from 0.0050 to 0.0118 with a much smaller NDCG change, from 0.1256 to 0.1231. CAFE and TPRec also increase LIR, whereas KGGLM and PEARLM show only small movement and essentially unchanged sweep NDCG endpoints. Figure 4.4 retains the complete trajectories.

The ML-1M profiles differ in both scale and ranking cost. PGPR moves from 0.4655 to 0.9627 in LIR while NDCG changes from 0.1019 to 0.0619. UCPR again preserves more of the paired ranking metric, moving from 0.4568 to 0.7342 in LIR and from 0.0862 to 0.0829 in NDCG. TPRec and CAFE show substantial LIR movement with larger paired ranking changes than UCPR, while KGGLM is unchanged and PEARLM moves only slightly. The curves establish distinct LIR trade-off profiles without selecting a universal operating point.

Viewed as curves rather than endpoints alone, the LIR results expose three empirical response types. PGPR combines a large LIR gain with a visible paired-NDCG cost at the upper part of the sweep. UCPR provides the contrasting profile of a moderate LIR gain with stronger preservation of paired NDCG. KGGLM and PEARLM show flat or restricted movement, while CAFE and TPRec occupy intermediate profiles whose movement and ranking cost vary by dataset.

The observed profiles also show that LIR response is dataset-dependent. The scale and ordering of movement on ML-1M do not reproduce the LastFM profiles, even though the evaluation contract and alpha grid are shared. At the result level, this indicates that recency-oriented control cannot be summarised by one model ordering or one expected cost. It does not by itself establish a causal mechanism; Chapter 5 considers which interpretations are supported by ablation and which remain descriptive.

In the notation above, these profiles compare \(\Delta \mathrm{LIR}_{m,d}\) with \(\Delta \mathrm{NDCG}_{m,d}^{\mathrm{sweep},\mathrm{LIR}}\). The notation records the direction and magnitude already shown by the registered endpoints; it does not add a new result or infer a mechanism.

## 4.5 SEP-oriented Trade-off Results

SEP asks a different question: how does ranking change when paths assigned larger repository-specific degree-derived bridge-entity scores are favoured? It records the response of that repository score rather than interaction recency or path-type diversity. The canonical SEP-NDCG views listed as optional Figure 4.5 remain optional or appendix candidates rather than part of the four-figure core.

On LastFM, PGPR increases SEP from 0.5688 to 0.9877 while sweep NDCG changes from 0.1130 to 0.0676. UCPR reaches SEP 0.9336 from 0.5170 while NDCG changes only from 0.1256 to 0.1238. CAFE and TPRec also reach high SEP endpoints, whereas KGGLM and PEARLM show smaller movement. The contrast shows that similar directional SEP gains can carry different paired ranking costs.

On ML-1M, PGPR, CAFE, and TPRec again reach high alpha=1 SEP values but incur different NDCG changes. UCPR increases SEP from 0.4935 to 0.7406 while NDCG changes only from 0.0862 to 0.0825. KGGLM remains unchanged on both measures, and PEARLM records a small SEP increase with nearly unchanged NDCG. The optional Figure 4.5 views retain the complete trajectories. These profiles show that SEP-weight exposure can be redirected to different degrees and at different paired ranking costs; they do not make SEP a complete explanation-quality measure.

Across the two datasets, SEP often permits strong endpoint movement, but the common direction of that movement does not imply a common ranking cost. PGPR, UCPR, CAFE, and TPRec can all move towards higher SEP while preserving different proportions of paired NDCG, and KGGLM and PEARLM expose more restricted controllability in the registered sweeps. The result-level finding is therefore variation in SEP controllability, not one uniformly favourable trade-off.

SEP is a repository-specific degree-derived bridge-entity score. Higher SEP in the registered curves therefore means greater exposure to larger stored SEP weights; it is not interpreted as lower bridge-entity degree, rarity, novelty, usefulness, or better explanations for users. The curves do not identify the model mechanism responsible for their different shapes; that interpretation remains in Chapter 5.

Accordingly, the SEP result is expressed as the paired descriptive quantities \(\Delta \mathrm{SEP}_{m,d}\) and \(\Delta \mathrm{NDCG}_{m,d}^{\mathrm{sweep},\mathrm{SEP}}\). Their signs and sizes summarise the registered endpoints only and do not constitute statistical inference.

The registered SEP values and Batch 1 curve findings are retained unchanged. The accessible generator's ascending-degree and increasing-ordinal-weight direction is verified, and the path-metric guide's low-degree / high-weight wording appears stale. However, the historical SEP matrix cache used for the registered sweeps is unavailable; final cache provenance and direction therefore still require manual verification.

## 4.6 ETD-oriented Trade-off Results

ETD adds a third perspective by measuring the diversity of explanation path types within a user's recommendation list. Its sweep tests whether this diversity can increase while the paired ranking metric is preserved. Optional Figure 4.6 identifies the existing dataset-specific ETD-NDCG views supporting the section.

On LastFM, TPRec has the largest ETD endpoint increase, from 0.1766 to 0.3983, while its sweep NDCG changes from 0.1178 to 0.1138. PGPR and CAFE also increase ETD with comparatively limited paired NDCG changes. UCPR has a smaller increase, and KGGLM and PEARLM show minimal endpoint movement. The profile differs from both LIR and SEP, confirming that path-type diversity adds separate information.

ML-1M again changes the scale and ordering. CAFE records the largest ETD movement, from 0.2902 to 0.8542, while its sweep NDCG changes from 0.1115 to 0.0862. TPRec and PGPR also move substantially. UCPR increases ETD from 0.2088 to 0.2555 with a smaller NDCG change from 0.1008 to 0.0992, while KGGLM remains unchanged and PEARLM changes only slightly. The optional Figure 4.6 views retain the complete trajectories. These results establish differences in ETD controllability; they do not by themselves establish the mechanism causing those differences.

ETD therefore behaves differently from LIR and SEP. Increasing path-type diversity does not reproduce an identical paired-ranking-cost pattern, and the largest mover changes from TPRec on LastFM to CAFE on ML-1M. Some profiles show substantial diversity movement with limited paired-NDCG change, while others show a larger cost or almost no movement. This makes ETD a separate control dimension rather than a substitute for recency or the repository-specific degree-derived SEP score.

Movement in ETD is also narrower than a claim about overall explanation quality. It establishes that more path types are represented under the declared taxonomy and denominator; it does not establish that the resulting paths are more understandable, useful, or persuasive. Chapter 5 uses the registered PGPR/UCPR ablation to strengthen only the mechanism claims that the ablation can support and keeps the remaining model explanations descriptive.

The ETD trajectories are therefore summarised by \(\Delta \mathrm{ETD}_{m,d}\) together with \(\Delta \mathrm{NDCG}_{m,d}^{\mathrm{sweep},\mathrm{ETD}}\). As in the LIR and SEP sections, this notation formalises an observed endpoint trade-off without creating an efficiency ratio, significance claim, or causal conclusion.

## 4.7 Cross-Dataset Comparison

Across the two evidence streams, the central empirical result is heterogeneity rather than universal dominance. Strict accuracy leadership changes by dataset and metric: UCPR and TPRec lead different measures on LastFM, while CAFE leads all four measures on ML-1M. Explanation endpoints likewise do not yield one model ordering across LIR, SEP, and ETD, and the paired NDCG response differs across models.

The datasets also change the scale and pattern of movement. PGPR, UCPR, CAFE, and TPRec generally show larger absolute LIR changes on ML-1M than on LastFM. CAFE, TPRec, and PGPR have substantial ETD movement on ML-1M, but their ordering and magnitude differ on LastFM. KGGLM and PEARLM provide contrasting cases with limited movement in several sweeps. A model's trade-off profile is thus conditional on both the dataset and the explanation property being controlled.

No single model dominates all strict accuracy measures, explanation dimensions, and datasets. The common native-path contract instead reveals multiple trade-off profiles whose evidence roles must remain distinct. Comparative curves alone, however, cannot establish why those profiles differ. Chapter 5 therefore examines the registered PGPR and UCPR ablation, uses model mechanisms only as cautious interpretive context, and treats Amazon-Book KGAT separately as a coverage boundary.

The Batch 1C empirical trade-off pattern schematic groups the already reported profiles as flat or stable, efficient movement, restricted costly, or high-gain high-cost. These labels summarise descriptive pattern types only; they do not create a new metric, assign statistical significance, or establish mechanism.

The empirical findings can be summarised without converting the observed associations into mechanism claims:

| Empirical pattern | Evidence from Chapter 4 | Example models / datasets | Result-level interpretation | Evidence limit |
| --- | --- | --- | --- | --- |
| No universal strict-accuracy winner | Strict leadership is split between UCPR and TPRec on LastFM, whereas CAFE leads all four strict metrics on ML-1M. | UCPR and TPRec on LastFM; CAFE on ML-1M | Accuracy leadership is conditional on dataset and metric. | The primary row-level strict JSON files are unavailable, and no statistical-significance artifact is registered. |
| Accuracy leadership and explanation movement are different properties | The strict leaders do not form one common ordering across the LIR, SEP, and ETD sweeps. | LastFM strict leaders compared with PGPR LIR movement and TPRec ETD movement; CAFE on ML-1M | Strict ranking position does not directly predict explanation-objective controllability. | Sweep endpoints and paired ranking metrics are not strict accuracy measurements. |
| The same explanation objective can have different paired ranking costs | Models moving in the same objective direction retain different paired NDCG trajectories. | PGPR and UCPR in the LIR and SEP sweeps on both datasets | A shared objective does not imply a shared utility cost or operating point. | The curves are descriptive and do not establish statistical significance or causal mechanism. |
| LIR, SEP, and ETD produce different model orderings | The largest or most visible movements change across explanation dimensions. | PGPR for LastFM LIR, TPRec for LastFM ETD, and CAFE for ML-1M ETD | The three metrics expose non-interchangeable path properties. | Metric scales differ, and no endpoint constitutes overall explanation superiority. |
| Flat response profiles are informative | Some model-objective-dataset combinations show identical or only small endpoint movement. | KGGLM on ML-1M; KGGLM and PEARLM in several LastFM sweeps | The registered control exposes limited movement under the available native-path evidence. | A flat profile does not identify its cause or establish poor explanation quality. |
| Trade-off profiles are dataset-dependent | Movement scale, ordering, and paired cost change between LastFM and ML-1M. | PGPR, UCPR, CAFE, and TPRec across the two datasets | A profile observed on one dataset should not be transferred as a universal model property. | Only two datasets provide complete six-model trade-off evidence. |
| Mechanism interpretation requires Chapter 5 evidence | Comparative curves reveal heterogeneity but cannot determine why it occurs. | PGPR/UCPR ablation versus descriptive context for CAFE, TPRec, KGGLM, and PEARLM | Result-level findings motivate, but do not replace, ablation and mechanism analysis. | Stronger mechanism statements are limited to the registered PGPR/UCPR ablation; other explanations remain descriptive. |

This summary closes the result-level analysis. It identifies what the validated outputs show while leaving causal attribution, ablation-supported controllability, and dataset-boundary interpretation to Chapter 5.
