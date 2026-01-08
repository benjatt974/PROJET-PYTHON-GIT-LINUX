import streamlit as st
st.set_page_config(page_title="Quant Dashboard", layout="wide")

from quant_a.page_quant_a import run_quant_a_page
from quant_b.page_quant_b import run_quant_b_page

st.sidebar.title("Modules")
page = st.sidebar.radio("Choisir un module", ["Quant A", "Quant B"])

if page == "Quant A":
    run_quant_a_page()
else:
    run_quant_b_page()
