// All values here are derived client-side from the sentence-level data the
// API already returns (perplexity, text, top_features) — no new backend
// data, no invented metrics. mean/burstiness use the same population
// standard deviation convention documented in backend/app/lm_features.py.

function mean(values) {
  return values.reduce((sum, v) => sum + v, 0) / values.length;
}

function populationStdev(values) {
  const m = mean(values);
  const variance = mean(values.map((v) => (v - m) ** 2));
  return Math.sqrt(variance);
}

function wordCount(text) {
  const trimmed = text.trim();
  return trimmed ? trimmed.split(/\s+/).length : 0;
}

function computeKeyMetrics(sentences) {
  const perplexities = sentences.map((s) => s.perplexity).filter((v) => v !== null && v !== undefined);
  const meanPerplexity = perplexities.length ? mean(perplexities) : null;
  const burstiness = perplexities.length > 1 ? populationStdev(perplexities) : 0;

  const lengths = sentences.map((s) => wordCount(s.text));
  const lengthMean = lengths.length ? mean(lengths) : 0;
  const lengthStdev = lengths.length > 1 ? populationStdev(lengths) : 0;
  const coefficientOfVariation = lengthMean > 0 ? lengthStdev / lengthMean : 0;
  let sentenceVariation = "Low";
  if (coefficientOfVariation > 0.5) sentenceVariation = "High";
  else if (coefficientOfVariation > 0.25) sentenceVariation = "Moderate";

  const clicheSignals = sentences.filter((s) =>
    s.top_features.some((f) => f.name === "cliche" && f.plain_language_note.startsWith("Contains a phrase"))
  ).length;

  return { meanPerplexity, burstiness, sentenceVariation, clicheSignals };
}

const METRICS = [
  {
    key: "meanPerplexity",
    label: "Mean perplexity",
    description: "How predictable the wording is to the language model. Lower means more predictable.",
    format: (v) => (v === null ? "n/a" : v.toFixed(1)),
  },
  {
    key: "burstiness",
    label: "Burstiness",
    description: "How much sentence-level predictability varies across the essay.",
    format: (v) => v.toFixed(1),
  },
  {
    key: "sentenceVariation",
    label: "Sentence variation",
    description: "How much sentence length varies across the essay, estimated from word counts.",
    format: (v) => v,
  },
  {
    key: "clicheSignals",
    label: "Cliché signals",
    description: "Number of sentences containing a phrase from the detector's curated cliché list.",
    format: (v) => String(v),
  },
];

export default function KeyMetrics({ sentences }) {
  const values = computeKeyMetrics(sentences);

  return (
    <div className="key-metrics">
      {METRICS.map((metric) => (
        <div key={metric.key} className="key-metric">
          <div className="key-metric-label-row">
            <span className="key-metric-label">{metric.label}</span>
            <button
              type="button"
              className="key-metric-info"
              aria-label={`${metric.label}: ${metric.description}`}
            >
              ?
              <span className="key-metric-tooltip" role="tooltip">
                {metric.description}
              </span>
            </button>
          </div>
          <span className="key-metric-value">{metric.format(values[metric.key])}</span>
        </div>
      ))}
    </div>
  );
}
