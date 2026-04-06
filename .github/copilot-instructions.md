# Copilot Instructions

This repository uses GitHub Copilot as a coding assistant. This file defines the project constitution: architectural constraints, conventions, and decisions that must be treated as binding unless explicitly changed here.

If a design decision is made during a session, update this file immediately. Do not rely on conversational history as a source of truth.

## Prime Directive

- Optimize for "works makes beautiful": pragmatic, minimal, working solutions over architectural purity.
- Do not introduce abstraction unless it removes real duplication or reduces real complexity.
- Prefer clarity over cleverness.

## High Priority Rules

- Respect existing architecture and naming unless explicitly asked to refactor.
- Do not reintroduce previously rejected ideas.
- Avoid large rewrites. Prefer small, reviewable diffs.
- When uncertain, ask a short clarifying question rather than guessing.

## Output and Formatting Rules

- All code and command output must be ASCII only.
- When generating Markdown intended to be saved as a file, return raw Markdown suitable for direct saving.
- Keep formatting simple and readable.
- When referring to filenames or symbols in the user's workspace, use plain filenames without special formatting (do not wrap them in backticks).
- When asked for a decision, respond concisely.
- Do not include extended explanations unless explicitly requested.
- Prefer minimal diffs over narrative analysis.

## Coding Style

- Prefer direct, explicit code over clever patterns.
- Keep functions small and testable.
- Favor explicit error handling over silent failure.
- Keep dependencies minimal.
- Do not introduce frameworks or heavy patterns without a concrete need.

## Project Conventions

- Follow the existing directory structure and module boundaries.
- Match the existing naming style (files, functions, classes).
- Keep configuration close to the code it configures.
- If adding a new script or tool, document it briefly in the README or relevant doc.

## Tests

- If tests exist, update or add tests that cover behavioral changes.
- Prefer fast unit tests unless integration testing is required by the change.

## Documentation

- Update documentation when behavior or interfaces change.
- Architectural decisions must be recorded under "Design Constraints" below.

## Design Constraints

### Function Literals and Syntax

- Function literals are anonymous expressions: function (params) { ... }
- Named function syntax is statement sugar only: function name(params) { ... } rewrites to name = function(params) { ... }
- Expression statements are allowed, so function(...) { ... }; is legal as an expression statement, but function name(...) { ... } is not legal inside expressions.

### If/Else Requires Compound Statements

Constraint:
- if and else branches must always use compound (bracketed) statements.
- Single-statement branches are not supported.

Valid example:

    if (condition) {
        statement1;
        statement2;
    } else {
        statement3;
    }

Invalid example:

    if (condition) statement1;

Rationale:
- Keeps the grammar simpler.
- Avoids ambiguity in recursive descent parsing.
- Eliminates dangling-else edge cases.
- Makes the AST structure uniform and predictable.

Notes:
- Do not introduce optional single-statement branches.
- Do not add implicit block wrapping.
- Any change to this rule requires updating this document.

### Core Language Minimalism

Constraint:
- The core language favors a small, consistent grammar over banning semantically useless constructs.
- Expression statements are allowed even if they have no side effects (e.g., `2;`).

Rationale:
- Keeps the grammar minimal and orthogonal.
- Enforces clarity in the core; warnings belong in a linter.

Notes:
- Do not add grammar restrictions solely to prevent "useless" statements.

## Non-Goals

- Do not add features because they are common in other languages.
- Do not increase grammar complexity without a clear functional benefit.
- Do not refactor for stylistic reasons alone.

## Rejected Ideas

Use this section to record decisions that were explicitly rejected.

Template:

Rejected:
- Description of the rejected idea.

Reason:
- Why it was rejected.

Revisit if:
- Conditions under which the decision might change.

## Change Protocol

When suggesting a code change:
- State the intent briefly.
- Provide the smallest diff that accomplishes it.
- Indicate any required test updates.
- Indicate whether documentation needs updating.

## Documentation Site Structure (/docs)

This repository serves course materials via GitHub Pages from the `/docs` directory.

### Directory Structure

- `/docs/index.html`
  Static landing page with a table of contents (TOC) linking to slide decks.
  This page is NOT Reveal-based.

- `/docs/slides/`
  Contains all Reveal.js slide decks.

### Slide Deck Structure

Each topic deck must consist of:

- `/docs/slides/<deck>.md`
- `/docs/slides/<deck>.html`

Naming convention for "topics":

- `<deck>` = `topic-XX-short-slug`
- Topic numbers are always two-digit (01, 02, 03, ..., 10, 11, ...).
- Example: `topic-01-expressions`

Reveal.js usage:

- Each deck HTML wrapper loads its matching Markdown file using:
  `data-markdown="<deck>.md"`
- The HTML wrapper must remain minimal and consistent across decks.
- No build step is used.
- Do not introduce other slide frameworks (Marp, Pandoc, etc.).
- Do not introduce build systems or generators.

Markdown Conventions (Reveal Markdown plugin):

- `---` separates horizontal slides.
- `--` separates vertical slides.
- `Note:` introduces speaker notes.
- Use standard fenced code blocks.
- Keep slide content ASCII-only unless explicitly required otherwise.
- Prefer clarity over decorative formatting.

### Root TOC Page Rules

- `/docs/index.html` is a simple static HTML page.
- It contains a clean unordered list of links to slide decks.
- Links must use relative paths like:
  `slides/topic-01-expressions.html`
- Keep formatting consistent across entries.
- Do not convert the root index into a Reveal deck.
- Do not add frameworks, JS libraries, or unnecessary styling.

### TOC Ordering Rule

- Topics in `/docs/index.html` must be sorted numerically by topic number.
- Topic numbers are two-digit and determine ordering.
- Insert new topics in the correct numeric position.
- Do NOT append new topics to the bottom unless it is the next sequential number.
- Preserve formatting and indentation of existing entries.

### When Creating a New Slide Deck

1. Create `/docs/slides/<deck>.md`.
2. Create `/docs/slides/<deck>.html` using the standard Reveal wrapper.
3. Update `/docs/index.html` to include the new deck in correct numeric order.
4. Maintain consistent formatting and naming.

### When Modifying Slides

- Prefer small, reviewable edits.
- Preserve existing naming conventions.
- Do not reorganize directories unless explicitly requested.

### Design Principle

The documentation site must remain:

- Static
- Minimal
- Artifact-driven
- Tool-light

Avoid build systems, generators, or architectural expansion unless explicitly requested.