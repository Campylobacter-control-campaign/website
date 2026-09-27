#!/usr/bin/env python3
"""Validate the public CCC dashboard aggregate JSON.

This deliberately accepts only the dashboard's aggregate data model.
It must never be used to publish participant-level exports.
"""
import json, sys
from pathlib import Path

path = Path(sys.argv[1] if len(sys.argv) > 1 else "dashboard.json")
data = json.loads(path.read_text(encoding="utf-8"))

required = {"updated","site","source","recruitment","human_specimens","human_lab","demographics","animals","environment","notes"}
missing = required - set(data)
if missing:
    raise SystemExit("Missing top-level keys: " + ", ".join(sorted(missing)))

for forbidden in ("record_id","participant_id","name","dob","date_of_birth","address","phone","email","gps","latitude","longitude","free_text"):
    def walk(x, trail="root"):
        if isinstance(x, dict):
            for k,v in x.items():
                if k.lower() == forbidden:
                    raise SystemExit(f"Forbidden participant-level field {k!r} at {trail}")
                walk(v, trail+"."+k)
        elif isinstance(x, list):
            for i,v in enumerate(x): walk(v, f"{trail}[{i}]")
    walk(data)

def nonneg_int(v,label):
    if not isinstance(v,int) or isinstance(v,bool) or v < 0:
        raise SystemExit(f"{label} must be a non-negative integer")

r=data["recruitment"]
nonneg_int(r["screened"],"recruitment.screened"); nonneg_int(r["eligible"],"recruitment.eligible")
for i,c in enumerate(r["cohorts"]):
    nonneg_int(c["enrolled"],f"recruitment.cohorts[{i}].enrolled")
    if c.get("target") is not None: nonneg_int(c["target"],f"recruitment.cohorts[{i}].target")

hs=data["human_specimens"]; nonneg_int(hs["people"],"human_specimens.people"); nonneg_int(hs["total"],"human_specimens.total")
spec_sum=sum(x["value"] for x in hs["types"])
if spec_sum != hs["total"]:
    raise SystemExit(f"Specimen-type counts sum to {spec_sum}, not total {hs['total']}")

sex=data["demographics"]["sex"]
if sex["male"] + sex["female"] != hs["people"]:
    raise SystemExit("Sex totals do not match human_specimens.people")

a=data["animals"]["community"]
for k in ("sampled","target","specimens","tested","positive"): nonneg_int(a[k],"animals.community."+k)
if a["positive"] > a["tested"]: raise SystemExit("Animal positives exceed tested")

print(f"OK: {path} contains aggregate dashboard data for {data['site']} ({data['updated']})")
