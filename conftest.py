import sys
import os

# Ensure the project root is on sys.path so 'app' is importable
# regardless of which Python environment's pytest is invoked.
sys.path.insert(0, os.path.dirname(__file__))
