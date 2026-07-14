# Chapter 5 Ablation, Mechanism Analysis, and Boundary Cases

## 5.1 Ablation Analysis of Framework Controllability

Chapter 4 established heterogeneous trade-off profiles, but comparative curves alone cannot show whether an explanation-oriented control begins from the registered baseline or can satisfy an explicit ranking-utility condition. The ablation addresses that narrower question. It tests framework controllability for PGPR and UCPR; it is not designed to show that either model becomes a stronger recommender after modification. Its evidence remains separate from the strict six-model accuracy results and the main alpha sweeps in Chapter 4.

The Batch 1C ablation evidence-flow diagram makes this scope explicit: interpretation proceeds only after alpha-zero baseline preservation, an objective-specific ablation sweep, and paired NDCG-retention assessment. The flow does not extend the evidence to the other four models.

The experiment uses a strict baseline-preserving canonical alpha sweep over the frozen original top-k item set. PGPR is the main ablation model and UCPR is an auxiliary replication. On both LastFM and ML-1M, the alpha=0 checks pass for LIR, SEP, and ETD. The exported top-k rankings and explanation pairs are preserved exactly, with a maximum metric difference of 0.0 from the original result. The control mechanism therefore begins from the registered baseline rather than a separately reconstructed ranking.

Baseline preservation is formalised as

\[
D_{\mathrm{base}}
=
\max_{u}
\mathbf{1}
\left[
\hat{R}_{u,\alpha=0}^{K,\mathrm{abl}}
\neq
\hat{R}_{u}^{K,\mathrm{base}}
\right].
\]

When \(D_{\mathrm{base}}=0\), the ablation sweep preserves the alpha-zero baseline recommendation list under the tested condition.

The second test selects the maximum explanation gain subject to NDCG retention greater than or equal to 95%. All twelve dataset-model-objective combinations in Table 5.1 have an operating point satisfying this rule. The selected alpha varies with the objective: some settings choose alpha=1.0; PGPR SEP chooses 0.75 on LastFM and 0.95 on ML-1M; and intermediate settings also occur for ML-1M PGPR LIR and ML-1M UCPR SEP. This variation is the relevant controllability result because the operating point follows the joint response of the explanation objective and NDCG rather than a fixed endpoint.

For the ablation evidence stream, NDCG retention is

\[
\mathrm{Retention}_{m,d,q}(\alpha)
=
\frac{
\mathrm{NDCG}_{m,d,q}^{\mathrm{abl}}(\alpha)
}{
\mathrm{NDCG}_{m,d,q}^{\mathrm{abl}}(0)
}.
\]

The constrained operating point is

\[
\alpha^{*}
=
\arg\max_{\alpha}
Q_{m,d}^{q}(\alpha)
\quad
\mathrm{s.t.}
\quad
\mathrm{Retention}_{m,d,q}(\alpha) \ge 0.95.
\]

This formalises the operating-point selection used in the ablation evidence stream. It does not define six-model superiority and must not be mixed with strict accuracy results.

The Batch 1C 95% retention operating-point diagram restates this constrained selection as a decision flow. The threshold applies only to the registered ablation stream and is not a general model-ranking criterion.

The scale of movement is also objective-dependent. The selected LastFM PGPR LIR setting records a 502.1737281916887% explanation gain with 99.94241852350147% NDCG retention, whereas the selected ETD setting records a 3.470375996962718% gain with 98.85509635280121% retention. These percentages are not directly comparable because LIR and ETD use different scales and represent different path properties. They demonstrate that the same retention rule can expose different response ranges across objectives.

UCPR supplies an auxiliary protocol check rather than a second main ablation claim. Its alpha=0 preservation passes on both datasets, and each selected point satisfies the 95% NDCG-retention rule. Agreement in protocol behaviour across PGPR and UCPR supports a framework-level statement about auditable control. It does not establish improvement of the underlying recommender, because the experiment controls path or explanation selection over a frozen original item set.

Figure 5.1 presents the registered PGPR/UCPR trade-off curves for LastFM and ML-1M. Together with Table 5.1, the evidence supports a bounded conclusion: the framework provides an auditable control variable, exactly preserves the registered ranking at alpha=0, and identifies explanation-oriented operating points under an explicit NDCG-retention constraint.

## 5.2 Mechanism-Level Comparison of Native-Path Models

The ablation establishes controllability only within its registered scope. Interpreting the broader Chapter 4 patterns requires a different evidential level. The six models differ in candidate-path generation, constraints, and selection, and the repository architecture and candidate audit support the mechanism groupings below. These differences provide plausible context, but they do not independently demonstrate causality. External model papers support architectural context only; repository evidence determines the behaviour evaluated in this dissertation. Table 5.2 summarises the mechanism groupings, evidence grades, and current citation status.

