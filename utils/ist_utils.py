"""
IST (Indian Standard Time) conversion utilities.
All times in the app should be shown in IST for the target audience.
"""

from datetime import datetime
import pytz
import pandas as pd

IST = pytz.timezone("Asia/Kolkata")
UTC = pytz.UTC


def convert_to_ist(dt_utc: datetime | pd.Timestamp | str) -> str:
    """Convert a UTC datetime (or string) to formatted IST string."""
    if isinstance(dt_utc, str):
        dt_utc = pd.to_datetime(dt_utc, errors="coerce")
    if pd.isna(dt_utc):
        return "TBD"
    if isinstance(dt_utc, pd.Timestamp):
        if dt_utc.tz is None:
            dt_utc = dt_utc.tz_localize(UTC)
        dt_ist = dt_utc.tz_convert(IST)
    else:
        if dt_utc.tzinfo is None:
            dt_utc = UTC.localize(dt_utc)
        dt_ist = dt_utc.astimezone(IST)
    return dt_ist.strftime("%d %b %Y, %I:%M %p IST")


def get_current_ist() -> datetime:
    return datetime.now(IST)


def parse_match_datetime(date_str: str, time_str: str) -> pd.Timestamp | None:
    """Safely parse date + time from openfootball style data."""
    try:
        time_clean = pd.Series([time_str]).str.extract(r"(\d{2}:\d{2})")[0].iloc[0]
        return pd.to_datetime(
            f"{date_str} {time_clean}", format="%Y-%m-%d %H:%M", errors="coerce"
        )
    except Exception:
        return None
