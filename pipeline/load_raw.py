from datetime import datetime

from db import get_engine
from extract import extract_applications, extract_sis


def make_run_id():
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


def load_raw(df, table, run_id, engine):
    df["run_id"] = run_id
    df.to_sql(table, engine,schema="raw", if_exists="append", index=False)


if __name__ == "__main__":
    engine = get_engine()
    run_id = make_run_id()

    load_raw(extract_applications(), "applications", run_id, engine)
    load_raw(extract_sis(), "sis_students", run_id, engine)
    print(f"loaded run {run_id}")
