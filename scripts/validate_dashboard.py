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


# Strict allowlist for mutable aggregate streams.
from datetime import date
def keys(v, expected):
    if not isinstance(v,dict) or set(v)!=set(expected): fail("Unexpected aggregate fields")
def counts(v, expected, nullable=()):
    keys(v,expected)
    for k,n in v.items():
        if n is None and k in nullable: continue
        nonneg_int(n,k)
def iso(v):
    if not isinstance(v,str) or date.fromisoformat(v).isoformat()!=v: fail("Invalid ISO source date")
def check_streams(streams):
    keys(streams,("gambia","nigeria","cote-divoire"))
    for country, ss in streams.items():
        expected={"recruitment","human_collection","human_lab","community"}
        if country=="nigeria" and "earlier_report" in ss: expected.add("earlier_report")
        keys(ss,expected)
        for kind,s in ss.items():
            keys(s,("data","status","as_of"))
            v=s["data"]
            if v is None:
                if s["status"]!="missing" or s["as_of"] is not None: fail("Missing stream metadata invalid")
                continue
            if s["status"] not in ("approved","provisional","retained","historical"): fail("Invalid stream status")
            iso(s["as_of"])
            if kind=="recruitment":
                counts(v,("screened_record_ids","eligible","cases","controls","household"),("controls","household"))
                if not v["cases"]<=v["eligible"]<=v["screened_record_ids"]: fail("Recruitment cascade")
            elif kind=="human_collection": counts(v,("collected",))
            elif kind=="earlier_report": counts(v,("animals_sampled",))
            elif kind=="human_lab":
                counts(v,("received","culture_tested","culture_positive","pcr_tested","pcr_positive"))
                for t in ("culture","pcr"):
                    if not v[t+"_positive"]<=v[t+"_tested"]<=v["received"]: fail("Laboratory cascade")
            else:
                keys(v,("animal","environment","water"))
                for t,a in v.items():
                    fields=("collected","received","culture_tested","culture_positive")
                    if t=="animal":
                        keys(a,(*fields,"animal_sampling_records","species_sampling_records"))
                        nonneg_int(a["animal_sampling_records"],"animal records")
                        sp=a["species_sampling_records"]
                        if not isinstance(sp,dict) or set(sp)-({str(i) for i in range(1,12)}|{"unknown_or_conflicting"}): fail("Species keys")
                        for n in sp.values(): nonneg_int(n,"species count")
                        if sum(sp.values())!=a["animal_sampling_records"]: fail("Species reconciliation")
                    else: keys(a,fields)
                    counts({k:a[k] for k in fields},fields)
                    if not a["culture_positive"]<=a["culture_tested"]<=a["received"]<=a["collected"]: fail("Community cascade")
if "streams" not in root: fail("Missing independently dated streams")
check_streams(root["streams"])
