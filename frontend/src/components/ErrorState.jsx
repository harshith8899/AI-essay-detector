export default function ErrorState({ message, onRetry }) {
  return (
    <div className="error-state" role="alert">
      <p className="error-state-title">Analysis failed</p>
      <p className="error-state-body">
        The detector could not analyze this essay. Check that the backend is running and try
        again.
      </p>
      {message && <p className="error-state-detail">{message}</p>}
      <button type="button" className="error-state-retry" onClick={onRetry}>
        Try again
      </button>
    </div>
  );
}
