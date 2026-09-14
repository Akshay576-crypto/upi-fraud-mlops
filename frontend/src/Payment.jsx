import {
    useEffect,
    useState,
} from "react";


function Payment() {

    const [recipients, setRecipients] =
        useState([]);

    const [recipient, setRecipient] =
        useState("");

    const [amount, setAmount] =
        useState("");

    const [result, setResult] =
        useState(null);

    const [loading, setLoading] =
        useState(false);

    const [error, setError] =
        useState(null);


    useEffect(() => {

        async function loadRecipients() {

            try {

                const response = await fetch(
                    "http://127.0.0.1:8000/recipients"
                );

                if (!response.ok) {
                    throw new Error(
                        "Could not load recipients"
                    );
                }

                const data =
                    await response.json();

                setRecipients(data);

                if (data.length > 0) {
                    setRecipient(data[0].upi);
                }

            } catch (err) {
                setError(err.message);
            }
        }

        loadRecipients();

    }, []);


    async function handlePayment(event) {

        event.preventDefault();

        setError(null);
        setResult(null);
        setLoading(true);

        try {

            const response = await fetch(
                "http://127.0.0.1:8000/payment",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json",
                    },

                    body: JSON.stringify({
                        recipient_upi: recipient,
                        amount: Number(amount),
                    }),
                }
            );

            if (!response.ok) {
                throw new Error(
                    "Payment evaluation failed"
                );
            }

            const data =
                await response.json();

            setResult(data);

        } catch (err) {

            setError(err.message);

        } finally {

            setLoading(false);

        }
    }


    return (

        <main className="payment-page">

            <section className="payment-header">

                <p className="eyebrow">
                    LIVE MODEL INFERENCE
                </p>

                <h1>
                    Payment Simulator
                </h1>

                <p>
                    Simulate a UPI transaction and let
                    the production fraud model decide
                    whether it should be allowed,
                    reviewed or blocked.
                </p>

            </section>


            <section className="payment-layout">

                <form
                    className="payment-card"
                    onSubmit={handlePayment}
                >

                    <label>
                        Recipient

                        <select
                            value={recipient}
                            onChange={(event) =>
                                setRecipient(
                                    event.target.value
                                )
                            }
                        >
                            {recipients.map((item) => (
                                <option
                                    key={item.upi}
                                    value={item.upi}
                                >
                                    {item.name}
                                    {" — "}
                                    {item.upi}
                                </option>
                            ))}
                        </select>
                    </label>


                    <label>
                        Amount

                        <div className="amount-input">

                            <span>₹</span>

                            <input
                                type="number"
                                min="1"
                                max="100000"
                                placeholder="Enter amount"
                                value={amount}
                                onChange={(event) =>
                                    setAmount(
                                        event.target.value
                                    )
                                }
                                required
                            />

                        </div>

                    </label>


                    <button
                        className="primary-button payment-button"
                        type="submit"
                        disabled={loading}
                    >
                        {loading
                            ? "Evaluating..."
                            : "Evaluate Payment"}
                    </button>

                </form>


                <div className="result-card">

                    {!result && !error && (

                        <div className="empty-result">
                            <span>AI</span>

                            <h3>
                                Waiting for transaction
                            </h3>

                            <p>
                                Transaction risk analysis
                                will appear here.
                            </p>
                        </div>

                    )}


                    {error && (

                        <div className="payment-error">
                            {error}
                        </div>

                    )}


                    {result && (

                        <PaymentResult
                            result={result}
                        />

                    )}

                </div>

            </section>

        </main>
    );
}


function PaymentResult({ result }) {

    const probability =
        result.fraud_probability * 100;

    const decisionClass =
        result.decision.toLowerCase();


    return (

        <div
            className={
                `payment-result ${decisionClass}`
            }
        >

            <p className="card-label">
                MODEL DECISION
            </p>

            <h2>
                {result.decision}
            </h2>

            <div className="result-probability">

                <strong>
                    {probability.toFixed(2)}%
                </strong>

                <span>
                    fraud probability
                </span>

            </div>


            <div className="result-details">

                <div>
                    <span>Recipient</span>
                    <strong>
                        {result.recipient}
                    </strong>
                </div>

                <div>
                    <span>Amount</span>
                    <strong>
                        ₹{result.amount}
                    </strong>
                </div>

                <div>
                    <span>Risk</span>
                    <strong>
                        {result.risk}
                    </strong>
                </div>

                <div>
                    <span>Model</span>
                    <strong>
                        {result.model_version.toUpperCase()}
                    </strong>
                </div>

            </div>

        </div>
    );
}


export default Payment;