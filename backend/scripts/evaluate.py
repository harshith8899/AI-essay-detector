"""Official development-dataset evaluation.

Runs four analyses against the SAME train/test split used by
scripts/train_classifier.py (same RANDOM_SEED, same TEST_SIZE, so results
are directly comparable to what was reported at training time):

  1. Held-out test metrics for the saved (deployed) model.
  2. Confident-failure analysis on that test set.
  3. An ablation experiment: a second Logistic Regression trained WITHOUT
     cliche_count / cliche_rate / transition_opener_rate, to test how much
     of the result depends on the deliberately hand-injected cliche/
     transition artifacts in the development AI essays.
  4. Polished-essay scoring (reference only — polished essays have no
     binary ground truth).

*** DEVELOPMENT DATASET RESULTS ONLY ***
44 hand-authored placeholder essays. Not a scientific validation of
real-world accuracy. See data/README.md and REPORT.md.
"""

import numpy as np
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

from app.scoring import FEATURE_NAMES, analyze_essay, load_classifier
from scripts.build_dataset import build_dataset
from scripts.train_classifier import RANDOM_SEED, TEST_SIZE, load_binary_dataset

ABLATED_FEATURES = {"cliche_count", "cliche_rate", "transition_opener_rate"}
ABLATION_FEATURE_NAMES = [f for f in FEATURE_NAMES if f not in ABLATED_FEATURES]


def metrics_report(y_true, y_pred) -> dict:
    return {
        "accuracy": accuracy_score(y_true, y_pred),
        "precision": precision_score(y_true, y_pred, zero_division=0),
        "recall": recall_score(y_true, y_pred, zero_division=0),
        "f1": f1_score(y_true, y_pred, zero_division=0),
        "confusion_matrix": confusion_matrix(y_true, y_pred).tolist(),
    }


def print_metrics(name: str, m: dict, n: int) -> None:
    print(f"\n--- {name} (DEVELOPMENT SET, n={n}) ---")
    print(
        f"accuracy={m['accuracy']:.3f}  precision={m['precision']:.3f}  "
        f"recall={m['recall']:.3f}  f1={m['f1']:.3f}"
    )
    print(f"confusion matrix (rows=actual [human,ai], cols=predicted):\n{np.array(m['confusion_matrix'])}")


def _print_case(essay_id, true_cat, pred_cat, score, row) -> None:
    print(f"\n  essay_id: {essay_id}")
    print(f"    true category: {true_cat}   predicted: {pred_cat}   model score: {score}/100")
    print(
        f"    mean_perplexity={row['mean_perplexity']:.1f}  burstiness={row['burstiness']:.1f}  "
        f"cliche_count={row['cliche_count']}  transition_opener_rate={row['transition_opener_rate']:.2f}  "
        f"sentence_length_std={row['sentence_length_std']:.1f}"
    )


def print_confident_failures(label: str, y_test, preds, probs, id_test, binary_df, top_n: int = 3) -> list:
    wrong_idx = np.where(preds != y_test)[0]
    print(f"\n--- {label}: confident-failure analysis ---")
    print(f"Genuine misclassifications on this test set: {len(wrong_idx)} out of {len(y_test)}")

    if len(wrong_idx) == 0:
        print(
            "No misclassifications occurred on this 8-essay held-out test set. "
            "The development test set is too small to provide three genuine "
            "failures; reporting 0 confident failures honestly rather than "
            "manufacturing any. Falling back to the most informative BORDERLINE "
            "cases instead (correctly classified, but closest to the decision "
            "boundary) for qualitative discussion:"
        )
        boundary_dist = np.abs(probs - 0.5)
        ranked = np.argsort(boundary_dist)[:top_n]
        cases = []
        for idx in ranked:
            essay_id = id_test[idx]
            row = binary_df[binary_df["essay_id"] == essay_id].iloc[0]
            true_cat = "ai" if y_test[idx] == 1 else "human"
            pred_cat = "ai" if preds[idx] == 1 else "human"
            score = round(100 * probs[idx], 1)
            _print_case(essay_id, true_cat, pred_cat, score, row)
            cases.append(
                {
                    "essay_id": essay_id,
                    "true_category": true_cat,
                    "predicted_category": pred_cat,
                    "score": score,
                    "borderline": True,
                }
            )
        return cases

    confidence = np.abs(probs[wrong_idx] - 0.5)
    ranked = wrong_idx[np.argsort(-confidence)][:top_n]

    cases = []
    for idx in ranked:
        essay_id = id_test[idx]
        row = binary_df[binary_df["essay_id"] == essay_id].iloc[0]
        true_cat = "ai" if y_test[idx] == 1 else "human"
        pred_cat = "ai" if preds[idx] == 1 else "human"
        score = round(100 * probs[idx], 1)
        _print_case(essay_id, true_cat, pred_cat, score, row)
        cases.append(
            {
                "essay_id": essay_id,
                "true_category": true_cat,
                "predicted_category": pred_cat,
                "score": score,
                "borderline": False,
            }
        )
    return cases


