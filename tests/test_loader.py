import json

import joblib
import pytest

from app.models.loader import DEFAULT_MODEL_PATH, ModelLoader
from training.train import build_pipeline


@pytest.fixture
def tiny_model(tmp_path):
    """Train a throwaway model and write it with metadata to tmp_path."""
    pipeline = build_pipeline().fit(
        ["free prize call now", "see you at lunch", "win cash now", "meeting at 3pm"],
        [1, 0, 1, 0],
    )
    path = tmp_path / "tiny.joblib"
    joblib.dump(pipeline, path)
    path.with_suffix(".json").write_text(json.dumps({"version": "tiny-test"}))
    return path


def test_default_path_is_repo_models_dir(monkeypatch):
    monkeypatch.delenv("MODEL_PATH", raising=False)
    assert ModelLoader().model_path == DEFAULT_MODEL_PATH


def test_loads_model_from_env_path(monkeypatch, tiny_model):
    monkeypatch.setenv("MODEL_PATH", str(tiny_model))
    loader = ModelLoader()
    loader.load()
    assert loader.model_version == "tiny-test"
    assert 0.0 <= loader.predict("free prize") <= 1.0


def test_missing_model_file_raises(monkeypatch, tmp_path):
    monkeypatch.setenv("MODEL_PATH", str(tmp_path / "missing.joblib"))
    with pytest.raises(FileNotFoundError):
        ModelLoader().load()


def test_fail_model_load_hook(monkeypatch):
    monkeypatch.setenv("FAIL_MODEL_LOAD", "true")
    with pytest.raises(RuntimeError):
        ModelLoader().load()


def test_predict_before_load_raises():
    with pytest.raises(RuntimeError):
        ModelLoader().predict("hello")
