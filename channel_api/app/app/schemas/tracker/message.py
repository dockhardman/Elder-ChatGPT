import databases
import ormar
import sqlalchemy

from app.config import settings


message_database = databases.Database(settings.tracker_store_service_url)
message_metadata = sqlalchemy.MetaData()


class MessageBaseMeta(ormar.ModelMeta):
    metadata = message_metadata
    database = message_database


class Message(ormar.Model):
    class Meta(MessageBaseMeta):
        tablename = "TrackerStoreMessage"

    id: int = ormar.Integer(primary_key=True)
    text: str = ormar.String(
        max_length=4096,
        encrypt_secret=settings.tracker_store_message_encrypt_secret,
        encrypt_backend=ormar.EncryptBackends.FERNET,
    )