def section_official_evaluation(binary_df):
    print("=" * 70)
    print("SECTION 1 - OFFICIAL DEVELOPMENT-SET EVALUATION (saved/deployed model)")
    print("*** DEVELOPMENT DATASET RESULTS - NOT REAL-WORLD ACCURACY ***")
    print("=" * 70)

    model, scaler, feature_names, metadata = load_classifier()
    if feature_names != FEATURE_NAMES:
        raise RuntimeError("Saved feature_names.json does not match the current FEATURE_NAMES ordering.")

    X = binary_df[FEATURE_NAMES].values
    y = binary_df["label"].astype(int).values
    ids = binary_df["essay_id"].values

    X_train, X_test, y_train, y_test, id_train, id_test = train_test_split(
        X, y, ids, test_size=TEST_SIZE, random_state=RANDOM_SEED, stratify=y
    )
    print(f"\nDataset size (human+ai): {len(binary_df)}   Train: {len(X_train)}   Test: {len(X_test)}")

    X_test_input = scaler.transform(X_test) if metadata.get("requires_scaling") else X_test
    preds = model.predict(X_test_input)
    probs = model.predict_proba(X_test_input)[:, 1]

    m = metrics_report(y_test, preds)
    print_metrics(f"Saved model ({metadata['model_type']})", m, len(y_test))

    failures = print_confident_failures("Saved model", y_test, preds, probs, id_test, binary_df)

    return {
        "metrics": m,
        "failures": failures,
        "split": (X_train, X_test, y_train, y_test, id_train, id_test),
    }


def section_ablation(binary_df, split):
    print("\n" + "=" * 70)
    print("SECTION 2 - ABLATION EXPERIMENT (cliche/transition features removed)")
    print("=" * 70)
    print(f"Removed features: {sorted(ABLATED_FEATURES)}")
    print(f"Remaining features: {len(ABLATION_FEATURE_NAMES)} (full model has {len(FEATURE_NAMES)})")

    X_train_full, X_test_full, y_train, y_test, id_train, id_test = split
    full_idx = {name: i for i, name in enumerate(FEATURE_NAMES)}
    keep = [full_idx[name] for name in ABLATION_FEATURE_NAMES]

    X_train = X_train_full[:, keep]
    X_test = X_test_full[:, keep]

    scaler = StandardScaler().fit(X_train)
    X_train_scaled = scaler.transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    ablation_model = LogisticRegression(max_iter=1000, random_state=RANDOM_SEED)
    ablation_model.fit(X_train_scaled, y_train)

    preds = ablation_model.predict(X_test_scaled)
    probs = ablation_model.predict_proba(X_test_scaled)[:, 1]

    m = metrics_report(y_test, preds)
    print_metrics("Ablation Model", m, len(y_test))

    print("\n--- Ablation Model: top 10 features by |coefficient| ---")
    coefs = ablation_model.coef_[0]
    for i in np.argsort(-np.abs(coefs))[:10]:
        print(f"  {ABLATION_FEATURE_NAMES[i]:30s} {coefs[i]:+.4f}")

    failures = print_confident_failures("Ablation model", y_test, preds, probs, id_test, binary_df)

    return {"metrics": m, "failures": failures}


