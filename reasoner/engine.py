"""Reasoning over the knowledge graph for a new input.

Input:  a target Python version + a plain-text description of the typing
        features a team wants to use.
Output: a structured report: per-feature verdict, the minimum version, the
        fallback path if blocked, risk flags, design reasoning, and the
        evidence (edges walked) behind every claim.

Every conclusion comes from walking typed edges in knowledge_state/graph.json.
No LLM is involved.
"""
import difflib
import json
import os
import re
import sys
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "kg"))
import schema  # noqa: E402

DEFAULT_GRAPH = os.path.join(ROOT, "knowledge_state", "graph.json")
NEVER_SHIPS = {"Rejected", "Withdrawn"}
NOT_SHIPPED_YET = {"Draft", "Deferred"}
MAX_FALLBACK_DEPTH = 3


def vkey(v):
    return tuple(int(x) for x in v.split("."))


class Graph:
    def __init__(self, path=DEFAULT_GRAPH):
        data = json.load(open(path, encoding="utf-8"))
        self.meta = data["meta"]
        self.nodes = {n["id"]: n for n in data["nodes"]}
        self.out = defaultdict(lambda: defaultdict(list))
        self.inc = defaultdict(lambda: defaultdict(list))
        for e in data["edges"]:
            self.out[e["source"]][e["type"]].append(e)
            self.inc[e["target"]][e["type"]].append(e)
        for src in self.out:  # fallbacks are tried in the order the catalog ranks them
            self.out[src]["falls_back_to"].sort(key=lambda e: e.get("priority", 0))

    def one(self, node, etype):
        edges = self.out[node][etype]
        return edges[0]["target"] if edges else None

    # ---- version chain ----
    def first_version(self):
        roots = [n for n in self.nodes if n.startswith("version:") and not self.inc[n]["next_version"]]
        return roots[0]

    def versions_up_to(self, target):
        """Walk next_version edges from the oldest version to `target`.

        Returns the list of version nodes a team on `target` has, in order.
        """
        chain, cur = [], self.first_version()
        while cur:
            if vkey(self.nodes[cur]["version"]) > vkey(target):
                break
            chain.append(cur)
            cur = self.one(cur, "next_version")
        return chain

    def versions_after(self, target):
        cur, out = self.first_version(), []
        while cur:
            if vkey(self.nodes[cur]["version"]) > vkey(target):
                out.append(cur)
            cur = self.one(cur, "next_version")
        return out


# ---------------------------------------------------------------- matching
def match_features(graph, description):
    """Map free text onto Feature nodes using each feature's alias list.

    Longest alias wins where two overlap, so "X | None" is not also read as
    the shorter alias "none". Returns (matched feature ids in order of
    appearance, unrecognized fragments with suggestions).
    """
    text = description.lower()
    hits = []
    for nid, n in graph.nodes.items():
        if n["type"] != "Feature":
            continue
        for al in n["aliases"]:
            for m in re.finditer(re.escape(al.lower()), text):
                hits.append((m.start(), m.end(), nid, al))
    hits.sort(key=lambda h: (-(h[1] - h[0]), h[0]))
    taken, chosen = [], {}
    for s, e, nid, al in hits:
        if any(s < te and ts < e for ts, te in taken):
            continue
        taken.append((s, e))
        chosen.setdefault(nid, (s, al))

    # Within one fragment ("X | None unions"), if a feature and its own
    # fallback both match, the user named the specific one; drop the fallback.
    def fragment_of(pos):
        return len(re.findall(r",|;|\band\b|\bplus\b|\n", text[:pos]))
    for nid in list(chosen):
        for e in graph.out[nid]["falls_back_to"]:
            t = e["target"]
            if t in chosen and fragment_of(chosen[t][0]) == fragment_of(chosen[nid][0]):
                del chosen[t]
    ordered = [nid for nid, _ in sorted(chosen.items(), key=lambda kv: kv[1][0])]

    unrecognized = []
    all_aliases = {al: nid for nid, n in graph.nodes.items() if n["type"] == "Feature" for al in n["aliases"]}
    pos = 0
    for frag in re.split(r",|;|\band\b|\bplus\b|\n", text):
        start = text.find(frag, pos)
        pos = start + len(frag)
        frag_s = frag.strip(" .")
        if len(frag_s) < 3 or any(start <= ts < start + len(frag) for ts, _ in taken):
            continue
        close = difflib.get_close_matches(frag_s, all_aliases.keys(), n=3, cutoff=0.5)
        unrecognized.append({"text": frag_s,
                             "did_you_mean": sorted({graph.nodes[all_aliases[c]]["name"] for c in close})})
    return ordered, unrecognized


# ---------------------------------------------------------------- analysis
def feature_facts(graph, fid):
    pep = graph.one(fid, "introduced_by")
    ver = graph.one(fid, "available_from")
    return {
        "feature": fid, "name": graph.nodes[fid]["name"],
        "pep": pep, "pep_status": graph.nodes[pep]["status"],
        "version": graph.nodes[ver]["version"] if ver else None,
    }


