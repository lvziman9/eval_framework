# Chapter 4 Accuracy–Explainability Trade-off Results

## 4.1 Experimental Scope and Result Organisation

Chapter 3 established which native-path outputs satisfy the common export and validation contract. This chapter uses that admissible evidence to test whether validated native-path recommenders exhibit a universal accuracy leader or a common explanation response. The evidence covers the two complete main datasets, LastFM and ML-1M, and the six implementations that pass the Chapter 3 validation gates on both datasets: PGPR, UCPR, CAFE, TPRec, KGGLM, and PEARLM. The chapter reports empirical results rather than revisiting framework design.

Two evidence streams remain separate throughout the analysis. Strict accuracy results come from the accessible canonical status matrix and the exactly matching final accuracy summary presented in Table 4.1; the twelve expected row-level primary JSON files remain unavailable. Alpha-sweep results come from the canonical trade-off CSVs and describe changes in LIR, SEP, ETD, and their paired sweep ranking metrics as alpha varies. Alpha-sweep ranking values are not used as substitutes for strict accuracy. All explanation results concern paths produced natively within the recommendation workflow; the main comparison contains no post-hoc explanations.

Amazon-Book KGAT is excluded because the current evidence does not contain a complete six-model alpha-sweep result set. Chapter 5 treats it only as a partial boundary case. The present chapter first establishes the strict accuracy pattern, then examines explanation endpoints and metric-specific trade-offs, and finally compares the resulting profiles across datasets. Ablation and mechanism-level interpretation remain separate and are deferred to Chapter 5.

## 4.2 Strict Accuracy Results

The strict results do not identify a universal winner across datasets and metrics. Table 4.1 reports HR@10, NDCG@10, Precision@10, and Recall@10, while Figures 4.1 and 4.2 visualise HR@10 and NDCG@10 for LastFM and ML-1M. This section uses no alpha-sweep evidence.

LastFM divides leadership between two models. UCPR records the highest HR@10 at 0.216416 and the highest Recall@10 at 0.023155. TPRec records the highest NDCG@10 at 0.038981 and the highest Precision@10 at 0.032736. PGPR, CAFE, KGGLM, and PEARLM are lower than these metric-specific leaders on all four measures. The result is therefore a metric-dependent ordering rather than a single LastFM leader.

ML-1M produces a different pattern. CAFE leads all four strict metrics, with HR@10 of 0.554305, NDCG@10 of 0.116655, Precision@10 of 0.107119, and Recall@10 of 0.052024. PGPR is second on HR@10 and NDCG@10, while TPRec is second on Precision@10 and Recall@10. The leading identity thus changes from the split UCPR and TPRec result on LastFM to CAFE on ML-1M. Any assessment of model performance must consequently remain conditional on dataset and metric.

## 4.3 Explanation Metric Endpoint Results

The next question is whether explanation behaviour can be reduced to a single dimension or common response pattern. Table 4.2 and Figure 4.3 report alpha=0 and alpha=1 endpoints from the NDCG alpha-sweep summaries for three distinct properties. LIR measures the recency of the linked historical interaction used by a path, SEP measures the serendipity associated with its bridge entity, and ETD measures diversity among explanation path types. Movement in one dimension does not establish overall explanation superiority.

On LastFM, PGPR shows the largest LIR endpoint movement, from 0.0062 to 0.0219. SEP increases for all six models, reaching alpha=1 values from 0.6106 for PEARLM to 0.9890 for CAFE. ETD responses are more varied: TPRec has the largest movement, while PGPR and CAFE also move visibly and KGGLM and PEARLM change only slightly. Table 4.2 retains the complete endpoint set.

ML-1M yields both larger movements and a different ordering in several cases. PGPR and TPRec show large LIR responses, and PGPR, CAFE, and TPRec all approach the upper end of the SEP scale at alpha=1. CAFE records the largest ETD movement, from 0.2902 to 0.8542, followed by visible TPRec and PGPR changes. KGGLM has identical alpha=0 and alpha=1 values for all three metrics, and PEARLM changes only slightly. Explanation-objective controllability is therefore conditional on metric, model, and dataset rather than captured by one endpoint ranking.

## 4.4 LIR-oriented Trade-off Results

The LIR sweep tests how favouring paths linked to more recent historical interactions affects the paired ranking metric. Figure 4.4 plots LIR against the NDCG sweep metric for both datasets. These NDCG values belong to the alpha-sweep evidence stream and are distinct from the strict NDCG@10 results in Section 4.2.

