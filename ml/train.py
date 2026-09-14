import os
import joblib
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    classification_report,
    precision_score,
    recall_score,
    f1_score,
    average_precision_score,
)


DATA_PATH = "data/transactions.csv"
MODEL_PATH = "models/model_v1.pkl"

FEATURES = [
    "amount",
    "amount_deviation",
    "new_beneficiary",
    "txn_count_last_10min",
    "receiver_unique_senders_24h",
    "receiver_txn_velocity",
    "previous_fraud_reports",
    "device_changed_recently",
    "failed_auth_attempts",
    "unusual_transaction_hour",
    "destination_account_age_days",
]

TARGET = "is_fraud"


def load_data():

    df = pd.read_csv(DATA_PATH)

    print(f"Dataset loaded: {len(df)} transactions")
    print(f"Fraud rate: {df[TARGET].mean():.2%}")

    return df


def train_model(df):

    X = df[FEATURES]
    y = df[TARGET]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42,
        stratify=y,
    )

    print(f"\nTraining rows: {len(X_train)}")
    print(f"Testing rows: {len(X_test)}")

    model = RandomForestClassifier(
        n_estimators=150,
        max_depth=10,
        min_samples_leaf=3,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1,
    )

    print("\nTraining Model V1...")

    model.fit(
        X_train,
        y_train,
    )

    return model, X_test, y_test


def evaluate_model(
    model,
    X_test,
    y_test,
):

    predictions = model.predict(
        X_test
    )

    probabilities = model.predict_proba(
        X_test
    )[:, 1]

    precision = precision_score(
        y_test,
        predictions,
    )

    recall = recall_score(
        y_test,
        predictions,
    )

    f1 = f1_score(
        y_test,
        predictions,
    )

    pr_auc = average_precision_score(
        y_test,
        probabilities,
    )

    print("\n========== MODEL V1 ==========")

    print(
        classification_report(
            y_test,
            predictions,
        )
    )

    print(f"Fraud Precision : {precision:.4f}")
    print(f"Fraud Recall    : {recall:.4f}")
    print(f"Fraud F1        : {f1:.4f}")
    print(f"PR-AUC          : {pr_auc:.4f}")

    print("==============================")

    return {
        "precision": float(precision),
        "recall": float(recall),
        "f1": float(f1),
        "pr_auc": float(pr_auc),
    }


def save_model(
    model,
    metrics,
):

    os.makedirs(
        "models",
        exist_ok=True,
    )

    joblib.dump(
        {
            "model": model,
            "features": FEATURES,
            "version": "v1",
            "model_type": "random_forest",
            "metrics": metrics,
        },
        MODEL_PATH,
    )

    print(
        f"\nModel V1 saved → {MODEL_PATH}"
    )


def main():

    df = load_data()

    model, X_test, y_test = train_model(
        df
    )

    metrics = evaluate_model(
        model,
        X_test,
        y_test,
    )

    save_model(
        model,
        metrics,
    )


if __name__ == "__main__":
    main()