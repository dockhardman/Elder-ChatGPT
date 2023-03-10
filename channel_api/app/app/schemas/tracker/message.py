import datetime
import ormar
import sqlalchemy
from typing import Optional, Text

from app.config import settings
from app.db.tracker_store import message_metadata, message_database


class MessageBaseMeta(ormar.ModelMeta):
    metadata = message_metadata
    database = message_database


class Message(ormar.Model):
    class Meta(MessageBaseMeta):
        tablename = "TrackerStoreMessage"

    id: int = ormar.Integer(primary_key=True)
    message_type: Text = ormar.String(nullable=False, index=True, max_length=32)
    message_text: Optional[Text] = ormar.String(
        nullable=True,
        default=None,
        max_length=4096,
        encrypt_secret=settings.tracker_store_message_encrypt_secret,
        encrypt_backend=ormar.EncryptBackends.FERNET,
    )
    source_type: Text = ormar.String(nullable=False, index=True, max_length=32)
    source_user_id: Text = ormar.String(
        nullable=True, default=None, index=True, max_length=64
    )
    message_datetime: datetime.datetime = ormar.DateTime(
        nullable=False, index=True, timezone=True
    )


if __name__ == "__main__":
    engine = sqlalchemy.create_engine(settings.tracker_store_service_url)
    # message_metadata.drop_all(engine)
    message_metadata.create_all(engine)
