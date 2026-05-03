from engine.anomaly import run_all
from engine.financials import generate_balance_sheet, generate_pl, generate_variance
from engine.generator import generate_transactions, load_from_db, save_to_db


def main() -> None:
    print("\n=== STEP 1: DATA GENERATION ===")
    df = generate_transactions(1000)
    save_to_db(df)

    df = load_from_db()

    print("\n=== STEP 2: ANOMALY DETECTION ===")
    df = run_all(df)

    print("\n=== STEP 3: FINANCIAL SUMMARIES ===")

    pl = generate_pl(df)
    print("\n-- P&L Statement --")
    for k, v in pl.items():
        print(f"  {k}: {v}")

    bs = generate_balance_sheet(df)
    print("\n-- Balance Sheet --")
    for k, v in bs.items():
        print(f"  {k}: {v}")

    var = generate_variance(df)
    print("\n-- Variance Analysis --")
    print(var.to_string(index=False))

    print("\n=== FLAGGED TRANSACTIONS (sample) ===")
    flagged = df[df["any_anomaly"] == True][
        [
            "transaction_id",
            "account_type",
            "debit",
            "credit",
            "flag_reason",
            "z_anomaly",
            "ml_anomaly",
        ]
    ].head(15)
    print(flagged.to_string(index=False))


if __name__ == "__main__":
    main()
