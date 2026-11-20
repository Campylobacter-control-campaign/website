#!/usr/bin/env python3
"""Private-side REDCap report diagnostics. NEVER run this in public GitHub Actions.

Requires: requests. REDCAP_API_URL and REDCAP_API_TOKEN environment variables.
Prints only report row counts and field names (not records, IDs or credentials).
No network request is made unless --execute is explicitly supplied.
"""
import argparse
import json
import os
import sys
from collections import Counter
from datetime import datetime, timezone

REPORTS = {
    "enrollment_screening": 12854,
    "human_specimen_linkage": 12856,
    "animal_environment": 12857,
    "enrolled_cases": 12861,
    "culture_positive_cases": 12865,
    "total_screening": 12870,
    "control_enrolled": 12873,
    "household_enrolled": 12875,
}

def fetch_report(session, url, token, report_id):
    response = session.post(url, data={
        "token": token, "content": "report", "format": "json",
        "report_id": str(report_id), "rawOrLabel": "raw",
        "rawOrLabelHeaders": "raw", "exportCheckboxLabel": "false",
        "returnFormat": "json",
    }, timeout=90, allow_redirects=False)
    response.raise_for_status()
    rows = response.json()
    if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
        raise ValueError(f"Report {report_id} did not return a list of objects")
    return rows

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--execute", action="store_true", help="Fetch reports from REDCap")
    parser.add_argument("--report", choices=list(REPORTS), default="total_screening")
    parser.add_argument("--output", help="Optional local JSON diagnostics file (aggregate metadata only)")
    args = parser.parse_args()
    if not args.execute:
        print("Dry run only. Report:", args.report, "ID:", REPORTS[args.report])
        print("Use --execute only inside an approved secure research environment.")
        return
    url = os.environ.get("REDCAP_API_URL")
    token = os.environ.get("REDCAP_API_TOKEN")
    if not url or not token or not url.startswith("https://"):
        parser.error("Set REDCAP_API_URL (HTTPS) and REDCAP_API_TOKEN securely")
    import requests
    with requests.Session() as session:
        rows = fetch_report(session, url, token, REPORTS[args.report])
    fields = sorted(set().union(*(r.keys() for r in rows))) if rows else []
    # Do not print values, sample rows, identifiers, or any free text.
    result = {
        "report": args.report,
        "report_id": REPORTS[args.report],
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
        "row_count": len(rows),
        "field_names": fields,
        "warning": "Rows may be repeating instruments/specimens, not unique participants. Not approved for publication.",
    }
    if args.output:
        from pathlib import Path
        p = __import__("pathlib").Path(args.output)
        if p.exists():
            parser.error("Output already exists; refusing overwrite")
        p.write_text(json.dumps(result, indent=2) + "\n")
        p.chmod(0o600)
    else:
        print(json.dumps(result, indent=2))
    # Deliberately do not generate dashboard.json until field mapping, denominators,
    # deduplication, PCR/culture definitions and data-governance signoff are confirmed.

if __name__ == "__main__":
    main()
