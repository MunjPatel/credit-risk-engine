from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))  # local shared/ for standalone + Streamlit Cloud
sys.path.insert(0, str(ROOT / "src"))

from shared.plot_theme import COLORS, apply_plotly_theme  # noqa: E402
from data import illustrative_debt_face, load_equity_panel  # noqa: E402
from irb import risk_weight, rw_grid  # noqa: E402
from merton import implied_asset_value, distance_to_default, dd_to_pd  # noqa: E402
from migration import simulate_losses  # noqa: E402

st.set_page_config(page_title="Credit Risk Engine", layout="wide")
st.markdown(
    f"<style>.stApp {{ background-color: {COLORS['bg']}; color: {COLORS['text']}; }}</style>",
    unsafe_allow_html=True,
)
st.title("Credit Risk Engine")
st.caption("Merton DD · migration loss simulation · Basel IRB sensitivities (public / illustrative inputs)")

tab1, tab2, tab3 = st.tabs(["Distance to Default", "Loss Simulation", "IRB Sensitivities"])

with tab1:
    prices = load_equity_panel()
    tickers = list(prices.columns)
    t = st.selectbox("Ticker", tickers, index=0)
    debt = float(illustrative_debt_face(tickers)[t])
    debt = st.number_input("Illustrative debt face (USD)", value=debt, format="%.0f")
    r = st.slider("Risk-free rate", 0.0, 0.1, 0.03, 0.005)
    hist = prices[t].dropna().tail(252)
    E = float(hist.iloc[-1]) * 1_000_000
    sigma_e = float(hist.pct_change().std() * np.sqrt(252))
    V, sig_v = implied_asset_value(E, debt, 1.0, r, sigma_e)
    dd = distance_to_default(V, debt, 1.0, r, sig_v)
    pd_ = dd_to_pd(dd)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Equity vol", f"{sigma_e:.1%}")
    c2.metric("Asset vol", f"{sig_v:.1%}")
    c3.metric("DD", f"{dd:.2f}")
    c4.metric("Mapped PD", f"{pd_:.2%}")
    fig = px.line(hist, title=f"{t} adjusted close (1y)")
    apply_plotly_theme(fig)
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Debt face values are illustrative placeholders (not live EDGAR filings). I map PD with Φ(-DD), not a proprietary EDF calibration.")

with tab2:
    n_sims = st.slider("Simulations", 500, 5000, 2000, 500)
    lgd = st.slider("Mean LGD", 0.1, 0.8, 0.45, 0.05)
    losses = simulate_losses(n_sims=n_sims, lgd_mean=lgd, seed=42)
    c1, c2, c3 = st.columns(3)
    c1.metric("Mean loss", f"${losses['loss'].mean():,.0f}")
    c2.metric("95% loss", f"${losses['loss'].quantile(0.95):,.0f}")
    c3.metric("Avg default rate", f"{losses['default_rate'].mean():.2%}")
    fig = px.histogram(losses, x="loss", nbins=40, title="Portfolio credit loss distribution")
    apply_plotly_theme(fig)
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    m = st.slider("Effective maturity (years)", 1.0, 5.0, 2.5, 0.5)
    pds = [0.001, 0.005, 0.01, 0.02, 0.05, 0.1]
    lgds = [0.25, 0.45, 0.65]
    z = np.array([[risk_weight(pd, lgd, m) for pd in pds] for lgd in lgds])
    fig = go.Figure(
        data=go.Heatmap(
            z=z,
            x=[f"{pd:.1%}" for pd in pds],
            y=[f"LGD {lgd:.0%}" for lgd in lgds],
            colorscale="Teal",
            colorbar_title="RW",
        )
    )
    fig.update_layout(title="Corporate IRB risk weights (simplified public formula)")
    apply_plotly_theme(fig)
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(pd.DataFrame(z, index=lgds, columns=pds), use_container_width=True)
