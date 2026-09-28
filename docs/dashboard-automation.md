# Automated public dashboard feed

The public dashboard is rendered from `dashboard.json`. Schema version 2 is designed for the CCC programme to add sites without changing the page layout.

## Data model

The public JSON has two levels:

- `programme` — safe totals across all sites that currently have an approved aggregate dataset. These figures drive the homepage and the **All sites** dashboard.
- `sites` — one registry entry per CCC country/site. Each entry has a status (`active`, `preparing`, `inactive` or `complete`) and either an aggregate `data` object or `null`.

A site with `data: null` can be shown as preparing without publishing invented zero counts. When Nigeria or Côte d’Ivoire produces its first approved report, its `data` object can use the same blocks as The Gambia: recruitment, human specimens, laboratory results, grouped demographics, animals, environment and notes. Testing metadata should travel with each site dataset as well: for The Gambia, culture applies across enrolled human cohorts while PCR is restricted to diarrhoea cases, and non-human samples are culture-based. This avoids the front end assuming every country uses an identical testing pathway.

The front end automatically:
1. shows the detailed reporting site while only one site has data;
2. adds interactive tabs for every reporting/preparing site;
3. switches the default to **All sites** once two or more sites have data;
4. reads the homepage snapshot from `programme.headline`.

## Safety rule

Do **not** point the workflow at a REDCap or SurveyCTO participant-level export.

The upstream process should aggregate inside the controlled study environment and expose only approved counts, targets, grouped demographics, specimen totals and grouped laboratory results. No record IDs, names, dates of birth, contact details, GPS, free text or row-level observations should reach GitHub.

The validator in `scripts/validate_dashboard.py`:
- requires schema version 2;
- validates every site that contains data;
- rejects common participant-identifier fields anywhere in the JSON;
- checks specimen, cohort and demographic reconciliation;
- checks that positive counts do not exceed denominators;
- checks that `programme.reporting_sites` matches the number of sites with data.

## Connecting the feed

Configure these repository Actions secrets:

- `CCC_DASHBOARD_FEED_URL` — HTTPS endpoint returning the complete schema-v2 programme JSON.
- `CCC_DASHBOARD_FEED_TOKEN` — optional bearer token if the aggregate endpoint requires authentication.

The workflow checks for updates **fortnightly after the CCC Programme meeting**. GitHub schedules it every Friday evening, but the job calculates the exact number of days since the **25 September 2026** programme-meeting anchor and proceeds only when that interval is divisible by 14. This avoids ISO-week parity drifting in years with week 53. It can also be run manually, which bypasses the cadence gate.

The feed URL must use HTTPS. The download deliberately does **not** follow redirects, so an optional bearer token cannot be forwarded to a different redirect host.

When a validated feed changes `dashboard.json`, the workflow creates an `automated/dashboard-<run id>` branch and opens a pull request instead of pushing directly to the default branch. This keeps a human review step between the aggregate feed and the public website. If the feed has not changed, no branch or pull request is created.

## Recommended upstream pattern

The preferred boundary is:

`REDCap / SurveyCTO → controlled aggregation → programme aggregate JSON → validation → public dashboard`

The programme feed should calculate `programme.headline` from the site aggregates rather than requiring the browser to infer which measures are comparable across countries. That leaves room for country-specific protocol differences while keeping programme-wide totals deliberate.

### REDCap

Use a scheduled process in the institutionally controlled environment to query the REDCap API, calculate approved aggregate counts, and write the small public JSON feed. Keep the API token and raw records on the controlled side of this boundary.

Official overview: https://projectredcap.org/wp-content/uploads/2025/01/REDCapTechnicalOverview.pdf

### SurveyCTO

Use the SurveyCTO API or a server dataset/workflow to create approved aggregate data before the programme feed is generated. Keep form credentials and row-level exports out of this repository.

Official API documentation: https://docs.surveycto.com/05-exporting-and-publishing-data/05-api-access/01.api-access.html

## Bringing a new site online

For Nigeria, Côte d’Ivoire or another site:

1. Leave the site as `preparing` with `data: null` until the first approved aggregate report exists.
2. Generate the site's aggregate blocks inside the controlled environment.
3. Set the site's `updated` and `source`, attach the aggregate `data`, and change status to `active`.
4. Recalculate the approved `programme.headline` totals and `programme.reporting_sites`.
5. Run `python scripts/validate_dashboard.py dashboard.json`.
6. Let the scheduled/manual workflow open a dashboard-update pull request and review the aggregate totals, source date and site status before merging.

Burkina Faso and Ghana can remain registered but inactive until the programme decides which data stream should populate the public dashboard.


## Operational checklist

Before enabling the live feed:

1. Set `CCC_DASHBOARD_FEED_URL` to the approved **HTTPS aggregate-only endpoint**.
2. Add `CCC_DASHBOARD_FEED_TOKEN` only if that endpoint requires a bearer token.
3. Run the workflow manually once.
4. Confirm the candidate JSON passes validation and that a pull request is created only when the aggregate data differ from `main`.
5. Review the first automated pull request against the corresponding site/programme report before merging.
6. Keep participant-level exports, REDCap/SurveyCTO credentials and raw records entirely outside this repository and GitHub Actions.
