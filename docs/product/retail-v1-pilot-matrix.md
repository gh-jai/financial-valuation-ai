# Retail v1 Pilot and Holdout Matrix

Status: M8 reviewed design; M9-I1 offline primitives approved; issuer selection and data
acquisition are not authorized

Issuer names are deliberately not selected in M8. Selection happens under M13 data-license and conflict-of-interest review, before viewing whether an issuer produces an attractive valuation.

M9-I1 adds no issuer candidates, real-company fixtures, provider responses, or acquisition
capability. Its provider registry remains pending and default deny. Pilot and holdout selection,
data acquisition, and use of outcomes for mapping or tuning each require their later gates.

## Development pilots

| Pilot | Required class | Primary risk exercised | Independent reconciliation |
|---|---|---|---|
| `PILOT-MATURE-01` | Mature non-financial operating company | Standard annual/quarterly/TTM mapping and enterprise-to-equity bridge | Full spreadsheet DCF |
| `PILOT-MATURE-02` | Mature company with leases/minority or non-operating claims | Claim classification and share bridge | Full spreadsheet DCF and claims schedule |
| `PILOT-GROWTH-01` | Asset-light growth company | Revenue scale, margin fade, SBC and sales-to-capital | Full spreadsheet growth route |
| `PILOT-GROWTH-02` | Capital-intensive growth company | Capacity, capex, depreciation, reinvestment lag | Full spreadsheet growth route |
| `PILOT-YOUNG-01` | Young/negative-FCFF operating company | Financing need, survival and dilution | Specialist spreadsheet with failure scenario |
| `PILOT-CYCLE-01` | Cyclical operating company | Normalized/current-expectations route and immutable intrinsic value | DCF plus separate cycle review |
| `PILOT-DISTRESS-01` | Declining or distressed operating company | Closure, recovery, financing, contingent survival | Specialist going-concern/recovery reconciliation |
| `PILOT-XBRL-EDGE-01` | Custom-XBRL or material corporate-action case | Custom tags, amendment/split/acquisition/disposal | Raw-to-normalized mapping audit |

## Holdouts

| Holdout | Selection rule | Purpose |
|---|---|---|
| `HOLDOUT-01` | Supported issuer not used to build concept mappings or route fixtures | Detect mapping overfit and undocumented assumptions |
| `HOLDOUT-02` | Different supported lifecycle and filing complexity from Holdout 01 | Test generalization of ingestion, routing, reporting, and safe stop |

## Required evidence per pilot

- immutable, legally usable filing and market-data snapshots;
- issuer-selection rationale written before valuation results are known;
- expected support/route decision and explicit stop conditions;
- raw-to-normalized mapping review with period/unit/currency/accession checks;
- exact assumptions reproduced by a reviewer-owned spreadsheet or independent program;
- per-share reconciliation difference no greater than 0.1% under identical assumptions;
- explanation of every material difference and reviewer sign-off;
- report comprehension, accessibility, prohibited-advice, stale-data, provider-outage, and approval-tampering tests.

The pilots validate data, method application, reproducibility, controls, and communication. Subsequent share-price performance is not an acceptance metric.
