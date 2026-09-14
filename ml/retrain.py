import os
import joblib
import numpy as np
import pandas as pd
import tensorflow as tf

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
    average_precision_score,
)


HISTORICAL_PATH = "data/transactions.csv"
PRODUCTION_PATH = "data/production_drift.csv"

V2_PATH = "models/model_v2.pkl"

RANDOM_STATE = 42

np.random.seed(RANDOM_STATE)
tf.random.set_seed(RANDOM_STATE)


FEATURES_V2 = [
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
    "receiver_outflow_ratio",
]

TARGET = "is_fraud"


def calculate_metrics(y_true, predictions, probabilities):

    return {
        "precision": precision_score(
            y_true,
            predictions,
            zero_division=0,
        ),
        "recall": recall_score(
            y_true,
            predictions,
            zero_division=0,
        ),
        "f1": f1_score(
            y_true,
            predictions,
            zero_division=0,
        ),
        "pr_auc": average_precision_score(
            y_true,
            probabilities,
        ),
    }


def print_metrics(name, metrics):

    print(f"\n========== {name} ==========")

    for metric, value in metrics.items():
        print(f"{metric.upper():10}: {value:.4f}")

    print("=" * 35)


def load_and_split_data():

    historical = pd.read_csv(HISTORICAL_PATH)
    production = pd.read_csv(PRODUCTION_PATH)

    # V1-era historical data did not contain this feature.
    historical["receiver_outflow_ratio"] = 0.30

    # IMPORTANT:
    # Split production BEFORE using any of it for retraining.
    production_train, production_holdout = train_test_split(
        production,
        test_size=0.30,
        random_state=RANDOM_STATE,
        stratify=production["fraud_pattern"],
    )

    retraining_data = pd.concat(
        [
            historical,
            production_train,
        ],
        ignore_index=True,
    )

    print("\n========== DATA SPLIT ==========")

    print(f"Historical rows          : {len(historical)}")
    print(f"Production total         : {len(production)}")
    print(f"Production retrain rows  : {len(production_train)}")
    print(f"Production holdout rows  : {len(production_holdout)}")
    print(f"Combined retrain rows    : {len(retraining_data)}")

    print("\nHoldout pattern distribution:")
    print(
        production_holdout[
            "fraud_pattern"
        ].value_counts()
    )

    print("================================")

    return retraining_data, production_holdout


def split_retraining_data(retraining_data):

    X = retraining_data[FEATURES_V2]
    y = retraining_data[TARGET]

    return train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=RANDOM_STATE,
        stratify=y,
    )


def train_random_forest(
    X_train,
    y_train,
    X_validation,
    y_validation,
):

    print("\nTraining Random Forest candidate...")

    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=12,
        min_samples_leaf=3,
        class_weight="balanced",
        random_state=RANDOM_STATE,
        n_jobs=-1,
    )

    model.fit(
        X_train,
        y_train,
    )

    predictions = model.predict(
        X_validation
    )

    probabilities = model.predict_proba(
        X_validation
    )[:, 1]

    metrics = calculate_metrics(
        y_validation,
        predictions,
        probabilities,
    )

    return model, metrics


def train_tensorflow(
    X_train,
    y_train,
    X_validation,
    y_validation,
):

    print("\nTraining TensorFlow candidate...")

    scaler = StandardScaler()

    X_train_scaled = scaler.fit_transform(
        X_train
    )

    X_validation_scaled = scaler.transform(
        X_validation
    )

    model = tf.keras.Sequential([
        tf.keras.layers.Input(
            shape=(len(FEATURES_V2),)
        ),
        tf.keras.layers.Dense(
            64,
            activation="relu",
        ),
        tf.keras.layers.Dropout(0.20),
        tf.keras.layers.Dense(
            32,
            activation="relu",
        ),
        tf.keras.layers.Dense(
            1,
            activation="sigmoid",
        ),
    ])

    model.compile(
        optimizer=tf.keras.optimizers.Adam(
            learning_rate=0.001
        ),
        loss="binary_crossentropy",
    )

    negative = np.sum(y_train == 0)
    positive = np.sum(y_train == 1)

    class_weight = {
        0: 1.0,
        1: negative / positive,
    }

    model.fit(
        X_train_scaled,
        y_train,
        validation_data=(
            X_validation_scaled,
            y_validation,
        ),
        epochs=15,
        batch_size=128,
        class_weight=class_weight,
        verbose=1,
    )

    probabilities = model.predict(
        X_validation_scaled,
        verbose=0,
    ).ravel()

    predictions = (
        probabilities >= 0.5
    ).astype(int)

    metrics = calculate_metrics(
        y_validation,
        predictions,
        probabilities,
    )

    return model, scaler, metrics


