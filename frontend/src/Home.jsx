function Home({ onNavigate }) {
    return (
        <main className="home-page">

            <section className="home-hero">

                <p className="eyebrow">
                    REAL-TIME FRAUD INTELLIGENCE
                </p>

                <h1>
                    When fraud changes,
                    <br />
                    the model must change too.
                </h1>

                <p className="home-description">
                    A production-style UPI fraud detection
                    system that demonstrates model drift,
                    monitoring, retraining, validation and
                    safe model promotion.
                </p>

                <div className="home-actions">

                    <button
                        className="primary-button"
                        onClick={() =>
                            onNavigate("dashboard")
                        }
                    >
                        View MLOps Dashboard
                    </button>

                    <button
                        className="secondary-button"
                        onClick={() =>
                            onNavigate("payment")
                        }
                    >
                        Try Payment Simulator
                    </button>

                </div>

            </section>


            <section className="story-grid">

                <div className="story-card">
                    <span>01</span>

                    <h3>Model V1</h3>

                    <p>
                        We trained a fraud detection model
                        on historical transaction behaviour.
                    </p>
                </div>


                <div className="story-card">
                    <span>02</span>

                    <h3>Production Drift</h3>

                    <p>
                        A new mule-account pattern appeared
                        that Model V1 had never learned.
                    </p>
                </div>


                <div className="story-card">
                    <span>03</span>

                    <h3>Detection</h3>

                    <p>
                        Fraud recall dropped sharply,
                        triggering the degradation signal.
                    </p>
                </div>


                <div className="story-card">
                    <span>04</span>

                    <h3>Recovery</h3>

                    <p>
                        The system retrained, validated V2
                        and promoted the stronger candidate.
                    </p>
                </div>

            </section>


            <section className="about-section">

                <div>

                    <p className="eyebrow">
                        WHAT WE BUILT
                    </p>

                    <h2>
                        More than a fraud classifier.
                    </h2>

                </div>

                <div className="about-copy">

                    <p>
                        This project focuses on the complete
                        machine-learning lifecycle rather than
                        only training a high-accuracy model.
                    </p>

                    <p>
                        It demonstrates synthetic transaction
                        generation, fraud modelling, production
                        drift, model degradation, retraining,
                        candidate validation and real-time
                        FastAPI inference.
                    </p>

                </div>

            </section>


            <section className="stack-section">

                <p className="eyebrow">
                    SYSTEM
                </p>

                <div className="stack-list">
                    <span>Python</span>
                    <span>Scikit-learn</span>
                    <span>TensorFlow</span>
                    <span>FastAPI</span>
                    <span>React</span>
                    <span>MLOps</span>
                </div>

            </section>

        </main>
    );
}


export default Home;