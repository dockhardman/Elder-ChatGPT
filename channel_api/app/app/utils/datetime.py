import datetime
import pytz
from typing import Text


def datetime_now(tz: Text = "UTC") -> datetime.datetime:
    """Get datetime now with timezone.

    Parameters
    ----------
    tz : Text, optional
        Timezone name, by default "UTC"

    Returns
    -------
    datetime.datetime
        Datetime now with timezone
    """

    datetime_utcnow = pytz.UTC.localize(datetime.datetime.utcnow())
    datetime_local = datetime_utcnow.astimezone(pytz.timezone(tz))
    return datetime_local