LastFM separates a costly LIR response from more strongly preserved or limited responses. PGPR increases LIR from 0.0062 to 0.0219 while sweep NDCG changes from 0.1130 to 0.0680. UCPR increases LIR from 0.0050 to 0.0118 with a much smaller NDCG change, from 0.1256 to 0.1231. CAFE and TPRec also increase LIR, whereas KGGLM and PEARLM show only small movement and essentially unchanged sweep NDCG endpoints. Figure 4.4 retains the complete trajectories.

The ML-1M profiles differ in both scale and ranking cost. PGPR moves from 0.4655 to 0.9627 in LIR while NDCG changes from 0.1019 to 0.0619. UCPR again preserves more of the paired ranking metric, moving from 0.4568 to 0.7342 in LIR and from 0.0862 to 0.0829 in NDCG. TPRec and CAFE show substantial LIR movement with larger paired ranking changes than UCPR, while KGGLM is unchanged and PEARLM moves only slightly. The curves establish distinct LIR trade-off profiles without selecting a universal operating point.

## 4.5 SEP-oriented Trade-off Results

SEP asks a different question: how does ranking change when paths with rarer bridge entities are favoured? It measures serendipity through the normalised rarity of the bridge entity rather than through interaction recency. The canonical SEP-NDCG views listed as optional Figure 4.5 remain optional or appendix candidates rather than part of the four-figure core.

On LastFM, PGPR increases SEP from 0.5688 to 0.9877 while sweep NDCG changes from 0.1130 to 0.0676. UCPR reaches SEP 0.9336 from 0.5170 while NDCG changes only from 0.1256 to 0.1238. CAFE and TPRec also reach high SEP endpoints, whereas KGGLM and PEARLM show smaller movement. The contrast shows that similar directional SEP gains can carry different paired ranking costs.

On ML-1M, PGPR, CAFE, and TPRec again reach high alpha=1 SEP values but incur different NDCG changes. UCPR increases SEP from 0.4935 to 0.7406 while NDCG changes only from 0.0862 to 0.0825. KGGLM remains unchanged on both measures, and PEARLM records a small SEP increase with nearly unchanged NDCG. The optional Figure 4.5 views retain the complete trajectories. These profiles show that popularity exposure can be redirected to different degrees and at different paired ranking costs; they do not make SEP a complete explanation-quality measure.

## 4.6 ETD-oriented Trade-off Results

ETD adds a third perspective by measuring the diversity of explanation path types within a user's recommendation list. Its sweep tests whether this diversity can increase while the paired ranking metric is preserved. Optional Figure 4.6 identifies the existing dataset-specific ETD-NDCG views supporting the section.

On LastFM, TPRec has the largest ETD endpoint increase, from 0.1766 to 0.3983, while its sweep NDCG changes from 0.1178 to 0.1138. PGPR and CAFE also increase ETD with comparatively limited paired NDCG changes. UCPR has a smaller increase, and KGGLM and PEARLM show minimal endpoint movement. The profile differs from both LIR and SEP, confirming that path-type diversity adds separate information.

ML-1M again changes the scale and ordering. CAFE records the largest ETD movement, from 0.2902 to 0.8542, while its sweep NDCG changes from 0.1115 to 0.0862. TPRec and PGPR also move substantially. UCPR increases ETD from 0.2088 to 0.2555 with a smaller NDCG change from 0.1008 to 0.0992, while KGGLM remains unchanged and PEARLM changes only slightly. The optional Figure 4.6 views retain the complete trajectories. These results establish differences in ETD controllability; they do not by themselves establish the mechanism causing those differences.

## 4.7 Cross-Dataset Comparison

Across the two evidence streams, the central empirical result is heterogeneity rather than universal dominance. Strict accuracy leadership changes by dataset and metric: UCPR and TPRec lead different measures on LastFM, while CAFE leads all four measures on ML-1M. Explanation endpoints likewise do not yield one model ordering across LIR, SEP, and ETD, and the paired NDCG response differs across models.

The datasets also change the scale and pattern of movement. PGPR, UCPR, CAFE, and TPRec generally show larger absolute LIR changes on ML-1M than on LastFM. CAFE, TPRec, and PGPR have substantial ETD movement on ML-1M, but their ordering and magnitude differ on LastFM. KGGLM and PEARLM provide contrasting cases with limited movement in several sweeps. A model's trade-off profile is thus conditional on both the dataset and the explanation property being controlled.

No single model dominates all strict accuracy measures, explanation dimensions, and datasets. The common native-path contract instead reveals multiple trade-off profiles whose evidence roles must remain distinct. Comparative curves alone, however, cannot establish why those profiles differ. Chapter 5 therefore examines the registered PGPR and UCPR ablation, uses model mechanisms only as cautious interpretive context, and treats Amazon-Book KGAT separately as a coverage boundary.
