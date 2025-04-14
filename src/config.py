import os

from dotenv import load_dotenv


def config() -> dict:
    """
    Конфига
    """
    load_dotenv()

    db_conf = {
        "user": os.getenv("DB_USER"),
        "host": os.getenv("HOST"),
        "port": os.getenv("PORT"),
        "password": os.getenv("PASSWORD"),
    }
    return db_conf
