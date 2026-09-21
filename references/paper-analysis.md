## Phase 1: write an accessible technical analysis

Read the whole paper. Create a self-contained explanation for readers who have general science and technology literacy but may not know the paper's field. Cover every major technical contribution, including the paper's problem framing, core design, mechanisms, training or experimental setup, results.

Start with the paper's central claim, move from an accessible overview into the technical mechanisms, then return to results. Organize by the reader's causal questions—what problem exists, what each contribution changes, how it works, and what result follows—rather than mechanically reproducing paper section headings.

Lead each section with its substantive conclusion, then explain the supporting mechanism or evidence. Make paragraphs read as a continuous technical account: use natural sentence-length variation and let the subject matter, rather than “the paper” or “the authors,” be the grammatical subject whenever attribution is not needed.

### Preserve technical detail without losing clarity

- Keep architecture, algorithms, data or training choices, system design, experimental conditions, and quantitative results when they are necessary to understand a major contribution. Do not remove a technical detail simply because it is unfamiliar.
- On first use, explain every technical term, acronym, component name, variable, or specialized process. Use this order: **name → concrete problem it addresses → how it works → why the change matters**.
- For concepts that need intuition, give a concrete example or a bounded analogy, then return immediately to the paper's actual mechanism. Never present an analogy as evidence or as a complete equivalence.
- Use short sections, descriptive headings, compact bullets, comparison tables, and text flow diagrams when they improve comprehension. A process flow may use `input → operation → output`; do not use equations or TeX.
- When the paper contains an important formula, explain it in words: identify the quantities, describe how they affect one another, state the condition under which the relationship applies, and explain why the paper uses it. Do not reproduce the formula or its symbols. The later video may copy that formula's TeX from the paper.
- Define a term once in enough detail to make later use natural. Thereafter use the concise paper term when it improves precision; do not repeatedly replace it with a vague simplification.
- Give each number its measurement, comparison, and condition. Distinguish a model specification, a benchmark result, a development measurement, and a participant report.
- Summarize a result table's overall pattern before giving individual values. Include only the values that support a distinct conclusion, comparison; do not narrate rows one by one.

### Keep the prose natural

- Do not narrate the writing process or rely on repeated template constructions. State the positive mechanism or conclusion directly unless a negative qualification is scientifically necessary.
- Prefer descriptive headings and concrete verbs; headings should add structure rather than restate the paragraph that follows.

### Maintain factual boundaries

- Base all factual content on the paper. Supplemental material may explain general prerequisites, but cannot change the paper's claims.
- Say “the paper reports,” “the authors attribute,” or equivalent language only when a result is self-reported, observational, based on selected cases, or lacks an independent causal comparison.
- If the paper contains a material internal inconsistency, report the conflicting statements plainly and do not pick one silently.


## Phase 1 output

Create `output/<paper_short_name>/paper-analysis.md` with:

1. **Title and central claim** — title, author/source metadata, and a concise explanation of what the paper argues or contributes.
2. **Executive overview** — the problem, the paper's overall approach, and the main result or implication.
3. **Major technical contributions** — one section per major contribution. For each, explain its problem, mechanism, technical details, and result using the rules above.
4. **How the pieces fit together** — a concise causal account of how the contributions combine into the reported system or finding.
5. **Results** — reported results with their conditions

Present the analysis and ask the user to approve it or request changes, then stop. Do not write `video-script.md` until the analysis is approved.
