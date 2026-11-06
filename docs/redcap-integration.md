# REDCap private-side adapter (draft)

This is a **diagnostic scaffold**, not an approved automated data export. It must run in an institutionally approved secure environment, **not in public GitHub Actions, ChatGPT, or a developer laptop without approval**.

## Security first

An API token appeared in screenshots during setup. **Revoke/rotate that token before use.** Never commit tokens, API request screenshots, participant records or raw report responses. Use a dedicated read-only service account restricted to the approved Gambia Data Access Group if available.

## Local use (after MRCG approval)

Install `requests` in the controlled environment. Configure `REDCAP_API_URL` and `REDCAP_API_TOKEN` using the local secrets manager; never paste them into a command or chat.

```sh
python scripts/redcap_report_probe.py
python scripts/redcap_report_probe.py --report total_screening --execute
```

The script prints **only** the report ID, number of returned rows and field names. Note: field names may themselves expose custom naming conventions; share the output only with the authorised project team. It does not create public dashboard data.

## Next implementation milestones

1. Confirm report access and obtain the REDCap data dictionary and KPI report filters **within MRCG**.
2. Define per-metric denominators and deduplication keys: screening event, enrolled participant, specimen, culture, PCR, and culture-or-PCR positivity are not interchangeable.
3. Independently reconcile the secure aggregates against the approved site report and REDCap consolidated dashboard.
4. Produce the existing schema-v2 `dashboard.json` **only from reviewed, approved aggregate counts**, with source dates and pending-test caveats.
5. Host that aggregate-only feed behind HTTPS and configure `CCC_DASHBOARD_FEED_URL` (and optional bearer token) for the existing fortnightly PR workflow. Keep REDCap API credentials and raw responses entirely within the approved environment.

The public dashboard and French translation already consume the same `dashboard.json`. No direct REDCap connection should be made from a browser or public GitHub runner.

## Candidate dashboard generation from reviewed aggregates

A second script, `scripts/redcap_aggregate_adapter.py`, converts a **complete, approved site-level aggregate snapshot** into a candidate `dashboard.next.json` and runs the repository validator before writing the file. It is intentionally **not** a raw REDCap-to-public converter: the report field mapping and participant/specimen deduplication rules have not yet been verified.

Input format (structure only; values below are placeholders and must **not** be published):

```json
{
  "site": "gambia",
  "as_of": "2026-11-06",
  "source": "Approved Gambia aggregate summary",
  "approved_by": "Authorised CCC data reviewer",
  "data": {}
}
```

Replace `data` with a **complete** site `data` object matching `dashboard.json > sites > gambia > data`, using a single approved reporting cut-off. Incomplete snapshots fail. The script also refuses unvalidated multi-site headline aggregation. The existing dashboard validator checks totals, but it cannot establish the scientific correctness of the source definitions or guarantee that arbitrary free-text values are anonymous: review and approval are mandatory.

```sh
python scripts/redcap_aggregate_adapter.py approved_gambia_aggregates.json --output dashboard.next.json
python scripts/validate_dashboard.py dashboard.next.json
```

Do not commit `approved_gambia_aggregates.json` or `dashboard.next.json` until reviewed. No live REDCap calls have been made by these repository changes.
