import os
import feather
import streamlit as st

st.markdown("Hello world!")

results = feather.read_dataframe(os.environ['SOLSIM_RESULTS_PATH'])

st.table(results)