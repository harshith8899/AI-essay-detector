import { useState } from "react";
import Header from "./components/Header.jsx";
import EssayInput from "./components/EssayInput.jsx";
import ScoreMeter from "./components/ScoreMeter.jsx";
import EssayHighlighter from "./components/EssayHighlighter.jsx";
import EvidencePanel from "./components/EvidencePanel.jsx";
import PerplexityChart from "./components/PerplexityChart.jsx";
import LimitationsPanel from "./components/LimitationsPanel.jsx";
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

  const selectedSentence =
    result && selectedIndex !== null ? result.sentences[selectedIndex] : null;

  return (
    <div className="app">
      <Header />
      <main className="layout">
        <EssayInput
          essay={essay}
          onChange={setEssay}
          onAnalyze={handleAnalyze}
          loading={loading}
          error={error}
        />

        {result && (
          <section className="results">
            <ScoreMeter score={result.essay_score} label={result.label} />

            <div className="workspace">
              <EssayHighlighter
                sentences={result.sentences}
                selectedIndex={selectedIndex}
                onSelect={setSelectedIndex}
              />
              <EvidencePanel sentence={selectedSentence} />
            </div>

            <PerplexityChart sentences={result.sentences} />

            <LimitationsPanel limitations={result.limitations} />
          </section>
        )}
      </main>
    </div>
  );
}
