#!/usr/bin/env python3
"""Apply a reviewed Gambia aggregate snapshot to CCC schema-v2 dashboard JSON.

No REDCap credentials, individual rows, or network access. Intended for approved
aggregate JSON produced inside the MRCG environment. Refuses incomplete data.
"""
import argparse
import copy
import json
from datetime import date
from pathlib import Path

REQUIRED = ("screened", "eligible", "cases_enrolled", "controls_enrolled",
            "household_enrolled", "case_specimens", "control_specimens",
            "household_specimens", "culture_tested", "culture_positive",
            "pcr_tested", "pcr_positive", "confirmed_positive")
def integer(value, name):
    if type(value) is not int or value < 0:
        raise ValueError(f"{name} must be a non-negative integer")
    return value

def build(template, snapshot):
    if snapshot.get("site") != "gambia":
        raise ValueError("This adapter only supports the Gambia")
    stamp = date.fromisoformat(snapshot["as_of"])
    if stamp > date.today():
        raise ValueError("Snapshot date cannot be in the future")
    if not snapshot.get("approved_by") or not snapshot.get("source"):
        raise ValueError("Approval and source provenance are required")
    counts = snapshot["counts"]
    if set(counts) != set(REQUIRED):
        raise ValueError(f"Expected exactly these aggregate fields: {', '.join(REQUIRED)}")
    c = {key: integer(counts[key], key) for key in REQUIRED}
    if c["eligible"] > c["screened"]:
        raise ValueError("Eligible exceeds screened")
    for cohort in ("cases", "controls", "household"):
        if c[cohort + "_enrolled"] > sum(c[k] for k in ("cases_enrolled","controls_enrolled","household_enrolled")):
            raise ValueError("Invalid cohort count")
    if c["culture_positive"] > c["culture_tested"] or c["pcr_positive"] > c["pcr_tested"]:
        raise ValueError("Positive results exceed completed tests")
    people = sum(c[k] for k in ("cases_enrolled","controls_enrolled","household_enrolled"))
    specimens = sum(c[k] for k in ("case_specimens","control_specimens","household_specimens"))
    if c["confirmed_positive"] > people:
        raise ValueError("Unique positive participants exceed enrolled people")
    if not isinstance(template.get("sites",{}).get("gambia",{}).get("data"),dict):
        raise ValueError("Missing Gambia site data template")
    out = copy.deepcopy(template)
    site = out["sites"]["gambia"]
    d = site["data"]
    # Only fields with explicitly approved definitions are updated. Existing
    # demographics, animals and environmental results remain historical.
    d["recruitment"]["screened"] = c["screened"]
    d["recruitment"]["eligible"] = c["eligible"]
    for cohort in d["recruitment"]["cohorts"]:
        cohort["enrolled"] = c[cohort["id"] + "_enrolled"]
    d["human_specimens"]["people"] = people
    d["human_specimens"]["total"] = specimens
    for i, (enrolled, spec) in enumerate((("cases_enrolled","case_specimens"),
                                           ("controls_enrolled","control_specimens"),
                                           ("household_enrolled","household_specimens"))):
        d["human_specimens"]["types"][i]["value"] = c[spec]
        d["human_specimens"]["types"][i]["purpose"] = f"{c[enrolled]} enrolled · {c[spec]} specimens"
        d["human_specimens"]["cohorts"][i]["people"] = c[enrolled]
        d["human_specimens"]["cohorts"][i]["total"] = c[spec]
    lab = d["human_lab"]
    lab["totals"].update(culture_results=c["culture_tested"],culture_positive=c["culture_positive"],
                         pcr_results=c["pcr_tested"],pcr_positive=c["pcr_positive"],
                         confirmed_positive=c["confirmed_positive"],enrolled=people)
    lab["testing"]["culture"].update(tested=c["culture_tested"],positive=c["culture_positive"])
    lab["testing"]["pcr"].update(tested=c["pcr_tested"],positive=c["pcr_positive"])
    # Pending PCR cannot be inferred from total enrolled cases: remove obsolete
    # assumptions unless explicitly derived in a later approved report.
    lab["testing"]["pcr"].pop("eligible",None)
    lab["testing"]["pcr"].pop("pending",None)
    # Detailed lab cohort and demographic breakdowns are not supplied in this
    # snapshot. Publishing the old breakdown beside new totals would mislead.
    # Require a complete snapshot rather than silently mixing reporting dates.
    raise ValueError("NOT PUBLISHABLE: cohort-level laboratory and demographic breakdowns "
                     "are required to update the full dashboard consistently. "
                     "Use redcap_report_probe.py and agree the report field mapping first.")

def main():
    p = argparse.ArgumentParser()
    p.add_argument("approved_snapshot",type=Path)
    p.add_argument("--template",type=Path,default=Path("dashboard.json"))
    p.add_argument("--output",type=Path,default=Path("dashboard.next.json"))
    args = p.parse_args()
    snapshot=json.loads(args.approved_snapshot.read_text())
    template=json.loads(args.template.read_text())
    result=build(template,snapshot)
    if args.output.exists():
        p.error("Output exists; refusing overwrite")
    args.output.write_text(json.dumps(result,indent=2)+"\n")

if __name__=="__main__":
    main()
