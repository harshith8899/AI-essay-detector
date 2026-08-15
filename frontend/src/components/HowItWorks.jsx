const PIPELINE = `Essay
  ↓
GPT-2 token probabilities
  ↓
Perplexity + burstiness

+

Stylometric features
  ↓
61 features
  ↓
Logistic Regression
  ↓
Signal + evidence`;

export default function HowItWorks() {
  return (
    <section className="methodology" id="methodology">
      <p className="section-label">Methodology</p>
      <pre className="pipeline-diagram">{PIPELINE}</pre>
      <p className="methodology-note">
        GPT-2 is used as a statistical instrument. It does not receive the essay and decide
        whether it is AI. The final classification is produced by our own feature-based model.
      </p>
    </section>
  );
}
