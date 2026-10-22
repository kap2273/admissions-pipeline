import subprocess
import sys
from pathlib import Path

from sqlalchemy import text

from db import get_engine

PIPELINE_DIR = Path(__file__).resolve().parent
STEPS = ["load_raw.py", "stage.py", "match.py", "load_core.py"]


def run_step(name):
    print(f"--- {name}")
    subprocess.run([sys.executable, str(PIPELINE_DIR / name)], check=True)


def summary(engine):
    with engine.connect() as conn:
        people = conn.execute(text("SELECT count(*) FROM core.person")).scalar()
        links = conn.execute(text("SELECT count(*) FROM core.source_link")).scalar()
    print(f"done: {links} source records → {people} people")


if __name__ == "__main__":
    for step in STEPS:
        run_step(step)
    summary(get_engine())
