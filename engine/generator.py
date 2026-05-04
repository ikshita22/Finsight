from datetime import date, timedelta
from pathlib import Path
import random

import numpy as np
import pandas as pd
from faker import Faker
from sqlalchemy import create_engine


fake = Faker()


def _random_date_str(start: date, end: date) -> str:
    day_offset = random.randint(0, (end - start).days)
    return (start + timedelta(days=day_offset)).strftime("%Y-%m-%d")


def generate_transactions(n: int = 1000) -> pd.DataFrame:
    start_date = date(2024, 1, 1)
    end_date = date.today()

    transaction_ids = [f"TXN{i:05d}" for i in range(1, n + 1)]
    account_types = np.random.choice(
        ["Asset", "Liability", "Equity", "Revenue", "Expense"],
        size=n,
        p=[0.2, 0.2, 0.2, 0.2, 0.2],
    )

    debit = np.round(np.random.lognormal(mean=8, sigma=1.5, size=n), 2)
    credit = np.round(np.random.lognormal(mean=8, sigma=1.5, size=n), 2)

    df = pd.DataFrame(
        {
            "transaction_id": transaction_ids,
            "date": [_random_date_str(start_date, end_date) for _ in range(n)],
            "entity": [fake.company() for _ in range(n)],
            "account_type": account_types,
            "debit": debit,
            "credit": credit,
            "currency": np.random.choice(
                ["USD", "INR", "EUR", "GBP"], size=n, p=[0.5, 0.2, 0.2, 0.1]
            ),
            "region": np.random.choice(["APAC", "EMEA", "Americas"], size=n),
        }
    )

    df["budget"] = np.round(df["debit"] * np.random.uniform(0.8, 1.2, size=n), 2)

    if n > 10:
        df.loc[10 : min(15, n - 1), "debit"] = 9999999.00

    if n > 22:
        df.loc[20:22] = df.loc[0:2].values

    if n > 30:
        df.loc[30, "credit"] = -500.00

    if n > 40:
        df.loc[40, "currency"] = "XYZ"

    if n > 50:
        df.loc[50, "debit"] = -999.00

    return df


def save_to_db(df: pd.DataFrame) -> None:
    project_root = Path(__file__).resolve().parent.parent
    db_path = project_root / "db" / "finsight.db"
    csv_path = project_root / "data" / "transactions.csv"

    engine = create_engine(f"sqlite:///{db_path}")
    df.to_sql("transactions", con=engine, if_exists="replace", index=False)
    df.to_csv(csv_path, index=False)

    print("[✓] Data saved to db/finsight.db and data/transactions.csv")


def load_from_db() -> pd.DataFrame:
    project_root = Path(__file__).resolve().parent.parent
    db_path = project_root / "db" / "finsight.db"

    engine = create_engine(f"sqlite:///{db_path}")
    return pd.read_sql_table("transactions", con=engine)
