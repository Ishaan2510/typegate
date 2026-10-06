"""Stage 2: build the knowledge graph from data/peps_raw.json + the feature
catalog, and write the inspectable snapshot to knowledge_state/graph.json.

Usage:
    python kg/build_graph.py
"""
import argparse
import json
import os
import re
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import schema  # noqa: E402

PEP_URL = "https://peps.python.org/pep-{:04d}/"


def vkey(v):
    return tuple(int(x) for x in v.split("."))


def clean_rst(text):
    text = re.sub(r":pep:`(?:[^`<]*<)?(\d+)>?`", r"PEP \1", text)
    text = re.sub(r":[a-z:]+:`~?([^`]+)`", r"\1", text)
    text = re.sub(r"`([^`<]+?)\s*<[^>]+>`_+", r"\1", text)  # `text <url>`_ -> text
    text = text.replace("``", "")
    return re.sub(r"\s+", " ", text).strip()


def summarize(text, limit=400):
    """First prose paragraphs of a section, skipping code blocks and fragments."""
    parts = []
    for para in (text or "").split("\n\n"):
        if not para.strip() or para[:1] in (" ", "\t") or para.strip().startswith(".."):
            continue  # blank, indented code block, or RST directive
        p = clean_rst(para)
        if p.endswith("::"):
            p = p[:-1]
        if len(p) < 30 and not parts:
            continue  # fragments like "PROS:" or "::"
        parts.append(p)
        if sum(len(x) for x in parts) >= limit:
            break
    out = " ".join(parts)
    return out if len(out) <= limit else out[:limit].rsplit(" ", 1)[0] + " ..."


def pep_ints(value):
    return [int(x) for x in re.findall(r"\d+", value or "")]


def reasoning_sections(record, pattern):
    """Sections that sit under a heading matching `pattern`.

    If the matching heading has children, each child is one entry (each
    rejected idea is usually its own subsection). Otherwise the heading's own
    text is the entry.
    """
    secs = record["sections"]
    out = []
    for i, s in enumerate(secs):
        own = bool(pattern.search(s["title"]))
        under = any(pattern.search(a) for a in s["ancestors"])
        has_children = i + 1 < len(secs) and secs[i + 1]["level"] > s["level"]
        if (under and not own) or (own and not under and not has_children):
            if s["text"]:
                out.append({"title": clean_rst(s["title"]), "summary": summarize(s["text"])})
    return out


