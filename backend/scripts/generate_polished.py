"""Generates a "polished" version of a human essay via a configurable LLM
provider, plus a sentence-level diff against the original.

OFFLINE DATASET GENERATION ONLY. This script is never imported by, or run
from, the request-processing path of the API. The running detector never
sends a user's essay to a chat model for anything, including polishing.

This script does not run automatically as part of the training pipeline
(build_dataset.py / build_features.py / train_classifier.py never import
it). It must be invoked deliberately, per essay, by a human.

Before running, configure a provider by setting the matching environment
variable, e.g. (Windows):
    set ANTHROPIC_API_KEY=...
or (macOS/Linux):
    export ANTHROPIC_API_KEY=...

If no provider is configured, this script fails loudly with instructions
rather than silently falling back to some other behavior (e.g. it will
NOT fabricate a "polished" essay locally).

Usage:
    python -m scripts.generate_polished data/human_essays/human_001.txt
"""

import argparse
import difflib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

from app.spacy_pipeline import nlp

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
POLISHED_DIR = DATA_DIR / "polished_essays"

DEFAULT_PROMPT = (
    "Lightly polish the following college admissions essay for grammar, "
    "flow, and word choice while preserving its meaning and voice."
)


def _sentences(text: str) -> list[str]:
    doc = nlp(text)
    return [sent.text.strip() for sent in doc.sents if sent.text.strip()]


def sentence_diff(original: str, polished: str) -> list[dict]:
    """Sentence-level diff between `original` and `polished` essay text.

    Uses spaCy for sentence segmentation (consistent with the rest of the
    project) and difflib.SequenceMatcher to align sentences, so the diff
    reports which original sentences were kept unchanged, changed, removed,
    or which sentences were newly added in the polished version.
    """
    orig_sents = _sentences(original)
    pol_sents = _sentences(polished)
    matcher = difflib.SequenceMatcher(a=orig_sents, b=pol_sents, autojunk=False)

    diff = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            for oi, pj in zip(range(i1, i2), range(j1, j2)):
                diff.append({"status": "unchanged", "original": orig_sents[oi], "polished": pol_sents[pj]})
        elif tag == "replace":
            orig_chunk = orig_sents[i1:i2]
            pol_chunk = pol_sents[j1:j2]
            for k in range(max(len(orig_chunk), len(pol_chunk))):
                diff.append(
                    {
                        "status": "changed",
                        "original": orig_chunk[k] if k < len(orig_chunk) else None,
                        "polished": pol_chunk[k] if k < len(pol_chunk) else None,
                    }
                )
        elif tag == "delete":
            for oi in range(i1, i2):
                diff.append({"status": "removed", "original": orig_sents[oi], "polished": None})
        elif tag == "insert":
            for pj in range(j1, j2):
                diff.append({"status": "added", "original": None, "polished": pol_sents[pj]})
    return diff


def _polish_with_anthropic(text: str, prompt: str) -> str:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError(
            "No ANTHROPIC_API_KEY configured. Set the ANTHROPIC_API_KEY "
            "environment variable before running this script. Refusing to "
            "silently fall back to any other behavior."
        )
    raise NotImplementedError(
        "The Anthropic polishing call is not implemented in this development "
        "environment. Wire up the actual API call in _polish_with_anthropic() "
        "once you're ready to generate real polished essays; ANTHROPIC_API_KEY "
        "is set, but no request is made without that implementation."
    )


def _polish_with_openai(text: str, prompt: str) -> str:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "No OPENAI_API_KEY configured. Set the OPENAI_API_KEY environment "
            "variable before running this script. Refusing to silently fall "
            "back to any other behavior."
        )
    raise NotImplementedError(
        "The OpenAI polishing call is not implemented in this development "
        "environment. Wire up the actual API call in _polish_with_openai() "
        "once you're ready to generate real polished essays; OPENAI_API_KEY "
        "is set, but no request is made without that implementation."
    )


PROVIDERS = {
    "anthropic": _polish_with_anthropic,
    "openai": _polish_with_openai,
}


def polish_essay(text: str, provider: str, prompt: str) -> str:
    if provider not in PROVIDERS:
        raise ValueError(f"Unknown provider {provider!r}. Choose from: {sorted(PROVIDERS)}")
    return PROVIDERS[provider](text, prompt)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("essay_path", type=Path, help="Path to a human essay .txt file")
    parser.add_argument("--provider", default="anthropic", choices=sorted(PROVIDERS))
    parser.add_argument("--prompt", default=DEFAULT_PROMPT)
    args = parser.parse_args()

    original = args.essay_path.read_text(encoding="utf-8")
    polished = polish_essay(original, args.provider, args.prompt)  # raises if unconfigured

    POLISHED_DIR.mkdir(parents=True, exist_ok=True)
    existing = sorted(POLISHED_DIR.glob("polished_*.txt"))
    next_id = len(existing) + 1
    stem = f"polished_{next_id:03d}"

    (POLISHED_DIR / f"{stem}.txt").write_text(polished, encoding="utf-8")
    metadata = {
        "category": "polished",
        "source_human_essay": args.essay_path.name,
        "model": args.provider,
        "prompt": args.prompt,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    (POLISHED_DIR / f"{stem}.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    diff = sentence_diff(original, polished)
    (POLISHED_DIR / f"{stem}.diff.json").write_text(json.dumps(diff, indent=2), encoding="utf-8")

    print(f"Wrote {stem}.txt, {stem}.json, {stem}.diff.json to {POLISHED_DIR}")


if __name__ == "__main__":
    main()
