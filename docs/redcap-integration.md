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
