import pandas as pd
from sqlalchemy import text

from db import get_engine

TIERS = {
    1: """
        SELECT a.record_id AS left_id, b.record_id AS right_id
        FROM stage.records a
        JOIN stage.records b
          ON a.email = b.email AND a.record_id < b.record_id
        WHERE a.email IS NOT NULL
    """,
    2: """
        SELECT a.record_id AS left_id, b.record_id AS right_id
        FROM stage.records a
        JOIN stage.records b
          ON a.birth_date = b.birth_date AND 
          a.last_name = b.last_name AND 
          left(a.first_name,1) = left(b.first_name,1) AND 
          a.record_id < b.record_id;
    """,
    3: """
        SELECT a.record_id AS left_id, b.record_id AS right_id
        FROM stage.records a
        JOIN stage.records b
          ON a.birth_date = b.birth_date AND 
          a.phone = b.phone AND 
          a.record_id < b.record_id;
    """,
}


def find_pairs(engine):
    frames = []
    for tier, sql in TIERS.items():
        pairs = pd.read_sql(text(sql), engine)
        pairs["tier"] = tier
        frames.append(pairs)
    all_pairs = pd.concat(frames, ignore_index=True)
    # keep each pair once, credited to the strictest tier that found it
    return all_pairs.sort_values("tier").drop_duplicates(["left_id", "right_id"])

def find (parent,x):
    if parent[x] != x:
        parent[x] = find(parent,parent[x])
    return parent[x]


def union(parent,a,b):
    root_a = find(parent,a)
    root_b = find(parent,b)
    if root_a != root_b:
        parent[max(root_a,root_b)] = min(root_a,root_b)


def assign_clusters(record_ids, pairs):
    parent = {r: r for r in record_ids}
    for a, b in zip(pairs["left_id"], pairs["right_id"]):
        union(parent, a, b)
    return {r: find(parent, r) for r in record_ids}


def save_clusters(clusters, engine):
    df = pd.DataFrame(list(clusters.items()), columns=["record_id", "cluster_id"])
    df.to_sql("clusters", engine, schema="stage", if_exists="replace", index=False)


if __name__ == "__main__":
    engine = get_engine()
    pairs = find_pairs(engine)
    record_ids = pd.read_sql(text("SELECT record_id FROM stage.records"), engine)["record_id"]
    clusters = assign_clusters(record_ids, pairs)
    save_clusters(clusters, engine)
    print(f"{len(record_ids)} records → {len(set(clusters.values()))} people")
