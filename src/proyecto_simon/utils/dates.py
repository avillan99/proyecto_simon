
from datetime import date, timedelta


def nearest_future_friday(d: date | None = None) -> date:
    d = d or date.today()
    days_ahead = (4 - d.weekday()) % 7  # Friday=4
    if days_ahead == 0:
        days_ahead = 7  # strictly future
    return d + timedelta(days=days_ahead)