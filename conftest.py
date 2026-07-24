"""Makes operators/ importable from tests/ regardless of invocation directory
-- mirrors spotify_dag.py's own sys.path.append("/opt/airflow/operators")
for its (container-only) runtime environment."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "operators"))
