import os
import re


# ── Keyword dictionaries with per-category weights ──────────────────

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

_CRITICAL_WEIGHT = 0.30
_HIGH_WEIGHT     = 0.18
_MEDIUM_WEIGHT   = 0.10


class ModelLoader:
    def __init__(self):
        self.model_version = "heuristic-1.0.0"
        self.loaded = False

    def load(self):
        if os.getenv("FAIL_MODEL_LOAD") == "true":
            raise RuntimeError("model load failed intentionally")
        self.loaded = True

    # ── Prediction ──────────────────────────────────────────────────

    def predict(self, text: str) -> float:
        """Return a risk score between 0.0 and 1.0 based on heuristics."""
        if not self.loaded:
            raise RuntimeError("model not loaded")

        lower = text.lower()
        score = 0.0

        # 1. Keyword matching (each unique hit adds its category weight)
        for kw in _CRITICAL_KEYWORDS:
            if kw in lower:
                score += _CRITICAL_WEIGHT

        for kw in _HIGH_KEYWORDS:
            if kw in lower:
                score += _HIGH_WEIGHT

        for kw in _MEDIUM_KEYWORDS:
            if kw in lower:
                score += _MEDIUM_WEIGHT

        # 2. Text-style signals
        #    Excessive CAPS (more than 60% uppercase letters → +0.10)
        alpha_chars = [c for c in text if c.isalpha()]
        if alpha_chars:
            caps_ratio = sum(1 for c in alpha_chars if c.isupper()) / len(alpha_chars)
            if caps_ratio > 0.6:
                score += 0.10

        #    Excessive exclamation / question marks → +0.05
        if text.count("!") + text.count("?") >= 3:
            score += 0.05

        #    URL-like patterns (common in phishing) → +0.08
        if re.search(r"https?://", lower):
            score += 0.08

        # 3. Ensure baseline minimum & clamp to [0.0, 1.0]
        if score == 0.0:
            score = 0.05          # safe baseline for benign text
        score = round(min(score, 1.0), 2)

        return score
