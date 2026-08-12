# Agent-First Documentation System Design

**Date:** 2026-08-13
**Status:** Approved design awaiting written-spec review
**Scope:** Documentation governance, document templates, machine-readable registry, and local validation

## 1. Purpose

Eidos needs an agent-first documentation system before its research architecture is formalized. The existing Chinese concept note is useful historical input, but it is not an approved project vision, architecture, roadmap, or implementation specification.

This design establishes the authority model and tooling that future agents will use to create, discover, relate, validate, and replace formal project documents. It deliberately does not decide the ARC tokenizer, model backbone, data-generation strategy, training objectives, evaluation design, or research roadmap.

## 2. Design Goals

The first version must:

1. Give agents one deterministic entry point for repository instructions.
2. Separate binding requirements, proposed changes, recorded decisions, experimental evidence, and historical notes.
3. Store document identity and lifecycle metadata in one machine-readable source of truth.
4. Detect malformed metadata, broken relationships, authority conflicts that are structurally discoverable, and drift between the registry and the filesystem.
5. Keep formal documentation in English while preserving the original concept note in its original language.
6. Provide reusable templates without prematurely creating research specifications.

## 3. Non-Goals

The first version will not:

- Select or recommend a tokenizer, model backbone, recurrent-memory mechanism, data generator, training objective, or evaluation suite.
- Convert the early concept note into an approved vision, architecture, specification, or roadmap.
- Create training code, datasets, experiment implementations, or other product code.
- Add continuous integration.
- Treat unverified statements in the concept note as requirements or accepted decisions.
- Add formal research documents merely to populate otherwise empty directories.

## 4. Repository Structure

The initial repository structure will be:

```text
Eidos/
|-- AGENTS.md
|-- README.md
|-- docs/
|   |-- README.md
|   |-- registry.json
|   |-- registry.schema.json
|   |-- governance/
|   |   `-- GOV-0001-documentation-system.md
|   |-- templates/
|   |   |-- rfc.md
|   |   |-- adr.md
|   |   |-- specification.md
|   |   `-- experiment.md
|   `-- notes/
|       |-- README.md
|       `-- early-arc-specialized-reasoning-concept.zh-TW.md
|-- tools/
|   `-- docs/
|       |-- requirements.txt
|       `-- validate.py
`-- tests/
    `-- docs/
        `-- test_validate.py
