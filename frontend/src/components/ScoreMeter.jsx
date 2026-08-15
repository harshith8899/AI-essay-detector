export default function ScoreMeter({ score, label }) {
  const clamped = Math.max(0, Math.min(100, score));
  const interpretation = label === "higher AI-like signal" ? "Higher signal" : "Lower signal";

  return (
    <div className="score-meter">
      <div className="score-meter-header">
        <span className="score-meter-title">AI-likeness signal</span>
        <span className="score-meter-value">{clamped.toFixed(0)} / 100</span>
      </div>
      <div
        className="score-meter-track"
        role="img"
        aria-label={`AI-likeness signal: ${clamped.toFixed(0)} out of 100`}
      >
        <div className="score-meter-fill" style={{ width: `${clamped}%` }} />
      </div>
      <p className="score-meter-interpretation">{interpretation}</p>
      <p className="score-meter-caveat">
        This is an experimental model score based on measurable text statistics — not proof of
        authorship.
      </p>
    </div>
  );
}
