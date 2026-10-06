"""The knowledge graph schema: node types, edge types, and the rules that map
raw PEP data onto them. Everything that decides *meaning* lives in this file,
so it can be read and argued with in one place.
"""
import re

SCOPE_TOPIC = "Typing"  # only PEPs whose Topic header contains this

NODE_TYPES = {
    "PEP": "A typing PEP. Carries status, title, authors, and its design reasoning (rejected ideas, backwards compatibility notes) as text.",
    "Feature": "One usable typing feature (e.g. X | Y unions). Users ask about these, not about PEP numbers.",
    "PythonVersion": "A CPython minor version (3.5 ... 3.16). Linked in release order.",
}

EDGE_TYPES = {
    # Feature edges (from the curated catalog + PEP headers)
    "introduced_by":   ("Feature", "PEP", "The PEP that added this feature."),
    "available_from":  ("Feature", "PythonVersion", "First version with the feature, taken from the introducing PEP's Python-Version header."),
    "requires":        ("Feature", "Feature", "Cannot be used without the target feature."),
    "falls_back_to":   ("Feature", "Feature", "Older substitute; edge carries the condition under which it is valid."),
    # Version edges
    "next_version":    ("PythonVersion", "PythonVersion", "Release order."),
    # PEP header edges (explicit, stated by PEP authors)
    "superseded_by":   ("PEP", "PEP", "From the Superseded-By header."),
    "replaces":        ("PEP", "PEP", "From the Replaces header."),
    "pep_requires":    ("PEP", "PEP", "From the Requires header."),
    # PEP body edges, typed by the section the mention appears in
    "builds_on":       ("PEP", "PEP", "Mentioned in Abstract/Motivation/Rationale/Specification-type sections."),
    "compat_concern":  ("PEP", "PEP", "Mentioned in a Backwards Compatibility-type section."),
    "rejected_idea_ref": ("PEP", "PEP", "Mentioned inside a rejected idea or alternative."),
    "cites":           ("PEP", "PEP", "Mentioned anywhere else (references, open issues, how to teach, ...)."),
}

# Section title patterns, in priority order. A mention gets the first edge
# type whose pattern matches ANY title in its section chain (the section
# itself or any ancestor). Priority matters: a mention inside
# "Rejected Ideas > Motivation for X" is about a rejected idea, so
# rejected_idea_ref is checked before builds_on.
SECTION_RULES = (
    ("rejected_idea_ref", re.compile(r"rejected|rejection|alternatives|objection|discarded|not adopted|considered", re.I)),
    ("compat_concern",    re.compile(r"backward|compatib|incompatib|migration|deprecat|breaking", re.I)),
    ("builds_on",         re.compile(r"abstract|motivation|rationale|specification|proposal|overview|background|introduction|semantics|design", re.I)),
)
DEFAULT_MENTION_EDGE = "cites"

# Sections whose text is kept on the PEP node as design reasoning.
REASONING_SECTIONS = {
    "rejected_ideas": SECTION_RULES[0][1],
    "backwards_compatibility": SECTION_RULES[1][1],
}

# Statuses that make a feature risky to depend on, and why.
STATUS_RISK = {
    "Draft": "the PEP is still a Draft; the feature may change or never ship",
    "Deferred": "the PEP is Deferred; no one is moving it forward",
    "Withdrawn": "the PEP was Withdrawn by its author; the feature will not ship",
    "Rejected": "the PEP was Rejected; the feature does not exist in Python",
    "Superseded": "the PEP was Superseded by a newer PEP",
    "Provisional": "the PEP is Provisional; the API may still change",
}


def classify_section(section):
    """Return the edge type for a mention found in this section."""
    if section is None:
        return DEFAULT_MENTION_EDGE
    chain = [section["title"]] + list(section["ancestors"])
    for edge, pattern in SECTION_RULES:
        if any(pattern.search(title) for title in chain):
            return edge
    return DEFAULT_MENTION_EDGE
