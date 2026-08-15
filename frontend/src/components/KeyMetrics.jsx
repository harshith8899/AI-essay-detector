import { computeKeyMetrics } from "../metrics.js";

const VARIATION_PERCENT = { Low: 20, Moderate: 55, High: 90 };

const METRICS = [
  {
    key: "meanPerplexity",
    label: "Mean perplexity",
    note: "How predictable the wording is to the language model.",
    value: (v) => (v.meanPerplexity === null ? "n/a" : v.meanPerplexity.toFixed(1)),
    percent: (v) => (v.meanPerplexity === null ? 0 : Math.min(100, (v.meanPerplexity / 120) * 100)),
  },
  {
    key: "burstiness",
    label: "Burstiness",
    note: "How much sentence-level predictability varies across the essay.",
    value: (v) => v.burstiness.toFixed(1),
    percent: (v) => Math.min(100, (v.burstiness / 60) * 100),
  },
  {
    key: "sentenceVariation",
    label: "Sentence variation",
    note: "How much sentence length varies, estimated from word counts.",
    value: (v) => v.sentenceVariation,
    percent: (v) => VARIATION_PERCENT[v.sentenceVariation] ?? 20,
  },
  {
    key: "clicheSignals",
    label: "Cliché signals",
    note: "Sentences containing a phrase from the curated cliché list.",
    value: (v) => String(v.clicheSignals),
    percent: (v, total) => Math.min(100, (v.clicheSignals / Math.max(1, total)) * 100),
  },
];

export default function KeyMetrics({ sentences }) {
  const values = computeKeyMetrics(sentences);

  return (
    <div className="gauge-stack">
      {METRICS.map((metric) => (
        <div key={metric.key} className="gauge-row">
          <div className="gauge-top">
            <span className="gauge-name">{metric.label}</span>
            <span className="gauge-value">{metric.value(values)}</span>
          </div>
          <div className="gauge-track">
            <div
              className="gauge-fill"
              style={{ width: `${Math.max(4, metric.percent(values, sentences.length))}%` }}
            />
          </div>
          <p className="gauge-note">{metric.note}</p>
        </div>
      ))}
    </div>
  );
}
