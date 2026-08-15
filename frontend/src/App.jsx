import { useState } from "react";
import Header from "./components/Header.jsx";
import EssayInput from "./components/EssayInput.jsx";
import SampleEssays from "./components/SampleEssays.jsx";
import AnalysisStatus from "./components/AnalysisStatus.jsx";
import ErrorState from "./components/ErrorState.jsx";
import ScoreMeter from "./components/ScoreMeter.jsx";
import KeyMetrics from "./components/KeyMetrics.jsx";
import EssayHighlighter from "./components/EssayHighlighter.jsx";
import EvidencePanel from "./components/EvidencePanel.jsx";
import PerplexityChart from "./components/PerplexityChart.jsx";
import LimitationsPanel from "./components/LimitationsPanel.jsx";
import HowItWorks from "./components/HowItWorks.jsx";
import { analyzeEssay } from "./api.js";

export default function App() {
  const [essay, setEssay] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);
  const [selectedIndex, setSelectedIndex] = useState(null);

  async function handleAnalyze() {
    if (!essay.trim() || loading) return;
    setLoading(true);
    setError(null);
    try {
      const data = await analyzeEssay(essay);
      setResult(data);
      setSelectedIndex(null);
    } catch (err) {
      setError(err.message || "Something went wrong while analyzing the essay.");
      setResult(null);
    } finally {
      setLoading(false);
    }
  }

  function handleReset() {
    setEssay("");
    setResult(null);
    setSelectedIndex(null);
    setError(null);
  }

  function handleSelectSample(text) {
    setError(null);
    setEssay(text);
  }

  const selectedSentence =
    result && selectedIndex !== null ? result.sentences[selectedIndex] : null;

  return (
    <div className="app">
      <Header />
      <main className="layout">
        <section className="input-panel">
          <p className="empty-state-hint">
            Paste an admissions essay to explore measurable signals associated with
            machine-generated prose. The tool does not determine authorship with certainty.
          </p>

          <SampleEssays onSelect={handleSelectSample} disabled={loading} />

          <EssayInput essay={essay} onChange={setEssay} onAnalyze={handleAnalyze} loading={loading} />

          {loading && <AnalysisStatus />}
          {error && !loading && <ErrorState message={error} onRetry={handleAnalyze} />}
        </section>

        {result && (
          <section className="results" id="results">
            <div className="results-header">
              <h2 className="results-heading">Results</h2>
              <button type="button" className="new-essay-button" onClick={handleReset}>
                New Essay
              </button>
            </div>

            <ScoreMeter score={result.essay_score} label={result.label} />

            <KeyMetrics sentences={result.sentences} />

            <div className="workspace">
              <EssayHighlighter
                sentences={result.sentences}
                selectedIndex={selectedIndex}
                onSelect={setSelectedIndex}
              />
              <EvidencePanel sentence={selectedSentence} />
            </div>

            <PerplexityChart
              sentences={result.sentences}
              selectedIndex={selectedIndex}
              onSelect={setSelectedIndex}
            />

            <LimitationsPanel limitations={result.limitations} />
          </section>
        )}

        <HowItWorks />
      </main>
    </div>
  );
}
