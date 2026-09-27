# Automated public dashboard feed

The public dashboard is rendered entirely from `dashboard.json`. The repository now includes a scheduled GitHub Action that can replace that file from a **pre-aggregated** JSON endpoint.

## Safety rule

Do **not** point the workflow at a REDCap or SurveyCTO participant-level export.

The upstream process should aggregate inside the controlled study environment and expose only the fields represented in `dashboard.json`: counts, targets, grouped demographics, specimen totals and grouped laboratory results. No record IDs, names, dates of birth, contact details, GPS, free text or row-level observations should reach GitHub.

The validator in `scripts/validate_dashboard.py` checks the expected aggregate structure, rejects several common identifier fields, and performs basic reconciliation checks before a new dashboard file can be published.

## Connecting the feed

Configure these repository Actions secrets:

- `CCC_DASHBOARD_FEED_URL` — HTTPS endpoint returning JSON in the same structure as `dashboard.json`.
- `CCC_DASHBOARD_FEED_TOKEN` — optional bearer token if the aggregate endpoint requires authentication.

The workflow checks for updates **fortnightly after the CCC Programme meeting**. It is scheduled for Friday evening and gated to the odd ISO weeks anchored on the 25 September 2026 programme meeting (week 39), so the next scheduled checks are 9 October, 23 October, and so on. It can also be run manually at any time.

## Recommended upstream patterns

### REDCap

Use a scheduled process in the institutionally controlled environment to query the REDCap API, calculate the approved aggregate counts, and write the small public JSON feed. REDCap supports programmatic API export; keep the API token and raw records on the controlled side of this boundary.

Official overview: https://projectredcap.org/wp-content/uploads/2025/01/REDCapTechnicalOverview.pdf

### SurveyCTO

Use the SurveyCTO API or a server dataset/workflow to create an approved aggregate dataset, then expose only that aggregate output to the website updater. SurveyCTO supports CSV/JSON API access and server datasets.

Official API documentation: https://docs.surveycto.com/05-exporting-and-publishing-data/05-api-access/01.api-access.html

## Adding sites

The front end currently shows The Gambia as the active site and carries a `site_status` registry for the wider programme. Nigeria and Côte d’Ivoire are marked as preparing so the interface is ready for their first approved aggregate reports. Once sampling starts, the next schema step is to store the same aggregate dashboard blocks per site and make those tabs interactive. Burkina Faso and Ghana remain inactive until the programme decides which aggregate data stream should populate them.
