export default function LimitationsPanel({ limitations }) {
  return (
    <section className="limitations-panel">
      <h2 className="panel-title">Important limitations</h2>
      <ul className="limitations-list">
        {limitations.map((item, i) => (
          <li key={i}>{item}</li>
        ))}
      </ul>
    </section>
  );
}
