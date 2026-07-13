# Chapter 4 Accuracy–Explainability Trade-off Results

## 4.1 Experimental Scope and Result Organisation

This chapter reports the empirical results obtained through the evaluation framework described
in Chapter 3. It focuses on the two complete main datasets, LastFM and ML-1M, and on the six
native-path recommender implementations that passed the required validation gates on both
datasets: PGPR, UCPR, CAFE, TPRec, KGGLM, and PEARLM. The chapter reports results rather than
revisiting framework design.

Two evidence streams are kept separate throughout the chapter. Strict accuracy results are
taken from the per-row accuracy evidence summarised in Table 4.1. The alpha-sweep results are
taken from the canonical trade-off CSVs and describe changes in LIR, SEP, ETD, and their paired
sweep ranking metrics as alpha varies. Alpha-sweep values are therefore not used as substitutes
for strict accuracy values. All explanation results concern native paths produced within the
recommendation workflow; no post-hoc explanations are included in the main comparison.

Amazon-Book KGAT is excluded from the main trade-off analysis because the current evidence
does not provide a complete six-model alpha-sweep result set. Its role as a partial boundary
case is reserved for Chapter 5. The present chapter is organised around strict accuracy,
explanation-metric endpoints, three metric-specific trade-off views, and a cross-dataset
comparison. Mechanism-level interpretation and ablation analysis are also deferred to Chapter 5.

## 4.2 Strict Accuracy Results

Table 4.1 reports HR@10, NDCG@10, Precision@10, and Recall@10 from the strict accuracy
evidence. Figures 4.1 and 4.2 visualise HR@10 and NDCG@10 for LastFM and ML-1M, respectively. No
alpha-sweep values are used in this section.

On LastFM, UCPR obtains the highest HR@10 at 0.216416 and the highest Recall@10 at 0.023155. TPRec
obtains the highest NDCG@10 at 0.038981 and the highest Precision@10 at 0.032736. PGPR, CAFE,
KGGLM, and PEARLM record lower values on all four metrics than these metric-specific leaders. The
LastFM results therefore do not identify one model as the leader for every strict accuracy measure.

On ML-1M, CAFE records the highest value for all four strict metrics: HR@10 of 0.554305,
NDCG@10 of 0.116655, Precision@10 of 0.107119, and Recall@10 of 0.052024. PGPR is second on
HR@10 and NDCG@10, while TPRec is second on Precision@10 and Recall@10. The identity of the
leading model consequently changes between datasets: LastFM is split between UCPR and TPRec,
whereas CAFE leads the reported strict metrics on ML-1M. There is no universal strict-accuracy
winner across the two datasets.

## 4.3 Explanation Metric Endpoint Results

Table 4.2 and Figure 4.3 report the alpha=0 and alpha=1 endpoints from the NDCG alpha-sweep
summaries. LIR measures the recency of the linked historical interaction used by an explanation
path, SEP measures the serendipity associated with the path's bridge entity, and ETD measures
diversity among explanation path types. These dimensions are reported separately because movement
in one metric does not establish overall explanation superiority.

On LastFM, the largest LIR endpoint movement is observed for PGPR, from 0.0062 to 0.0219. SEP
increases for all six models, with alpha=1 values ranging from 0.6106 for PEARLM to 0.9890 for
CAFE. ETD also varies by model: TPRec moves from 0.1766 to 0.3983, PGPR from 0.1396 to 0.3552,
and CAFE from 0.2314 to 0.3728, whereas KGGLM and PEARLM show only small endpoint changes.

On ML-1M, PGPR and TPRec show large LIR movements, from 0.4655 to 0.9627 and from 0.4502 to
0.9451, respectively. SEP reaches 0.9833 for PGPR, 0.9791 for CAFE, and 0.9704 for TPRec at
alpha=1. The largest ETD endpoint movement is recorded for CAFE, from 0.2902 to 0.8542, followed
by TPRec from 0.2874 to 0.7301 and PGPR from 0.1611 to 0.5191. KGGLM has identical alpha=0 and
alpha=1 values for all three metrics on ML-1M, while PEARLM changes only slightly. The endpoints
therefore show that explanation-objective controllability differs by metric, model, and dataset.

## 4.4 LIR-oriented Trade-off Results

The LIR sweep examines how favouring paths linked to more recent historical interactions changes
the paired ranking metric. Figure 4.4 presents LIR against the NDCG sweep metric for both main
datasets. The NDCG values in this figure belong to the alpha-sweep evidence stream and are not
the strict NDCG@10 values reported in Section 4.2.

On LastFM, PGPR increases LIR from 0.0062 to 0.0219 while the sweep NDCG changes from 0.1130 to
0.0680. UCPR increases LIR from 0.0050 to 0.0118 while NDCG changes from 0.1256 to 0.1231. CAFE
and TPRec also increase LIR, from 0.0012 to 0.0042 and from 0.0056 to 0.0111, with endpoint
NDCG values of 0.0939 and 0.1065, respectively. KGGLM and PEARLM show only small LIR movement
and essentially unchanged sweep NDCG endpoints.

