import os
import sys

import pytest

# Ensure the project root is on sys.path so 'app' is importable
# regardless of which Python environment's pytest is invoked.
sys.path.insert(0, os.path.dirname(__file__))


@pytest.fixture
def client():
    """TestClient as a context manager, so the lifespan handler loads the model."""
    from fastapi.testclient import TestClient

    from app.main import app

    with TestClient(app) as c:
        yield c
