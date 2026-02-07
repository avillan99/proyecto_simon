import json
from pathlib import Path
from html import escape

from .debug import debug_dump 

from collections import defaultdict
from datetime import date, datetime, timedelta


def build_weekly_calendar(schedules):
    days_order = ["LUNES", "MARTES", "MIERCOLES", "JUEVES", "VIERNES", "SABADO", "DOMINGO"]

    # calendar[time][day] = court_id
    calendar = defaultdict(dict)

    for s in schedules:
        time_slot = f"{s['SCHEDULE_START_HOUR'][:5]}-{s['SCHEDULE_END_HOUR'][:5]}"
        day = s["DAY_CODE"]
        court = s["SCENARY_DIVISION_DETAIL_PK"]

        calendar[time_slot][day] = court

    # ---- print grid ----
    header = "Time     | " + " | ".join(d[:3] for d in days_order)
    print(header)
    print("-" * len(header))

    for time in sorted(calendar):
        row = [time.ljust(8)]
        for day in days_order:
            cell = calendar[time].get(day, "")
            row.append(str(cell).ljust(3))
        print(" | ".join(row))

from collections import defaultdict
from html import escape

def schedules_to_html_table(schedules, title="Weekly schedules"):
    days_order = ["LUNES", "MARTES", "MIERCOLES", "JUEVES", "VIERNES", "SABADO", "DOMINGO"]
    day_labels = {"LUNES":"Mon","MARTES":"Tue","MIERCOLES":"Wed","JUEVES":"Thu","VIERNES":"Fri","SABADO":"Sat","DOMINGO":"Sun"}

    # calendar[time][day] = court_id
    calendar = defaultdict(dict)
    for s in schedules:
        time_slot = f"{s['SCHEDULE_START_HOUR'][:5]}-{s['SCHEDULE_END_HOUR'][:5]}"
        day = s["DAY_CODE"]
        court = s["SCENARY_DIVISION_DETAIL_PK"]  # your "court identifier"
        calendar[time_slot][day] = court

    times = sorted(calendar.keys())

    css = """
    <style>
      body { font-family: Arial, sans-serif; padding: 16px; }
      table { border-collapse: collapse; width: 100%; max-width: 900px; }
      th, td { border: 1px solid #ddd; padding: 10px; text-align: center; }
      th { background: #f5f5f5; }
      td.slot { background: #eaffea; font-weight: 600; }
      caption { caption-side: top; text-align: left; font-size: 18px; font-weight: 700; margin-bottom: 10px; }
    </style>
    """

    html = [f"<!doctype html><html><head><meta charset='utf-8'>{css}</head><body>"]
    html.append("<table>")
    html.append(f"<caption>{escape(title)}</caption>")

    # header row
    html.append("<thead><tr>")
    html.append("<th>Time</th>")
    for d in days_order:
        html.append(f"<th>{escape(day_labels.get(d, d[:3]))}</th>")
    html.append("</tr></thead>")

    # body rows
    html.append("<tbody>")
    for t in times:
        html.append("<tr>")
        html.append(f"<th>{escape(t)}</th>")
        for d in days_order:
            court = calendar[t].get(d)
            if court is None:
                html.append("<td></td>")
            else:
                html.append(f"<td class='slot'>{escape(str(court))}</td>")
        html.append("</tr>")
    html.append("</tbody></table></body></html>")

    return "".join(html)

from collections import defaultdict
from html import escape

def bookings_to_html_grid(bookings, court_id, title="Bookings"):
    """
    bookings: list[dict]
    court_id: int or str  (your explicit court identifier)
    """
    # Filter bookings to only include dates up to one month in the future
    today = datetime.now().date()
    one_month_future = today + timedelta(days=30)
    
    filtered_bookings = [
        b for b in bookings
        if today <= datetime.strptime(b["BOOKING_DATE"], "%Y-%m-%d").date() <= one_month_future
    ]
    
    # grid[time][date] = list of courts booked (in case multiple)
    grid = defaultdict(lambda: defaultdict(list))
    dates = set()
    times = set()

    for b in filtered_bookings:
        date = b["BOOKING_DATE"]  # "YYYY-MM-DD"
        time_slot = f"{b['SCHEDULE_START_HOUR'][:5]}-{b['SCHEDULE_END_HOUR'][:5]}"
        # court = court_id_fn(b)

        grid[time_slot][date].append(court_id)
        dates.add(date)
        times.add(time_slot)

    dates = sorted(dates)
    times = sorted(times)

    css = """
    <style>
      body { font-family: Arial, sans-serif; padding: 16px; }
      table { border-collapse: collapse; width: 100%; max-width: 1100px; }
      th, td { border: 1px solid #ddd; padding: 10px; text-align: center; vertical-align: top; }
      th { background: #f5f5f5; position: sticky; top: 0; }
      td.booked { background: #ffecec; font-weight: 600; }
      caption { caption-side: top; text-align: left; font-size: 18px; font-weight: 700; margin-bottom: 10px; }
      .small { font-size: 12px; font-weight: 500; opacity: 0.85; }
    </style>
    """

    html = [f"<!doctype html><html><head><meta charset='utf-8'>{css}</head><body>"]
    html.append("<table>")
    html.append(f"<caption>{escape(title)}</caption>")

    # header
    html.append("<thead><tr>")
    html.append("<th>Time</th>")
    for d in dates:
        html.append(f"<th>{escape(d)}</th>")
    html.append("</tr></thead>")

    # body
    html.append("<tbody>")
    for t in times:
        html.append("<tr>")
        html.append(f"<th>{escape(t)}</th>")

        for d in dates:
            courts = grid[t].get(d, [])
            if not courts:
                html.append("<td></td>")
            else:
                # If multiple bookings exist for the same cell, show them stacked.
                content = "<br>".join(escape(str(c)) for c in courts)
                html.append(f"<td class='booked'>{content}</td>")

        html.append("</tr>")
    html.append("</tbody></table></body></html>")

    return "".join(html)