On ML-1M, PGPR increases LIR from 0.4655 to 0.9627 while NDCG changes from 0.1019 to 0.0619. TPRec
moves from 0.4502 to 0.9451 in LIR and from 0.0942 to 0.0754 in NDCG. CAFE moves from 0.3949 to
0.6986 in LIR while its NDCG changes from 0.1167 to 0.0555. UCPR shows a smaller ranking change,
with LIR moving from 0.4568 to 0.7342 and NDCG from 0.0862 to 0.0829. KGGLM is unchanged across
the sweep, and PEARLM shows only a small LIR increase with nearly constant NDCG. These curves
demonstrate dataset- and model-dependent trade-off patterns without implying a single preferred
operating point.

## 4.5 SEP-oriented Trade-off Results

SEP measures the serendipity of an explanation path through the normalised rarity of its bridge
entity. The SEP sweep therefore examines the ranking cost or preservation observed when paths
with higher SEP are favoured. The canonical SEP-NDCG figures listed as optional Figure 4.5
provide dataset-specific supporting views; they are retained as optional or appendix candidates
rather than added to the four-figure core of this chapter.

On LastFM, PGPR moves from SEP 0.5688 to 0.9877 while sweep NDCG changes from 0.1130 to
0.0676. UCPR moves from 0.5170 to 0.9336 with NDCG changing only from 0.1256 to 0.1238. CAFE
and TPRec reach SEP values of 0.9890 and 0.9132, with NDCG endpoints of 0.0822 and 0.1034,
respectively. KGGLM and PEARLM show smaller SEP endpoint movements than the other four models.

On ML-1M, PGPR, CAFE, and TPRec reach SEP values of 0.9833, 0.9791, and 0.9704 at alpha=1,
while their sweep NDCG values change from 0.1019 to 0.0579, from 0.1167 to 0.0426, and from
0.0942 to 0.0680, respectively. UCPR increases SEP from 0.4935 to 0.7406 while NDCG changes
from 0.0862 to 0.0825. KGGLM is unchanged on both SEP and NDCG, and PEARLM shows a small SEP
increase with nearly unchanged NDCG. The results support model-specific SEP trade-off statements,
but they do not support treating SEP as a complete measure of explanation quality.

## 4.6 ETD-oriented Trade-off Results

ETD measures the diversity of explanation path types represented in a user's recommendation
list. The ETD sweep tests whether this diversity can be increased while preserving the paired
ranking metric. Optional Figure 4.6 identifies the existing dataset-specific ETD-NDCG figures
that support this section.

On LastFM, TPRec has the largest ETD endpoint increase among the six models, from 0.1766 to 0.3983,
while its sweep NDCG changes from 0.1178 to 0.1138. PGPR moves from 0.1396 to 0.3552 in ETD and
from 0.1113 to 0.1049 in NDCG. CAFE moves from 0.2314 to 0.3728 with NDCG changing from 0.1072 to
0.1048. UCPR shows a smaller ETD increase, while KGGLM and PEARLM show minimal endpoint movement.

On ML-1M, CAFE records the largest ETD movement, from 0.2902 to 0.8542, while its sweep NDCG
changes from 0.1115 to 0.0862. TPRec moves from 0.2874 to 0.7301 with NDCG changing from 0.0903
to 0.0809, and PGPR moves from 0.1611 to 0.5191 with NDCG changing from 0.0949 to 0.0818. UCPR
increases ETD from 0.2088 to 0.2555 with a smaller NDCG change from 0.1008 to 0.0992. KGGLM
is unchanged, and PEARLM changes only slightly. The observed endpoint movements establish
differences in ETD controllability; their mechanism-level causes are examined in Chapter 5.

## 4.7 Cross-Dataset Comparison

The strict accuracy comparison and the alpha-sweep results both show dataset-dependent
outcomes. UCPR and TPRec lead different strict metrics on LastFM, whereas CAFE leads all four
strict metrics on ML-1M. At the same time, the explanation endpoints do not follow a single model
ordering across LIR, SEP, and ETD. A model with a large movement in one explanation metric may
show a smaller movement in another, and the paired NDCG change also differs across models.

The scale and pattern of endpoint movement differ between LastFM and ML-1M. LIR changes are
generally larger in absolute terms on ML-1M for PGPR, UCPR, CAFE, and TPRec, while the LastFM
results occupy a much smaller LIR range. ETD movement is substantial for CAFE, TPRec, and PGPR
on ML-1M, but the ordering and magnitude differ on LastFM. KGGLM and PEARLM provide contrasting
cases with limited movement in several sweeps. These observations show that explanation-metric
controllability is conditional on both dataset and model.

No single model dominates all strict accuracy measures, explanation dimensions, and datasets. The
results instead identify multiple trade-off profiles under a common native-path evaluation
contract. This empirical variation motivates the mechanism and ablation analysis in Chapter
5, where the reasons for these patterns and the Amazon-Book KGAT boundary case are examined
separately.
