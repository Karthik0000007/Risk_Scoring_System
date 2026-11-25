import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_schemas_import_without_warnings():
    """ScoreResponse.model_version must not trigger Pydantic's 'model_' namespace warning."""
    result = subprocess.run(
        [sys.executable, "-W", "error", "-c", "import app.schemas.score"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
