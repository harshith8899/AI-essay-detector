function countWords(text) {
  const trimmed = text.trim();
  if (!trimmed) return 0;
  return trimmed.split(/\s+/).length;
}

export default function EssayInput({ essay, onChange, onAnalyze, loading }) {
  const words = countWords(essay);
  const characters = essay.length;

  return (
    <div className="essay-input">
      <label className="essay-textarea-label" htmlFor="essay-textarea">
        Paste your admissions essay
      </label>
      <textarea
        id="essay-textarea"
        className="essay-textarea"
        placeholder="Paste your admissions essay here..."
        value={essay}
        onChange={(e) => onChange(e.target.value)}
        rows={12}
        disabled={loading}
      />
      <div className="input-controls">
        <span className="word-count" aria-live="polite">
          {words} word{words === 1 ? "" : "s"} / {characters} character{characters === 1 ? "" : "s"}
        </span>
        <button
          type="button"
          className="analyze-button"
          onClick={onAnalyze}
          disabled={loading || !essay.trim()}
        >
          {loading ? "Analyzing…" : "Analyze Essay"}
        </button>
      </div>
    </div>
  );
}