def section_polished(polished_df):
    print("\n" + "=" * 70)
    print("SECTION 3 - POLISHED ESSAY EVALUATION (reference only, no ground truth)")
    print("=" * 70)

    model, scaler, feature_names, metadata = load_classifier()
    X = polished_df[FEATURE_NAMES].values
    X_input = scaler.transform(X) if metadata.get("requires_scaling") else X
    probs = model.predict_proba(X_input)[:, 1]
    scores = np.round(probs * 100, 1)

    for essay_id, score in zip(polished_df["essay_id"], scores):
        print(f"  {essay_id}: {score}/100")

    print(f"\nmean score: {scores.mean():.1f}")
    print(f"min score:  {scores.min():.1f}  ({polished_df['essay_id'].iloc[scores.argmin()]})")
    print(f"max score:  {scores.max():.1f}  ({polished_df['essay_id'].iloc[scores.argmax()]})")

    # Qualitative sentence-level evidence for the min- and max-scoring polished essays.
    dataset = build_dataset()
    for label, i in [("lowest-scoring", scores.argmin()), ("highest-scoring", scores.argmax())]:
        essay_id = polished_df["essay_id"].iloc[i]
        text = dataset.loc[dataset["essay_id"] == essay_id, "text"].iloc[0]
        result = analyze_essay(text)
        print(f"\n  {label} polished essay ({essay_id}, {scores[i]}/100):")
        top_sentence = max(result["sentences"], key=lambda s: s["score"])
        print(f"    highest-signal sentence ({top_sentence['score']}/100): {top_sentence['text']!r}")
        print(f"    top feature: {top_sentence['top_features'][0]['name']} — {top_sentence['top_features'][0]['plain_language_note']}")

    return {"scores": scores.tolist(), "mean": float(scores.mean()), "min": float(scores.min()), "max": float(scores.max())}


def main():
    binary_df, polished_df = load_binary_dataset()

    official = section_official_evaluation(binary_df)
    ablation = section_ablation(binary_df, official["split"])
    polished = section_polished(polished_df)

    print("\n" + "=" * 70)
    print("SECTION 4 - FULL MODEL vs ABLATION MODEL")
    print("=" * 70)
    fm, am = official["metrics"], ablation["metrics"]
    print(f"{'metric':12s} {'full model':>12s} {'ablation model':>16s}")
    for key in ("accuracy", "precision", "recall", "f1"):
        print(f"{key:12s} {fm[key]:12.3f} {am[key]:16.3f}")

    drop = fm["f1"] - am["f1"]
    if drop > 0.15:
        print(
            f"\nF1 dropped by {drop:.3f} when the cliche/transition features were removed. "
            "This indicates the development-set result depends heavily on those "
            "deliberately hand-injected artifacts, not just on genuine linguistic signal."
        )
    else:
        print(
            f"\nF1 changed by only {drop:+.3f} when the cliche/transition features were "
            "removed. The model retains useful signal from the remaining measurements "
            "(perplexity, burstiness, sentence rhythm, vocabulary richness, POS "
            "entropy, function-word patterns) even without the cliche/transition crutch."
        )

    print("\n" + "=" * 70)
    print("SECTION 5 - ESL / FAIRNESS EVALUATION")
    print("=" * 70)
    print("ESL fairness evaluation: NOT YET ESTABLISHED.")
    print(
        "No controlled ESL-authored evaluation subset currently exists in this "
        "dataset, so no quantitative ESL false-positive comparison can be "
        "honestly reported. This is a known, documented limitation. Future "
        "evaluation should include human-written essays from writers who "
        "learned English as a second language before any fairness claim is made."
    )


if __name__ == "__main__":
    main()