def build_availability_grid(schedules, bookings, days_ahead=30):
    """
    Returns:
      grid[time_slot][date] = list[court_id]
      dates = list[date_str]
      times = list[time_slot]
    """

    daycode_to_weekday = {
        "LUNES": 0, "MARTES": 1, "MIERCOLES": 2, "JUEVES": 3,
        "VIERNES": 4, "SABADO": 5, "DOMINGO": 6
    }

    def tslot(d):
        return f"{d['SCHEDULE_START_HOUR'][:5]}-{d['SCHEDULE_END_HOUR'][:5]}"

    # 1) Weekly availability
    weekly = defaultdict(set)
    for s in schedules:
        wd = daycode_to_weekday[s["DAY_CODE"]]
        weekly[(wd, tslot(s))].add(int(s["SCENARY_DIVISION_DETAIL_PK"]))

    # 2) Booked slots
    blocked = defaultdict(set)
    for b in bookings:
        blocked[(b["BOOKING_DATE"], tslot(b))].add(int(b["SCENARY_DIVISION_DETAIL_PK"]))

    # 3) Date range
    start = date.today() + timedelta(days=1)
    dates = [(start + timedelta(days=i)) for i in range(days_ahead + 1)]
    date_strs = [d.isoformat() for d in dates]

    grid = defaultdict(dict)
    times_seen = set()

    for d in dates:
        wd = d.weekday()
        date_s = d.isoformat()

        for (w, time_slot), courts in weekly.items():
            if w != wd:
                continue

            available = courts - blocked.get((date_s, time_slot), set())
            if available:
                grid[time_slot][date_s] = sorted(available)
                times_seen.add(time_slot)

    return grid, date_strs, sorted(times_seen)

def availability_grid_to_html(grid, dates, times, title="Availability (next 30 days)"):
    css = """
    <style>
      body { font-family: Arial, sans-serif; padding: 16px; }
      table { border-collapse: collapse; width: 100%; max-width: 1200px; }
      th, td { border: 1px solid #ddd; padding: 8px; text-align: center; vertical-align: top; }
      th { background: #f5f5f5; position: sticky; top: 0; z-index: 1; }
      td.avail { background: #eaffea; font-weight: 600; }
      caption { caption-side: top; text-align: left; font-size: 18px; font-weight: 700; margin-bottom: 10px; }
      .court { display: inline-block; margin: 2px 4px; padding: 2px 6px; border: 1px solid #cfe9cf; border-radius: 10px; }
    </style>
    """

    html = [f"<!doctype html><html><head><meta charset='utf-8'>{css}</head><body>"]
    html.append("<table>")
    html.append(f"<caption>{escape(title)}</caption>")

    # header
    html.append("<thead><tr>")
    html.append("<th>Time</th>")
    for d in dates:
        html.append(f"<th>{escape(d)}</th>")
    html.append("</tr></thead>")

    # body
    html.append("<tbody>")
    for t in times:
        html.append("<tr>")
        html.append(f"<th>{escape(t)}</th>")
        for d in dates:
            courts = grid.get(t, {}).get(d, [])
            if not courts:
                html.append("<td></td>")
            else:
                pills = "".join(f"<span class='court'>{escape(str(c))}</span>" for c in courts)
                html.append(f"<td class='avail'>{pills}</td>")
        html.append("</tr>")
    html.append("</tbody></table></body></html>")

    return "".join(html)


def bind_schedules_and_bookings(divisions_data: dict[int, dict]) -> tuple[list, list]:
    schedules = []
    bookings = []
    for division_pk in divisions_data.keys():
        print(f"Accumulating data for division_pk={division_pk}...")
        if "schedules" not in divisions_data[division_pk]:
            print(f"  No schedules found for division_pk={division_pk}, skipping.")
            continue
        if "bookings" not in divisions_data[division_pk]:
            print(f"  No bookings found for division_pk={division_pk}, skipping.")
            continue
        schedules.extend(divisions_data[division_pk]["schedules"])
        for booking in divisions_data[division_pk]["bookings"]:
            booking["SCENARY_DIVISION_DETAIL_PK"] = division_pk  # add court id to each booking
            bookings.append(booking)
    debug_dump(schedules, "schedules_combined", as_csv=True)
    debug_dump(bookings, "bookings_combined", as_csv=True)
    return schedules, bookings


def generate_availability_html(divisions_data: dict[int, dict]) -> None:
    
    bind_schedules_and_bookings(divisions_data)

    with open("debug/schedules_combined.json", "r", encoding="utf-8") as f:
        schedules_input = json.load(f)

    with open("debug/bookings_combined.json", "r", encoding="utf-8") as f:
        bookings_input = json.load(f)

    grid, dates, times = build_availability_grid(
        schedules=schedules_input,
        bookings=bookings_input,
        days_ahead=30,
    )

    html = availability_grid_to_html(grid, dates, times, title="Available courts (next 30 days)")
    results_dir = Path("results")
    results_dir.mkdir(parents=True, exist_ok=True)
    (results_dir / "availability.html").write_text(html, encoding="utf-8")
    print("✅ Availability HTML generated at results/availability.html")
