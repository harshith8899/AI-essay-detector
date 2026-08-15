import { SAMPLE_ESSAYS } from "../sampleEssays.js";

export default function SampleEssays({ onSelect, disabled }) {
  return (
    <p className="sample-essays">
      <span className="sample-essays-label">Try a sample:</span>{" "}
      {SAMPLE_ESSAYS.map((sample, i) => (
        <span key={sample.key}>
          <button
            type="button"
            className="sample-essay-link"
            onClick={() => onSelect(sample.text)}
            disabled={disabled}
          >
            {sample.label}
          </button>
          {i < SAMPLE_ESSAYS.length - 1 ? <span className="sample-essays-sep"> · </span> : null}
        </span>
      ))}
    </p>
  );
}
