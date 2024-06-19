import os
from dotenv import load_dotenv
from database import postgres_handler

ROOT_DIR = os.getcwd()

load_dotenv()

POSTGRES_HOST = "34.229.145.119"
POSTGRES_PORT = "5432"
POSTGRES_DATABASE = "fourel"
POSTGRES_USER = "foureluser"
POSTGRES_PASSWORD = "X7FdZy0OfUPnj7Q"


# sqlite = sqlite_handler.SQLiteHandler(
#     os.path.join(ROOT_DIR, "database", "fourel_ai.db"))

postgres = postgres_handler.PostgresHandler(
    database=POSTGRES_DATABASE,
    user=POSTGRES_USER,
    password=POSTGRES_PASSWORD,
    host=POSTGRES_HOST,
    port=POSTGRES_PORT
)
