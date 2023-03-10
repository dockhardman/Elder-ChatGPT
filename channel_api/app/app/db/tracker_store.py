from typing import Text

import databases
import sqlalchemy

from app.config import settings


message_database = databases.Database(settings.tracker_store_service_url)
message_metadata = sqlalchemy.MetaData()


def create_message_database(
    database_url: Text = str(message_database.url),
) -> None:
    engine = sqlalchemy.create_engine(database_url)
    message_metadata.create_all(engine)