def build(raw_path, catalog_path, peps_commit):
    raw = json.load(open(raw_path, encoding="utf-8"))
    catalog = json.load(open(catalog_path, encoding="utf-8"))["features"]

    in_scope = {r["number"]: r for r in raw
                if schema.SCOPE_TOPIC in r["header"].get("Topic", "")}
    nodes, edges, warnings = {}, [], []

    # ---- PEP nodes ----
    for n, r in sorted(in_scope.items()):
        h = r["header"]
        nodes[f"pep:{n}"] = {
            "id": f"pep:{n}", "type": "PEP", "number": n,
            "title": clean_rst(h.get("Title", "")),
            "status": h.get("Status"), "pep_type": h.get("Type"),
            "python_version": h.get("Python-Version") or None,
            "created": h.get("Created"), "authors": h.get("Author"),
            "url": PEP_URL.format(n),
            "mentions_typing_extensions": r["mentions_typing_extensions"],
            "rejected_ideas": reasoning_sections(r, schema.REASONING_SECTIONS["rejected_ideas"]),
            "backwards_compatibility": reasoning_sections(r, schema.REASONING_SECTIONS["backwards_compatibility"]),
        }

    # ---- PEP -> PEP edges from headers ----
    header_edges = {"Superseded-By": "superseded_by", "Replaces": "replaces", "Requires": "pep_requires"}
    for n, r in in_scope.items():
        for field, etype in header_edges.items():
            for t in pep_ints(r["header"].get(field)):
                if t in in_scope:
                    edges.append({"source": f"pep:{n}", "target": f"pep:{t}", "type": etype,
                                  "evidence": f"{field} header of PEP {n}"})

    # ---- PEP -> PEP edges from body mentions, typed by section ----
    agg = defaultdict(lambda: {"count": 0, "sections": set()})
    dropped = 0
    for n, r in in_scope.items():
        for m in r["mentions"]:
            if m["target"] not in in_scope:
                dropped += 1
                continue
            sec = r["sections"][m["section_index"]] if m["section_index"] is not None else None
            etype = schema.classify_section(sec)
            a = agg[(n, m["target"], etype)]
            a["count"] += 1
            a["sections"].add(clean_rst(sec["title"]) if sec else "(preamble)")
    for (s, t, etype), a in sorted(agg.items()):
        edges.append({"source": f"pep:{s}", "target": f"pep:{t}", "type": etype,
                      "count": a["count"], "evidence": sorted(a["sections"])})

    # ---- PythonVersion nodes + release order ----
    versions = {r["header"]["Python-Version"] for r in in_scope.values()
                if re.fullmatch(r"3\.\d+", r["header"].get("Python-Version", ""))}
    lo, hi = min(versions, key=vkey), max(versions, key=vkey)
    ordered = [f"3.{m}" for m in range(vkey(lo)[1], vkey(hi)[1] + 1)]
    for v in ordered:
        nodes[f"version:{v}"] = {"id": f"version:{v}", "type": "PythonVersion", "version": v}
    for a, b in zip(ordered, ordered[1:]):
        edges.append({"source": f"version:{a}", "target": f"version:{b}", "type": "next_version"})

    # ---- Feature nodes + edges ----
    ids = {f["id"] for f in catalog}
    alias_owner = {}
    for f in catalog:
        fid = f"feature:{f['id']}"
        pep = f["intro_pep"]
        if pep not in in_scope:
            warnings.append(f"{f['id']}: intro PEP {pep} is not a typing PEP")
            continue
        version = in_scope[pep]["header"].get("Python-Version")
        nodes[fid] = {"id": fid, "type": "Feature", "name": f["name"], "example": f["example"],
                      "aliases": f["aliases"]}
        edges.append({"source": fid, "target": f"pep:{pep}", "type": "introduced_by"})
        if version and f"version:{version}" in nodes:
            edges.append({"source": fid, "target": f"version:{version}", "type": "available_from",
                          "evidence": f"Python-Version header of PEP {pep}"})
        else:
            warnings.append(f"{f['id']}: PEP {pep} has no usable Python-Version header")
        for req in f["requires"]:
            if req not in ids:
                warnings.append(f"{f['id']}: requires unknown feature {req}")
            edges.append({"source": fid, "target": f"feature:{req}", "type": "requires"})
        for rank, fb in enumerate(f["fallbacks"]):
            if fb["to"] not in ids:
                warnings.append(f"{f['id']}: fallback to unknown feature {fb['to']}")
            edges.append({"source": fid, "target": f"feature:{fb['to']}", "type": "falls_back_to",
                          "condition": fb["condition"], "priority": rank})
        for al in f["aliases"]:
            if al in alias_owner and alias_owner[al] != f["id"]:
                warnings.append(f"alias '{al}' used by both {alias_owner[al]} and {f['id']}")
            alias_owner[al] = f["id"]

    counts = defaultdict(int)
    for e in edges:
        counts[e["type"]] += 1
    ntypes = defaultdict(int)
    for nd in nodes.values():
        ntypes[nd["type"]] += 1

    return {
        "meta": {
            "description": "Knowledge graph of Python typing PEPs, the features they introduced, and the Python versions those features need.",
            "source": "https://github.com/python/peps",
            "source_commit": peps_commit,
            "scope": f"PEPs whose Topic header contains '{schema.SCOPE_TOPIC}'",
            "node_types": schema.NODE_TYPES,
            "edge_types": {k: {"from": v[0], "to": v[1], "meaning": v[2]} for k, v in schema.EDGE_TYPES.items()},
            "section_rules": [{"edge": e, "title_pattern": p.pattern} for e, p in schema.SECTION_RULES],
            "counts": {"nodes": dict(sorted(ntypes.items())), "edges": dict(sorted(counts.items())),
                       "out_of_scope_mentions_dropped": dropped},
            "build_warnings": warnings,
        },
        "nodes": sorted(nodes.values(), key=lambda n: (n["type"], n["id"])),
        "edges": sorted(edges, key=lambda e: (e["type"], e["source"], e["target"])),
    }


