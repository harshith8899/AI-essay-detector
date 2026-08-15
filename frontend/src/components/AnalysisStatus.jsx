const STEPS = [
  "Measuring language-model predictability",
  "Analyzing writing style",
  "Generating sentence evidence",
];

export default function AnalysisStatus() {
  return (
    <div className="analysis-status" role="status" aria-live="polite">
      <div className="analysis-spinner" aria-hidden="true" />
      <div>
        <p className="analysis-status-title">Analyzing essay…</p>
        <ul className="analysis-status-steps">
          {STEPS.map((step) => (
            <li key={step}>{step}</li>
          ))}
        </ul>
      </div>
    </div>
  );
}