def availability(graph, fid, have_versions, seen=None):
    """Can this feature be used on the target version?

    Returns (usable: bool, reason: str, effective_min_version, evidence list).
    Follows `requires` edges, so a feature is only usable if everything it
    requires is usable too.
    """
    seen = (seen or set()) | {fid}
    f = feature_facts(graph, fid)
    ev = [f"{fid} -introduced_by-> {f['pep']} (Status: {f['pep_status']})"]
    if f["version"]:
        ev.append(f"{fid} -available_from-> version:{f['version']}")
    if f["pep_status"] in NEVER_SHIPS:
        return False, f"never shipped (PEP {f['pep_status'].lower()})", None, ev
    if f["pep_status"] in NOT_SHIPPED_YET:
        return False, f"not shipped yet (PEP is {f['pep_status']}, targets {f['version']})", None, ev
    usable = f"version:{f['version']}" in have_versions
    reason = "available" if usable else f"needs Python {f['version']}"
    eff = f["version"]
    for e in graph.out[fid]["requires"]:
        req = e["target"]
        ev.append(f"{fid} -requires-> {req}")
        if req in seen:
            continue
        r_ok, r_reason, r_min, r_ev = availability(graph, req, have_versions, seen)
        ev += r_ev
        if r_min and eff and vkey(r_min) > vkey(eff):
            eff = r_min
        if not r_ok:
            usable = False
            reason = f"requires {graph.nodes[req]['name']}, which {r_reason}"
    return usable, reason, eff, ev


def find_fallback(graph, fid, have_versions):
    """Breadth-first walk over falls_back_to edges to the nearest usable substitute."""
    frontier = [(fid, [])]
    seen = {fid}
    for _ in range(MAX_FALLBACK_DEPTH):
        nxt = []
        for node, path in frontier:
            for e in graph.out[node]["falls_back_to"]:
                t = e["target"]
                if t in seen:
                    continue
                seen.add(t)
                step = path + [{"from": graph.nodes[node]["name"], "to": graph.nodes[t]["name"],
                                "condition": e["condition"], "edge": f"{node} -falls_back_to-> {t}"}]
                ok, _, _, _ = availability(graph, t, have_versions)
                if ok:
                    return {"use": t, "name": graph.nodes[t]["name"], "example": graph.nodes[t]["example"],
                            "path": step, "risks": risk_flags(graph, t)}
                nxt.append((t, step))
        frontier = nxt
    return None


def all_fallbacks(graph, fid, have_versions):
    """Every direct fallback that is usable, so the team can compare conditions."""
    out = []
    for e in graph.out[fid]["falls_back_to"]:
        t = e["target"]
        ok, _, _, _ = availability(graph, t, have_versions)
        if ok:
            out.append({"use": t, "name": graph.nodes[t]["name"], "condition": e["condition"],
                        "example": graph.nodes[t]["example"], "risks": risk_flags(graph, t)})
    return out


def risk_flags(graph, fid):
    flags = []
    pep = graph.one(fid, "introduced_by")
    p = graph.nodes[pep]
    if p["status"] in schema.STATUS_RISK:
        flags.append({"kind": "status", "detail": schema.STATUS_RISK[p["status"]],
                      "evidence": f"{pep} Status: {p['status']}"})
    for e in graph.out[pep]["superseded_by"]:
        t = graph.nodes[e["target"]]
        flags.append({"kind": "superseded", "detail": f"superseded by PEP {t['number']} ({t['title']}, Python {t['python_version']})",
                      "evidence": f"{pep} -superseded_by-> {e['target']}"})
    for e in graph.inc[pep]["replaces"]:
        s = graph.nodes[e["source"]]
        flags.append({"kind": "replaced", "detail": f"replaced by PEP {s['number']} ({s['title']})",
                      "evidence": f"{e['source']} -replaces-> {pep}"})
    for e in graph.inc[pep]["compat_concern"]:
        s = graph.nodes[e["source"]]
        flags.append({"kind": "compat_concern_from", "detail": f"PEP {s['number']} ({s['title']}) discusses compatibility with this PEP",
                      "evidence": f"{e['source']} -compat_concern-> {pep} in {e['evidence']}"})
    for e in graph.out[pep]["compat_concern"]:
        t = graph.nodes[e["target"]]
        flags.append({"kind": "compat_concern_with", "detail": f"this PEP discusses compatibility with PEP {t['number']} ({t['title']})",
                      "evidence": f"{pep} -compat_concern-> {e['target']} in {e['evidence']}"})
    for e in graph.out[fid]["requires"]:
        r = feature_facts(graph, e["target"])
        flags.append({"kind": "dependency", "detail": f"depends on {r['name']} (Python {r['version']})",
                      "evidence": f"{fid} -requires-> {e['target']}"})
    return flags


