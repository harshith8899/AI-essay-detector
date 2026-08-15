import { computeKeyMetrics } from "../metrics.js";

function scoreTier(score) {
  if (score < 35) return "a lower reading";
  if (score <= 65) return "a moderate reading";
  return "a higher reading";
}

function predictabilityPhrase(meanPerplexity) {
  if (meanPerplexity === null) return "GPT-2 could not score this essay's predictability";
  if (meanPerplexity < 30) return `GPT-2 found the wording fairly predictable on average (perplexity ${meanPerplexity.toFixed(1)})`;
  if (meanPerplexity < 70) return `GPT-2 found the wording moderately predictable on average (perplexity ${meanPerplexity.toFixed(1)})`;
  return `GPT-2 found the wording relatively unpredictable on average (perplexity ${meanPerplexity.toFixed(1)})`;
}

function clichePhrase(count) {
  if (count === 0) return "No phrases from the curated cliché list were detected.";
  return `${count} sentence${count === 1 ? "" : "s"} contained a phrase from the curated cliché list.`;
}

export default function ReadingSummary({ result }) {
  const metrics = computeKeyMetrics(result.sentences);
  const n = result.sentences.length;

  const text =
    `This essay's signal sits at ${result.essay_score.toFixed(0)}/100 — ${scoreTier(result.essay_score)}. ` +
    `Sentence length varies at a ${metrics.sentenceVariation.toLowerCase()} pace across its ${n} sentence${n === 1 ? "" : "s"}, ` +
    `and ${predictabilityPhrase(metrics.meanPerplexity)}. ${clichePhrase(metrics.clicheSignals)}`;

  return (
    <section className="reading" id="reading">
      <p className="section-label">Reading</p>
      <p className="reading-summary">{text}</p>
    </section>
  );
}
