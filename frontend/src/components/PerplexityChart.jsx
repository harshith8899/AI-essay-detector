import { useState } from "react";

const WIDTH = 680;
const HEIGHT = 200;
const PADDING_LEFT = 36;
const PADDING_RIGHT = 12;
const PADDING_TOP = 12;
const PADDING_BOTTOM = 34;
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

export default function PerplexityChart({ sentences, selectedIndex, onSelect }) {
  const [hoverIndex, setHoverIndex] = useState(null);

  const values = sentences.map((s) => s.perplexity).filter((v) => v !== null && v !== undefined);
  if (values.length === 0) return null;

  const maxValue = Math.max(...values) * 1.05;
  const plotWidth = WIDTH - PADDING_LEFT - PADDING_RIGHT;
  const plotHeight = HEIGHT - PADDING_TOP - PADDING_BOTTOM;
  const barWidth = Math.min(MAX_BAR_WIDTH, plotWidth / sentences.length - BAR_GAP);
  const baselineY = HEIGHT - PADDING_BOTTOM;

  const activeIndex = hoverIndex !== null ? hoverIndex : selectedIndex;

  return (
    <div className="perplexity-chart">
      <h2 className="panel-title">Perplexity by sentence</h2>
      <p className="panel-hint">
        Higher bars mean GPT-2 found the sentence less predictable. Large swings between
        neighboring sentences — burstiness — are more typical of human writing than of
        AI-generated text, which tends to be more uniformly predictable.
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
          const isSelected = selectedIndex === i;
          const isHovered = hoverIndex === i;
          return (
            <g key={i}>
              <path
                d={roundedTopBarPath(x, y, barWidth, barHeight, 4)}
                className={isHovered || isSelected ? "chart-bar chart-bar-hover" : "chart-bar"}
                onMouseEnter={() => setHoverIndex(i)}
                onMouseLeave={() => setHoverIndex(null)}
                onFocus={() => setHoverIndex(i)}
                onBlur={() => setHoverIndex(null)}
                onClick={() => onSelect(i)}
                tabIndex={0}
                role="button"
                aria-pressed={isSelected}
                aria-label={`Sentence ${i + 1}, perplexity ${s.perplexity.toFixed(1)}`}
              />
              {isSelected && (
                <circle
                  cx={x + barWidth / 2}
                  cy={y - 6}
                  r={3}
                  className="chart-selected-marker"
                  aria-hidden="true"
                />
              )}
              {barWidth >= 14 && (
                <text
                  x={x + barWidth / 2}
                  y={baselineY + 16}
                  textAnchor="middle"
                  className="chart-axis-label"
                >
                  {i + 1}
                </text>
              )}
            </g>
          );
        })}
        <text
          x={PADDING_LEFT + plotWidth / 2}
          y={HEIGHT - 4}
          textAnchor="middle"
          className="chart-axis-title"
        >
          Sentence
        </text>
      </svg>
      <div className="chart-tooltip" aria-live="polite">
        {activeIndex !== null && sentences[activeIndex]?.perplexity !== undefined
          ? `Sentence ${activeIndex + 1}: perplexity ${sentences[activeIndex].perplexity.toFixed(1)}`
          : " "}
      </div>
    </div>
  );
}