PGPR and UCPR form the reinforcement-learning path-search family, with UCPR additionally treated in the repository as a user-centric variant [@xian2019pgpr; @tai2021ucpr]. Their registered ablation directly shows that the path-selection layer can be redirected towards LIR, SEP, or ETD while preserving the alpha=0 baseline. It does not show that reinforcement learning or user-centric modelling causes every difference between the two models. That stronger interpretation would require targeted evidence; the verified primary papers establish model context, not the cause of repository-specific curve differences.

CAFE represents the coarse-to-fine neural-symbolic reasoning family in the repository audit [@xian2020cafe]. Chapter 4 shows substantial movement for CAFE in some ML-1M explanation dimensions while CAFE also leads the strict ML-1M accuracy metrics. This evidence establishes that high strict accuracy and visible explanation movement can coexist. It does not establish coarse-to-fine reasoning as the cause of the curve shape, because the evidence pack contains no CAFE-specific module ablation. The verified primary paper supports the family description; the interpretation of the observed curve remains descriptive.

TPRec represents time-aware path reasoning [@zhao2022tprec]. Because LIR depends on valid interaction timestamps, temporal data availability becomes part of the evaluation contract. TPRec participates in the complete LastFM and ML-1M comparisons, but its Amazon row is blocked: the canonical Amazon timestamps are sentinel -1, and no formal temporal reward is approved. This contrast shows that a model requirement can determine whether an experiment is reportable. The external citation supports model context, while the Amazon status is established by internal validation evidence.

KGGLM and PEARLM form the language-model-style path generation or scoring group [@balloccu2024kgglm; @balloccu2023pearlm]. The candidate audit records constrained decoding for PEARLM and path-language-model infrastructure for both models. Their limited endpoint movement in several Chapter 4 sweeps is consistent with a more restricted set of available or selected paths. Candidate-path flexibility was not independently measured, however, so constrained generation cannot be claimed as the demonstrated cause of smaller movement. KGGLM publication metadata is verified. PEARLM is cited through its verified arXiv record, while its final venue and publisher DOI still require manual verification.

The mechanism comparison therefore supports two different levels of statement. The experiments directly establish that observed controllability varies across models and datasets. Repository architecture supplies plausible context through path-generation and path-selection constraints. Model-specific causal explanations remain hypotheses until they are supported by targeted ablations and verified primary sources.

## 5.3 Accuracy–Explainability Interaction Patterns

Chapter 4 established the empirical trade-off patterns; this section asks which parts can be strengthened by ablation or mechanism-level evidence. The interpretive task is therefore not to repeat the curve summary, but to grade the support available for statements about control and possible model context.

The PGPR/UCPR ablation supplies the stronger evidence in this chapter. It verifies exact alpha=0 preservation over the frozen original top-k item set and selects objective-specific operating points under the declared 95% NDCG-retention rule. Because the selected alpha and explanation gain vary by model, objective, and dataset, the ablation supports a bounded claim that the registered path or explanation selection layer is controllable under this protocol. It does not establish improvement of the underlying recommenders or a mechanism shared by all six models.

The evidence for CAFE, TPRec, KGGLM, and PEARLM remains descriptive. Their Chapter 4 profiles can be placed alongside documented architectural or execution constraints, but no targeted module ablation isolates those constraints as the cause of a curve shape. Statements about coarse-to-fine reasoning, temporal requirements, path-language modelling, constrained generation, or candidate availability therefore remain contextual explanations or hypotheses rather than demonstrated causal findings.

Dataset dependence has the same evidential boundary. The PGPR/UCPR ablation confirms that operating points and gains differ between LastFM and ML-1M under one controlled protocol. The datasets also differ in interactions, timestamps, graph structure, bridge-entity degrees, path types, and candidate paths, but the current experiments do not isolate the contribution of each property. The observed differences can therefore motivate targeted future tests without assigning a single dataset characteristic as their cause.

These findings depend on the separation of evidence streams. Strict HR@10, NDCG@10, Precision@10, and Recall@10 describe validated baseline recommendation outputs. The main alpha sweeps describe six-model trade-off trajectories. The PGPR/UCPR ablation applies a frozen-item-set, baseline-preserving protocol to test control of the explanation or path module. Neither sweep NDCG nor ablation NDCG can replace the strict final-accuracy table.

This separation is the practical value of the canonical framework. It makes clear whether an observed difference is a validated baseline result, an explanation-objective trajectory, an ablation outcome, or an experiment that current evidence cannot support. Without common identifiers, validation gates, metric definitions, path-fidelity rules, and evidence roles, those categories could be incorrectly combined.

## 5.4 Amazon-Book KGAT as a Boundary Case

