import { useEffect, useRef } from "react";
import SentenceNav from "./SentenceNav.jsx";

// Single-hue sequential intensity (never a red/green verdict scale): opacity
// of the shared teal accent scales continuously with the sentence score.
function intensityStyle(score) {
  const clamped = Math.max(0, Math.min(100, score));
  const alpha = 0.08 + (clamped / 100) * 0.5;
  return { backgroundColor: `rgba(63, 109, 99, ${alpha.toFixed(3)})` };
}

export default function EssayHighlighter({ sentences, selectedIndex, onSelect }) {
  const sentenceRefs = useRef([]);

  useEffect(() => {
    if (selectedIndex === null) return;
    const el = sentenceRefs.current[selectedIndex];
    if (el) {
      el.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }
  }, [selectedIndex]);

  return (
    <>
      <SentenceNav selectedIndex={selectedIndex} total={sentences.length} onSelect={onSelect} />

      <div className="essay-text">
        {sentences.map((sentence, i) => (
          <span
            key={i}
            ref={(el) => (sentenceRefs.current[i] = el)}
            className={`sentence${selectedIndex === i ? " sentence-selected" : ""}`}
            style={intensityStyle(sentence.score)}
            onClick={() => onSelect(i)}
            tabIndex={0}
            role="button"
            aria-pressed={selectedIndex === i}
            aria-label={`Sentence signal ${sentence.score.toFixed(0)} out of 100: ${sentence.text}`}
            onKeyDown={(e) => {
              if (e.key === "Enter" || e.key === " ") {
                e.preventDefault();
                onSelect(i);
              }
            }}
          >
            {sentence.text}{" "}
          </span>
        ))}
      </div>
      <p className="intensity-legend" aria-hidden="true">
        Lower signal <span className="intensity-legend-bar" /> Higher signal
      </p>
    </>
  );
}
