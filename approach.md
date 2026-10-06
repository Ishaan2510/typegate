# Approach

## The problem, and where it came from

I found this problem in my own code. I have three Python projects on GitHub. Pitlane Live pins Python 3.11.9. TechReg Analyst and my F1 pit stop predictor pin nothing, so the hosting platform picks the version. TechReg's `retriever.py` uses `str | None` in a function signature. That syntax comes from PEP 604 and only exists from Python 3.10. On 3.9 the module fails at import time. Nothing broke, but nothing guaranteed it would not, and I had no way to see which features my code depended on. I never chose a Python version on purpose. I installed whatever was current.

A team adopting Python typing has the same problem at a larger scale. Before they standardise on a version or start using a feature, they need to know four things:

1. Can we use this feature on the Python version we run? If not, which version do we need?
2. If we cannot, what do we write instead, and under what condition is that substitute valid?
3. What could go wrong: is the feature still a draft, superseded, or dependent on something else?
4. Why does it work this way? What did its designers reject?

This is the third situation in the brief, a team evaluating a feature, narrowed to the question that actually blocks adoption: compatibility with the version they run.

## The data subset and why

I used the 49 PEPs whose `Topic` header contains `Typing`, from `github.com/python/peps` at a pinned commit.

1. **The boundary is not mine to argue about.** The PEP authors tag these PEPs as typing. Concurrency or syntax would have needed my own keyword list and a defence of every inclusion.
2. **It is dense.** The 49 PEPs mention each other 147 times, 42 have a rejected-ideas or alternatives section, and 36 have a backwards compatibility section. That is enough structure to reason over, not just to store.
3. **It is where my own problem lives.** Both syntaxes from my code, `X | None` (PEP 604) and `tuple[bool, str]` (PEP 585), are typing PEPs.

I did not use the CPython issue tracker or commit history. The question here is "which version introduced this and why", and the PEP headers and sections answer it directly. Commits would add precision about point releases, which is a next step, not a requirement.

## Entities and relationships

| Node | What it is |
|---|---|
| `PEP` | A typing PEP: status, title, authors, version, and its design reasoning (rejected ideas and backwards compatibility notes) stored as text |
| `Feature` | One usable typing feature, such as `X \| Y` unions or `TypedDict` |
| `PythonVersion` | A CPython minor version, 3.5 to 3.16 |

| Edge | From to | Source |
|---|---|---|
| `introduced_by` | Feature to PEP | feature catalog |
| `available_from` | Feature to PythonVersion | the introducing PEP's `Python-Version` header |
| `requires` | Feature to Feature | feature catalog |
| `falls_back_to` | Feature to Feature, with a condition and a rank | feature catalog |
| `next_version` | PythonVersion to PythonVersion | release order |
| `superseded_by`, `replaces`, `pep_requires` | PEP to PEP | PEP headers, written by the PEP authors |
| `builds_on`, `compat_concern`, `rejected_idea_ref`, `cites` | PEP to PEP | where in the citing PEP the mention appears |

The decisions behind this:

**Feature is its own node, separate from PEP.** A PEP is like a pull request and features are what it shipped. PEP 484 alone introduced `Union`, `Optional`, `Callable`, `TypeVar`, generics, type comments, and more, and each has a different answer to "what do I use instead". Users also ask about features, not PEP numbers. Treating each PEP as one feature would have answered "can we use `TypeVar`" at the level of all of PEP 484. The cost is a hand-built catalog of 43 features.

**Python versions are nodes linked in release order, not labels.** The reasoning walks this chain. "What does a team on 3.9 have" is a walk from the oldest version to 3.9. "What does each upgrade unlock" is a walk forward from 3.9. Making versions nodes also makes the timeline visible in the knowledge state itself.

**Rejected ideas are stored as text on the PEP, not as their own nodes.** Nodes would have connected rejected ideas across PEPs. I chose text to keep the graph focused on the compatibility question, which is what the team acts on. The design reasoning still reaches the user for the PEP that introduced their feature. Part of the cross-PEP connection survives anyway through the PEP-level `rejected_idea_ref` edges: when a team asks about `X | Y`, the output shows that PEP 655 referenced PEP 604 while rejecting the idea of renaming `Optional` to `Nullable`.

**PEP-to-PEP links are typed by the section the mention appears in.** A mention in a Specification section and a mention in a Backwards Compatibility section mean different things. A single "mentions" edge cannot tell "builds on" apart from "argues against". The rules are four title patterns in `kg/schema.py`, applied in priority order across the section and all its parent sections, so a mention inside "Rejected Ideas > Motivation for X" counts as a rejected-idea reference, not as builds-on.

**Header links are kept apart from body links.** `Superseded-By`, `Replaces`, and `Requires` are statements by the PEP authors. Section-typed edges are my inference from where a mention sits. Keeping them as different edge types means the risk flags can trust the first kind more than the second.

## How the knowledge state was built, and the tradeoffs

The build has two stages, and neither uses NLP or an LLM.

