# Chapter 3 Dataflow and Validation Diagrams

## 1. End-to-End Framework Dataflow

### Purpose

Show how canonical dataset truth, model-specific execution, native-path exports, validation, and distinct reporting streams connect without presenting the framework as a new recommender architecture.

### Mermaid Specification

```mermaid
flowchart TD
    A[Canonical dataset truth] --> B[Model-specific view construction]
    B --> C[Model execution or imported outputs]
    C --> D[Native-path export contract]
    D --> D1[uid_topk.csv]
    D --> D2[pred_paths.csv]
    D --> D3[uid_pid_explanation.csv]
    D1 --> E[Validation gates]
    D2 --> E
    D3 --> E
    E -->|PASS| F[Reportable model-dataset row]
    E -->|BLOCKED or PARTIAL| G[Boundary-case record]
    F --> H[Strict accuracy metrics]
    F --> I[Explanation metrics: LIR / SEP / ETD]
    F --> J[Alpha-sweep trade-off outputs]
    F --> K[Ablation outputs]
    H --> L[Chapter 4 strict accuracy results]
    I --> M[Chapter 4 explanation endpoint results]
    J --> N[Chapter 4 trade-off findings]
    K --> O[Chapter 5 ablation interpretation]
    G --> P[Chapter 5 boundary-case analysis]
```

### Graphviz DOT Specification

```dot
digraph FrameworkDataflow {
  rankdir=TB;
  node [shape=box];
  A [label="Canonical dataset truth"];
  B [label="Model-specific view construction"];
  C [label="Model execution or imported outputs"];
  D [label="Native-path export contract"];
  D1 [label="uid_topk.csv"];
  D2 [label="pred_paths.csv"];
  D3 [label="uid_pid_explanation.csv"];
  E [label="Validation gates", shape=diamond];
  F [label="Reportable model-dataset row"];
  G [label="Boundary-case record"];
  H [label="Strict accuracy metrics"];
  I [label="Explanation metrics: LIR / SEP / ETD"];
  J [label="Alpha-sweep trade-off outputs"];
  K [label="Ablation outputs"];
  L [label="Chapter 4 strict accuracy results"];
  M [label="Chapter 4 explanation endpoint results"];
  N [label="Chapter 4 trade-off findings"];
  O [label="Chapter 5 ablation interpretation"];
  P [label="Chapter 5 boundary-case analysis"];
  A -> B -> C -> D;
  D -> D1; D -> D2; D -> D3;
  D1 -> E; D2 -> E; D3 -> E;
  E -> F [label="PASS"];
  E -> G [label="BLOCKED or PARTIAL"];
  F -> H; F -> I; F -> J; F -> K;
  H -> L; I -> M; J -> N; K -> O; G -> P;
}
```

### Proposed Caption

End-to-end canonical native-path evaluation dataflow. This diagram describes the evaluation framework dataflow and does not define a new recommender architecture. PASS rows enter distinct reporting streams, whereas BLOCKED or PARTIAL rows remain boundary evidence.

### Evidence Role

Conceptual map of the implemented evaluation contract. It contains no experimental values and does not establish model performance.

### Final Rendering Recommendation

Render from DOT to monochrome SVG after chapter wording and placement are frozen.

### Placement Recommendation

Chapter 3.1, main text.

## 2. Validation Gate Flowchart

### Purpose

Make reportability eligibility explicit and distinguish validation failure from recommendation performance.

### Mermaid Specification

```mermaid
flowchart TD
    A[Export package for model m on dataset d] --> B{Coverage complete?}
    B -->|No| X[BLOCKED or PARTIAL evidence]
    B -->|Yes| C{Duplicate top-k items?}
    C -->|Yes| X
    C -->|No| D{Seen-item leakage?}
    D -->|Yes| X
    D -->|No| E{Canonical uid / pid consistent?}
    E -->|No| X
    E -->|Yes| F{Path endpoints align with user-item pair?}
    F -->|No| X
    F -->|Yes| G{Top-k and explanation rows aligned?}
    G -->|No| X
    G -->|Yes| H{Candidate paths consistent?}
    H -->|No| X
    H -->|Yes| I{Scores sane?}
    I -->|No| X
    I -->|Yes| Y[PASS: reportable evidence row]
```

