import { useEffect, useState } from "react";


function Dashboard() {

    const [status, setStatus] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);


    useEffect(() => {

        async function loadModelStatus() {

            try {

                const response = await fetch(
                    "http://127.0.0.1:8000/status"
                );

                if (!response.ok) {
                    throw new Error(
                        "Could not load model status"
                    );
                }

                const data = await response.json();

                setStatus(data);

            } catch (err) {

                setError(err.message);

            } finally {

                setLoading(false);

            }
        }

        loadModelStatus();

    }, []);


    if (loading) {
        return (
            <div className="state-message">
                Loading production model...
            </div>
        );
    }


    if (error) {
        return (
            <div className="state-message error">
                {error}
            </div>
        );
    }


    const metrics = status.metrics;


    return (

        <main className="dashboard">

            <section className="hero">

                <div>
                    <p className="eyebrow">
                        PRODUCTION MONITORING
                    </p>

                    <h1>
                        UPI Fraud Detection
                    </h1>

                    <p className="hero-description">
                        Real-time fraud detection with
                        model monitoring, drift detection
                        and automated retraining.
                    </p>
                </div>

                <div className="production-status">
                    <span className="status-dot"></span>
                    Production Healthy
                </div>

            </section>


            <section className="model-card">

                <div>
                    <p className="card-label">
                        ACTIVE MODEL
                    </p>

                    <h2>
                        Model {status.model_version.toUpperCase()}
                    </h2>

                    <p className="model-type">
                        {status.model_type.replace("_", " ")}
                    </p>
                </div>

                <div className="model-badge">
                    PRODUCTION
                </div>

            </section>


            <section className="metrics-grid">

                <MetricCard
                    label="Precision"
                    value={metrics.precision}
                />

                <MetricCard
                    label="Recall"
                    value={metrics.recall}
                />

                <MetricCard
                    label="F1 Score"
                    value={metrics.f1}
                />

                <MetricCard
                    label="PR-AUC"
                    value={metrics.pr_auc}
                />

            </section>


            <section className="lifecycle-card">

                <div className="section-heading">

                    <div>
                        <p className="card-label">
                            MODEL LIFECYCLE
                        </p>

                        <h2>
                            Production Recovery
                        </h2>
                    </div>

                </div>


                <div className="timeline">

                    <TimelineItem
                        version="V1"
                        title="Baseline"
                        value="88.47%"
                        description="Historical fraud recall"
                    />

                    <TimelineArrow />

                    <TimelineItem
                        version="DRIFT"
                        title="Degraded"
                        value="37.21%"
                        description="Production fraud recall"
                        danger
                    />

                    <TimelineArrow />

                    <TimelineItem
                        version="V2"
                        title="Recovered"
                        value={`${(
                            metrics.recall * 100
                        ).toFixed(2)}%`}
                        description="Holdout fraud recall"
                        success
                    />

                </div>

            </section>

        </main>
    );
}


function MetricCard({
    label,
    value,
}) {

    return (

        <div className="metric-card">

            <p>{label}</p>

            <strong>
                {(value * 100).toFixed(2)}%
            </strong>

        </div>

    );
}


function TimelineItem({
    version,
    title,
    value,
    description,
    danger,
    success,
}) {

    let className = "timeline-item";

    if (danger) {
        className += " danger";
    }

    if (success) {
        className += " success";
    }


    return (

        <div className={className}>

            <span className="timeline-version">
                {version}
            </span>

            <h3>{title}</h3>

            <strong>{value}</strong>

            <p>{description}</p>

        </div>

    );
}


function TimelineArrow() {

    return (
        <div className="timeline-arrow">
            →
        </div>
    );
}


export default Dashboard;