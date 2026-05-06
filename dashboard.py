import streamlit as st
import pandas as pd
import plotly.express as px
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
    st.subheader("P&L Summary")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Gross Revenue", f"${pl['Gross Revenue']:,.2f}")
    with col2:
        st.metric("Total Expenses", f"${pl['Total Expenses']:,.2f}")
    with col3:
        net = pl['Net Income']
        st.metric("Net Income", f"${net:,.2f}", delta=f"${net:,.2f}")
    with col4:
        st.metric("Margin %", f"{pl['Margin %']}%")

    st.divider()

    left, right = st.columns(2)

    with left:
        st.subheader("Balance Sheet")
        bs_data = {
            "Metric": list(bs.keys()),
            "Value": [f"${v:,.2f}" if isinstance(v, float) else v for v in bs.values()]
        }
        bs_df = pd.DataFrame(bs_data)
        st.dataframe(bs_df, use_container_width=True, hide_index=True)

    with right:
        st.subheader("Variance Analysis")
        variance["color"] = variance["variance_pct"].apply(
            lambda x: "Over Budget" if x > 0 else "Under Budget"
        )
        fig = px.bar(
            variance,
            x="account_type",
            y="variance_pct",
            color="color",
            color_discrete_map={"Over Budget": "#e74c3c", "Under Budget": "#2ecc71"},
            title="Variance % by Account Type (Actual vs Budget)",
            template="plotly_dark"
        )
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.write("Anomaly Explorer coming in Part 3")

with tab3:
    st.write("Report Generator coming in Part 4")