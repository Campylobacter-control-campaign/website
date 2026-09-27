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

The workflow runs daily at 06:17 UTC and can also be run manually.

## Recommended upstream patterns

### REDCap

Use a scheduled process in the institutionally controlled environment to query the REDCap API, calculate the approved aggregate counts, and write the small public JSON feed. REDCap supports programmatic API export; keep the API token and raw records on the controlled side of this boundary.

Official overview: https://projectredcap.org/wp-content/uploads/2025/01/REDCapTechnicalOverview.pdf

### SurveyCTO

Use the SurveyCTO API or a server dataset/workflow to create an approved aggregate dataset, then expose only that aggregate output to the website updater. SurveyCTO supports CSV/JSON API access and server datasets.

Official API documentation: https://docs.surveycto.com/05-exporting-and-publishing-data/05-api-access/01.api-access.html

## Adding sites

The front end currently shows The Gambia as the active site. When another site's approved aggregate feed is available, extend the JSON contract to a `sites` object or create one aggregate JSON file per site, then enable the corresponding dashboard tab.
