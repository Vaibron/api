import os

DATABASE_URL = os.environ.get("DATABASE_URL") or "postgresql://postgres:5981@localhost:5432/new_db"
BROKER_URL = os.environ.get("BROKER_URL") or "amqp://guest:guest@localhost:5672//"
