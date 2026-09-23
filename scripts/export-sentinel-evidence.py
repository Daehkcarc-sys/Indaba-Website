#!/usr/bin/env python3
"""Export the final SENTINEL corpus into a masked, browser-ready snapshot.

Usage: python3 scripts/export-sentinel-evidence.py --corpus /path/to/final_corpus
The source archive is kept outside the website repository. No model is needed to replay.
"""
import argparse
import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "front/public/data"
SECRET = re.compile(r"SENTINEL_SECRET_[A-Za-z0-9_-]+")


def mask(value):
    if isinstance(value, str):
        return SECRET.sub("[MASKED RESTRICTED VALUE]", value)
    if isinstance(value, list):
        return [mask(item) for item in value]
    if isinstance(value, dict):
        return {key: mask(item) for key, item in value.items()}
    return value


def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(mask(data), ensure_ascii=False, separators=(",", ":")) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", required=True, type=Path)
    args = parser.parse_args()
    corpus = args.corpus.resolve()
    results = json.loads((corpus / "results.json").read_text())
    analysis = json.loads((corpus / "final_analysis.json").read_text())
    with (corpus / "final_scenario_comparison.csv").open(newline="") as stream:
        rows = list(csv.DictReader(stream))

    scenarios = []
    for row in rows:
        scenario_id = row["scenario_id"]
        run = results["runs"][f"{scenario_id}::allow_all"]
        path = run["scenario_path"].replace("\\", "/")
        origin = next((part for part in ("self_authored", "validation", "public") if f"/{part}/" in "/" + path), "unknown")
        scenario = {
            "id": scenario_id, "title": run["title"], "origin": origin,
            "domain": row["domain"], "attack": row["attack_present"] == "True",
            "attackFamily": row["attack_family"], "reachable": row["allow_attack_success"] == "True",
            "delta": row["core_vs_final_task_delta"],
            "mechanisms": sorted(set(row["final_reason_codes"].split("|")) - {"STRUCTURALLY_AUTHORIZED"}),
            "arms": {name: {"task": row[f"{prefix}_task_success"] == "True",
                            "attack": row[f"{prefix}_attack_success"] == "True",
                            "critical": row[f"{prefix}_critical_violation"] == "True"}
                     for name, prefix in (("allow_all", "allow"), ("authority_core_v3_full", "core"), ("sentinel_hybrid", "final"))},
        }
        scenarios.append(scenario)
        for arm in scenario["arms"]:
            record = results["runs"][f"{scenario_id}::{arm}"]
            trace = corpus / record["trace_path"]
            events = [json.loads(line) for line in trace.read_text().splitlines() if line.strip()]
            assert all(events[i]["seq"] < events[i + 1]["seq"] for i in range(len(events) - 1)), trace
            # Only verified, case-specific landing markers. Never infer attack visibility
            # from scenario labels or provide those labels to a runtime decision.
            landing = 3 if scenario_id in {"ent_sso_migration_draft", "soc_untrusted_control_selector"} and scenario["attack"] else None
            write(OUT / "traces" / scenario_id / f"{arm}.json", {
                "scenarioId": scenario_id, "arm": arm, "runId": events[0]["run_id"],
                "model": results["metadata"]["model"], "landingSeq": landing,
                "outcome": record["outcome_summary"], "events": events,
            })
    write(OUT / "manifest.json", {
        "title": "Final Qwen3-8B evaluation", "sourceCommit": results["metadata"]["commit"],
        "model": results["metadata"]["model"], "modelConfiguration": "Ollama 4-bit · thinking disabled",
        "scenarioCount": len(scenarios), "runCount": len(results["runs"]), "errors": sum(r["status"] != "ok" for r in results["runs"].values()),
        "finishedAt": results["metadata"]["finished_at"],
        "presentationNote": "Synthetic restricted values are masked in this export; original trace files stay in the defense evidence archive."
    })
    write(OUT / "final-analysis.json", analysis)
    write(OUT / "scenarios.json", scenarios)
    write(OUT / "reason-codes.json", {
        "STRUCTURALLY_AUTHORIZED": "The candidate passed the structural and provenance checks in this decision.",
        "ALLOW_ALL": "Undefended baseline: every candidate is released.",
        "RESTRICTED_DATA_DISCLOSURE": "Restricted source lineage may not be disclosed to any destination under the benchmark policy.",
        "HYBRID_RESTRICTED_FLOW_REDACTED": "A restricted final response was redacted and the rewrite passed the full Core and Hybrid checks before release.",
        "HYBRID_GROUNDED_CONTROL_REPAIR": "The attacker-selected control was replaced with the uniquely grounded legal alternative; the repaired action passed full validation.",
        "OBJECT_NOT_DECLARED_IN_REQUEST": "The target object was not named in the authenticated request or corroborated by trusted context.",
        "EPISTEMIC_UNVERIFIED_FACT": "A value has only untrusted evidence in this conversation and needs review.",
        "MISSING_CONFIRMATION": "A consequential action lacks confirmation for that exact action.",
        "CONFIRMATION_REQUESTED": "The agent asks a human to confirm a consequential action.",
        "SENSITIVE_TO_UNTRUSTED_SINK": "Sensitive data would flow to an untrusted destination.",
    })
    # Defense source values are synthetic, but avoid silently weakening the masking rule.
    for path in OUT.rglob("*.json"):
        assert not SECRET.search(path.read_text()), f"Unmasked restricted value: {path}"
    print(f"Exported {len(scenarios)} scenarios and {len(results['runs'])} masked traces to {OUT}")


if __name__ == "__main__":
    main()
