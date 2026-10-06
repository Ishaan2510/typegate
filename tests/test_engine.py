"""Behavioural tests: each one states a fact the graph must reason its way to."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from reasoner.engine import Graph, analyze, match_features  # noqa: E402

G = Graph()


def by_id(report, fid):
    return next(f for f in report["features"] if f["feature_id"] == f"feature:{fid}")


def test_version_gate_and_ordered_fallback():
    r = analyze(G, "3.9", "X | None unions")
    f = by_id(r, "union_pipe")
    assert f["verdict"] == "use_fallback" and f["min_python"] == "3.10"
    assert f["fallback"]["use"] == "feature:typing_union"  # ranked first, before __future__
    assert len(r["features"]) == 1  # 'unions' must not also match Union[X, Y]


def test_same_feature_is_fine_on_newer_python():
    assert by_id(analyze(G, "3.10", "X | Y"), "union_pipe")["verdict"] == "use"


def test_requires_chain_raises_effective_version():
    f = by_id(analyze(G, "3.7", "optional keys"), "required_notrequired")
    assert any("TypedDict" in r["detail"] for r in f["risk_flags"])
    assert f["min_python"] == "3.11"


def test_requirement_blocks_feature_on_old_python():
    f = by_id(analyze(G, "3.7", "total=false"), "typeddict_total")
    assert not f["usable_on_target"] and "requires TypedDict" in f["reason"]


def test_multi_step_fallback_walk():
    f = by_id(analyze(G, "3.9", "type statement"), "type_statement")
    path = [s["to"] for s in f["fallback"]["path"]]
    assert path == ["TypeAlias annotation", "Implicit type alias (Vector = list[float])"]


def test_rejected_pep_is_never_available_but_has_fallback():
    f = by_id(analyze(G, "3.14", "arrow callable syntax"), "callable_arrow_syntax")
    assert f["verdict"] == "never_available"
    assert f["fallback"]["use"] == "feature:typing_callable"


def test_superseded_fallback_carries_risk():
    f = by_id(analyze(G, "3.8", "deferred annotations"), "deferred_annotations")
    fb = f["fallback"]
    assert fb["use"] == "feature:postponed_annotations"
    assert any(r["kind"] == "superseded" for r in fb["risks"])


def test_draft_pep_not_shipped():
    f = by_id(analyze(G, "3.16", "inline typeddict"), "inline_typeddict")
    assert f["verdict"] == "use_fallback" and "not shipped yet" in f["reason"]


def test_upgrade_path_walks_versions_in_order():
    r = analyze(G, "3.9", "X | Y, optional keys, type statement")
    assert [s["version"] for s in r["summary"]["upgrade_path"]] == ["3.10", "3.11", "3.12"]


def test_cross_pep_debate_is_surfaced():
    d = by_id(analyze(G, "3.10", "X | Y"), "union_pipe")["design_reasoning"]
    assert 655 in [x["pep"] for x in d["referenced_in_other_peps_rejected_ideas"]]


def test_unrecognized_input_is_reported():
    ids, unknown = match_features(G, "TypedDict and quantum annotations")
    assert ids == ["feature:typeddict"] and unknown


def test_every_feature_has_version_and_pep():
    for n in G.nodes.values():
        if n["type"] == "Feature":
            assert G.one(n["id"], "introduced_by")
            assert G.one(n["id"], "available_from")
