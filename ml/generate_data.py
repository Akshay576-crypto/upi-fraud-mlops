import random
import uuid
from datetime import datetime, timedelta

import numpy as np
import pandas as pd


ROWS = 15_000
OUTPUT_PATH = "data/transactions.csv"

random.seed(42)
np.random.seed(42)


RECIPIENTS = [
    {"name": "Rahul", "upi_id": "rahul@demo"},
    {"name": "Neha", "upi_id": "neha@demo"},
    {"name": "QuickCash", "upi_id": "quickcash@demo"},
    {"name": "RewardDesk", "upi_id": "rewarddesk@demo"},
]


def generate_transaction():

    recipient = random.choice(RECIPIENTS)

    # ~10% fraud
    is_fraud = np.random.rand() < 0.10

    # -----------------------------
    # COMMON BASE TRANSACTION
    # -----------------------------

    amount = np.random.lognormal(
        mean=7.4,
        sigma=0.9,
    )

    amount = min(amount, 50_000)

    amount_deviation = np.random.uniform(0.2, 3.5)

    new_beneficiary = np.random.binomial(1, 0.25)

    txn_count_last_10min = np.random.poisson(1.5)

    receiver_unique_senders_24h = np.random.randint(1, 35)

    receiver_txn_velocity = np.random.uniform(0.05, 0.75)

    previous_fraud_reports = np.random.choice(
        [0, 1, 2, 3],
        p=[0.88, 0.08, 0.03, 0.01],
    )

    device_changed_recently = np.random.binomial(1, 0.15)

    failed_auth_attempts = np.random.choice(
        [0, 1, 2, 3],
        p=[0.70, 0.20, 0.08, 0.02],
    )

    unusual_transaction_hour = np.random.binomial(1, 0.15)

    destination_account_age_days = np.random.randint(
        20,
        2500,
    )

    # -----------------------------
    # FRAUD BEHAVIOUR
    # -----------------------------

    if is_fraud:

        # Fraud is more likely suspicious,
        # but nothing is guaranteed.

        if np.random.rand() < 0.55:
            amount *= np.random.uniform(1.2, 2.8)

        if np.random.rand() < 0.55:
            amount_deviation += np.random.uniform(0.8, 2.5)

        if np.random.rand() < 0.55:
            new_beneficiary = 1

        if np.random.rand() < 0.60:
            txn_count_last_10min += np.random.randint(2, 6)

        if np.random.rand() < 0.65:
            receiver_unique_senders_24h += np.random.randint(
                10,
                50,
            )

        if np.random.rand() < 0.60:
            receiver_txn_velocity += np.random.uniform(
                0.15,
                0.40,
            )

        if np.random.rand() < 0.35:
            previous_fraud_reports += np.random.randint(1, 3)

        if np.random.rand() < 0.40:
            device_changed_recently = 1

        if np.random.rand() < 0.40:
            failed_auth_attempts += np.random.randint(1, 3)

        if np.random.rand() < 0.35:
            unusual_transaction_hour = 1

        if np.random.rand() < 0.50:
            destination_account_age_days = np.random.randint(
                5,
                400,
            )

    # -----------------------------
    # GENUINE BUT SUSPICIOUS-LOOKING
    # -----------------------------

    else:

        # Some legitimate users behave strangely.
        # This creates false-positive pressure.

        if np.random.rand() < 0.08:
            txn_count_last_10min += np.random.randint(2, 5)

        if np.random.rand() < 0.08:
            receiver_unique_senders_24h += np.random.randint(
                10,
                30,
            )

        if np.random.rand() < 0.05:
            device_changed_recently = 1

        if np.random.rand() < 0.05:
            unusual_transaction_hour = 1

        if np.random.rand() < 0.05:
            destination_account_age_days = np.random.randint(
                5,
                150,
            )

    # Keep within useful ranges

    amount = min(max(amount, 10), 75_000)

    receiver_txn_velocity = min(
        receiver_txn_velocity,
        1.0,
    )

    timestamp = datetime.now() - timedelta(
        days=random.randint(0, 120),
        minutes=random.randint(0, 1440),
    )

    return {
        "transaction_id": str(uuid.uuid4()),
        "timestamp": timestamp.isoformat(),
        "recipient_name": recipient["name"],
        "recipient_upi": recipient["upi_id"],
        "amount": round(amount, 2),
        "amount_deviation": round(amount_deviation, 4),
        "new_beneficiary": new_beneficiary,
        "txn_count_last_10min": txn_count_last_10min,
        "receiver_unique_senders_24h": receiver_unique_senders_24h,
        "receiver_txn_velocity": round(receiver_txn_velocity, 4),
        "previous_fraud_reports": previous_fraud_reports,
        "device_changed_recently": device_changed_recently,
        "failed_auth_attempts": failed_auth_attempts,
        "unusual_transaction_hour": unusual_transaction_hour,
        "destination_account_age_days": destination_account_age_days,
        "is_fraud": int(is_fraud),
    }


def main():

    print("Generating realistic synthetic transactions...")

    rows = [
        generate_transaction()
        for _ in range(ROWS)
    ]

    df = pd.DataFrame(rows)

    df = df.sample(
        frac=1,
        random_state=42,
    ).reset_index(drop=True)

    df.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    print("\nDataset generated.")
    print(f"Rows: {len(df)}")
    print(
        f"Fraud transactions: "
        f"{df['is_fraud'].sum()}"
    )
    print(
        f"Genuine transactions: "
        f"{(df['is_fraud'] == 0).sum()}"
    )
    print(
        f"Fraud rate: "
        f"{df['is_fraud'].mean():.2%}"
    )

    print(f"\nSaved → {OUTPUT_PATH}")


if __name__ == "__main__":
    main()