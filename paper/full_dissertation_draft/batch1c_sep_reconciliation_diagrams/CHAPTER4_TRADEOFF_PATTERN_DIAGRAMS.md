# Chapter 4 Trade-off Pattern Diagrams

## 1. Alpha-Sweep Trade-off Process

### Purpose

Show how the registered objective-specific sweep is summarised by explanation movement and paired sweep NDCG movement, without defining a universal alpha formula.

### Mermaid Specification

```mermaid
flowchart LR
    A["alpha = 0: ranking-oriented baseline"] --> B["intermediate alpha values"]
    B --> C["alpha = 1: explanation-objective-oriented endpoint"]
    C --> D["Measure Delta q"]
    C --> E["Measure Delta NDCG_sweep"]
    D --> F["Result-level trade-off pattern"]
    E --> F
```

### Graphviz DOT Specification

```dot
digraph AlphaSweepProcess {
  rankdir=LR;
  node [shape=box];
  A [label="alpha = 0: ranking-oriented baseline"];
  B [label="intermediate alpha values"];
  C [label="alpha = 1: explanation-objective-oriented endpoint"];
  D [label="Measure Delta q"];
  E [label="Measure Delta NDCG_sweep"];
  F [label="Result-level trade-off pattern"];
  A -> B -> C;
  C -> D -> F;
  C -> E -> F;
}
```

### Proposed Caption

Objective-specific alpha-sweep reporting process. The sweep NDCG in this diagram is paired alpha-sweep evidence and must not be interpreted as strict NDCG@10. LIR, SEP, and ETD retain their implementation-specific controls; the diagram does not impose one universal linear score.

### Evidence Role

Conceptual reporting aid for the registered sweep endpoints and trajectories. It adds no result and no inferential statistic.

### Final Rendering Recommendation

Render from DOT to monochrome SVG after the Chapter 4 placement is frozen.

### Placement Recommendation

Chapter 4.1, main text. A shorter cross-reference may also appear in Chapter 3.6.

## 2. Empirical Trade-off Pattern Schematic

### Purpose

Provide a vocabulary for grouping the descriptive response patterns discussed in Chapter 4 without creating a metric, threshold, or model ranking.

### Markdown Matrix

| Ranking cost / explanation movement | Low movement | High movement |
| --- | --- | --- |
| Low ranking cost | Flat / stable | Efficient movement |
| High ranking cost | Restricted costly | High-gain high-cost |

### Mermaid Specification

```mermaid
flowchart TB
    S["Descriptive trade-off pattern"] --> LL["Low movement / low ranking cost: flat or stable"]
    S --> LH["High movement / low ranking cost: efficient movement"]
    S --> HL["Low movement / high ranking cost: restricted costly"]
    S --> HH["High movement / high ranking cost: high-gain high-cost"]
```

### Graphviz DOT Specification

```dot
digraph TradeoffPatternMatrix {
  graph [label="Explanation movement: low to high", labelloc=t];
  node [shape=box, fixedsize=true, width=2.4, height=0.8];
  lowlow [label="Flat / stable", pos="0,1!"];
  lowhigh [label="Efficient movement", pos="3,1!"];
  highlow [label="Restricted costly", pos="0,0!"];
  highhigh [label="High-gain high-cost", pos="3,0!"];
  lowlow -> lowhigh [style=invis];
  highlow -> highhigh [style=invis];
}
```

### Proposed Caption

Schematic vocabulary for the descriptive Chapter 4 trade-off patterns. This schematic summarises empirical pattern types. It is not a new metric and does not assign statistical significance. Placement in a cell does not establish model superiority or causal mechanism.

### Evidence Role

Result-level synthesis aid for patterns already reported in the registered strict and alpha-sweep evidence streams.

### Final Rendering Recommendation

Retain the Markdown matrix if a compact table is clearer. If rendered, recreate as a simple monochrome quadrant in DOT or draw.io without plotting experimental points.

### Placement Recommendation

Chapter 4.7, main text; keep as a table rather than a numbered figure if the supervisor prefers fewer conceptual figures.

## 3. Evidence-Stream Separation

### Purpose

Make the role and boundary of each evidence stream explicit so that strict accuracy is not replaced by sweep or ablation values.

### Mermaid Specification

```mermaid
flowchart TD
    A[Validated export row] --> B[Strict accuracy stream]
    A --> C[Explanation endpoint stream]
    A --> D[Alpha-sweep trade-off stream]
    A --> E[Ablation stream]
    A --> F[Boundary validation stream]
    B --> B1[HR@10 / NDCG@10 / Precision@10 / Recall@10]
    C --> C1[LIR / SEP / ETD endpoints]
    D --> D1[Delta q and Delta NDCG_sweep]
    E --> E1[Baseline preservation and retention]
    F --> F1[PASS / BLOCKED / PARTIAL]
```

### Graphviz DOT Specification

```dot
digraph EvidenceStreams {
  rankdir=TB;
  node [shape=box];
  A [label="Validated export row"];
  B [label="Strict accuracy stream"];
  C [label="Explanation endpoint stream"];
  D [label="Alpha-sweep trade-off stream"];
  E [label="Ablation stream"];
  F [label="Boundary validation stream"];
  B1 [label="HR@10 / NDCG@10 / Precision@10 / Recall@10"];
  C1 [label="LIR / SEP / ETD endpoints"];
  D1 [label="Delta q and Delta NDCG_sweep"];
  E1 [label="Baseline preservation and retention"];
  F1 [label="PASS / BLOCKED / PARTIAL"];
  A -> B -> B1;
  A -> C -> C1;
  A -> D -> D1;
  A -> E -> E1;
  A -> F -> F1;
}
```

### Proposed Caption

Separation of the five registered evidence streams. The streams are intentionally separated to avoid replacing strict accuracy with sweep evidence or ablation evidence. Boundary statuses record reportability and are not comparative performance values.

### Evidence Role

Conceptual evidence-provenance map; no values or new experimental conclusions are introduced.

### Final Rendering Recommendation

Render from DOT to monochrome SVG with equal visual weight for the five streams.

### Placement Recommendation

Chapter 3.6, main text. Chapter 4 may cite it rather than repeat it.
