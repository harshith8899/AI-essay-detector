export default function LimitationsPanel({ limitations }) {
  return (
    <section className="limitations-panel">
      <h2 className="panel-title">Important limitations</h2>
      <p className="limitations-intro">
        This is a development-stage research instrument, not a validated authorship detector.
      </p>
      <ul className="limitations-list">
        {limitations.map((item, i) => (
          <li key={i}>{item}</li>
        ))}
      </ul>
    </section>
  );
}
