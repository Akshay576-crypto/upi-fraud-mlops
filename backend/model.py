import joblib
import pandas as pd


V1_PATH = "models/model_v1.pkl"
V2_PATH = "models/model_v2.pkl"


class FraudModel:

    def __init__(self, version="v2"):

        path = V1_PATH if version == "v1" else V2_PATH

        bundle = joblib.load(path)

        self.model = bundle["model"]
        self.features = bundle["features"]
        self.version = bundle["version"]
        self.model_type = bundle.get(
            "model_type",
            "random_forest",
        )
        self.metrics = bundle.get(
            "metrics",
            {},
        )

    def predict(self, transaction: dict):

        row = {}

        for feature in self.features:
            row[feature] = transaction.get(
                feature,
                0,
            )

        df = pd.DataFrame([row])

        probability = self.model.predict_proba(
            df
        )[0][1]

        if probability >= 0.70:
            decision = "BLOCK"
            risk = "HIGH"

        elif probability >= 0.35:
            decision = "REVIEW"
            risk = "MEDIUM"

        else:
            decision = "ALLOW"
            risk = "LOW"

        return {
            "fraud_probability": round(
                float(probability),
                4,
            ),
            "risk": risk,
            "decision": decision,
            "model_version": self.version,
        }

    def get_status(self):

        return {
            "model_version": self.version,
            "model_type": self.model_type,
            "metrics": self.metrics,
            "features": self.features,
        }