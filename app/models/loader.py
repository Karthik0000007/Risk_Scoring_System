import json
import os
import re
from pathlib import Path

import joblib

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MODEL_PATH = ROOT / "models" / "risk-v1.joblib"


class ModelLoader:
    """Loads the trained scikit-learn pipeline and returns spam probabilities."""

    def __init__(self):
        self.model_path = Path(os.getenv("MODEL_PATH", str(DEFAULT_MODEL_PATH)))
        self.model_version = "unloaded"
        self.pipeline = None
        self.loaded = False
        self.load_error: str | None = None

    def load(self):
        """Load the pipeline and metadata. Records the error and re-raises on failure."""
        self.loaded = False
        self.load_error = None
        try:
            if os.getenv("FAIL_MODEL_LOAD") == "true":
                raise RuntimeError("model load failed intentionally")
            self.pipeline = joblib.load(self.model_path)
            metadata = json.loads(self.model_path.with_suffix(".json").read_text())
            self.model_version = metadata["version"]
        except Exception as e:
            self.load_error = f"{type(e).__name__}: {e}"
            raise
        self.loaded = True

    def predict(self, text: str) -> float:
        """Return the probability (0.0 to 1.0) that the text is spam."""
        if not self.loaded:
            raise RuntimeError("model not loaded")
        return float(self.pipeline.predict_proba([text])[0][1])


# ── Keyword fallback, used only when the model fails at runtime ─────

_CRITICAL_KEYWORDS = [
    "kill", "bomb", "attack", "murder", "shoot", "destroy", "terror",
    "explode", "weapon", "assassinate", "massacre", "kidnap", "hostage",
    "suicide", "detonate",
]

_HIGH_KEYWORDS = [
    "hack", "steal", "fraud", "phishing", "malware", "ransomware",
    "exploit", "breach", "credential", "password", "scam", "launder",
    "trafficking", "abuse", "threat", "harass", "stalk", "blackmail",
    "extort", "illegal",
]

_MEDIUM_KEYWORDS = [
    "urgent", "verify", "suspend", "click here", "act now", "limited time",
    "account", "expire", "confirm", "login", "SSN", "credit card",
    "bank", "wire transfer", "prize", "winner", "congratulations",
    "free money", "risk", "warning", "alert", "danger",
]


def _compile(keywords: list[str]) -> list[re.Pattern]:
    """Whole-word, case-insensitive patterns, so 'skill' does not match 'kill'."""
    return [re.compile(rf"\b{re.escape(kw)}\b", re.IGNORECASE) for kw in keywords]


class KeywordFallback:
    """Rule-based scorer with whole-word keyword matching."""

    version = "keyword-fallback-1.0"

    _RULES = [
        (_compile(_CRITICAL_KEYWORDS), 0.30),
        (_compile(_HIGH_KEYWORDS), 0.18),
        (_compile(_MEDIUM_KEYWORDS), 0.10),
    ]

    def predict(self, text: str) -> float:
        """Return a risk score between 0.0 and 1.0."""
        score = self._keyword_score(text) + self._style_score(text)
        if score == 0.0:
            score = 0.05  # safe baseline for benign text
        return round(min(score, 1.0), 2)

    def _keyword_score(self, text: str) -> float:
        return sum(
            weight
            for patterns, weight in self._RULES
            for pattern in patterns
            if pattern.search(text)
        )

    @staticmethod
    def _style_score(text: str) -> float:
        score = 0.0
        letters = [c for c in text if c.isalpha()]
        if letters and sum(c.isupper() for c in letters) / len(letters) > 0.6:
            score += 0.10  # excessive CAPS
        if text.count("!") + text.count("?") >= 3:
            score += 0.05  # excessive punctuation
        if re.search(r"https?://", text, re.IGNORECASE):
            score += 0.08  # URL, common in phishing
        return score


# Shared instances. The model is loaded by the lifespan handler in app/main.py.
model = ModelLoader()
fallback = KeywordFallback()
