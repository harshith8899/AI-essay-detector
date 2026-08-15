const FEATURE_META = {
  perplexity: { label: "Perplexity", tag: "LM" },
  burstiness: { label: "Rhythm variation", tag: "LM" },
  cliche: { label: "Cliché phrase", tag: "PHRASE" },
  transition_opener: { label: "Transition opener", tag: "PHRASE" },
  sentence_length: { label: "Sentence rhythm", tag: "STYLE" },
};

export default function EvidencePanel({ sentence }) {
  if (!sentence) {
    return (
      <div className="evidence-panel evidence-panel-empty">
        <p className="panel-hint">Click a sentence to see its evidence here.</p>
      </div>
    );
  }

  return (
    <div className="evidence-panel">
      <div className="evidence-score">
        <span className="section-label">Sentence signal</span>
        <span className="evidence-score-value">{sentence.score.toFixed(0)} / 100</span>
      </div>

      <p className="evidence-heading">Why this sentence received this signal</p>

      <ul className="evidence-list">
        {sentence.top_features.map((feature, i) => {
          const meta = FEATURE_META[feature.name] || { label: feature.name, tag: "" };
          return (
            <li key={i} className="evidence-item">
              <div className="evidence-item-header">
                <span className="evidence-item-tag">{meta.tag}</span>
                <span className="evidence-item-name">{meta.label}</span>
              </div>
              <p className="evidence-item-note">{feature.plain_language_note}</p>
            </li>
          );
        })}
      </ul>

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
          <div>
            <dt>Primary LM signals</dt>
            <dd>perplexity, burstiness</dd>
          </div>
          <div>
            <dt>Stylometric signals</dt>
            <dd>sentence length, TTR, hapax rate, POS entropy, function words, phrase signals</dd>
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
                <td>{feature.name}</td>
                <td>{feature.contribution.toFixed(4)}</td>
              </tr>
            ))}
            <tr>
              <td>raw perplexity</td>
              <td>
                {sentence.perplexity !== null && sentence.perplexity !== undefined
                  ? sentence.perplexity.toFixed(2)
                  : "n/a"}
              </td>
            </tr>
          </tbody>
        </table>
      </details>
    </div>
  );
}
