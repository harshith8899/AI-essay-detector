import { SAMPLE_ESSAYS } from "../sampleEssays.js";

export default function SampleEssays({ onSelect, disabled }) {
  return (
    <div className="sample-essays">
      <span className="sample-essays-label">Try an example:</span>
      <div className="sample-essays-buttons">
        {SAMPLE_ESSAYS.map((sample) => (
          <button
            key={sample.key}
            type="button"
            className="sample-essay-button"
            onClick={() => onSelect(sample.text)}
            disabled={disabled}
          >
            {sample.label}
          </button>
        ))}
      </div>
      <p className="sample-essays-note">Examples are for demonstration only.</p>
    </div>
  );
}
