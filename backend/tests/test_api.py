from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")

    assert response.status_code == 200

    data = response.json()

    assert data["service"] == "UPI Fraud Detection API"
    assert data["status"] == "running"
    assert data["active_model"] == "v2"


def test_model_status():
    response = client.get("/status")

    assert response.status_code == 200

    data = response.json()

    assert data["model_version"] == "v2"
    assert "model_type" in data
    assert "metrics" in data
    assert "features" in data


def test_recipients_endpoint():
    response = client.get("/recipients")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) == 4

    upis = {
        recipient["upi"]
        for recipient in data
    }

    assert "rahul@demo" in upis
    assert "neha@demo" in upis
    assert "quickcash@demo" in upis
    assert "rewarddesk@demo" in upis


def test_valid_payment_returns_prediction():
    response = client.post(
        "/payment",
        json={
            "recipient_upi": "rahul@demo",
            "amount": 850,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["recipient"] == "Rahul"
    assert data["recipient_upi"] == "rahul@demo"
    assert data["amount"] == 850

    assert "fraud_probability" in data
    assert "risk" in data
    assert "decision" in data
    assert data["model_version"] == "v2"

    assert 0 <= data["fraud_probability"] <= 1
    assert data["risk"] in {
        "LOW",
        "MEDIUM",
        "HIGH",
    }
    assert data["decision"] in {
        "ALLOW",
        "REVIEW",
        "BLOCK",
    }


def test_unknown_recipient_returns_404():
    response = client.post(
        "/payment",
        json={
            "recipient_upi": "unknown@demo",
            "amount": 1000,
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Recipient not found"


def test_zero_amount_is_rejected():
    response = client.post(
        "/payment",
        json={
            "recipient_upi": "rahul@demo",
            "amount": 0,
        },
    )

    assert response.status_code == 422


def test_negative_amount_is_rejected():
    response = client.post(
        "/payment",
        json={
            "recipient_upi": "rahul@demo",
            "amount": -500,
        },
    )

    assert response.status_code == 422


def test_amount_above_limit_is_rejected():
    response = client.post(
        "/payment",
        json={
            "recipient_upi": "rahul@demo",
            "amount": 100001,
        },
    )

    assert response.status_code == 422