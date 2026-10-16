from faker import Faker
from datetime import date
SEED = 42
N_PEOPLE = 2000

Faker.seed(SEED)
fake = Faker()


def make_people(n):
    people = []
    for i in range(1, n + 1):
        first = fake.first_name()
        last = fake.last_name()
        person = {
            "person_id": f"P{i:04d}",
            "first_name": first,
            "last_name": last,
            "email": f"{first.lower()}.{last.lower()}{i}@example.com",
            "phone": fake.numerify("##########"),
            "birth_date": fake.date_between(start_date=date(2007, 9, 1), end_date=date(2009, 8, 31)).isoformat(),
            "state": fake.state_abbr(),
        }
        
        people.append(person)
    return people


if __name__ == "__main__":
    people = make_people(N_PEOPLE)
    print(len(people))
    for p in people[:3]:
        print(p)
