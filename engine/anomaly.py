import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest


def _append_flag(df: pd.DataFrame, mask: pd.Series, label: str) -> None:
    if not mask.any():
        return

    flagged = mask & (df["flag_reason"] != "")
    unflagged = mask & (df["flag_reason"] == "")

    df.loc[flagged, "flag_reason"] = df.loc[flagged, "flag_reason"] + " | " + label
    df.loc[unflagged, "flag_reason"] = label


def rule_based_flags(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["flag_reason"] = ""

    duplicate_mask = df["transaction_id"].duplicated(keep=False)
    _append_flag(df, duplicate_mask, "DUPLICATE_ID")

    _append_flag(df, df["debit"] < 0, "NEGATIVE_DEBIT")
    _append_flag(df, df["credit"] < 0, "NEGATIVE_CREDIT")
    _append_flag(df, ~df["currency"].isin(["USD", "INR", "EUR", "GBP"]), "INVALID_CURRENCY")
    _append_flag(df, df["debit"] > 1000000, "EXTREME_AMOUNT")

    return df


def zscore_flags(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["z_anomaly"] = False

    group_mean = df.groupby("account_type")["debit"].transform("mean")
    group_std = df.groupby("account_type")["debit"].transform("std")
    z_scores = (df["debit"] - group_mean) / group_std.replace(0, np.nan)

    df.loc[z_scores.abs() > 3, "z_anomaly"] = True
    df["z_anomaly"] = df["z_anomaly"].fillna(False)

    return df


def isolation_forest_flags(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["ml_anomaly"] = False

    features = df[["debit", "credit"]].astype(float)
    model = IsolationForest(contamination=0.05, random_state=42)
    preds = model.fit_predict(features)

    df.loc[preds == -1, "ml_anomaly"] = True
    return df


def run_all(df: pd.DataFrame) -> pd.DataFrame:
    df = rule_based_flags(df)
    df = zscore_flags(df)
    df = isolation_forest_flags(df)

    df["any_anomaly"] = (df["flag_reason"] != "") | (df["z_anomaly"]) | (df["ml_anomaly"])

    rule_count = int((df["flag_reason"] != "").sum())
    z_count = int(df["z_anomaly"].sum())
    ml_count = int(df["ml_anomaly"].sum())
    total_count = int(df["any_anomaly"].sum())

    print("[✓] Anomaly Detection Complete")
    print(f"    Rule-based flags : {rule_count}")
    print(f"    Z-score flags    : {z_count}")
    print(f"    ML flags         : {ml_count}")
    print(f"    Total flagged    : {total_count} (unique rows)")

    return df
