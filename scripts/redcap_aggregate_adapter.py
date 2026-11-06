#!/usr/bin/env python3
"""Build a candidate public CCC dashboard from a reviewed *complete* site aggregate.

Input is a JSON document with keys: site, as_of (YYYY-MM-DD), source,
approved_by, and data (the complete schema-v2 site.data object).
This script does not access REDCap or accept participant-level exports.
"""
import argparse
import copy
import json
import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path

def build(template, snapshot):
    if snapshot.get("site") != "gambia":
        raise ValueError("Only Gambia is supported by this adapter")
    stamp = date.fromisoformat(snapshot["as_of"])
    if stamp > date.today():
        raise ValueError("Reporting date is in the future")
    if not all(isinstance(snapshot.get(k), str) and snapshot[k].strip()
               for k in ("source", "approved_by")):
        raise ValueError("Nonempty source and approved_by are required")
    if not isinstance(snapshot.get("data"), dict):
        raise ValueError("Complete site data is required; partial counts cannot be published")
    expected = set(template["sites"]["gambia"]["data"])
    if set(snapshot["data"]) != expected:
        raise ValueError("Snapshot must contain all site data sections: " + ", ".join(sorted(expected)))
    out = copy.deepcopy(template)
    site = out["sites"]["gambia"]
    site["data"] = copy.deepcopy(snapshot["data"])
    site["updated"] = stamp.strftime("%-d %B %Y")
    site["source"] = snapshot["source"]
    out["updated"] = site["updated"]
    # Legacy fields drive older site views; keep them consistent.
    for key in ("headline", "recruitment", "human_specimens", "human_lab",
                "demographics", "animals", "environment", "notes"):
        if key in out:
            out[key] = copy.deepcopy(site["data"][key])
    out["source"] = site["source"]
    for i, item in enumerate(out["programme"]["headline"]):
        # One approved numeric site at present. Fail closed when multi-site.
        if out["programme"]["reporting_sites"] != 1:
            raise ValueError("Multi-site programme headline aggregation needs separate approval")
        item["value"] = site["data"]["headline"][i]["value"]
        item["context"] = site["data"]["headline"][i].get("context","The Gambia")
    return out

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("approved_snapshot", type=Path)
    parser.add_argument("--template", type=Path, default=Path("dashboard.json"))
    parser.add_argument("--output", type=Path, default=Path("dashboard.next.json"))
    args = parser.parse_args()
    snapshot = json.loads(args.approved_snapshot.read_text(encoding="utf-8"))
    template = json.loads(args.template.read_text(encoding="utf-8"))
    result = build(template, snapshot)
    # Validate *before* writing anything; reject row-level keys and mismatches.
    with tempfile.TemporaryDirectory() as temp:
        candidate = Path(temp) / "candidate.json"
        candidate.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        validator = Path(__file__).with_name("validate_dashboard.py")
        subprocess.run([sys.executable, str(validator), str(candidate)], check=True)
    if args.output.exists():
        parser.error("Output exists; refusing overwrite")
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Candidate written to {args.output}; human review still required.")

if __name__ == "__main__":
    main()
