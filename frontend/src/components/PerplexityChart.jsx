import { useState } from "react";

const WIDTH = 680;
const HEIGHT = 180;
const PADDING_LEFT = 36;
const PADDING_RIGHT = 12;
const PADDING_TOP = 12;
const PADDING_BOTTOM = 24;
const BAR_GAP = 4;
const MAX_BAR_WIDTH = 24;

// 4px rounded top corners, square baseline — a bar "grows from" the axis.
function roundedTopBarPath(x, y, width, height, radius) {
  const r = Math.min(radius, width / 2, Math.max(height, 0));
  if (height <= 0) return "";
  return `M ${x} ${y + height}
    L ${x} ${y + r}
    Q ${x} ${y} ${x + r} ${y}
    L ${x + width - r} ${y}
    Q ${x + width} ${y} ${x + width} ${y + r}
    L ${x + width} ${y + height}
    Z`;
}

export default function PerplexityChart({ sentences }) {
  const [hoverIndex, setHoverIndex] = useState(null);

  const values = sentences.map((s) => s.perplexity).filter((v) => v !== null && v !== undefined);
  if (values.length === 0) return null;

  const maxValue = Math.max(...values) * 1.05;
  const plotWidth = WIDTH - PADDING_LEFT - PADDING_RIGHT;
  const plotHeight = HEIGHT - PADDING_TOP - PADDING_BOTTOM;
  const barWidth = Math.min(MAX_BAR_WIDTH, plotWidth / sentences.length - BAR_GAP);
  const baselineY = HEIGHT - PADDING_BOTTOM;

  return (
    <div className="perplexity-chart">
      <h2 className="panel-title">Perplexity by sentence</h2>
      <p className="panel-hint">
        Higher bars mean GPT-2 found the sentence less predictable. Large swings between
        neighboring sentences — burstiness — are more typical of human writing than of AI-generated
        text, which tends to be more uniformly predictable.
      </p>
      <svg
        width={WIDTH}
        height={HEIGHT}
        viewBox={`0 0 ${WIDTH} ${HEIGHT}`}
        role="img"
        aria-label="Bar chart of GPT-2 perplexity for each sentence in the essay"
        className="perplexity-svg"
      >
        <line
          x1={PADDING_LEFT}
          y1={baselineY}
          x2={WIDTH - PADDING_RIGHT}
          y2={baselineY}
          className="chart-baseline"
        />
        <text x={2} y={baselineY + 4} className="chart-axis-label">
          0
        </text>
        <text x={2} y={PADDING_TOP + 8} className="chart-axis-label">
          {Math.round(maxValue)}
        </text>

        {sentences.map((s, i) => {
          if (s.perplexity === null || s.perplexity === undefined) return null;
          const barHeight = (s.perplexity / maxValue) * plotHeight;
          const x = PADDING_LEFT + i * (barWidth + BAR_GAP);
          const y = baselineY - barHeight;
          const isHovered = hoverIndex === i;
          return (
            <path
              key={i}
              d={roundedTopBarPath(x, y, barWidth, barHeight, 4)}
              className={isHovered ? "chart-bar chart-bar-hover" : "chart-bar"}
              onMouseEnter={() => setHoverIndex(i)}
              onMouseLeave={() => setHoverIndex(null)}
              onFocus={() => setHoverIndex(i)}
              onBlur={() => setHoverIndex(null)}
              tabIndex={0}
              role="img"
              aria-label={`Sentence ${i + 1}, perplexity ${s.perplexity.toFixed(1)}`}
            />
          );
        })}
      </svg>
      <div className="chart-tooltip" aria-live="polite">
        {hoverIndex !== null
          ? `Sentence ${hoverIndex + 1}: perplexity ${sentences[hoverIndex].perplexity.toFixed(1)}`
          : " "}
      </div>
    </div>
  );
}
