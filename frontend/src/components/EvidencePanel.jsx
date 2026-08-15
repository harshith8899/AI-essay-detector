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
      <aside className="evidence-panel evidence-panel-empty">
        <h2 className="panel-title">Why did this sentence receive this signal?</h2>
        <p className="panel-hint">Click a sentence in the essay to see its evidence here.</p>
      </aside>
    );
  }

  return (
    <aside className="evidence-panel">
      <h2 className="panel-title">Why did this sentence receive this signal?</h2>

      <div className="evidence-score">
        <span className="evidence-score-label">Sentence signal</span>
        <span className="evidence-score-value">{sentence.score.toFixed(0)} / 100</span>
      </div>

      <ul className="evidence-list">
        {sentence.top_features.map((feature, i) => (
          <li key={i} className="evidence-item">
            <span className="evidence-item-name">{FEATURE_LABELS[feature.name] || feature.name}</span>
            <p className="evidence-item-note">{feature.plain_language_note}</p>
          </li>
        ))}
      </ul>

      <details className="technical-details">
        <summary>Technical details</summary>
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
                <td>{feature.name}</td>
                <td>{feature.contribution.toFixed(4)}</td>
              </tr>
            ))}
            <tr>
              <td>raw perplexity</td>
              <td>{sentence.perplexity !== null && sentence.perplexity !== undefined ? sentence.perplexity.toFixed(2) : "n/a"}</td>
            </tr>
          </tbody>
        </table>
      </details>
    </aside>
  );
}
