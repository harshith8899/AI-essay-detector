export default function LimitationsPanel({ limitations }) {
  return (
    <section className="limitations" id="limitations">
      <p className="section-label">Limitations</p>
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
