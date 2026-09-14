import joblib
import pandas as pd

from sklearn.metrics import (
    classification_report,
    precision_score,
    recall_score,
    f1_score,
    average_precision_score,
)


MODEL_PATH = "models/model_v1.pkl"
DATA_PATH = "data/production_drift.csv"


def main():

    print("Loading Model V1...")

    bundle = joblib.load(MODEL_PATH)

    model = bundle["model"]
    features = bundle["features"]
    version = bundle["version"]

    print(f"Loaded model: {version}")

    df = pd.read_csv(DATA_PATH)

    X = df[features]
    y = df["is_fraud"]

    predictions = model.predict(X)
    probabilities = model.predict_proba(X)[:, 1]

    precision = precision_score(y, predictions)
    recall = recall_score(y, predictions)
    f1 = f1_score(y, predictions)
    pr_auc = average_precision_score(y, probabilities)

    print("\n========== PRODUCTION PERFORMANCE ==========")

    print(classification_report(y, predictions))

    print(f"Fraud Precision : {precision:.4f}")
    print(f"Fraud Recall    : {recall:.4f}")
    print(f"Fraud F1        : {f1:.4f}")
    print(f"PR-AUC          : {pr_auc:.4f}")

    print("============================================")

    # -----------------------------
    # PERFORMANCE BY FRAUD PATTERN
    # -----------------------------

    print("\n========== FRAUD PATTERN ANALYSIS ==========")

    fraud_df = df[df["is_fraud"] == 1].copy()

    fraud_df["prediction"] = predictions[df["is_fraud"] == 1]

    pattern_results = (
        fraud_df
        .groupby("fraud_pattern")["prediction"]
        .agg(["count", "sum"])
    )

    pattern_results["recall"] = (
        pattern_results["sum"]
        / pattern_results["count"]
    )

    print(pattern_results)

    print("============================================")

    # Specifically inspect emerging mule fraud

    mule_df = fraud_df[
        fraud_df["fraud_pattern"] == "new_mule_fraud"
    ]

    caught = mule_df["prediction"].sum()
    total = len(mule_df)
    missed = total - caught

    print("\nNEW MULE FRAUD")
    print(f"Total  : {total}")
    print(f"Caught : {caught}")
    print(f"Missed : {missed}")

    if total > 0:
        print(f"Recall : {caught / total:.2%}")


if __name__ == "__main__":
    main()