"""Runs the GPT-2 instrument and stylometric extractor over every essay in
the dataset and writes data/features.csv plus data/feature_names.json.

Feature-extraction failures are never papered over with fabricated
values: an essay that fails is skipped and reported, not silently zeroed.
"""

import json
from pathlib import Path

import pandas as pd

from app.scoring import FEATURE_NAMES, FeatureExtractionError, build_feature_vector
from scripts.build_dataset import build_dataset

DATA_DIR = Path(__file__).resolve().parents[2] / "data"


def build_features() -> tuple[pd.DataFrame, list[tuple[str, str]]]:
    dataset = build_dataset()
    rows = []
    failures = []

    for _, row in dataset.iterrows():
        try:
            features = build_feature_vector(row["text"])
        except FeatureExtractionError as exc:
            failures.append((row["essay_id"], str(exc)))
            continue
        except Exception as exc:  # unexpected failure: still don't fabricate a value
            failures.append((row["essay_id"], f"unexpected error: {exc!r}"))
            continue

        record = {"essay_id": row["essay_id"], "category": row["category"], "label": row["label"]}
        record.update(features)
        rows.append(record)

    df = pd.DataFrame(rows, columns=["essay_id", "category", "label"] + FEATURE_NAMES)
    return df, failures


if __name__ == "__main__":
    df, failures = build_features()

    if failures:
        print(f"WARNING: {len(failures)} essay(s) failed feature extraction and were skipped:")
        for essay_id, reason in failures:
            print(f"  - {essay_id}: {reason}")

    features_path = DATA_DIR / "features.csv"
    df.to_csv(features_path, index=False)
    print(f"Saved {len(df)} feature rows ({len(FEATURE_NAMES)} features each) to {features_path}")

    names_path = DATA_DIR / "feature_names.json"
    with open(names_path, "w", encoding="utf-8") as f:
        json.dump(FEATURE_NAMES, f, indent=2)
    print(f"Saved feature name ordering to {names_path}")
