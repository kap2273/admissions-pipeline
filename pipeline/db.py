import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()


def get_engine():
    # build the login line from the .env values
    url = (
        f"postgresql+psycopg://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}"
        f"@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"
    )
    return create_engine(url)


if __name__ == "__main__":
    engine = get_engine()
    with engine.connect() as conn:
        count = conn.execute(text("SELECT count(*) FROM raw.applications")).scalar()
    print(count)
