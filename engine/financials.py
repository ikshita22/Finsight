import numpy as np
import pandas as pd


def generate_pl(df: pd.DataFrame) -> dict:
    gross_revenue = float(df.loc[df["account_type"] == "Revenue", "credit"].sum())
    total_expenses = float(df.loc[df["account_type"] == "Expense", "debit"].sum())
    net_income = gross_revenue - total_expenses

    if gross_revenue == 0:
        margin_pct = 0.0
    else:
        margin_pct = round((net_income / gross_revenue) * 100, 2)

    return {
        "Gross Revenue": gross_revenue,
        "Total Expenses": total_expenses,
        "Net Income": net_income,
        "Margin %": margin_pct,
    }


def generate_balance_sheet(df: pd.DataFrame) -> dict:
    total_assets = float(df.loc[df["account_type"] == "Asset", "debit"].sum())
    total_liabilities = float(df.loc[df["account_type"] == "Liability", "credit"].sum())
    equity = float(df.loc[df["account_type"] == "Equity", "credit"].sum())

    if abs(total_assets - (total_liabilities + equity)) < 1.0:
        balance_check = "BALANCED"
    else:
        balance_check = "MISMATCH — review required"

    return {
        "Total Assets": total_assets,
        "Total Liabilities": total_liabilities,
        "Equity": equity,
        "Balance Check": balance_check,
    }


def generate_variance(df: pd.DataFrame) -> pd.DataFrame:
    variance_df = (
        df.groupby("account_type", as_index=False)
        .agg(actual=("debit", "sum"), budget=("budget", "sum"))
        .astype({"actual": float, "budget": float})
    )

    variance_df["variance"] = variance_df["actual"] - variance_df["budget"]
    variance_df["variance_pct"] = np.where(
        variance_df["budget"] != 0,
        np.round((variance_df["variance"] / variance_df["budget"]) * 100, 2),
        0.0,
    )

    variance_df = variance_df.sort_values("variance_pct", ascending=False).reset_index(drop=True)
    return variance_df
