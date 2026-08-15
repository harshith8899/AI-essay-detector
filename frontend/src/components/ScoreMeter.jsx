function interpretScore(score) {
  if (score < 35) return "Lower signal";
  if (score <= 65) return "Moderate signal";
  return "Higher signal";
}

export default function ScoreMeter({ score }) {
  const clamped = Math.max(0, Math.min(100, score));
  const interpretation = interpretScore(clamped);

  return (
    <div className="score-meter">
      <p className="section-label">AI-likeness signal</p>
      <div className="score-meter-header">
        <span className="score-meter-value">{clamped.toFixed(0)} / 100</span>
      </div>
      <div
        className="gauge-track"
        role="img"
        aria-label={`AI-likeness signal: ${clamped.toFixed(0)} out of 100`}
      >
        <div className="gauge-fill" style={{ width: `${clamped}%` }} />
      </div>
      <p className="score-meter-interpretation">{interpretation}</p>
    </div>
  );
}
