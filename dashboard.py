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

# ─── TAB 1: OVERVIEW ───────────────────────────────────────────────
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

# ─── TAB 2: ANOMALY EXPLORER ───────────────────────────────────────
with tab2:
    st.subheader("Anomaly Detection Summary")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Rule-Based Flags", int((df["flag_reason"] != "").sum()))
    with c2:
        st.metric("Z-Score Flags", int(df["z_anomaly"].sum()))
    with c3:
        st.metric("ML Flags", int(df["ml_anomaly"].sum()))

    st.divider()

    st.subheader("Transaction Scatter — Anomalies Highlighted")
    scatter_df = df.copy()
    scatter_df["status"] = scatter_df["any_anomaly"].apply(
        lambda x: "Anomaly" if x else "Normal"
    )
    fig2 = px.scatter(
        scatter_df,
        x="debit",
        y="credit",
        color="status",
        color_discrete_map={"Anomaly": "#e74c3c", "Normal": "#7f8c8d"},
        opacity=0.7,
        log_x=True,
        log_y=True,
        title="Transaction Scatter — Anomalies Highlighted",
        template="plotly_dark"
    )
    fig2.update_traces(marker=dict(size=6))
    fig2.update_traces(marker=dict(size=10), selector=dict(name="Anomaly"))
    st.plotly_chart(fig2, use_container_width=True)

    st.divider()

    st.subheader("Flagged Transactions")
    filter_option = st.selectbox(
        "Filter by flag type",
        ["All Anomalies", "Rule-based only", "Z-score only", "ML only"]
    )

    if filter_option == "All Anomalies":
        filtered = df[df["any_anomaly"] == True]
    elif filter_option == "Rule-based only":
        filtered = df[df["flag_reason"] != ""]
    elif filter_option == "Z-score only":
        filtered = df[df["z_anomaly"] == True]
    else:
        filtered = df[df["ml_anomaly"] == True]

    st.dataframe(
        filtered[[
            "transaction_id", "date", "entity", "account_type",
            "debit", "credit", "currency", "region",
            "flag_reason", "z_anomaly", "ml_anomaly"
        ]],
        use_container_width=True,
        hide_index=True
    )

# ─── TAB 3: REPORT GENERATOR ───────────────────────────────────────
with tab3:
    st.subheader("Generate Audit Report")

    st.info("""
    **This report will contain:**
    - P&L Statement (Gross Revenue, Expenses, Net Income, Margin)
    - Balance Sheet with compliance status
    - Variance Analysis by account type
    - Top 15 anomalous transactions sorted by debit amount
    """)

    col_left, col_right = st.columns(2)
    with col_left:
        st.write(f"**Total Transactions Analysed:** {len(df):,}")
        st.write(f"**Total Anomalies Detected:** {int(df['any_anomaly'].sum()):,}")
        st.write(f"**Net Income:** ${pl['Net Income']:,.2f}")
        st.write(f"**Balance Status:** {bs['Balance Check']}")

    if st.button("Generate PDF Report", type="primary"):
        try:
            from report import generate_report
            generate_report(df, pl, bs, variance)
            st.success("Report generated successfully!")
            with open("data/finsight_report.pdf", "rb") as f:
                st.download_button(
                    label="Download Report",
                    data=f,
                    file_name="finsight_report.pdf",
                    mime="application/pdf"
                )
        except Exception as e:
            st.error(f"Error generating report: {e}")