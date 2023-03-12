import datetime
import ormar
import sqlalchemy
from typing import Optional, Text, TYPE_CHECKING

from app.config import settings
from app.db.tracker_store import message_metadata, message_database
from app.utils.datetime import datetime_now

if TYPE_CHECKING:
    from linebot.models import SourceUser, TextMessage


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
    source_type: Text = ormar.String(
        nullable=False, index=True, max_length=32
    )  # user, bot
    source_user_id: Text = ormar.String(
        nullable=True, default=None, index=True, max_length=64
    )
    message_datetime: datetime.datetime = ormar.DateTime(
        nullable=False, index=True, timezone=True
    )

    @classmethod
    def from_line_text_message(cls, text_message: "TextMessage", source: "SourceUser"):
        message = cls(
            message_type=text_message.type,
            message_text=text_message.text,
            source_type=source.type,
            source_user_id=source.user_id,
            message_datetime=datetime_now(tz=settings.app_timezone),
        )
        return message


if __name__ == "__main__":
    engine = sqlalchemy.create_engine(settings.tracker_store_service_url)
    # message_metadata.drop_all(engine)
    message_metadata.create_all(engine)