def evaluate_holdout(
    model,
    holdout,
    model_type,
    scaler=None,
):

    X_holdout = holdout[FEATURES_V2]
    y_holdout = holdout[TARGET]

    if model_type == "tensorflow":

        X_holdout = scaler.transform(
            X_holdout
        )

        probabilities = model.predict(
            X_holdout,
            verbose=0,
        ).ravel()

        predictions = (
            probabilities >= 0.5
        ).astype(int)

    else:

        probabilities = model.predict_proba(
            X_holdout
        )[:, 1]

        predictions = model.predict(
            X_holdout
        )

    metrics = calculate_metrics(
        y_holdout,
        predictions,
        probabilities,
    )

    # Pattern-specific recall
    result = holdout.copy()

    result["prediction"] = predictions

    fraud_only = result[
        result[TARGET] == 1
    ]

    pattern_recall = (
        fraud_only
        .groupby("fraud_pattern")["prediction"]
        .mean()
    )

    return metrics, pattern_recall


def save_random_forest(
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
            "features": FEATURES_V2,
            "version": "v2",
            "model_type": "random_forest",
            "metrics": metrics,
        },
        V2_PATH,
    )


def save_tensorflow(
    model,
    scaler,
    metrics,
):

    os.makedirs(
        "models",
        exist_ok=True,
    )

    keras_path = "models/model_v2.keras"

    model.save(
        keras_path
    )

    joblib.dump(
        {
            "features": FEATURES_V2,
            "version": "v2",
            "model_type": "tensorflow",
            "scaler": scaler,
            "model_path": keras_path,
            "metrics": metrics,
        },
        V2_PATH,
    )


def main():

    retraining_data, production_holdout = (
        load_and_split_data()
    )

    (
        X_train,
        X_validation,
        y_train,
        y_validation,
    ) = split_retraining_data(
        retraining_data
    )

    # -----------------------------
    # RANDOM FOREST
    # -----------------------------

    rf_model, rf_validation_metrics = (
        train_random_forest(
            X_train,
            y_train,
            X_validation,
            y_validation,
        )
    )

    print_metrics(
        "RF VALIDATION",
        rf_validation_metrics,
    )

    # -----------------------------
    # TENSORFLOW
    # -----------------------------

    (
        tf_model,
        scaler,
        tf_validation_metrics,
    ) = train_tensorflow(
        X_train,
        y_train,
        X_validation,
        y_validation,
    )

    print_metrics(
        "TF VALIDATION",
        tf_validation_metrics,
    )

    # -----------------------------
    # CANDIDATE SELECTION
    # -----------------------------

    if (
        tf_validation_metrics["f1"]
        > rf_validation_metrics["f1"]
    ):

        winner_name = "TensorFlow"
        winner_model = tf_model
        winner_scaler = scaler
        winner_type = "tensorflow"

    else:

        winner_name = "RandomForest"
        winner_model = rf_model
        winner_scaler = None
        winner_type = "random_forest"

    print(
        f"\nBest validation candidate: "
        f"{winner_name}"
    )

    # -----------------------------
    # TRUE PRODUCTION HOLDOUT TEST
    # -----------------------------

    holdout_metrics, pattern_recall = (
        evaluate_holdout(
            winner_model,
            production_holdout,
            winner_type,
            winner_scaler,
        )
    )

    print_metrics(
        "UNSEEN PRODUCTION HOLDOUT",
        holdout_metrics,
    )

    print(
        "\n========== HOLDOUT FRAUD PATTERNS =========="
    )

    print(pattern_recall)

    print(
        "============================================"
    )

    mule_recall = pattern_recall.get(
        "new_mule_fraud",
        0,
    )

    # -----------------------------
    # VALIDATION GATE
    # -----------------------------

    MIN_RECALL = 0.80
    MIN_F1 = 0.80
    MIN_MULE_RECALL = 0.80

    passes_gate = (
        holdout_metrics["recall"] >= MIN_RECALL
        and holdout_metrics["f1"] >= MIN_F1
        and mule_recall >= MIN_MULE_RECALL
    )

    if not passes_gate:

        print(
            "\n❌ Candidate failed production "
            "holdout validation."
        )

        print(
            "Model V1 remains production model."
        )

        return

    if winner_type == "random_forest":

        save_random_forest(
            winner_model,
            holdout_metrics,
        )

    else:

        save_tensorflow(
            winner_model,
            winner_scaler,
            holdout_metrics,
        )

    print(
        "\n Candidate passed unseen "
        "production validation."
    )

    print(
        f"Promoted Model V2 → {winner_name}"
    )

    print(
        f"Saved → {V2_PATH}"
    )


if __name__ == "__main__":
    main()