def write_summary(graph, path):
    """Human-readable view of the knowledge state, generated from graph.json."""
    N = {n["id"]: n for n in graph["nodes"]}
    out = defaultdict(lambda: defaultdict(list))
    for e in graph["edges"]:
        out[e["source"]][e["type"]].append(e)
    m = graph["meta"]
    lines = ["# Knowledge state summary", "",
             f"Generated from `graph.json` (source commit `{m['source_commit']}`). Scope: {m['scope']}.", "",
             "## Counts", "", "| Node type | Count |", "|---|---|"]
    lines += [f"| {k} | {v} |" for k, v in m["counts"]["nodes"].items()]
    lines += ["", "| Edge type | Count | Meaning |", "|---|---|---|"]
    lines += [f"| {k} | {v} | {m['edge_types'][k]['meaning']} |" for k, v in m["counts"]["edges"].items()]
    lines += ["", "## Features", "", "| Feature | Introduced by | Python | Requires | Falls back to |", "|---|---|---|---|---|"]
    feats = sorted((n for n in N.values() if n["type"] == "Feature"),
                   key=lambda n: (vkey(N[out[n["id"]]["available_from"][0]["target"]]["version"]), n["name"]))
    for f in feats:
        pep = N[out[f["id"]]["introduced_by"][0]["target"]]
        ver = N[out[f["id"]]["available_from"][0]["target"]]["version"]
        req = ", ".join(N[e["target"]]["name"] for e in out[f["id"]]["requires"]) or "-"
        fb = ", ".join(N[e["target"]]["name"] for e in sorted(out[f["id"]]["falls_back_to"], key=lambda e: e["priority"])) or "-"
        lines.append(f"| {f['name'].replace('|', '&#124;')} | PEP {pep['number']} ({pep['status']}) | {ver} | {req} | {fb.replace('|', '&#124;')} |")
    lines += ["", "## PEP to PEP links (typed by section)", "", "| From | Type | To | Found in sections |", "|---|---|---|---|"]
    for e in graph["edges"]:
        if e["type"] in ("builds_on", "compat_concern", "rejected_idea_ref", "cites", "superseded_by", "replaces", "pep_requires"):
            ev = e.get("evidence")
            ev = ", ".join(ev) if isinstance(ev, list) else (ev or "")
            lines.append(f"| PEP {N[e['source']]['number']} | {e['type']} | PEP {N[e['target']]['number']} | {ev.replace('|', '&#124;')} |")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def main():
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", default=os.path.join(here, "data", "peps_raw.json"))
    ap.add_argument("--catalog", default=os.path.join(here, "kg", "feature_catalog.json"))
    ap.add_argument("--out", default=os.path.join(here, "knowledge_state", "graph.json"))
    ap.add_argument("--peps-commit", default=os.environ.get("PEPS_COMMIT", "unknown"))
    args = ap.parse_args()
    graph = build(args.raw, args.catalog, args.peps_commit)
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(graph, fh, indent=1, ensure_ascii=False)
    write_summary(graph, os.path.join(os.path.dirname(args.out), "SUMMARY.md"))
    c = graph["meta"]["counts"]
    print(f"nodes {c['nodes']}\nedges {c['edges']}")
    for w in graph["meta"]["build_warnings"]:
        print("WARNING:", w)


if __name__ == "__main__":
    main()