def design_reasoning(graph, fid, max_ideas=5):
    pep = graph.one(fid, "introduced_by")
    p = graph.nodes[pep]
    builds_on = [{"pep": graph.nodes[e["target"]]["number"], "title": graph.nodes[e["target"]]["title"]}
                 for e in graph.out[pep]["builds_on"]]
    debated_elsewhere = [{"pep": graph.nodes[e["source"]]["number"], "title": graph.nodes[e["source"]]["title"],
                          "in_sections": e["evidence"]}
                         for e in graph.inc[pep]["rejected_idea_ref"]]
    return {
        "pep": p["number"], "title": p["title"], "url": p["url"],
        "builds_on": builds_on,
        "rejected_ideas": p["rejected_ideas"][:max_ideas],
        "rejected_ideas_total": len(p["rejected_ideas"]),
        "backwards_compatibility": p["backwards_compatibility"][:3],
        "referenced_in_other_peps_rejected_ideas": debated_elsewhere,
    }


def analyze(graph, target_version, description):
    if not re.fullmatch(r"3\.\d+", target_version.strip()):
        raise ValueError(f"target version must look like 3.9, got {target_version!r}")
    target_version = target_version.strip()
    have = graph.versions_up_to(target_version)
    have_set = set(have)
    notes = []
    known = [n["version"] for n in graph.nodes.values() if n["type"] == "PythonVersion"]
    if vkey(target_version) < vkey(min(known, key=vkey)):
        notes.append(f"Python {target_version} predates every typing PEP in the graph; nothing is available natively.")
    if vkey(target_version) > vkey(max(known, key=vkey)):
        notes.append(f"Python {target_version} is newer than any version the PEPs target; treating it as the latest.")

    feature_ids, unrecognized = match_features(graph, description)
    results = []
    for fid in feature_ids:
        ok, reason, eff, ev = availability(graph, fid, have_set)
        facts = feature_facts(graph, fid)
        pep_node = graph.nodes[facts["pep"]]
        item = {
            "feature": graph.nodes[fid]["name"], "feature_id": fid,
            "introduced_by": f"PEP {pep_node['number']}: {pep_node['title']}",
            "pep_status": facts["pep_status"],
            "min_python": eff,
            "usable_on_target": ok,
            "reason": reason,
            "fallback": None, "fallback_options": [],
            "backport_hint": None,
            "risk_flags": risk_flags(graph, fid),
            "design_reasoning": design_reasoning(graph, fid),
            "evidence": ev,
        }
        if ok:
            item["verdict"] = "use"
        else:
            fb = find_fallback(graph, fid, have_set)
            item["fallback"] = fb
            item["fallback_options"] = all_fallbacks(graph, fid, have_set)
            if pep_node["mentions_typing_extensions"] and facts["pep_status"] not in NEVER_SHIPS:
                item["backport_hint"] = (f"PEP {pep_node['number']} mentions typing_extensions; check whether "
                                         f"it backports {graph.nodes[fid]['name']} to Python {target_version}.")
            if facts["pep_status"] in NEVER_SHIPS:
                item["verdict"] = "never_available"
            elif fb:
                item["verdict"] = "use_fallback"
            else:
                item["verdict"] = "blocked"
        results.append(item)

    # Upgrade path: walk forward along next_version and record what each step unlocks.
    upgrade_path = []
    still_blocked = {r["feature_id"] for r in results if r["verdict"] in ("use_fallback", "blocked")}
    reachable = set(have)
    for v in graph.versions_after(target_version):
        reachable.add(v)
        unlocked = [fid for fid in sorted(still_blocked) if availability(graph, fid, reachable)[0]]
        if unlocked:
            upgrade_path.append({"version": graph.nodes[v]["version"],
                                 "unlocks": [graph.nodes[f]["name"] for f in unlocked]})
            still_blocked -= set(unlocked)

    shippable = [r for r in results if r["min_python"] and r["verdict"] != "never_available"
                 and r["pep_status"] not in NOT_SHIPPED_YET]
    min_all = max((r["min_python"] for r in shippable), key=vkey, default=None)
    summary = {
        "target_python": target_version,
        "features_requested": len(results),
        "usable_now": sum(r["verdict"] == "use" for r in results),
        "usable_with_fallback": sum(r["verdict"] == "use_fallback" for r in results),
        "blocked": sum(r["verdict"] == "blocked" for r in results),
        "never_available": sum(r["verdict"] == "never_available" for r in results),
        "min_python_for_all_native": min_all,
        "upgrade_path": upgrade_path,
        "unrecognized_input": unrecognized,
        "notes": notes,
    }
    return {"summary": summary, "features": results,
            "graph_source": {"commit": graph.meta["source_commit"], "scope": graph.meta["scope"]}}
