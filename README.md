# Admissions data pipeline

An ETL pipeline that pulls applicant records from two systems with no shared ID (an application CSV export and a student records database), cleans them, works out which records belong to the same person, and loads one trusted record per applicant into PostgreSQL.

All data is synthetic, generated with Faker. No real student records are used anywhere in this project.

## How it works

```
applications.csv ─┐
                  ├─► raw ─► clean ─► match ─► merge ─► core.person
student DB ───────┘   (untouched,  (stage)  (tiers +   (one row     core.source_link
                       every run            clusters)   per person)
                       kept)
```

1. **Extract** reads the CSV and the SQLite database as text, so nothing gets changed on the way in.
2. **Raw load** stores an untouched copy of both sources in Postgres, stamped with a run ID. Old runs are kept as history.
3. **Clean** standardizes names, emails, phones, dates, and states, then stacks both sources into `stage.records`.
4. **Match** finds pairs of records for the same person using three SQL rules, then groups the pairs into people with union-find.
5. **Merge** picks one winning record per person: the student records system if the person is in it, otherwise their most recent application.
6. **Core load** upserts the result into `core.person` and `core.source_link`, so running the pipeline twice never creates duplicates.

## Results

Measured against a hidden answer key the pipeline never reads.

| Metric | Value |
|---|---|
| Source records | 3,621 |
| People found | 2,000 (true: 2,000) |
| Precision | 100% |
| Recall | 100% |

The generator injects duplicate applications (10%), new emails on reapplication, name typos (5%), changed phone numbers, and inconsistent formatting for names, phones, dates, and states. Full numbers are in [docs/benchmark.md](docs/benchmark.md).

## Matching rules

| Tier | Rule | Why it exists |
|---|---|---|
| 1 | Same email | Safest signal, catches most duplicates |
| 2 | Same birth date, last name, and first initial | Catches students who reapplied with a new email |
| 3 | Same birth date and phone | Catches students who changed email and also have a typo in their name |

Birth date alone is never enough. On this data it would have produced about 10,900 pairs, most of them strangers who share a birthday.

## Running it

Requires Docker and Python 3.

```bash
git clone https://github.com/kap2273/admissions-pipeline.git
cd admissions-pipeline
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

docker compose up -d           # start Postgres
python scripts/seed.py         # generate the synthetic data
python pipeline/run.py         # run the whole pipeline
python pipeline/evaluate.py    # score the matching
pytest                         # run the tests
```

## Project layout

```
compose.yaml          Postgres in Docker
scripts/seed.py       synthetic data generator with tunable error rates
sql/                  raw and core table definitions
pipeline/
  extract.py          read the CSV and SQLite sources
  load_raw.py         land untouched copies with a run ID
  clean.py            field cleaning functions
  stage.py            build stage.records
  match.py            matching tiers and clustering
  merge.py            pick one record per person
  load_core.py        upsert the final tables
  run.py              run every step in order
  evaluate.py         precision and recall against the answer key
tests/                unit tests for the cleaning functions
```

## Limitations

- The synthetic noise is moderate. Heavier typos would need a fuzzy name-matching tier.
- Each run reloads the full source data. That's fine at this size, but a larger system would load only new or changed rows.
- The state lookup only covers the states the generator uses.