1. `ingest/parse_peps.py` extracts only what is literally in each `.rst` file: header fields, the section tree (RST heading levels are inferred from the order underline characters first appear), each section's text, and the section each PEP mention sits in.
2. `kg/build_graph.py` applies the schema: it filters to the typing scope, creates nodes, turns header fields into header edges, classifies every mention by its section, joins the feature catalog, and writes `knowledge_state/graph.json` plus a readable `SUMMARY.md`.

Tradeoffs I accepted:

1. **The feature catalog is hand-curated.** I chose precision over coverage. A feature's version is never typed by hand. It is always read from its PEP's header, and the build fails loudly (as a warning in `graph.json`) if a catalog entry points to a PEP outside the scope, a PEP without a version, an unknown feature, or an alias two features share.
2. **The version comes from the PEP header, not from the release.** This is right for Final PEPs. For Draft PEPs the header is a target, so the engine treats Draft and Deferred as "not shipped yet" regardless of version, and Rejected and Withdrawn as "never available".
3. **Section classification is a title heuristic.** It made one mistake I found and fixed: PEP 589's "Alternative Syntax" section describes a supported syntax, but the pattern "alternative" labelled it rejected. The pattern now requires the plural "alternatives" or an explicit rejection word.
4. **Reasoning text is the first prose paragraphs of each section**, skipping code blocks. It is a pointer into the PEP, not a summary written by a model, and every entry links back to the PEP URL.
5. **Input matching uses a fixed vocabulary** (each feature's aliases) instead of fuzzy NLP. Unknown phrases are reported back with "did you mean" suggestions instead of being guessed.

## What happens when a new input arrives

Input: a Python version and a description, for example `3.9` and "X | None unions, TypedDict with optional keys, and the type statement".

1. **Match.** Aliases are matched with the longest match winning, so "X | None" does not also count as the shorter alias "none". If one phrase names both a feature and its own fallback ("X | None unions"), the user meant the specific feature, and the fallback is dropped. Features people write as code rather than by name have a syntax pattern too, so "int | str" or "X|None" with any spacing is recognised. The version accepts forms like 3.11.9 or "python 3.9" and is reduced to major.minor.
2. **Availability.** The engine walks `next_version` from the oldest version to 3.9 to get the set of versions the team has. A feature is usable if its PEP has shipped, its `available_from` version is in that set, and every feature it `requires` is usable too. The requirement walk is recursive, so NotRequired correctly reports it needs TypedDict as well.
3. **Fallback.** If a feature is not usable, a breadth-first walk over `falls_back_to` edges, in the catalog's rank order, finds the nearest usable substitute. For the `type` statement on 3.9 this is two steps: `TypeAlias` needs 3.10 too, so it continues to a plain alias. Each step carries the condition under which the substitute is valid.
4. **Risk flags.** Status (Draft, Superseded, Rejected, ...), `superseded_by` and `replaces` edges, `compat_concern` edges in both directions, and `requires` dependencies. Fallbacks carry their own risks: falling back to `from __future__ import annotations` is flagged because PEP 563 was superseded by PEPs 649 and 749. One fact can arrive through several edges (a Superseded status, a `superseded_by` edge, and an incoming `replaces` edge all say a newer PEP took over), so each fact is reported once with every edge kept as evidence. My first version listed seven risk lines for this case that said three things.
5. **Design reasoning.** The introducing PEP's `builds_on` targets, its rejected ideas and backwards compatibility notes, and every other PEP that referenced it while rejecting an alternative.
6. **Upgrade path.** A forward walk along `next_version` from 3.9 records what each version unlocks: 3.10 unlocks `X | Y`, 3.11 unlocks NotRequired, 3.12 unlocks the type statement.

Every verdict lists the edges it walked (`--evidence`), so any claim can be checked against `graph.json`.

## What I chose not to build

1. **Reading the user's code directly.** This matches my original problem best, since the user should not need to know which features they use. Python's `ast` module could detect them. I chose a description as input to fit the deadline.
2. **An LLM layer.** Every answer comes from walking the graph. An LLM could rephrase the report, but it would add nothing the graph does not already know, and it would make the reasoning harder to verify.
3. **Other topics** such as concurrency or packaging. Depth in one area first.
4. **A web interface.** The CLI shows the reasoning directly, and `--json` makes the output usable by other tools.

## What I would build next

1. **Code as input**, using `ast` to detect features from source. This closes the gap between the problem I started with and the input the system accepts today.
2. **Real backport data.** Right now the system only notes when a PEP mentions `typing_extensions`. Adding `typing_extensions` release data as a node type would let it answer "on 3.9, install `typing_extensions>=4.x` and import it from there".
3. **CPython release data** to confirm the version each feature actually shipped in, including point releases.
4. **Rejected ideas as nodes**, to follow debates across PEPs instead of only within one.

## How I used AI tools

I used Claude as a coding assistant: to write the parser, builder, engine, CLI, and tests from my schema decisions, and to draft catalog entries, which are checked by the build against the PEP headers. The problem, the scope, the input and output, and the modeling decisions above are mine.
