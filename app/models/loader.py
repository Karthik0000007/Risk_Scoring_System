import os

class ModelLoader:
    def __init__(self):
        self.model_version = "baseline-0.0.1"
        self.loaded = False

    def load(self):
        if os.getenv("FAIL_MODEL_LOAD") == "true":
            raise RuntimeError("model load failed intentionally")
        self.loaded = True

    def predict(self, text: str) -> float:
        if not self.loaded:
            raise RuntimeError("model not loaded")
        return 0.1
