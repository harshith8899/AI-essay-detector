export default function SentenceNav({ selectedIndex, total, onSelect }) {
  if (total < 2) return null;

  function goPrev() {
    onSelect(selectedIndex === null ? total - 1 : (selectedIndex - 1 + total) % total);
  }

  function goNext() {
    onSelect(selectedIndex === null ? 0 : (selectedIndex + 1) % total);
  }

  return (
    <div className="sentence-nav">
      <button type="button" className="sentence-nav-button" onClick={goPrev} aria-label="Previous sentence">
        Previous
      </button>
      <span className="sentence-nav-position" aria-live="polite">
        Sentence {selectedIndex === null ? "–" : selectedIndex + 1} / {total}
      </span>
      <button type="button" className="sentence-nav-button" onClick={goNext} aria-label="Next sentence">
        Next
      </button>
    </div>
  );
}
