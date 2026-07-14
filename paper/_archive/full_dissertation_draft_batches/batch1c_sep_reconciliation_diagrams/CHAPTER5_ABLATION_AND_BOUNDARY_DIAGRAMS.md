# Chapter 5 Ablation and Boundary Diagrams

## 1. PGPR/UCPR Ablation Evidence Flow

### Purpose

Show the registered sequence from alpha-zero preservation through objective-specific ablation sweeps to a bounded controllability interpretation.

### Mermaid Specification

```mermaid
flowchart TD
    A[Baseline native-path recommendation list] --> B[alpha = 0 preservation check]
    B -->|preserved| C[Path-module / candidate-path ablation setting]
    B -->|not preserved| X[Do not interpret as controlled ablation]
    C --> D[Run LIR / SEP / ETD-oriented sweep]
    D --> E[Compute paired NDCG retention]
    E --> F{Retention >= 95%?}
    F -->|Yes| G[Eligible operating point]
    F -->|No| H[Ranking-cost boundary]
    G --> I[Controllability interpretation]
    H --> J[Limitation or unsupported operating point]
```

### Graphviz DOT Specification

```dot
digraph AblationEvidenceFlow {
  rankdir=TB;
  node [shape=box];
  A [label="Baseline native-path recommendation list"];
  B [label="alpha = 0 preservation check", shape=diamond];
  C [label="Path-module / candidate-path ablation setting"];
  X [label="Do not interpret as controlled ablation"];
  D [label="Run LIR / SEP / ETD-oriented sweep"];
  E [label="Compute paired NDCG retention"];
  F [label="Retention >= 95%?", shape=diamond];
  G [label="Eligible operating point"];
  H [label="Ranking-cost boundary"];
  I [label="Controllability interpretation"];
  J [label="Limitation or unsupported operating point"];
  A -> B;
  B -> C [label="preserved"];
  B -> X [label="not preserved"];
  C -> D -> E -> F;
  F -> G [label="Yes"];
  F -> H [label="No"];
  G -> I;
  H -> J;
}
```

### Proposed Caption

Registered PGPR/UCPR ablation evidence flow. This diagram describes the PGPR/UCPR ablation evidence stream. It does not establish six-model superiority. The interpretation is limited to the frozen-item-set, baseline-preserving protocol.

### Evidence Role

Protocol summary for the existing registered ablation artifacts; it adds no model result or causal claim.

### Final Rendering Recommendation

Render from DOT to monochrome SVG after the Chapter 5 wording is frozen.

### Placement Recommendation

Chapter 5.1, main text before the detailed formula and operating-point discussion.

## 2. 95% NDCG Retention Operating Point

### Purpose

Show how candidate alpha values enter the ablation-only retention set and how the objective-specific operating point is selected.

### Mermaid Specification

```mermaid
flowchart LR
    A["For each alpha"] --> B["Compute explanation metric Q(alpha)"]
    A --> C["Compute NDCG retention"]
    C --> D{Retention >= 0.95}
    D -->|Yes| E["Candidate operating point"]
    D -->|No| F["Excluded from 95% retention set"]
    E --> G["Select alpha* with highest Q(alpha)"]
```

### Graphviz DOT Specification

```dot
digraph RetentionOperatingPoint {
  rankdir=LR;
  node [shape=box];
  A [label="For each alpha"];
  B [label="Compute explanation metric Q(alpha)"];
  C [label="Compute NDCG retention"];
  D [label="Retention >= 0.95", shape=diamond];
  E [label="Candidate operating point"];
  F [label="Excluded from 95% retention set"];
  G [label="Select alpha* with highest Q(alpha)"];
  A -> B;
  A -> C -> D;
  D -> E [label="Yes"];
  D -> F [label="No"];
  B -> G;
  E -> G;
}
```

### Proposed Caption

Selection of an objective-specific operating point under the registered ablation constraint. The 95% threshold is used only within the ablation evidence stream and is not a general model-ranking criterion.

### Evidence Role

Visual restatement of the existing constrained operating-point rule. It does not add a threshold to strict accuracy or the Chapter 4 sweeps.

### Final Rendering Recommendation

Render from DOT to monochrome SVG; retain as an appendix candidate if the formula is sufficient in the main text.

### Placement Recommendation

Chapter 5.1 after the retention and constrained-selection formulas, or appendix with an in-text reference.

## 3. Amazon Boundary-Case Decision Flow

### Purpose

Show how native-path export completeness, validation, and explanation-sweep availability determine Amazon reportability without ranking blocked rows.

### Mermaid Specification

```mermaid
flowchart TD
    A[Amazon-Book KGAT row] --> B{Native-path export complete?}
    B -->|No| X[Boundary case]
    B -->|Yes| C{Validation gates pass?}
    C -->|No| X
    C -->|Yes| D{Explanation sweep available?}
    D -->|No| Y[Partial evidence only]
    D -->|Yes| Z[Eligible for main-style analysis]
    X --> E[Chapter 5 boundary discussion]
    Y --> E
```

### Graphviz DOT Specification

```dot
digraph AmazonBoundaryFlow {
  rankdir=TB;
  node [shape=box];
  A [label="Amazon-Book KGAT row"];
  B [label="Native-path export complete?", shape=diamond];
  C [label="Validation gates pass?", shape=diamond];
  D [label="Explanation sweep available?", shape=diamond];
  X [label="Boundary case"];
  Y [label="Partial evidence only"];
  Z [label="Eligible for main-style analysis"];
  E [label="Chapter 5 boundary discussion"];
  A -> B;
  B -> X [label="No"];
  B -> C [label="Yes"];
  C -> X [label="No"];
  C -> D [label="Yes"];
  D -> Y [label="No"];
  D -> Z [label="Yes"];
  X -> E;
  Y -> E;
}
```

### Proposed Caption

Decision flow for the partial Amazon-Book KGAT boundary case. This diagram records reportability and boundary status, not comparative recommendation performance. Current validated rows remain partial evidence because the complete explanation-sweep protocol is unavailable.

### Evidence Role

Boundary and reportability summary of existing validation status. PASS does not imply a complete six-model Amazon comparison, and BLOCKED / N/A does not imply poor model performance.

### Final Rendering Recommendation

Render from DOT to monochrome SVG only if the decision flow adds clarity beyond the existing status matrix.

### Placement Recommendation

Chapter 5.4 after the eligibility and boundary-set definitions, or appendix with an in-text reference.
