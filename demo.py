import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import date, timedelta
from simulation import Simulation
 
# ----------------------------------------------------------------------
# Page config
# ----------------------------------------------------------------------
st.set_page_config(page_title="Backtesting Dashboard", layout="wide")
 
st.title("Backtesting Dashboard")
st.caption("Enter one or more tickers, pick a strategy, and see how it would have performed historically.")
 
# ----------------------------------------------------------------------
# ============  🔌 BACKEND INTEGRATION POINT  ===========================
# Replace the inside of this function with a real call to your API.
# Keep the return shape the same and the rest of the app needs no changes.
#
# Expected return shape:
# {
#     "AAPL": {
#         "dates": ["2023-01-03", "2023-01-04", ...],
#         "portfolio_value": [10000, 10050, ...],   # strategy equity curve
#         "buy_hold_value": [10000, 10020, ...],    # baseline equity curve
#         "metrics": {
#             "total_return": 0.184,      # as a decimal, e.g. 0.184 = 18.4%
#             "cagr": 0.091,
#             "volatility": 0.22,
#             "sharpe_ratio": 1.12,
#             "max_drawdown": -0.15,
#             "win_rate": 0.54,
#             "calmar_ratio": 0.61,
#         }
#     },
#     # ...one entry per ticker, plus an optional "PORTFOLIO" key if you
#     # combine multiple tickers into one equal-weight backtest.
# }
# ========================================================================
 
# ----------------------------------------------------------------------
# Sidebar - Inputs
# ----------------------------------------------------------------------
with st.sidebar:
    st.header("Settings")
 
    tickers_input = st.text_input(
        "Ticker(s) — comma separated",
        value="AAPL, MSFT",
        help="Example: AAPL, MSFT, GOOGL"
    )
 
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start date", value=date.today() - timedelta(days=365 * 3))
    with col2:
        end_date = st.date_input("End date", value=date.today())
 
    initial_capital = st.number_input(
        "Initial capital ($)", min_value=100, value=10000, step=500
    )
 
    combine_portfolio = False
    weighting = st.radio(
        "Multi-stock allocation",
        ["Equal weight", "Compare separately"],
        help="Equal weight combines all tickers into one portfolio. "
             "Compare separately backtests and charts each ticker on its own."
    )
    combine_portfolio = (weighting == "Equal weight")
 
    st.divider()
    st.subheader("Strategy")
 
    strategy = st.selectbox(
        "Choose a strategy",
        ["Buy & Hold", "SMA Crossover", "LLM"]
    )
    
    strategy_params = {}
    if strategy == "SMA Crossover":
        c1, c2 = st.columns(2)
        with c1:
            strategy_params["fast_sma"] = st.number_input("Fast SMA (days)", min_value=2, value=20)
        with c2:
            strategy_params["slow_sma"] = st.number_input("Slow SMA (days)", min_value=5, value=50)
 
    st.divider() 
    run_one_button = st.button("Run One", use_container_width=True, type="primary")
    run_all_button = st.button("Run All", use_container_width=True, type="primary")

# ----------------------------------------------------------------------
# Display helpers
# ----------------------------------------------------------------------
 
def fmt_pct(x):
    return f"{x * 100:,.2f}%" if pd.notnull(x) else "N/A"
 
 
def fmt_num(x):
    return f"{x:,.2f}" if pd.notnull(x) else "N/A"
 
 
def metric_display_row(metrics):
    display_fmt = {
        "total_return": ("Total Return", fmt_pct),
        "cagr": ("CAGR", fmt_pct),
        "volatility": ("Volatility (ann.)", fmt_pct),
        "sharpe_ratio": ("Sharpe Ratio", fmt_num),
        "max_drawdown": ("Max Drawdown", fmt_pct),
        "win_rate": ("Win Rate", fmt_pct),
        "calmar_ratio": ("Calmar Ratio", fmt_num),
    }
    cols = st.columns(4)
    for i, (key, (label, fmt)) in enumerate(display_fmt.items()):
        with cols[i % 4]:
            st.metric(label, fmt(metrics.get(key, np.nan)))
 
 
def render_result_block(name, result):
    st.subheader(name)
 
    dates = pd.to_datetime(result["dates"])
    portfolio_value = pd.Series(result["portfolio_value"], index=dates)
    buy_hold_value = pd.Series(result["buy_hold_value"], index=dates)
 
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=portfolio_value.index, y=portfolio_value,
                              name=f"{strategy}", line=dict(width=3)))
    fig.add_trace(go.Scatter(x=buy_hold_value.index, y=buy_hold_value,
                              name="Buy & Hold", line=dict(dash="dot")))
    fig.update_layout(
        title=f"{name} — Portfolio Growth",
        xaxis_title="Date", yaxis_title="Portfolio Value ($)",
        hovermode="x unified", height=450,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig, use_container_width=True)
 
    metric_display_row(result["metrics"])
 
    with st.expander(f"Drawdown — {name}"):
        running_max = portfolio_value.cummax()
        drawdown = portfolio_value / running_max - 1
        dd_fig = go.Figure()
        dd_fig.add_trace(go.Scatter(x=drawdown.index, y=drawdown * 100,
                                     fill="tozeroy", name="Drawdown %",
                                     line=dict(color="crimson")))
        dd_fig.update_layout(title=f"{name} Drawdown", yaxis_title="Drawdown (%)", height=300)
        st.plotly_chart(dd_fig, use_container_width=True)
 
    st.divider()
 
def render(results):
    tickers = list(results.keys())
    if "PORTFOLIO" in results:
        render_result_block("Combined Portfolio", results["PORTFOLIO"])
        with st.expander("Per-ticker breakdown"):
            for t in tickers:
                if t in results:
                    st.line_chart(pd.Series(
                        results[t]["portfolio_value"],
                        index=pd.to_datetime(results[t]["dates"])
                    ), height=200)
    else:
        for t in tickers:
            if t in results:
                render_result_block(t, results[t])
            else:
                st.warning(f"No result returned for '{t}'.")

# ----------------------------------------------------------------------
# Main logic
# ----------------------------------------------------------------------
def initialize_portfolio():
    tickers = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]
    if not tickers:
        st.error("Please enter at least one ticker.")
        st.stop()

    if start_date >= end_date:
        st.error("Start date must be before end date.")
        st.stop()

    if strategy == "Buy & Hold":
        strategy_corres = "LS"
    elif strategy == "SMA Crossover":
        strategy_corres = "MAC"
    else:
        strategy_corres = strategy 

    strategy_dict = {
        "strategy": strategy_corres,
        "strategy_param": strategy_params
    }

    sim = Simulation(tickers, strategy_dict, start_date, end_date, initial_capital)
    sim.initialize_portfolio()
    return sim


sim = None
if run_one_button:
    if not sim or not sim.portfolio_init:
        sim = initialize_portfolio()
    
    with st.spinner("Running one epoch..."):    
        sim.run_one_epoch()
        results = sim.get_portfolio_history()

    print(results)

    render(results)

if run_all_button:
    if not sim or not sim.portfolio_init:
        sim = initialize_portfolio()
    
    with st.spinner("Running all epoch..."):
        sim.run_all()
        results = sim.get_portfolio_history()

    render(results)
 
else:
    st.info("Set your parameters in the sidebar and click **Run Backtest** to get started.")
