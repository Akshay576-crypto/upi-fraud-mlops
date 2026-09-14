import random
import uuid
from datetime import datetime, timedelta

import numpy as np
import pandas as pd


ROWS = 4000
OUTPUT_PATH = "data/production_drift.csv"

random.seed(99)
np.random.seed(99)


RECIPIENTS = [
    {"name": "Rahul", "upi_id": "rahul@demo"},
    {"name": "Neha", "upi_id": "neha@demo"},
    {"name": "QuickCash", "upi_id": "quickcash@demo"},
    {"name": "RewardDesk", "upi_id": "rewarddesk@demo"},
]


def generate_genuine(recipient):
    amount = min(
        np.random.lognormal(mean=7.2, sigma=0.8),
        40000,
    )

    return {
        "amount": round(amount, 2),
        "amount_deviation": round(np.random.uniform(0.2, 2.2), 4),
        "new_beneficiary": np.random.binomial(1, 0.20),
        "txn_count_last_10min": np.random.poisson(1.2),
        "receiver_unique_senders_24h": np.random.randint(1, 25),
        "receiver_txn_velocity": round(np.random.uniform(0.05, 0.55), 4),
        "previous_fraud_reports": np.random.choice(
            [0, 1],
            p=[0.96, 0.04],
        ),
        "device_changed_recently": np.random.binomial(1, 0.10),
        "failed_auth_attempts": np.random.choice(
            [0, 1],
            p=[0.85, 0.15],
        ),
        "unusual_transaction_hour": np.random.binomial(1, 0.10),
        "destination_account_age_days": np.random.randint(100, 2500),
        "is_fraud": 0,
    }


def generate_old_style_fraud(recipient):
    amount = np.random.uniform(8000, 45000)

    return {
        "amount": round(amount, 2),
        "amount_deviation": round(np.random.uniform(2.0, 5.5), 4),
        "new_beneficiary": np.random.binomial(1, 0.75),
        "txn_count_last_10min": np.random.randint(3, 8),
        "receiver_unique_senders_24h": np.random.randint(20, 80),
        "receiver_txn_velocity": round(np.random.uniform(0.65, 1.0), 4),
        "previous_fraud_reports": np.random.randint(1, 5),
        "device_changed_recently": np.random.binomial(1, 0.55),
        "failed_auth_attempts": np.random.randint(1, 4),
        "unusual_transaction_hour": np.random.binomial(1, 0.55),
        "destination_account_age_days": np.random.randint(5, 250),
        "is_fraud": 1,
    }


def generate_new_mule_fraud(recipient):

    # New fraud pattern:
    # Looks legitimate according to V1's existing features,
    # but rapidly transfers received funds elsewhere.

    return {
        "amount": round(
            np.random.uniform(700, 3500),
            2,
        ),

        "amount_deviation": round(
            np.random.uniform(0.3, 1.5),
            4,
        ),

        "new_beneficiary": np.random.binomial(
            1,
            0.15,
        ),

        "txn_count_last_10min": np.random.randint(
            0,
            2,
        ),

        "receiver_unique_senders_24h": np.random.randint(
            5,
            25,
        ),

        "receiver_txn_velocity": round(
            np.random.uniform(0.10, 0.50),
            4,
        ),

        "previous_fraud_reports": 0,

        "device_changed_recently": np.random.binomial(
            1,
            0.05,
        ),

        "failed_auth_attempts": 0,

        "unusual_transaction_hour": np.random.binomial(
            1,
            0.08,
        ),

        "destination_account_age_days": np.random.randint(
            300,
            1800,
        ),

        # NEW FEATURE
        # Model V1 has never seen this feature.
        "receiver_outflow_ratio": round(
            np.random.uniform(0.85, 1.0),
            4,
        ),

        "is_fraud": 1,
    }


def generate_transaction():
    recipient = random.choices(
        RECIPIENTS,
        weights=[30, 30, 15, 25],
        k=1,
    )[0]

    # Production population:
    # 88% genuine
    # 4% old fraud
    # 8% NEW mule fraud

    sample = np.random.rand()

    if sample < 0.88:
        features = generate_genuine(recipient)
        fraud_pattern = "genuine"

    elif sample < 0.92:
        features = generate_old_style_fraud(recipient)
        fraud_pattern = "old_fraud"

    else:
        features = generate_new_mule_fraud(recipient)
        fraud_pattern = "new_mule_fraud"

        # Most emerging fraud is concentrated around RewardDesk
        if np.random.rand() < 0.75:
            recipient = {
                "name": "RewardDesk",
                "upi_id": "rewarddesk@demo",
            }

    timestamp = datetime.now() - timedelta(
        hours=random.randint(0, 72),
        minutes=random.randint(0, 59),
    )

    return {
        "transaction_id": str(uuid.uuid4()),
        "timestamp": timestamp.isoformat(),
        "recipient_name": recipient["name"],
        "recipient_upi": recipient["upi_id"],
        **features,
        "fraud_pattern": fraud_pattern,
    }


def main():
    print("Generating production drift dataset...")

    rows = [
        generate_transaction()
        for _ in range(ROWS)
    ]

    df = pd.DataFrame(rows)

    df = df.sample(
        frac=1,
        random_state=99,
    ).reset_index(drop=True)

    df.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    print("\nProduction drift dataset created.")
    print(f"Rows: {len(df)}")
    print(f"Fraud rate: {df['is_fraud'].mean():.2%}")

    print("\nPattern distribution:")
    print(df["fraud_pattern"].value_counts())

    print(f"\nSaved → {OUTPUT_PATH}")


if __name__ == "__main__":
    main()