"""Add learner scope to an existing database. Back up the database before running."""
from sqlalchemy import inspect, text
from app.db.session import engine
from app.models.base_class import Base
from app import models

def migrate():
    Base.metadata.create_all(engine)
    columns = {c["name"] for c in inspect(engine).get_columns("masteryrecord")}
    if "learner_key" not in columns:
        with engine.begin() as connection:
            connection.execute(text("ALTER TABLE masteryrecord ADD COLUMN learner_key VARCHAR NOT NULL DEFAULT 'legacy'"))
if __name__ == "__main__":
    migrate()
