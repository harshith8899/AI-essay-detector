"""Trains and evaluates Logistic Regression and Gradient Boosting on
data/features.csv, then saves the better-performing model to
backend/app/models/.

*** DEVELOPMENT-DATASET RESULTS ONLY ***
The dataset this trains on is a small, hand-authored placeholder corpus
(see data/README.md). These numbers are a pipeline sanity check, not a
scientific validation of the detector's real-world accuracy.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

from app.scoring import FEATURE_NAMES

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
MODELS_DIR = Path(__file__).resolve().parents[1] / "app" / "models"
RANDOM_SEED = 42
TEST_SIZE = 0.25


def load_binary_dataset():
    df = pd.read_csv(DATA_DIR / "features.csv")
    binary_df = df[df["category"].isin(["human", "ai"])].reset_index(drop=True)
    polished_df = df[df["category"] == "polished"].reset_index(drop=True)
    return binary_df, polished_df


def evaluate(name, model, X_eval, y_test):
    preds = model.predict(X_eval)
    metrics = {
        "accuracy": accuracy_score(y_test, preds),
        "precision": precision_score(y_test, preds, zero_division=0),
        "recall": recall_score(y_test, preds, zero_division=0),
        "f1": f1_score(y_test, preds, zero_division=0),
        "confusion_matrix": confusion_matrix(y_test, preds).tolist(),
    }
    print(f"\n--- {name} (DEVELOPMENT SET, n_test={len(y_test)}) ---")
    print(
        f"accuracy={metrics['accuracy']:.3f}  precision={metrics['precision']:.3f}  "
        f"recall={metrics['recall']:.3f}  f1={metrics['f1']:.3f}"
    )
    print(f"confusion matrix (rows=actual [human,ai], cols=predicted):\n{np.array(metrics['confusion_matrix'])}")
    return metrics


def main():
    print("=" * 70)
    print("DEVELOPMENT DATASET RESULTS - NOT A SCIENTIFIC VALIDATION")
    print("Trained on a small, hand-authored placeholder corpus. See data/README.md.")
    print("=" * 70)

    binary_df, polished_df = load_binary_dataset()

    X = binary_df[FEATURE_NAMES].values
    y = binary_df["label"].astype(int).values

    print(f"\nDataset size (human+ai): {len(binary_df)}")
    print(f"Class distribution: {binary_df['category'].value_counts().to_dict()}")
    print(f"Polished essays held out for reference only: {len(polished_df)}")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_SEED, stratify=y
    )
    print(f"\nTrain size: {len(X_train)}   Test size: {len(X_test)}")
    print(f"Train class distribution: human={sum(y_train == 0)} ai={sum(y_train == 1)}")
    print(f"Test class distribution:  human={sum(y_test == 0)} ai={sum(y_test == 1)}")

    scaler = StandardScaler().fit(X_train)
    X_train_scaled = scaler.transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    logreg = LogisticRegression(max_iter=1000, random_state=RANDOM_SEED)
    logreg.fit(X_train_scaled, y_train)

    gbc = GradientBoostingClassifier(random_state=RANDOM_SEED)
    gbc.fit(X_train, y_train)

    results = {
        "Logistic Regression": evaluate("Logistic Regression", logreg, X_test_scaled, y_test),
        "Gradient Boosting": evaluate("Gradient Boosting", gbc, X_test, y_test),
    }

    print("\n--- Logistic Regression: top 10 features by |coefficient| ---")
    coefs = logreg.coef_[0]
    for i in np.argsort(-np.abs(coefs))[:10]:
        print(f"  {FEATURE_NAMES[i]:30s} {coefs[i]:+.4f}")

    print("\n--- Gradient Boosting: top 10 features by importance ---")
    importances = gbc.feature_importances_
    for i in np.argsort(-importances)[:10]:
        print(f"  {FEATURE_NAMES[i]:30s} {importances[i]:.4f}")

    print(
        "\nNOTE: cliche_count / transition_opener_rate dominate because the "
        "development AI essays were hand-written with deliberately cliche-heavy, "
        "transition-opener-heavy prose to exercise the stylometry detectors. "
        "This is a KNOWN DATASET ARTIFACT, not a validated real-world signal - "
        "a real AI-generated corpus would not separate this cleanly on these "
        "two features alone. mean_perplexity/burstiness (genuine GPT-2 signal, "
        "not hand-injected) also separate the classes, which is reassuring."
    )

    try:
        import shap

        explainer = shap.TreeExplainer(gbc)
        shap_values = explainer.shap_values(X_test)
        mean_abs_shap = np.abs(shap_values).mean(axis=0)
        print("\n--- Gradient Boosting: top 10 features by mean |SHAP value| ---")
        for i in np.argsort(-mean_abs_shap)[:10]:
            print(f"  {FEATURE_NAMES[i]:30s} {mean_abs_shap[i]:.4f}")
    except Exception as exc:
        print(f"\nSHAP analysis skipped ({exc!r}); coefficient/importance analysis above stands on its own.")

    if len(polished_df):
        Xp = polished_df[FEATURE_NAMES].values
        Xp_scaled = scaler.transform(Xp)
        logreg_preds = logreg.predict(Xp_scaled)
        gbc_preds = gbc.predict(Xp)
        print("\n--- Polished essays (reference only, NOT scored as ground truth) ---")
        print(f"Logistic Regression predicted 'ai-like': {logreg_preds.sum()}/{len(polished_df)}")
        print(f"Gradient Boosting predicted 'ai-like':    {gbc_preds.sum()}/{len(polished_df)}")

    best_name = max(results, key=lambda k: results[k]["f1"])
    if results["Logistic Regression"]["f1"] == results["Gradient Boosting"]["f1"]:
        best_name = "Logistic Regression"  # tie-break toward the simpler, more interpretable model
    best_model = logreg if best_name == "Logistic Regression" else gbc
    requires_scaling = best_name == "Logistic Regression"

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(best_model, MODELS_DIR / "model.pkl")
    joblib.dump(scaler, MODELS_DIR / "scaler.pkl")
    with open(MODELS_DIR / "feature_names.json", "w", encoding="utf-8") as f:
        json.dump(FEATURE_NAMES, f, indent=2)

    metadata = {
        "model_type": best_name,
        "requires_scaling": requires_scaling,
        "random_seed": RANDOM_SEED,
        "feature_count": len(FEATURE_NAMES),
        "training_dataset_size": len(binary_df),
        "train_size": len(X_train),
        "test_size": len(X_test),
        "test_metrics": results[best_name],
        "training_date": datetime.now(timezone.utc).isoformat(),
        "note": (
            "Development-dataset results only, trained on a small hand-authored "
            "placeholder corpus. Not a scientific validation of real-world "
            "accuracy. See data/README.md for dataset limitations."
        ),
    }
    with open(MODELS_DIR / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print(f"\nSaved best model ({best_name}) and artifacts to {MODELS_DIR}")


if __name__ == "__main__":
    main()
