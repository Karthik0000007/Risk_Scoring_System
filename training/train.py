"""Train the content risk model on the SMS Spam Collection dataset.

Usage: python training/train.py
"""

import json
from datetime import datetime, timezone
from pathlib import Path

import joblib
import sklearn
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "data" / "SMSSpamCollection"
MODEL_DIR = ROOT / "models"
VERSION = "risk-v1"
DATASET_NAME = "SMS Spam Collection (UCI)"
SEED = 42


def load_dataset(path: Path) -> tuple[list[str], list[int]]:
    """Read 'label<TAB>text' lines. Returns texts and labels (spam=1, ham=0)."""
    texts, labels = [], []
    with open(path, encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            label, text = line.rstrip("\n").split("\t", 1)
            texts.append(text)
            labels.append(1 if label == "spam" else 0)
    return texts, labels


def build_pipeline() -> Pipeline:
    return Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2))),
        ("clf", LogisticRegression(max_iter=1000)),
    ])


def evaluate(model: Pipeline, texts: list[str], labels: list[int]) -> dict:
    """Precision, recall and F1 for the spam (risky) class."""
    predicted = model.predict(texts)
    return {
        "precision": round(precision_score(labels, predicted, pos_label=1), 4),
        "recall": round(recall_score(labels, predicted, pos_label=1), 4),
        "f1": round(f1_score(labels, predicted, pos_label=1), 4),
    }


def save_artifacts(model: Pipeline, metrics: dict, rows: int, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, out_dir / f"{VERSION}.joblib")
    metadata = {
        "version": VERSION,
        "trained_at": datetime.now(timezone.utc).date().isoformat(),
        "dataset": DATASET_NAME,
        "rows": rows,
        "sklearn_version": sklearn.__version__,
        **metrics,
    }
    (out_dir / f"{VERSION}.json").write_text(json.dumps(metadata, indent=2) + "\n")


def main() -> None:
    texts, labels = load_dataset(DATA_PATH)
    X_train, X_test, y_train, y_test = train_test_split(
        texts, labels, test_size=0.2, stratify=labels, random_state=SEED
    )
    model = build_pipeline().fit(X_train, y_train)
    metrics = evaluate(model, X_test, y_test)
    print(f"rows={len(texts)} train={len(X_train)} test={len(X_test)}")
    print(f"spam precision={metrics['precision']} recall={metrics['recall']} f1={metrics['f1']}")
    save_artifacts(model, metrics, len(texts), MODEL_DIR)
    print(f"saved {MODEL_DIR / VERSION}.joblib and .json")


if __name__ == "__main__":
    main()
