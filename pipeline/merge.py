import pandas as pd
from sqlalchemy import text

from db import get_engine


def read_clustered(engine):
    # every stage record, with its cluster_id attached
    sql = """
        SELECT c.cluster_id, r.*
        FROM stage.records r
        JOIN stage.clusters c ON c.record_id = r.record_id
    """
    return pd.read_sql(text(sql), engine)


def pick_winners(df):
    # SIS wins; otherwise the most recent application wins
    df["is_sis"] = df["source"] == "sis"
    df = df.sort_values(
        ["cluster_id", "is_sis", "submitted_at"],
        ascending=[True, False, False],
    )
    return df.drop_duplicates("cluster_id", keep="first")


if __name__ == "__main__":
    engine = get_engine()
    df = read_clustered(engine)
    people = pick_winners(df)
    print(len(people))
    print(people[people["first_name"] == "Allison"][["cluster_id", "source", "first_name", "last_name"]])
