import streamlit as st
from engine.generator import load_from_db
from engine.anomaly import run_all
from engine.financials import generate_pl, generate_balance_sheet, generate_variance

st.set_page_config(
    page_title="FinSight",
    page_icon="📊",
    layout="wide"
)

@st.cache_data
def load_data():
    df_raw = load_from_db()
    df = run_all(df_raw)
    pl = generate_pl(df)
    bs = generate_balance_sheet(df)
    variance = generate_variance(df)
    return df, pl, bs, variance

df, pl, bs, variance = load_data()

st.title("FinSight — Financial Intelligence Report")
st.caption("Automated anomaly detection and regulatory reporting engine")

tab1, tab2, tab3 = st.tabs(["Overview", "Anomaly Explorer", "Report Generator"])

with tab1:
    st.write("Overview coming in Part 2")

with tab2:
    st.write("Anomaly Explorer coming in Part 3")

with tab3:
    st.write("Report Generator coming in Part 4")