import pandas as pd
from sqlalchemy import text
from clean import normalize_name, normalize_email, normalize_phone, normalize_state, normalize_date

from db import get_engine

COLUMNS = ["source", "source_id", "first_name", "last_name", "email",
           "phone", "birth_date", "state", "submitted_at"]

CLEANERS = {"first_name": normalize_name,
            "last_name": normalize_name, 
            "email": normalize_email, 
            "phone": normalize_phone, 
            "state": normalize_state, 
            "birth_date": normalize_date}

def get_latest_run_id(engine):
    with engine.connect() as conn:
        result = conn.execute(text("SELECT MAX(run_id) FROM raw.applications"))
        return result.scalar()


def read_raw(table, run_id, engine):
    # read only this run's rows from raw.<table>
    return pd.read_sql(
        text(f"SELECT * FROM raw.{table} WHERE run_id = :run_id"),
        engine,
        params={"run_id": run_id},
    )


def shape_applications(apps):
    # label the source, rename the ID column, keep only COLUMNS
    apps["source"]="applications"
    apps = apps.rename(columns={"application_id": "source_id"})
    return apps[COLUMNS]


def shape_sis(sis):
    # same idea, plus SIS has no submitted_at
    sis["source"]="sis"
    sis = sis.rename(columns={"sis_id": "source_id"})
    sis["submitted_at"] = None
    return sis[COLUMNS]


def clean_records(records):
    for col, cleaner in CLEANERS.items():
        records[col] = records[col].apply(cleaner)
    return records


def save_records(records, engine):
    records.insert(0, "record_id", range(1, len(records) + 1))
    with engine.begin() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS ____"))
    records.to_sql("____", engine, schema="____", if_exists="replace", index=False)


if __name__ == "__main__":
    engine = get_engine()
    run_id = get_latest_run_id(engine)
    apps = read_raw("applications", run_id, engine)
    sis = read_raw("sis_students", run_id, engine)
    print(run_id, len(apps), len(sis))

    records = pd.concat([shape_applications(apps), shape_sis(sis)], ignore_index=True)
    records = clean_records(records)
    save_records(records, engine)
    print(f"saved {len(records)} rows")
