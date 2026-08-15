import { useState } from "react";
import Header from "./components/Header.jsx";
import Navbar from "./components/Navbar.jsx";
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
      <Navbar />
      <main className="layout">
        <section className="workspace-grid">
          {/* LEFT: essay input / original essay */}
          <div className="workspace-column workspace-column-input" id="analyze">
            <p className="empty-state-hint">
              Paste an admissions essay to explore measurable signals associated with
              machine-generated prose. The tool does not determine authorship with certainty.
            </p>

            <SampleEssays onSelect={handleSelectSample} disabled={loading} />

            <EssayInput
              essay={essay}
              onChange={setEssay}
              onAnalyze={handleAnalyze}
              loading={loading}
            />

            {result && !loading && (
              <button type="button" className="new-essay-button" onClick={handleReset}>
                New Essay
              </button>
            )}

            {loading && <AnalysisStatus />}
            {error && !loading && <ErrorState message={error} onRetry={handleAnalyze} />}
          </div>

          {/* CENTER: analyzed essay with sentence highlighting */}
          <div className="workspace-column workspace-column-essay">
            {result ? (
              <EssayHighlighter
                sentences={result.sentences}
                selectedIndex={selectedIndex}
                onSelect={setSelectedIndex}
              />
            ) : (
              <div className="essay-highlighter essay-placeholder">
                <h2 className="panel-title">Essay</h2>
                <p className="panel-hint">
                  Your essay will appear here with sentence-level highlighting once analyzed.
                </p>
              </div>
            )}
          </div>

          {/* RIGHT: score + selected sentence evidence */}
          <div className="workspace-column workspace-column-signal">
            <div id="signal">
              {result ? (
                <ScoreMeter score={result.essay_score} />
              ) : (
                <div className="score-meter score-placeholder">
                  <span className="score-meter-title">AI-likeness signal</span>
                  <p className="panel-hint">Results will appear here after you analyze an essay.</p>
                </div>
              )}
            </div>

            <div id="evidence">
              {result ? (
                <EvidencePanel sentence={selectedSentence} />
              ) : (
                <aside className="evidence-panel evidence-panel-empty">
                  <h2 className="panel-title">Why did this sentence receive this signal?</h2>
                  <p className="panel-hint">
                    Evidence for the selected sentence will appear here after you analyze an
                    essay.
                  </p>
                </aside>
              )}
            </div>
          </div>
        </section>

        {result && (
          <>
            <KeyMetrics sentences={result.sentences} />
            <PerplexityChart
              sentences={result.sentences}
              selectedIndex={selectedIndex}
              onSelect={setSelectedIndex}
            />
          </>
        )}

        <div id="limitations">
          {result ? (
            <LimitationsPanel limitations={result.limitations} />
          ) : (
            <section className="limitations-panel">
              <h2 className="panel-title">Important limitations</h2>
              <p className="panel-hint">
                Limitations will appear here after you analyze an essay.
              </p>
            </section>
          )}
        </div>

        <HowItWorks />
      </main>
    </div>
  );
}
