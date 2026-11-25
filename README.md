# Credit Risk Engine

**Roles:** Credit Risk (primary), Model Validation input  
**Type:** Replication of structural + actuarial + regulatory building blocks

## Sources

1. Merton (1974) structural credit / option-theoretic firm value (classic).
2. Moody’s KMV conceptual EDF framing (educational; **not** proprietary EDF). NYU Stern KMV/Vasicek materials.
3. SOA credit incidence × severity framing.
4. Basel Committee IRB risk-component formulas (public CRE text).

## Run

```bash
python 02_credit_risk_engine/scripts/run_mvp.py
streamlit run 02_credit_risk_engine/app/dashboard.py
```

## Limitations

- Debt faces are illustrative constants (no WRDS/CapIQ).
- PD = Φ(-DD) is a teaching mapping, not an empirical default calibration.
- Migration matrix is an educational approximation.



1. Push this repo to GitHub (already done if you cloned from MunjPatel/credit-risk-engine).
2. Go to https://share.streamlit.io/ → **New app**
3. Select repo `MunjPatel/credit-risk-engine`, branch `main`
4. Main file path: `app/dashboard.py`
5. Python version 3.11+ recommended → Deploy

The app reads artifacts under `outputs/`. Re-run `scripts/run_mvp.py` locally if you need to refresh them before pushing.

## Live dashboard

[https://qr-credit-risk-engine.streamlit.app/](https://qr-credit-risk-engine.streamlit.app/)

