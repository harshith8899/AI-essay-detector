const FEATURE_LABELS = {
  perplexity: "Perplexity",
  burstiness: "Rhythm variation",
  cliche: "Cliché phrase",
  transition_opener: "Transition opener",
  sentence_length: "Sentence rhythm",
};

export default function EvidencePanel({ sentence }) {
  if (!sentence) {
    return (
      <div className="evidence-panel evidence-panel-empty">
        <p className="panel-hint">Click a sentence to see its evidence here.</p>
      </div>
    );
  }

  const topFeature = sentence.top_features[0];

  return (
    <div className="evidence-panel">
      <div className="evidence-score">
        <span className="section-label">Sentence signal</span>
        <span className="evidence-score-value">{sentence.score.toFixed(0)} / 100</span>
      </div>

      <p className="evidence-heading">Why this sentence</p>

      <div className="evidence-row">
        <span className="evidence-row-label">Perplexity</span>
        <span className="evidence-row-value">
          {sentence.perplexity !== null && sentence.perplexity !== undefined
            ? sentence.perplexity.toFixed(1)
            : "n/a"}
        </span>
      </div>

      {topFeature && (
        <div className="evidence-top-feature">
          <p className="evidence-item-name">{FEATURE_LABELS[topFeature.name] || topFeature.name}</p>
          <p className="evidence-item-note">{topFeature.plain_language_note}</p>
        </div>
      )}

      <details className="technical-details">
        <summary>Technical details</summary>

        <dl className="technical-model-info">
          <div>
            <dt>Model</dt>
            <dd>Logistic Regression</dd>
          </div>
          <div>
            <dt>Feature count</dt>
            <dd>61</dd>
          </div>
          <div>
            <dt>Language model instrument</dt>
            <dd>GPT-2</dd>
          </div>
        </dl>

        <p className="technical-disclosure">
          Sentence-level signals are explanatory estimates derived from sentence-local
          measurements. They are not independently trained sentence-level probabilities or
          proof of authorship — the classifier itself only ever sees whole-essay statistics;
          this sentence score approximates its reasoning by reusing the model's learned
          feature weights against this sentence's own local values, then scaling relative to
          the other sentences in this essay.
        </p>

        <table className="technical-table">
          <tbody>
            {sentence.top_features.map((feature, i) => (
              <tr key={i}>
                <td>{FEATURE_LABELS[feature.name] || feature.name}</td>
                <td>{feature.contribution.toFixed(4)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </details>
    </div>
  );
}
