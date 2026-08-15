export default function EssayInput({ essay, onChange, onAnalyze, loading, error }) {
  return (
    <section className="input-panel">
      <textarea
        className="essay-textarea"
        placeholder="Paste your admissions essay here..."
        value={essay}
        onChange={(e) => onChange(e.target.value)}
        rows={12}
        disabled={loading}
        aria-label="Essay text"
      />
      <div className="input-controls">
        <button
          type="button"
          className="analyze-button"
          onClick={onAnalyze}
          disabled={loading || !essay.trim()}
        >
          {loading ? "Analyzing…" : "Analyze Essay"}
        </button>
        {loading && (
          <span className="loading-note" role="status">
            Running GPT-2 and stylometric analysis…
          </span>
        )}
      </div>
      {error && (
        <p className="error-message" role="alert">
          {error}
        </p>
      )}
    </section>
  );
}