```

The following governed directories will be created only when their first document is introduced:

- `docs/rfcs/`
- `docs/decisions/`
- `docs/specifications/`
- `docs/experiments/`

Planning artifacts under `docs/superpowers/` are workflow records rather than governed project documents. They are excluded from the document registry and cannot establish project authority.

## 5. Authority Model

Authority is resolved in the following order:

1. `AGENTS.md` governs agent behavior and required repository workflow.
2. Active governance documents govern the documentation system.
3. Active specifications define required current system behavior.
4. Accepted ADRs record binding decisions and their rationale.
5. RFCs describe proposals. They remain non-normative even after acceptance until their binding outcomes are represented by an accepted ADR or active specification.
6. Experiment records contain evidence and interpretation, not requirements.
7. Files under `docs/notes/` are non-normative historical or exploratory material.
8. Planning artifacts under `docs/superpowers/` are non-normative workflow material.

An agent must not silently resolve a conflict between active authorities. It must report the conflicting document IDs and stop the affected work until the conflict is resolved through the documentation process.

The root README and documentation index must state that Eidos has no formally accepted research architecture at this stage.

## 6. Agent Operating Contract

The root `AGENTS.md` will be concise and operational. It will require every agent to:

1. Read `AGENTS.md`, `docs/README.md`, and `docs/registry.json` before substantive work.
2. Use the registry to identify applicable active governance documents, active specifications, accepted ADRs, and their relationships.
3. Treat RFCs as proposals, experiments as evidence, notes as background, and planning artifacts as workflow records.
4. Classify a new formal document before creating it and use the corresponding template.
5. Update a governed Markdown document and its registry entry in the same change.
6. Preserve immutable document IDs and paths after publication.
7. Run the documentation validator before claiming completion for any change that affects governed documentation or documentation tooling.
8. Stop and report conflicting active authorities rather than choosing one without an explicit decision.

`AGENTS.md` will point to authoritative documents; it will not duplicate research requirements or accumulate architecture design.

## 7. Registry Contract

`docs/registry.json` is the sole authority for governed-document metadata. Governed Markdown files will not duplicate registry metadata in YAML front matter.

The registry has this top-level shape:

```json
{
  "schema_version": 1,
  "documents": []
}
```

Each document entry contains exactly these required fields:

```json
{
  "id": "SPEC-0001",
  "title": "Example title",
  "type": "specification",
  "status": "active",
  "path": "docs/specifications/SPEC-0001-example-title.md",
  "language": "en",
  "summary": "One-sentence description.",
  "depends_on": [],
  "supersedes": [],
  "informed_by": ["NOTE-0001"]
}
```

The registry rules are:

- `schema_version` is the integer `1` in the first release.
- `documents` is sorted lexicographically by `id`.
- IDs use four decimal digits and one fixed prefix: `GOV`, `RFC`, `ADR`, `SPEC`, `EXP`, or `NOTE`.
- Paths are repository-relative, use `/` separators, contain no `.` or `..` segments, and are sorted deterministically through the ID-sorted entry order.
- IDs and paths are immutable after their first committed publication.
- Every substantive Markdown file in a governed document directory has exactly one registry entry.
- Registry entries cannot target indexes, templates, schemas, generated output, or files under `docs/superpowers/`.
- Formal documents use `language: "en"`. Archived notes may declare their actual language, including `zh-TW`.
- `depends_on`, `supersedes`, and `informed_by` contain unique IDs that exist in the same registry.
- No relation may reference its own document.
- `depends_on` and `supersedes` graphs must be acyclic.

The initial registry will contain `GOV-0001` and `NOTE-0001`. It will not contain README files, templates, the schema, the design specification under `docs/superpowers/`, or validator source and tests.

## 8. Document Types and Lifecycles

The allowed types, prefixes, directories, and statuses are:

| Type | Prefix | Directory | Allowed statuses |
| --- | --- | --- | --- |
| Governance | `GOV` | `docs/governance/` | `active`, `superseded`, `archived` |
| RFC | `RFC` | `docs/rfcs/` | `draft`, `in_review`, `accepted`, `rejected`, `withdrawn` |
| ADR | `ADR` | `docs/decisions/` | `proposed`, `accepted`, `deprecated`, `superseded` |
| Specification | `SPEC` | `docs/specifications/` | `draft`, `active`, `deprecated`, `superseded` |
| Experiment | `EXP` | `docs/experiments/` | `planned`, `running`, `completed`, `abandoned` |
| Note | `NOTE` | `docs/notes/` | `archived` |

Allowed forward transitions are:

- Governance: `active` to `superseded` or `archived`.
- RFC: `draft` to `in_review`; `in_review` to `accepted`, `rejected`, or `withdrawn`.
- ADR: `proposed` to `accepted`; `accepted` to `deprecated` or `superseded`.
- Specification: `draft` to `active`; `active` to `deprecated` or `superseded`.
- Experiment: `planned` to `running`; `running` to `completed` or `abandoned`.
- Note: remains `archived`.

The schema validates the current status vocabulary. The governance document defines transition policy because a standalone working-tree validator cannot infer a previous committed status without consulting version-control history.

Supersession has these consistency requirements:

- Only governance documents, ADRs, and specifications may use `supersedes`.
- A document may supersede only another document of the same type.
- Every ID listed in a replacement document's `supersedes` array must have status `superseded`.
- Every `superseded` document must be named by at least one same-type replacement document.
- Supersession relationships must not form cycles.

`depends_on` may point to a governance document, accepted ADR, active specification, or another same-type draft whose review explicitly requires it. `informed_by` may point to any registered document and communicates provenance without transferring authority.

## 9. Document Templates

The system will provide four templates:

### 9.1 RFC Template

Required sections:

- Problem
- Context
- Proposal
- Alternatives considered
- Risks and mitigations
- Unresolved questions
- Acceptance criteria
- Expected binding outputs

The template will explain that an accepted RFC is not itself a binding specification or decision record.

### 9.2 ADR Template

Required sections:

- Context
- Decision
- Consequences
- Rejected alternatives
- Supersession
- Verification impact

### 9.3 Specification Template

Required sections:

- Scope
- Definitions
- Normative requirements
- Interfaces
- Invariants
- Failure behavior
- Verification
- Dependencies and related decisions

Normative requirements use `MUST`, `SHOULD`, and `MAY` consistently.

### 9.4 Experiment Template

Required sections:

- Hypothesis
- Variables
- Controls
- Dataset or task set
- Metrics
- Procedure
- Results
- Artifacts
- Interpretation
- Threats to validity

An experiment record may support or challenge a proposal but cannot create a requirement.

## 10. Historical Concept Note

The existing `docs/從通用 LLM 到 ARC 專用推理架構.md` file will move to `docs/notes/early-arc-specialized-reasoning-concept.zh-TW.md` without translating or rewriting its substantive content.

A prominent English notice will be added before the original text. The notice will state that:

- the document is an archived, non-normative early concept;
- it is not an approved vision, roadmap, architecture, specification, or decision;
- its claims and technology references require independent verification;
- agents may use it only as background and provenance;
- any adopted idea must go through the formal RFC, ADR, specification, or experiment process.

The registry entry `NOTE-0001` will declare `language: "zh-TW"` and `status: "archived"`.

## 11. Schema and Validator

`docs/registry.schema.json` will use JSON Schema Draft 2020-12 and reject unknown fields. It will validate the top-level shape, required fields, primitive types, ID formats, basic path format, type and status vocabulary, relation-array uniqueness, and conditional prefix/status/path constraints by document type.

`tools/docs/validate.py` will perform checks that JSON Schema alone cannot express reliably:

1. Load and parse the registry and schema.
2. Validate the registry against the schema.
3. Check unique IDs and paths.
4. Check deterministic ID ordering and relation-array ordering.
5. Resolve every path against the repository root and reject absolute paths, backslashes, traversal, and paths outside the repository.
6. Verify that each registered document exists and each governed Markdown document is registered exactly once.
7. Verify relation targets, allowed target types and statuses, duplicate relations, and self-references.
8. Detect `depends_on` and `supersedes` cycles.
9. Verify supersession consistency in both directions.
10. Report all detected errors in one run, using concise messages that identify the affected field or document.

The validator will exit with status `0` on success and nonzero on failure. It will not rewrite or reorder files automatically.

The first release will not claim to enforce ID/path immutability or lifecycle transitions from version-control history. Those policies are binding through `GOV-0001`; repository-history enforcement can be proposed later.

## 12. Dependency and Commands

`jsonschema` will be the validator's only runtime dependency and will be declared in `tools/docs/requirements.txt` with a compatible-version constraint. Tests will use Python's standard `unittest` framework and temporary repository fixtures.

The documented commands will be:

```powershell
python -m pip install -r tools/docs/requirements.txt
python tools/docs/validate.py
python -m unittest discover -s tests/docs -v
```

## 13. Test Strategy

`tests/docs/test_validate.py` will exercise the validator through temporary repository fixtures. It will include:

- one fully valid registry and document tree;
- schema-invalid input;
- duplicate ID and duplicate path cases;
- a missing registered file;
- an unregistered governed Markdown file;
- an invalid type/status or prefix/path combination;
- a broken relation target;
- a duplicate or self relation;
- a dependency cycle;
- a supersession cycle;
- inconsistent forward and reverse supersession state;
- non-deterministic registry or relation ordering;
- a path traversal or non-normalized path;
- a formal document whose language is not English.

Tests will assert both the nonzero exit result and a stable identifying fragment of each actionable error message. No CI workflow will be added in this version.

## 14. Error Handling

Malformed JSON, an unreadable schema, a missing dependency, or an unresolved repository root is a validator execution error. The validator will report the cause without a Python traceback during normal command-line use and exit nonzero.

Registry violations are validation errors. The validator will accumulate independent validation errors so an agent can repair them in one iteration. Errors will be emitted in deterministic order.

An authority conflict that depends on semantic interpretation cannot be automatically adjudicated. `AGENTS.md` and `GOV-0001` will require the agent to identify the conflicting IDs, avoid affected implementation decisions, and request an explicit documentation change.

## 15. Acceptance Criteria

The documentation-system implementation is complete when:

1. The agreed repository structure exists.
2. `AGENTS.md` defines the agent-first discovery, authority, synchronization, conflict, and validation workflow.
3. Root and documentation READMEs state the current absence of an approved research architecture.
4. `GOV-0001` defines binding governance matching this design.
5. The four templates contain the required sections and authority notices.
6. The concept note is archived as `NOTE-0001` with its substantive Chinese content preserved and a clear non-normative notice added.
7. The registry and schema represent `GOV-0001` and `NOTE-0001` and pass validation.
8. The validator implements every check assigned to the first release in this design.
9. The complete documentation validator test suite passes locally.
10. No research vision, architecture, roadmap, or technology choice is represented as approved.

## 16. Deferred Work

Potential future proposals include CI integration, registry-aware document generation, repository-history checks for immutable IDs and lifecycle transitions, semantic conflict analysis, and the first formal research RFCs. None of these is implied or authorized by this design.
