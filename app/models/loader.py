class ModelLoader:
    def __init__(self):
        self.model_version = "baseline-0.0.1"

    def load(self):
        # Placeholder for real model loading
        return True

    def predict(self, text: str) -> float:
        # Baseline heuristic
        return 0.1
