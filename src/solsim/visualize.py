# type: ignore

import os
import altair as alt
import feather
import streamlit as st

from solsim.simulation import Simulation


results = feather.read_dataframe(os.environ["SOLSIM_RESULTS_PATH"])
idx_cols = Simulation.INDEX_COLS
watched_vars = [col for col in results.columns if col not in idx_cols]

# Sidebar

st.sidebar.image(os.path.join(os.path.dirname(__file__), "../../img/logo.png"))

st.sidebar.markdown("# 👉 Select quantities")
quantities = st.sidebar.multiselect("State variables or KPIs to explore", watched_vars)
st.sidebar.markdown(
    f"""
    # 🧮 Metadata

    - **Runs: {results["run"].max() + 1}**
    - **Steps per run: {results["step"].max() + 1}**
    - **Watched quantities: {len(watched_vars)}**
"""
)

st.markdown("# 🔬 Results Explorer")

if quantities:

    st.markdown("## 📈 Graph")

    results = results[quantities + idx_cols]
    charts = []

    for run, group in results.groupby("run"):
        chart = (
            alt.Chart(group.melt(idx_cols))
            .mark_line()
            .encode(
                x=alt.X("step", axis=alt.Axis(tickMinStep=1), title="Timestep"),
                y=alt.Y(
                    "value",
                    title="Value",
                ),
                color="variable",
            )
            .properties(title="Simulation Quantities over Time")
        )
        charts.append(chart)

    st.altair_chart(alt.layer(*charts), use_container_width=True)

    st.markdown("## 📝 Table")

    st.table(results)
