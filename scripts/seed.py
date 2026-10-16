import random
import sqlite3
from datetime import date, datetime, timedelta
from pathlib import Path

import pandas as pd
from faker import Faker

SEED = 42
N_PEOPLE = 2000

DUPLICATE_APPLICATION_RATE = 0.10  # applied twice
NEW_EMAIL_ON_REAPPLY_RATE = 0.50   # second application uses a new email
TYPO_RATE = 0.05                   # one-letter change in last name on an application
ADMITTED_SHARE = 0.70              # who ends up in SIS
SIS_PHONE_CHANGE_RATE = 0.15       # SIS has a newer phone than the application

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

STATES = {
    "MA": "Massachusetts", "NH": "New Hampshire", "NY": "New York",
    "CT": "Connecticut", "RI": "Rhode Island", "ME": "Maine",
    "VT": "Vermont", "NJ": "New Jersey", "PA": "Pennsylvania", "CA": "California",
}
STATE_WEIGHTS = [60, 8, 8, 5, 4, 4, 3, 3, 3, 2]  # mostly in-state
MAJORS = [
    "Computer Science", "Nursing", "Business", "Biology",
    "Mechanical Engineering", "Psychology", "Criminal Justice", "Undeclared",
]

Faker.seed(SEED)
random.seed(SEED)
fake = Faker()


def make_people(n):
    people = []
    for i in range(1, n + 1):
        first = fake.first_name()
        last = fake.last_name()
        birth = fake.date_between(start_date=date(2007, 9, 1), end_date=date(2009, 8, 31))
        person = {
            "person_id": f"P{i:04d}",
            "first_name": first,
            "last_name": last,
            "email": f"{first.lower()}.{last.lower()}{i}@example.com",
            "phone": fake.numerify("##########"),
            "birth_date": birth.isoformat(),
            "state": random.choices(list(STATES), weights=STATE_WEIGHTS)[0],
            "high_school": f"{fake.city()} High School",
        }
        people.append(person)
    return people


# --- mess-up functions: clean value in, messy value out ---

def mess_name(name):
    return random.choice([name, name, name.lower(), name.upper(), f" {name}", f"{name} "])


def add_typo(name):
    if len(name) < 3:
        return name
    pos = random.randint(1, len(name) - 1)
    letters = [c for c in "abcdefghijklmnopqrstuvwxyz" if c != name[pos].lower()]
    return name[:pos] + random.choice(letters) + name[pos + 1:]


def mess_email(email):
    return random.choice([email, email, email.upper(), email.title(), f" {email}"])


def mess_phone(digits):
    a, b, c = digits[:3], digits[3:6], digits[6:]
    return random.choice([digits, f"({a}) {b}-{c}", f"{a}.{b}.{c}", f"{a}-{b}-{c}", f"+1 {digits}"])


def mess_date(iso):
    d = date.fromisoformat(iso)
    return random.choice([d.strftime("%m/%d/%Y"), f"{d.month}/{d.day}/{d.year}"])


def mess_state(abbr):
    full = STATES[abbr]
    return random.choice([abbr, abbr.lower(), full, full.upper()])


# --- sources ---

def make_applications(people):
    rows = []
    latest = {}  # person_id -> email and term from their most recent application
    for p in people:
        first_time = fake.date_time_between(
            start_date=datetime(2026, 8, 1), end_date=datetime(2027, 1, 15)
        )
        times = [first_time]
        if random.random() < DUPLICATE_APPLICATION_RATE:
            gap = timedelta(days=random.randint(3, 45), minutes=random.randint(0, 600))
            times.append(first_time + gap)

        for n, submitted in enumerate(times):
            email = p["email"]
            if n == 1 and random.random() < NEW_EMAIL_ON_REAPPLY_RATE:
                email = f"{p['first_name'].lower()}{p['last_name'].lower()}{p['person_id'][1:]}@example.net"

            last = p["last_name"]
            if random.random() < TYPO_RATE:
                last = add_typo(last)

            term = random.choices(["Fall 2027", "Spring 2027"], weights=[85, 15])[0]
            rows.append({
                "person_id": p["person_id"],  # kept for truth.csv, not written to the CSV
                "first_name": mess_name(p["first_name"]),
                "last_name": mess_name(last),
                "email": mess_email(email),
                "phone": mess_phone(p["phone"]),
                "birth_date": mess_date(p["birth_date"]),
                "state": mess_state(p["state"]),
                "high_school": p["high_school"],
                "intended_major": random.choice(MAJORS),
                "term": term,
                "submitted_at": submitted.strftime("%Y-%m-%d %H:%M:%S"),
            })
            latest[p["person_id"]] = {"email": email, "term": term}

    # IDs follow submission order, like a real application system
    rows.sort(key=lambda r: r["submitted_at"])
    for i, row in enumerate(rows, start=1):
        row["application_id"] = f"A{i:05d}"
    return rows, latest


def make_sis(people, latest):
    admitted = [p for p in people if random.random() < ADMITTED_SHARE]
    random.shuffle(admitted)
    rows = []
    for i, p in enumerate(admitted, start=1):
        phone = p["phone"]
        if random.random() < SIS_PHONE_CHANGE_RATE:
            phone = fake.numerify("##########")
        rows.append({
            "person_id": p["person_id"],
            "sis_id": f"S{i:06d}",
            "first_name": p["first_name"],
            "last_name": p["last_name"],
            "birth_date": p["birth_date"],
            "email": latest[p["person_id"]]["email"],
            "phone": f"{phone[:3]}-{phone[3:6]}-{phone[6:]}",
            "state": p["state"],
            "admit_term": latest[p["person_id"]]["term"],
        })
    return rows


def save(applications, sis):
    DATA_DIR.mkdir(exist_ok=True)

    app_cols = ["application_id", "first_name", "last_name", "email", "phone", "birth_date",
                "state", "high_school", "intended_major", "term", "submitted_at"]
    pd.DataFrame(applications)[app_cols].to_csv(DATA_DIR / "applications.csv", index=False)

    sis_cols = ["sis_id", "first_name", "last_name", "birth_date", "email", "phone", "state", "admit_term"]
    db_path = DATA_DIR / "sis.db"
    db_path.unlink(missing_ok=True)
    conn = sqlite3.connect(db_path)
    pd.DataFrame(sis)[sis_cols].to_sql("students", conn, index=False)
    conn.close()

    truth = [{"source": "applications", "source_id": r["application_id"], "person_id": r["person_id"]}
             for r in applications]
    truth += [{"source": "sis", "source_id": r["sis_id"], "person_id": r["person_id"]} for r in sis]
    pd.DataFrame(truth).to_csv(DATA_DIR / "truth.csv", index=False)


if __name__ == "__main__":
    people = make_people(N_PEOPLE)
    applications, latest = make_applications(people)
    sis = make_sis(people, latest)
    save(applications, sis)

    print(f"true people:  {len(people)}")
    print(f"applications: {len(applications)}")
    print(f"sis students: {len(sis)}")
    print(f"files written to {DATA_DIR}")
