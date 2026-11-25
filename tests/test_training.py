import json

from training.train import VERSION, build_pipeline, evaluate, load_dataset, save_artifacts

SAMPLE = (
    "ham\tsee you at lunch tomorrow\n"
    "spam\tWIN a free prize now, call 0800\n"
    "ham\tcan you send the report\tthanks\n"
    "\n"
    "spam\tclaim your free cash prize today\n"
)


def _write_sample(tmp_path):
    path = tmp_path / "sample.tsv"
    path.write_text(SAMPLE, encoding="utf-8")
    return path


def test_load_dataset_parses_labels_and_text(tmp_path):
    texts, labels = load_dataset(_write_sample(tmp_path))
    assert labels == [0, 1, 0, 1]
    assert texts[2] == "can you send the report\tthanks"  # tabs inside text are kept


def test_pipeline_returns_probabilities(tmp_path):
    texts, labels = load_dataset(_write_sample(tmp_path))
    model = build_pipeline().fit(texts, labels)
    probs = model.predict_proba(["free prize", "lunch tomorrow"])[:, 1]
    assert all(0.0 <= p <= 1.0 for p in probs)


def test_save_artifacts_writes_model_and_metadata(tmp_path):
    texts, labels = load_dataset(_write_sample(tmp_path))
    model = build_pipeline().fit(texts, labels)
    metrics = evaluate(model, texts, labels)
    save_artifacts(model, metrics, len(texts), tmp_path / "models")

    assert (tmp_path / "models" / f"{VERSION}.joblib").exists()
    meta = json.loads((tmp_path / "models" / f"{VERSION}.json").read_text())
    for key in ("version", "trained_at", "dataset", "rows", "precision", "recall", "f1"):
        assert key in meta
    assert meta["rows"] == 4
