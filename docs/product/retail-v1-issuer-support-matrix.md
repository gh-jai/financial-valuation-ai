# Retail v1 Issuer Support Matrix

Status: M8 reviewed contract; M9-I1 offline primitives approved; issuer resolution unauthorized

| Issuer class | v1 decision | Required route or reason |
|---|---|---|
| US-listed, USD-reporting mature non-financial operating company | Supported after data review | `WFL-VAL-001`; M6 may add a non-numeric cycle overlay |
| US-listed, USD-reporting growth operating company | Supported after data review | `WFL-GRW-001` with stable-state and reinvestment controls |
| US-listed young or negative-FCFF operating company | Needs specialist review | `WFL-YNG-001`; stop if survival, financing, or claim data is material and unavailable |
| US-listed declining or distressed operating company | Needs specialist review | `WFL-DST-001`; stop if recovery, closure, financing, or claim inputs are unresolved |
| US-listed cyclical operating company | Needs specialist review | `WFL-CYC-001`; preserve intrinsic value and prohibit timing signals |
| Bank or deposit-taking institution | Unsupported | FCFF/enterprise-value framework does not model regulatory capital and financial intermediation correctly |
| Insurance company | Unsupported | Requires insurance liability, reserve, and regulatory-capital methods outside v1 |
| REIT | Unsupported | Requires sector-specific cash-flow and asset methods outside v1 |
| Fund, ETF, investment company, or holding vehicle without operating-company inputs | Unsupported | Net-asset/portfolio valuation is outside v1 |
| SPAC or blank-check company | Unsupported | Structure and transaction contingencies are outside v1 |
| Natural-resource company requiring real-option reserve valuation | Unsupported | Reserve and option models are outside v1 |
| Non-US primary listing or non-USD primary reporting | Unsupported | Currency, filing, accounting, and data contracts are outside v1 |
| Private company | Unsupported | Identity, filing, market-data, and liquidity inputs are outside v1 |
| Issuer with ambiguous ticker/CIK, insufficient history, stale data, mixed units/currency, or unresolved material corporate action | Stop | User-visible reason code; no alternate issuer or invented input |

Support is a routing decision, not a quality score. A supported class can still stop because its individual evidence is incomplete or irreconcilable.
