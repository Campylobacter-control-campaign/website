#!/usr/bin/env python3
"""Validate the public CCC multi-site aggregate dashboard JSON.

Only aggregate site summaries belong in this file. Participant-level exports
must remain inside the controlled study environment.
"""
import json, sys
from pathlib import Path

path = Path(sys.argv[1] if len(sys.argv) > 1 else "dashboard.json")
root = json.loads(path.read_text(encoding="utf-8"))

FORBIDDEN = {
    "record_id","participant_id","subject_id","name","first_name","last_name",
    "dob","date_of_birth","address","phone","email","gps","latitude","longitude",
    "free_text","notes_free_text"
}
ALLOWED_STATUS = {"active","sampling","preparing","inactive","complete"}
REPORTING_STATUS = {"active","complete"}

def fail(msg): raise SystemExit(msg)
def nonneg_int(v,label):
    if not isinstance(v,int) or isinstance(v,bool) or v < 0: fail(f"{label} must be a non-negative integer")
def walk(x, trail="root"):
    if isinstance(x, dict):
        for k,v in x.items():
            if k.lower() in FORBIDDEN: fail(f"Forbidden participant-level field {k!r} at {trail}")
            walk(v, trail+"."+k)
    elif isinstance(x, list):
        for i,v in enumerate(x): walk(v, f"{trail}[{i}]")

walk(root)
for key in ("schema_version","updated","programme","sites"):
    if key not in root: fail(f"Missing top-level key: {key}")
if root["schema_version"] != 2: fail("dashboard schema_version must be 2")
if not isinstance(root["sites"],dict) or not root["sites"]: fail("sites must be a non-empty object")

def validate_site(site_id, site):
    trail=f"sites.{site_id}"
    for key in ("label","status","note","updated","source","data"):
        if key not in site: fail(f"{trail} missing {key}")
    if site["status"] not in ALLOWED_STATUS: fail(f"{trail}.status is invalid")
    if site["data"] is None:
        if site["status"] == "active": fail(f"{trail} is active but has no aggregate data")
        # sampling means fieldwork has started, but no approved numeric site feed exists yet.
        return False
    if site["status"] not in REPORTING_STATUS:
        fail(f"{trail} contains aggregate data while status is {site['status']!r}")
    d=site["data"]
    for key in ("headline","recruitment","human_specimens","human_lab","demographics","animals","environment","notes"):
        if key not in d: fail(f"{trail}.data missing {key}")

    r=d["recruitment"]
    nonneg_int(r["screened"],trail+".recruitment.screened")
    nonneg_int(r["eligible"],trail+".recruitment.eligible")
    if r["eligible"] > r["screened"]: fail(f"{trail}: eligible exceeds screened")
    for i,c in enumerate(r["cohorts"]):
        nonneg_int(c["enrolled"],f"{trail}.recruitment.cohorts[{i}].enrolled")
        if c.get("target") is not None: nonneg_int(c["target"],f"{trail}.recruitment.cohorts[{i}].target")
        # The public cohort name is fixed across English and French dashboard
        # panels. Keep the stable 'controls' ID for backwards compatibility.
        if c.get("id") == "controls" and c.get("label") != "Community children":
            fail(f"{trail}: the controls cohort must be labelled 'Community children'")

    hs=d["human_specimens"]
    nonneg_int(hs["people"],trail+".human_specimens.people")
    nonneg_int(hs["total"],trail+".human_specimens.total")
    spec_sum=sum(x["value"] for x in hs["types"])
    if spec_sum != hs["total"]: fail(f"{trail}: specimen-type counts sum to {spec_sum}, not {hs['total']}")
    cohort_people=sum(x["people"] for x in hs["cohorts"])
    if cohort_people != hs["people"]: fail(f"{trail}: cohort people sum to {cohort_people}, not {hs['people']}")

    sex=d["demographics"]["sex"]
    if sex["male"] + sex["female"] != hs["people"]: fail(f"{trail}: sex totals do not match enrolled people")

    lab=d["human_lab"]["totals"]
    if lab["confirmed_positive"] > lab["enrolled"]: fail(f"{trail}: confirmed human positives exceed enrolled")
    testing=d["human_lab"].get("testing")
    if testing:
        culture=testing["culture"]; pcr=testing["pcr"]
        if culture["tested"] != lab["culture_results"] or culture["positive"] != lab["culture_positive"]:
            fail(f"{trail}: culture testing summary does not match laboratory totals")
        if pcr["tested"] != lab["pcr_results"] or pcr["positive"] != lab["pcr_positive"]:
            fail(f"{trail}: PCR testing summary does not match laboratory totals")
        if pcr.get("eligible") is not None and pcr["tested"] + pcr.get("pending",0) != pcr["eligible"]:
            fail(f"{trail}: PCR tested + pending does not match eligible case count")

    a=d["animals"]["community"]
    for k in ("sampled","target","specimens","tested","positive"): nonneg_int(a[k],trail+".animals.community."+k)
    if a["positive"] > a["tested"]: fail(f"{trail}: animal positives exceed tested")
    species=d["animals"].get("species",[])
    if species and all("tested" in x and "positive" in x for x in species):
        for x in species:
            nonneg_int(x["value"],trail+".animals.species.sampled")
            nonneg_int(x["tested"],trail+".animals.species.tested")
            nonneg_int(x["positive"],trail+".animals.species.positive")
            if x["positive"] > x["tested"] or x["tested"] > x["value"]:
                fail(f"{trail}: invalid species testing denominator")
        if sum(x["value"] for x in species) != a["sampled"] or sum(x["tested"] for x in species) != a["tested"] or sum(x["positive"] for x in species) != a["positive"]:
            fail(f"{trail}: species breakdown does not reconcile to community animal totals")
    return True

reporting=0
for site_id,site in root["sites"].items():
    if validate_site(site_id,site): reporting += 1

p=root["programme"]
nonneg_int(p["reporting_sites"],"programme.reporting_sites")
if p["reporting_sites"] != reporting:
    fail(f"programme.reporting_sites is {p['reporting_sites']} but {reporting} sites contain data")
if not isinstance(p.get("headline"),list) or not p["headline"]: fail("programme.headline must be a non-empty list")
for i,x in enumerate(p["headline"]): nonneg_int(x["value"],f"programme.headline[{i}].value")

print(f"OK: {path} contains schema v2 aggregate data for {reporting} reporting site(s) ({root['updated']})")
