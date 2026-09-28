# GETCampy-Africa archive dashboard

The public GETCampy archive is a **historical aggregate view**, separate from the live CCC dashboard.

## Source hierarchy

The archive uses aggregate project summaries rather than participant-level exports.

### The Gambia

Primary field snapshot:
- `GETCampy Samples update_All sites_18Aug2024_Updated.xlsx`
- 300 medically attended diarrhoea cases
- 135 community controls (45 + 90 in the source; the later reconciled metadata also records 135 controls)
- 80 household members
- 59 household environmental samples
- 32 household animal samples
- 78 community environmental samples
- 402 community animal samples
- source subtotal: 1,086
- source total reported positive: 43

Later metagenome reconciliation:
- `GETCampy_Gambia_metagenome_metadata_merged_cleaned.xlsx`
- 439 metagenome master rows: 224 cases, 135 controls, 80 household members
- 324 current analysis rows: 139 cases, 107 controls, 78 household members
- reconciled culture status in the 439-row master: 21 positive, 413 negative, 5 without a record

These are deliberately shown as separate study stages.

### Burkina Faso

Latest aggregate site update found:
- `GETCampy Samples update_The Burkina Faso_07November2024_IBEB.xlsx`
- 360 medically attended diarrhoea cases; 40 positive
- 78 community environmental/water samples; 10 positive
- 362 community animal samples; 100 positive
- source total: 800; 150 positive

This supersedes the earlier 18 August 2024 all-sites snapshot for the archive.

### Ghana

Aggregate sampling snapshot:
- `GETCampy Samples update_All sites_18Aug2024_Updated.xlsx`
- 253 diarrhoeal child samples
- 100 community human samples
- 17 community environmental/water samples
- 288 community animal samples

The Ghana section of the source describes laboratory calls as **presumptive**. The public archive therefore does not convert those calls into confirmed Campylobacter-positive counts, and it does not calculate a cross-category Ghana grand total.

## Public-data rule

Do not put REDCap exports, participant identifiers, sample-level clinical records or other participant-level data in this repository. If the archive is revised, update only aggregate values that can be traced to an approved summary, manuscript table or other appropriate aggregate source.

Do not silently reconcile contradictory source totals. Document the discrepancy or omit the derived value.