The validation gate from Chapter 3 partitions the registered model-dataset rows into the eligible set

\[
\mathcal{A}
=
\{(m,d): V_{m,d}=1\}
\]

and the boundary set

\[
\mathcal{B}
=
\{(m,d): V_{m,d}=0\}.
\]

Chapter 4 reports rows in \(\mathcal{A}\). Chapter 5 discusses selected rows in \(\mathcal{B}\) as boundary evidence rather than performance evidence.

The Batch 1C Amazon decision-flow specification follows export completeness, validation status, and explanation-sweep availability to distinguish boundary, partial, and main-style eligibility. It records reportability only and leaves the existing Amazon evidence status unchanged.

Amazon-Book KGAT tests where the framework can support comparison and where it must stop. It is a partial stress test, not a complete main experiment. The validation register contains PASS rows for KGGLM, PEARLM, and PGPR. Each covers 70,591 canonical test users, although the models produce different numbers of path and explanation records. The result establishes that several native-path exports can be validated in the larger Amazon setting.

The remaining UCPR, CAFE, and TPRec rows are BLOCKED / N/A for different contract reasons. UCPR has completed several port and smoke checks but lacks the required formal full-user export and strict-accuracy outputs. CAFE requires an Amazon-compatible schema and data-builder path, including a compatible UCPR view and checkpoint. TPRec has structural support, but the canonical interaction timestamps are sentinel -1 and do not support an approved formal temporal reward. None of these statuses is evidence of poor recommender performance.

Amazon explanation alpha sweeps are N/A because the current evidence contains no approved timestamp, SEP, and ETD denominator protocol for the dataset. The three passing rows therefore cannot be expanded into a six-model explanation comparison, and the blocked models cannot be ranked. Table 5.3 records the available and unavailable evidence for each row.

Figure 5.2 visualises the experiment-status matrix. The figure captures a methodological result: validation is itself part of the empirical outcome. Recording PASS and BLOCKED / N/A before comparative reporting prevents partial ports, unsupported temporal assumptions, and absent explanation denominators from being presented as comparable model evidence.

## 5.5 Limitations of the Current Framework and Experiments

The framework's conclusions are first bounded by coverage. Only LastFM and ML-1M provide complete six-model native-path comparisons. Amazon-Book KGAT has three PASS and three BLOCKED / N/A rows, and its explanation alpha sweeps are not reportable. Main comparative conclusions must therefore remain tied to the two complete datasets, with Amazon used only to demonstrate a boundary.

The explanation metrics add operational limitations. LIR requires valid timestamps and a recoverable interaction anchor. SEP is adopted as an implemented explanation-side metric rather than independently validated as a user-perceived serendipity construct. ETD depends on a declared taxonomy and denominator for legal path types. LIR / SEP / ETD exact implementation is repository-specific. These definitions are auditable but do not exhaust explanation quality and cannot be collapsed into one latent construct. Their conceptual source is verified through XRecSys, while the exact formulas and data assumptions evaluated here remain repository-specific [@balloccu2022xrecsys]. The historical cached SEP matrix is not available in the current evidence package, and no causal mechanism claim is inferred from SEP movement.

Native-path fidelity also affects strict accuracy. When a model cannot produce ten unique unseen path-ending items, the evaluator preserves the short or empty list, counts missing slots as non-hits, and reports slot coverage instead of padding with non-path recommendations. This policy protects the native-path contract, but strict accuracy can consequently reflect both recommendation quality and native-path candidate availability.

The current package contains no user study and therefore supports claims about computational path properties, not perceived usefulness, understanding, persuasiveness, or trust. No statistical-significance test artifact has been identified, and its final status requires manual checking. Numerical differences in Chapters 4 and 5 must remain observed experimental differences rather than inferential population claims.

Evidence quality also depends on model ports, canonical ID recovery, export completeness, and path validation. A blocked row may result from an incomplete data contract or unsupported mechanism requirement rather than weak model performance. Conversely, a PASS row establishes conformity with the registered evaluation contract, not universal correctness outside it.

Finally, the external citation layer is closed at draft level but not frozen for final submission. Primary sources for PGPR, UCPR, CAFE, TPRec, KGGLM, and XRecSys/LIR/SEP/ETD are verified. PEARLM remains safe as an arXiv citation, but its final venue and publisher DOI require manual checking. The same final-publication caveat applies to the “Measuring Why” survey if it is introduced later. These metadata gaps do not change the internal evidence, and external papers continue to support model or metric context rather than repository experimental values.

Table 5.4 consolidates these limitations, their implications, and possible mitigations. They define the valid scope of the current results and motivate the evidence-coverage, robustness, human-evaluation, and reproducibility recommendations in Chapter 6.
