from pathlib import Path

from sqlalchemy import text

from db import get_engine
from merge import read_clustered, pick_winners

SQL_FILE = Path(__file__).resolve().parent.parent / "sql" / "002_core.sql"

UPSERT_PERSON = """
    INSERT INTO core.person (person_key, first_name, last_name, email, phone, birth_date, state, updated_at)
    VALUES (:person_key, :first_name, :last_name, :email, :phone, CAST(:birth_date AS DATE), :state, now())
    ON CONFLICT (person_key) DO UPDATE SET
        first_name = EXCLUDED.first_name,
        last_name = EXCLUDED.last_name,
        email = EXCLUDED.email,
        phone = EXCLUDED.phone,
        birth_date = EXCLUDED.birth_date,
        state = EXCLUDED.state,
        updated_at = now()
"""

UPSERT_LINK = """
    INSERT INTO core.source_link (source, source_id, person_key)
    VALUES (:source, :source_id, :person_key)
    ON CONFLICT (source, source_id) DO UPDATE SET person_key = EXCLUDED.person_key
"""


def create_tables(engine):
    statements = [s for s in SQL_FILE.read_text().split(";") if s.strip()]
    with engine.begin() as conn:
        for statement in statements:
            conn.execute(text(statement))


def make_person_keys(df):
    # SIS id if the person has one, otherwise their earliest application id
    keys = {}
    for cluster_id, group in df.groupby("cluster_id"):
        sis = group[group["source"] == "sis"]
        if len(sis) > 0:
            keys[cluster_id] = sis["source_id"].iloc[0]
        else:
            keys[cluster_id] = group["source_id"].min()
    return keys


def load_core(engine):
    df = read_clustered(engine)
    keys = make_person_keys(df)
    people = pick_winners(df)

    people["person_key"] = people["cluster_id"].map(keys)
    df["person_key"] = df["cluster_id"].map(keys)

    person_rows = people[["person_key", "first_name", "last_name", "email",
                          "phone", "birth_date", "state"]].to_dict("records")
    link_rows = df[["source", "source_id", "person_key"]].to_dict("records")

    with engine.begin() as conn:
        conn.execute(text(UPSERT_PERSON), person_rows)
        conn.execute(text(UPSERT_LINK), link_rows)
    return len(person_rows), len(link_rows)


if __name__ == "__main__":
    engine = get_engine()
    create_tables(engine)
    n_people, n_links = load_core(engine)
    print(f"core.person: {n_people} rows, core.source_link: {n_links} rows")