### Graphviz DOT Specification

```dot
digraph ValidationGate {
  rankdir=TB;
  node [shape=diamond];
  A [label="Export package for model m on dataset d", shape=box];
  B [label="Coverage complete?"];
  C [label="Duplicate top-k items?"];
  D [label="Seen-item leakage?"];
  E [label="Canonical uid / pid consistent?"];
  F [label="Path endpoints align with user-item pair?"];
  G [label="Top-k and explanation rows aligned?"];
  H [label="Candidate paths consistent?"];
  I [label="Scores sane?"];
  X [label="BLOCKED or PARTIAL evidence", shape=box];
  Y [label="PASS: reportable evidence row", shape=box];
  A -> B;
  B -> X [label="No"]; B -> C [label="Yes"];
  C -> X [label="Yes"]; C -> D [label="No"];
  D -> X [label="Yes"]; D -> E [label="No"];
  E -> X [label="No"]; E -> F [label="Yes"];
  F -> X [label="No"]; F -> G [label="Yes"];
  G -> X [label="No"]; G -> H [label="Yes"];
  H -> X [label="No"]; H -> I [label="Yes"];
  I -> X [label="No"]; I -> Y [label="Yes"];
}
```

### Proposed Caption

Validation gate for a model-dataset export package. This flowchart shows validation eligibility, not recommendation performance. BLOCKED or PARTIAL status must not be interpreted as a low-performing model result.

### Evidence Role

Conceptual summary of the registered checks used to determine whether a row is reportable.

### Final Rendering Recommendation

Render from DOT to monochrome SVG, with decision nodes visually distinct from terminal statuses.

### Placement Recommendation

Chapter 3.4, main text.

## 3. Metric Anchor Schematic

### Purpose

Show which native-path component anchors LIR, SEP, and ETD while retaining the repository-specific boundary of each definition.

### Mermaid Specification

```mermaid
flowchart LR
    P["Native path p(u,i): user -> seed item -> bridge entity -> recommended item"] --> A["a(p): seed item anchor"]
    P --> B["b(p): bridge entity anchor"]
    P --> C["tau(p): path type / final relation"]
    A --> LIR["LIR: linked-interaction recency"]
    B --> SEP["SEP: repository-specific degree-derived bridge-entity score"]
    C --> ETD["ETD: path-type diversity over top-K"]
```

### Graphviz DOT Specification

```dot
digraph MetricAnchors {
  rankdir=LR;
  node [shape=box];
  P [label="Native path p(u,i): user -> seed item -> bridge entity -> recommended item"];
  A [label="a(p): seed item anchor"];
  B [label="b(p): bridge entity anchor"];
  C [label="tau(p): path type / final relation"];
  LIR [label="LIR: linked-interaction recency"];
  SEP [label="SEP: repository-specific degree-derived bridge-entity score"];
  ETD [label="ETD: path-type diversity over top-K"];
  P -> A; P -> B; P -> C;
  A -> LIR; B -> SEP; C -> ETD;
}
```

### Proposed Caption

Metric anchors in the registered native-path structure. LIR uses the seed-item interaction anchor, SEP uses a repository-specific degree-derived bridge-entity score, and ETD uses the path-type taxonomy over the top-K explanations. These computational properties do not establish user-perceived explanation quality.

### Evidence Role

Definition aid based on `docs/guides/PATH_METRICS_GUIDE.md`, `xrecsys/metrics.py`, and related repository code. Historical SEP matrix-cache provenance still requires manual verification.

### Final Rendering Recommendation

Render from DOT or recreate in draw.io as a monochrome vector schematic after SEP wording is frozen.

### Placement Recommendation

Chapter 3.4, main text if space permits; otherwise appendix with an in-text reference.
