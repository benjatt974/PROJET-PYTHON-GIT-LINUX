import streamlit as st
from quant_a.page_quant_a import run_quant_a_page

def main():
    st.sidebar.title("Dashboard Quant")
    page = st.sidebar.radio("Module", ["Quant A"])

    if page == "Quant A":
        run_quant_a_page()

if __name__ == "__main__":
    main()
