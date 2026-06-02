import sys
from pathlib import Path

# Ensure the project root is on sys.path so imports like
# `from app.app import app` work when running pytest.
ROOT = Path(__file__).resolve().parent.parent
root_str = str(ROOT)
if root_str not in sys.path:
    sys.path.insert(0, root_str)
