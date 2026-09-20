from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from backend.model import FraudModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="UPI Fraud Detection API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:4173",
        "http://upi-fraud-mlops.s3-website.eu-north-1.amazonaws.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

fraud_model = FraudModel(
    version="v2"
)


RECIPIENTS = {
    "rahul@demo": {
        "recipient_name": "Rahul",
        "amount_deviation": 0.3,
        "new_beneficiary": 0,
        "txn_count_last_10min": 0,
        "receiver_unique_senders_24h": 5,
        "receiver_txn_velocity": 0.15,
        "previous_fraud_reports": 0,
        "device_changed_recently": 0,
        "failed_auth_attempts": 0,
        "unusual_transaction_hour": 0,
        "destination_account_age_days": 1400,
        "receiver_outflow_ratio": 0.18,
    },

    "neha@demo": {
        "recipient_name": "Neha",
        "amount_deviation": 0.6,
        "new_beneficiary": 0,
        "txn_count_last_10min": 1,
        "receiver_unique_senders_24h": 7,
        "receiver_txn_velocity": 0.20,
        "previous_fraud_reports": 0,
        "device_changed_recently": 0,
        "failed_auth_attempts": 0,
        "unusual_transaction_hour": 0,
        "destination_account_age_days": 900,
        "receiver_outflow_ratio": 0.25,
    },

    "quickcash@demo": {
        "recipient_name": "QuickCash",
        "amount_deviation": 2.8,
        "new_beneficiary": 1,
        "txn_count_last_10min": 7,
        "receiver_unique_senders_24h": 85,
        "receiver_txn_velocity": 0.88,
        "previous_fraud_reports": 3,
        "device_changed_recently": 1,
        "failed_auth_attempts": 3,
        "unusual_transaction_hour": 1,
        "destination_account_age_days": 20,
        "receiver_outflow_ratio": 0.82,
    },

    "rewarddesk@demo": {
        "recipient_name": "RewardDesk",
        "amount_deviation": 0.8,
        "new_beneficiary": 0,
        "txn_count_last_10min": 1,
        "receiver_unique_senders_24h": 12,
        "receiver_txn_velocity": 0.30,
        "previous_fraud_reports": 0,
        "device_changed_recently": 0,
        "failed_auth_attempts": 0,
        "unusual_transaction_hour": 0,
        "destination_account_age_days": 700,
        "receiver_outflow_ratio": 0.94,
    },
}


class PaymentRequest(BaseModel):
    recipient_upi: str
    amount: float = Field(
        gt=0,
        le=100000,
    )


@app.get("/")
def root():

    return {
        "service": "UPI Fraud Detection API",
        "status": "running",
        "active_model": fraud_model.version,
    }


@app.get("/status")
def model_status():

    return fraud_model.get_status()


@app.get("/recipients")
def get_recipients():

    return [
        {
            "name": profile["recipient_name"],
            "upi": upi,
        }
        for upi, profile in RECIPIENTS.items()
    ]


@app.post("/payment")
def process_payment(
    payment: PaymentRequest,
):

    recipient = RECIPIENTS.get(
        payment.recipient_upi
    )

    if not recipient:
        raise HTTPException(
            status_code=404,
            detail="Recipient not found",
        )

    transaction = {
        "amount": payment.amount,
        "amount_deviation": recipient["amount_deviation"],
        "new_beneficiary": recipient["new_beneficiary"],
        "txn_count_last_10min": recipient["txn_count_last_10min"],
        "receiver_unique_senders_24h": recipient[
            "receiver_unique_senders_24h"
        ],
        "receiver_txn_velocity": recipient[
            "receiver_txn_velocity"
        ],
        "previous_fraud_reports": recipient[
            "previous_fraud_reports"
        ],
        "device_changed_recently": recipient[
            "device_changed_recently"
        ],
        "failed_auth_attempts": recipient[
            "failed_auth_attempts"
        ],
        "unusual_transaction_hour": recipient[
            "unusual_transaction_hour"
        ],
        "destination_account_age_days": recipient[
            "destination_account_age_days"
        ],
        "receiver_outflow_ratio": recipient[
            "receiver_outflow_ratio"
        ],
    }

    prediction = fraud_model.predict(
        transaction
    )

    return {
        "recipient": recipient[
            "recipient_name"
        ],
        "recipient_upi": payment.recipient_upi,
        "amount": payment.amount,
        **prediction,
    }