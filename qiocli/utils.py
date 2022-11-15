"""Helper functions."""
import datetime


def timestamp_to_half_hour_idx(timestamp):
    """Break down a timestamp to index by half hour in [0,47]."""
    return timestamp.hour * 2 + (0 if timestamp.minute < 30 else 1)


def form_gcal_office_hours_search():
    """Create query string to search for Office Hours."""
    now = datetime.datetime.now(datetime.timezone.utc)
    week_from_now = now + datetime.timedelta(days=6)
    return {
        "singleEvents": True,
        "q": "Office Hours",
        "timeMin": now.isoformat(),
        "timeMax": week_from_now.isoformat(),
        "orderBy": "startTime"
    }


def form_schedule(events):
    """Create office hours schedule 2d-array."""
    items = events['items']
    oh_sessions = filter(
        lambda x: x['status'] != 'cancelled' and 'Office Hours'
        in x['summary'], items)
    oh_sessions = list(oh_sessions)
    oh_sessions = [
        {
            "summary": x['summary'],
            "start": datetime.datetime.strptime(x['start']['dateTime'],
                                                "%Y-%m-%dT%H:%M:%S%z"),
            "end": datetime.datetime.strptime(x['end']['dateTime'],
                                              "%Y-%m-%dT%H:%M:%S%z")
        } for x in oh_sessions]
    schedule = [["c" for j in range(48)] for i in range(7)]
    for event in oh_sessions:
        start = timestamp_to_half_hour_idx(event['start'])
        end = timestamp_to_half_hour_idx(event['end'])
        # OH queue goes Sunday-Saturday
        day = (event['start'].weekday() + 1) % 7
        schedule[day][start:end] = ["o" for i in range(end - start)]
    return ["".join(x) for x in schedule]
