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
      <Navbar />
      <main className="layout">
        <Header />

        <section className="analyze-grid" id="analyze">
          <div className="analyze-essay">
            <div className="essay-panel">
              {result ? (
                <>
                  <div className="essay-panel-header">
                    <p className="section-label">Essay</p>
                    <button type="button" className="text-action" onClick={handleReset}>
                      New essay
                    </button>
                  </div>
                  <EssayHighlighter
                    sentences={result.sentences}
                    selectedIndex={selectedIndex}
                    onSelect={setSelectedIndex}
                  />
                </>
              ) : (
                <>
                  <p className="section-label">Essay</p>
                  <EssayInput
                    essay={essay}
                    onChange={setEssay}
                    onAnalyze={handleAnalyze}
                    loading={loading}
                  />
                  <SampleEssays onSelect={handleSelectSample} disabled={loading} />
                  {loading && <AnalysisStatus />}
                  {error && !loading && <ErrorState message={error} onRetry={handleAnalyze} />}
                </>
              )}
            </div>
          </div>

          <div className="analyze-signals">
            {result ? (
              <>
                <ScoreMeter score={result.essay_score} />
                <KeyMetrics sentences={result.sentences} />
                <EvidencePanel sentence={selectedSentence} />
              </>
            ) : (
              <div className="signals-placeholder">
                <p className="panel-hint">Results will appear here once you analyze an essay.</p>
              </div>
            )}
          </div>
        </section>

        <HowItWorks />

        {result ? (
          <LimitationsPanel limitations={result.limitations} />
        ) : (
          <section className="limitations" id="limitations">
            <p className="section-label">Limitations</p>
            <p className="panel-hint">Limitations will appear here after you analyze an essay.</p>
          </section>
        )}
      </main>
    </div>
  );
}
