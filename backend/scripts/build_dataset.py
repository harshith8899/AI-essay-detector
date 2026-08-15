"""Discovers essays under data/{human,ai,polished}_essays and builds a
dataset table: essay_id, filename, category, label, text, source metadata.

human = 0, ai = 1. Polished essays deliberately get label = None: they are
a mixed/realistic case (an edited human essay), not a clean example of
either class, so they must never silently be trained on as if they were
pure AI or pure human text.
"""

import json
from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parents[2] / "data"

CATEGORY_DIRS = {
    "human": DATA_DIR / "human_essays",
    "ai": DATA_DIR / "ai_essays",
    "polished": DATA_DIR / "polished_essays",
}

LABELS = {"human": 0, "ai": 1}


def _load_sidecar(txt_path: Path) -> dict:
    json_path = txt_path.with_suffix(".json")
    if json_path.exists():
        with open(json_path, encoding="utf-8") as f:
            return json.load(f)
    return {}


def build_dataset() -> pd.DataFrame:
    rows = []
    for category, directory in CATEGORY_DIRS.items():
        if not directory.exists():
            continue
        for txt_path in sorted(directory.glob("*.txt")):
            text = txt_path.read_text(encoding="utf-8")
            metadata = _load_sidecar(txt_path)
            rows.append(
                {
                    "essay_id": txt_path.stem,
                    "filename": txt_path.name,
                    "category": category,
                    "label": LABELS.get(category),
                    "text": text,
                    "source_human_essay": metadata.get("source_human_essay"),
                    "model": metadata.get("model"),
                }
            )
    return pd.DataFrame(rows)


if __name__ == "__main__":
    df = build_dataset()
    print(f"Total essays: {len(df)}")
    print(df["category"].value_counts().to_string())
