"""Build one calendar file per housemate (cal/<name>.ics).

Each of their weeks becomes a Thursday 6 PM event with a phone alert,
matching the rotation shown on index.html. Run: python3 make_calendars.py
"""
import datetime as dt
import os

A = ["Favour", "Wahab", "Tanaka", "Bernard"]
B = ["Wahab", "Favour", "Bernard", "Tanaka"]
START = dt.date(2026, 11, 20)  # Fri Nov 20, 2026 (already done)
WEEKS = 53

VTIMEZONE = """BEGIN:VTIMEZONE
TZID:America/Toronto
BEGIN:DAYLIGHT
TZOFFSETFROM:-0500
TZOFFSETTO:-0400
TZNAME:EDT
DTSTART:19700308T020000
RRULE:FREQ=YEARLY;BYMONTH=3;BYDAY=2SU
END:DAYLIGHT
BEGIN:STANDARD
TZOFFSETFROM:-0400
TZOFFSETTO:-0500
TZNAME:EST
DTSTART:19701101T020000
RRULE:FREQ=YEARLY;BYMONTH=11;BYDAY=1SU
END:STANDARD
END:VTIMEZONE"""


def fold(line):
    """Wrap long lines at 73 chars, as the calendar format requires."""
    parts = [line[:73]]
    rest = line[73:]
    while rest:
        parts.append(" " + rest[:72])
        rest = rest[72:]
    return "\r\n".join(parts)


def name_for(i):
    return (A if (i // 4) % 2 == 0 else B)[i % 4]


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    out = os.path.join(here, "cal")
    os.makedirs(out, exist_ok=True)
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    events = {n: [] for n in A}
    for i in range(1, WEEKS):  # skip Nov 20 (done)
        fri = START + dt.timedelta(weeks=i)
        thu = fri - dt.timedelta(days=1)
        garbage = i % 2 == 1
        bins = "green + blue bins + garbage" if garbage else "green + blue bins"
        title = "Trash night: " + bins
        desc = (f"Your turn. Put out the {bins} tonight after 6 PM. "
                f"Pickup Friday {fri.strftime('%b')} {fri.day} at 7 AM. "
                "Bring the bins back in on Friday.")
        if garbage:
            desc += " Garbage: max 4 bags."
        d = thu.strftime("%Y%m%d")
        n = name_for(i)
        events[n].append("\r\n".join([
            "BEGIN:VEVENT",
            f"UID:trash-{n.lower()}-{d}@trash-roster",
            f"DTSTAMP:{stamp}",
            f"DTSTART;TZID=America/Toronto:{d}T180000",
            f"DTEND;TZID=America/Toronto:{d}T181500",
            fold(f"SUMMARY:{title}"),
            fold(f"DESCRIPTION:{desc}"),
            "BEGIN:VALARM",
            "ACTION:DISPLAY",
            f"DESCRIPTION:{title}",
            "TRIGGER:PT0M",
            "END:VALARM",
            "END:VEVENT",
        ]))
    for n, evs in events.items():
        body = "\r\n".join([
            "BEGIN:VCALENDAR",
            "VERSION:2.0",
            "PRODID:-//Hetherington//Trash Roster//EN",
            "CALSCALE:GREGORIAN",
            "METHOD:PUBLISH",
            f"X-WR-CALNAME:Trash roster ({n})",
            "X-WR-TIMEZONE:America/Toronto",
            VTIMEZONE.replace("\n", "\r\n"),
            *evs,
            "END:VCALENDAR",
        ]) + "\r\n"
        with open(os.path.join(out, f"{n.lower()}.ics"), "w", newline="") as f:
            f.write(body)
        print(f"{n}: {len(evs)} reminders")


if __name__ == "__main__":
    main()
