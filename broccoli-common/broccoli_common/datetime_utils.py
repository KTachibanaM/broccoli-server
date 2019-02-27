import datetime
import pytz


def milliseconds_to_datetime(milliseconds: int) -> datetime.datetime:
    return datetime.datetime.utcfromtimestamp(milliseconds // 1000).replace(microsecond=milliseconds % 1000 * 1000)


def datetime_to_milliseconds(dt: datetime.datetime) -> int:
    return int(dt.replace(tzinfo=pytz.utc).timestamp() * 1000)
