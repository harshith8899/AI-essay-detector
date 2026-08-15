import { useState } from "react";

const WIDTH = 800;
const HEIGHT = 90;
const PAD_X = 16;
const PAD_TOP = 10;
const PAD_BOTTOM = 22;

export default function PerplexityChart({ sentences, selectedIndex, onSelect }) {
  const [hoverIndex, setHoverIndex] = useState(null);

  const values = sentences.map((s) => s.perplexity).filter((v) => v !== null && v !== undefined);
  if (values.length === 0) return null;

  const maxValue = Math.max(...values) || 1;
  const meanValue = values.reduce((a, b) => a + b, 0) / values.length;
  const variance = values.reduce((a, b) => a + (b - meanValue) ** 2, 0) / values.length;
  const stdValue = Math.sqrt(variance);

  const innerW = WIDTH - PAD_X * 2;
  const step = sentences.length > 1 ? innerW / (sentences.length - 1) : 0;

  const points = sentences.map((s, i) => {
    const perplexity = s.perplexity ?? 0;
    const x = PAD_X + step * i;
    const norm = maxValue ? perplexity / maxValue : 0;
    const y = HEIGHT - PAD_BOTTOM - norm * (HEIGHT - PAD_TOP - PAD_BOTTOM);
    const outlier = stdValue > 0 && Math.abs(perplexity - meanValue) > 1.15 * stdValue;
    return { x, y, perplexity, outlier };
  });

  const pathD = points.map((p, i) => `${i === 0 ? "M" : "L"} ${p.x.toFixed(1)} ${p.y.toFixed(1)}`).join(" ");
  const activeIndex = hoverIndex !== null ? hoverIndex : selectedIndex;

  return (
    <section className="rhythm-section">
      <p className="section-label">Perplexity by sentence</p>
      <p className="section-note">
        Higher points mean GPT-2 found the sentence less predictable. Wide swings between
        sentences — burstiness — are more typical of human writing than of AI-generated text.
      </p>
      <svg
        width="100%"
        viewBox={`0 0 ${WIDTH} ${HEIGHT}`}
        preserveAspectRatio="none"
        role="img"
        aria-label="Line chart of GPT-2 perplexity for each sentence in the essay"
        className="rhythm-strip"
      >
        <path d={pathD} className="rhythm-line" />
        {points.map((p, i) => {
          const isSelected = selectedIndex === i;
          const isActive = activeIndex === i;
          return (
            <circle
              key={i}
              cx={p.x}
              cy={p.y}
              r={isActive ? 5 : 3.4}
              className={`rhythm-dot${p.outlier ? " rhythm-dot-notable" : ""}${isSelected ? " rhythm-dot-selected" : ""}`}
              onMouseEnter={() => setHoverIndex(i)}
              onMouseLeave={() => setHoverIndex(null)}
              onFocus={() => setHoverIndex(i)}
              onBlur={() => setHoverIndex(null)}
              onClick={() => onSelect(i)}
              tabIndex={0}
              role="button"
              aria-pressed={isSelected}
              aria-label={`Sentence ${i + 1}, perplexity ${p.perplexity.toFixed(1)}`}
            />
          );
        })}
      </svg>
      <p className="rhythm-caption" aria-live="polite">
        {activeIndex !== null && sentences[activeIndex]?.perplexity !== undefined
          ? `Sentence ${activeIndex + 1} · perplexity ${sentences[activeIndex].perplexity.toFixed(1)}`
          : "Each point is one sentence · amber marks a statistical outlier"}
      </p>
    </section>
  );
}
