create schema raw;
create table raw.applications(
    run_id     TEXT NOT NULL,
    loaded_at  TIMESTAMP NOT NULL DEFAULT now(),
    application_id text,
    first_name text,
    last_name text,
    email text,
    phone text,
    birth_date text,
    state text,
    high_school text,
    intended_major text,
    term text,
    submitted_at text
);

create table raw.sis_students(
    run_id     TEXT NOT NULL,
    loaded_at  TIMESTAMP NOT NULL DEFAULT now(),
    sis_id text,
    first_name text,
    last_name text,
    birth_date text,
    email text,
    phone text,
    state text,
    admit_term text
);
