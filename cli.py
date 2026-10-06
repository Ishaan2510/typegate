"""Command-line interface.

Examples:
    python cli.py --python 3.9 --want "X | None unions, TypedDict with optional keys, Protocol"
    python cli.py --python 3.11 --want "@override and TypeIs" --json
    python cli.py --list-features
    python cli.py            # interactive: asks for the version and the description
"""
import argparse
import json
import sys
import textwrap

from reasoner.engine import Graph, analyze

VERDICT_LABEL = {
    "use": "USE IT",
    "use_fallback": "USE THE FALLBACK",
    "blocked": "BLOCKED",
    "never_available": "NEVER AVAILABLE",
}


def wrap(text, indent=6):
    return textwrap.fill(text, width=100, initial_indent=" " * indent, subsequent_indent=" " * indent)


def render(report, show_evidence=False):
    s = report["summary"]
    out = []
    out.append(f"Target Python: {s['target_python']}   Features recognized: {s['features_requested']}")
    out.append(f"  usable now: {s['usable_now']}   with fallback: {s['usable_with_fallback']}   "
               f"blocked: {s['blocked']}   never available: {s['never_available']}")
    if s["min_python_for_all_native"]:
        out.append(f"  minimum Python to use everything natively: {s['min_python_for_all_native']}")
    if s["upgrade_path"]:
        out.append("  upgrade path:")
        for step in s["upgrade_path"]:
            out.append(f"    {s['target_python']} -> {step['version']} unlocks: {', '.join(step['unlocks'])}")
    for n in s["notes"]:
        out.append(f"  note: {n}")
    for u in s["unrecognized_input"]:
        hint = f" (did you mean: {', '.join(u['did_you_mean'])})" if u["did_you_mean"] else ""
        out.append(f"  not recognized: '{u['text']}'{hint}")

    for i, f in enumerate(report["features"], 1):
        out.append("")
        out.append(f"[{i}] {f['feature']}  ->  {VERDICT_LABEL[f['verdict']]}")
        out.append(f"    {f['introduced_by']}  (status: {f['pep_status']}, needs Python {f['min_python'] or 'n/a'})")
        out.append(f"    reason: {f['reason']}")
        fb = f["fallback"]
        if fb:
            out.append("    fallback:")
            for step in fb["path"]:
                out.append(f"      {step['from']}  ->  {step['to']}")
                out.append(wrap(f"when: {step['condition']}", 8))
            out.append(f"      write it as: {fb['example'].splitlines()[0]}")
            for r in fb["risks"]:
                out.append(wrap(f"fallback risk: {r['detail']}", 6))
        others = [o for o in f["fallback_options"] if not fb or o["use"] != fb["use"]]
        for o in others:
            out.append(wrap(f"other option: {o['name']} ({o['condition']})", 6))
        if f["backport_hint"]:
            out.append(wrap(f"backport: {f['backport_hint']}", 4))
        if f["risk_flags"]:
            out.append("    risk flags:")
            for r in f["risk_flags"]:
                out.append(wrap(f"- {r['detail']}", 6))
        d = f["design_reasoning"]
        out.append(f"    design reasoning ({d['url']}):")
        if d["builds_on"]:
            out.append(wrap("builds on: " + ", ".join(f"PEP {b['pep']}" for b in d["builds_on"]), 6))
        for idea in d["rejected_ideas"][:3]:
            summ = idea["summary"]
            if len(summ) > 220:
                summ = summ[:220].rsplit(" ", 1)[0] + " ..."
            out.append(wrap(f"rejected: {idea['title']}: {summ}", 6))
        if d["rejected_ideas_total"] > 3:
            out.append(f"      (+{d['rejected_ideas_total'] - 3} more rejected ideas in --json output)")
        for x in d["referenced_in_other_peps_rejected_ideas"]:
            out.append(wrap(f"debated in PEP {x['pep']} ({x['title']}) while rejecting: {', '.join(x['in_sections'])}", 6))
        if show_evidence:
            out.append("    evidence (edges walked):")
            for e in f["evidence"]:
                out.append(f"      {e}")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description="Check which Python typing features a team can use on its Python version.")
    ap.add_argument("--python", help="target Python version, e.g. 3.9")
    ap.add_argument("--want", help="plain description of the typing features you plan to use")
    ap.add_argument("--json", action="store_true", help="print the full structured report as JSON")
    ap.add_argument("--evidence", action="store_true", help="show the graph edges behind each verdict")
    ap.add_argument("--graph", default=None, help="path to knowledge_state/graph.json")
    ap.add_argument("--list-features", action="store_true", help="list every feature the system knows")
    args = ap.parse_args()

    graph = Graph(args.graph) if args.graph else Graph()
    if args.list_features:
        for n in sorted((n for n in graph.nodes.values() if n["type"] == "Feature"), key=lambda n: n["name"]):
            print(f"{n['name']:<50} e.g. {', '.join(n['aliases'][:3])}")
        return
    version = args.python or input("Target Python version (e.g. 3.9): ").strip()
    want = args.want or input("Which typing features do you plan to use? ").strip()
    try:
        report = analyze(graph, version, want)
    except ValueError as exc:
        sys.exit(f"error: {exc}")
    if not report["features"]:
        print("No known typing feature found in that description. Run with --list-features to see the vocabulary.")
        for u in report["summary"]["unrecognized_input"]:
            if u["did_you_mean"]:
                print(f"  '{u['text']}': did you mean {', '.join(u['did_you_mean'])}?")
        sys.exit(1)
    print(json.dumps(report, indent=1, ensure_ascii=False) if args.json else render(report, args.evidence))


if __name__ == "__main__":
    main()
