import os
import altair as alt
import feather
import streamlit as st

from solsim.simulation import Simulation


results = feather.read_dataframe(os.environ['SOLSIM_RESULTS_PATH'])
idx_cols = Simulation.INDEX_COLS

st.markdown("# Results Explorer")

quantities = st.sidebar.multiselect(
    "Quantities to plot",
    [col for col in results.columns if col not in idx_cols]
)

if quantities:

    results = results[quantities + idx_cols]
    charts = []

    for run, group in results.groupby("run"):
        chart = alt.Chart(group.melt(idx_cols)).mark_line().encode(
            x=alt.X(
                "step",
                axis=alt.Axis(tickMinStep=1),
                title="Timestep"
            ),
            y=alt.Y(
                "value",
                title="Value",
            ),
            color='variable'
        ).properties(title="Simulation Quantities over Time")
        charts.append(chart)

    st.altair_chart(alt.layer(*charts), use_container_width=True)