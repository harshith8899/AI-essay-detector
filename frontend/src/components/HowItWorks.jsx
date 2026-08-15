const PIPELINE = `Essay
  ↓
GPT-2 token probabilities
  ↓
Perplexity + burstiness

+

Stylometric analysis
  ↓
61 measurable features
  ↓
Logistic Regression
  ↓
Evidence + signal`;

export default function HowItWorks() {
  return (
    <section className="how-it-works" id="how-it-works">
      <h2 className="panel-title">How it works</h2>
      <pre className="pipeline-diagram">{PIPELINE}</pre>
      <p className="how-it-works-explainer">
        The language model is used as a statistical instrument. It does not receive the essay
        and decide whether it is AI. The final classification is produced by our own
        feature-based model.
      </p>
    </section>
  );
}
