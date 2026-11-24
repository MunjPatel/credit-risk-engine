from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from data import illustrative_debt_face, load_equity_panel  # noqa: E402
from irb import capital_requirement, risk_weight, rw_grid  # noqa: E402
from merton import panel_dd_from_equity  # noqa: E402
from migration import simulate_losses  # noqa: E402


def main():
    out = ROOT / "outputs"
    out.mkdir(parents=True, exist_ok=True)

    px = load_equity_panel()
    debt = illustrative_debt_face(list(px.columns))
    # Weekly sampling over ~2y for speed (root-finding per point)
    px_recent = px.loc[px.index >= (px.index.max() - pd.Timedelta(days=800))]
    px_weekly = px_recent.resample("W-FRI").last().dropna(how="all")
    dd = panel_dd_from_equity(px_weekly, debt, vol_window=26)
    # Keep month-end snapshots
    if not dd.empty:
        dd["date"] = pd.to_datetime(dd["date"])
        snap = (
            dd.sort_values("date")
            .groupby("ticker")
            .tail(1)
            .sort_values("PD", ascending=False)
        )
    else:
        snap = pd.DataFrame()

    losses = simulate_losses(n_sims=3000, seed=42)
    grid = rw_grid()
    grid_df = pd.DataFrame(grid).T
    grid_df.index.name = "LGD"
    grid_df.columns = [f"PD={c}" for c in grid_df.columns]

    # Unit checks for IRB (corporate K rises over typical PD range)
    assert risk_weight(0.05, 0.45) > risk_weight(0.001, 0.45)
    assert capital_requirement(0.05, 0.45) > 0

    dd.to_csv(out / "dd_panel.csv", index=False)
    snap.to_csv(out / "dd_latest.csv", index=False)
    losses.to_csv(out / "loss_sims.csv", index=False)
    grid_df.to_csv(out / "irb_rw_grid.csv")
    debt.to_csv(out / "illustrative_debt.csv", header=["debt_face"])

    meta = {
        "n_dd_rows": int(len(dd)),
        "loss_mean": float(losses["loss"].mean()),
        "loss_95": float(losses["loss"].quantile(0.95)),
        "loss_99": float(losses["loss"].quantile(0.99)),
        "avg_default_rate": float(losses["default_rate"].mean()),
        "note": "Debt faces are illustrative; PD is normal-CDF mapping of DD, not Moody's EDF.",
    }
    (out / "meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print("P2 MVP complete ->", out)
    print(meta)


if __name__ == "__main__":
    main()
