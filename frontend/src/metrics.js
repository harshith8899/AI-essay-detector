// Client-side derivation of summary metrics from the sentence-level data the
// API already returns (perplexity, text, top_features). No new backend data,
// no invented metrics. mean/burstiness use the same population standard
// deviation convention documented in backend/app/lm_features.py.

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

export function computeKeyMetrics(sentences) {
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

  return { meanPerplexity, burstiness, sentenceVariation, coefficientOfVariation, clicheSignals };
}
