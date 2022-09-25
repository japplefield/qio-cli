import requests
import os
import urllib
import datetime
import sys
import json

# GCAL_BASE_URL
# OH_BASE_URL


def get_calendar_events(api_key, cal_id):
    base_url = "https://www.googleapis.com/calendar/v3/calendars"
    events_url = f"{base_url}/{cal_id}/events"
    now = datetime.datetime.now(datetime.timezone.utc)
    week_from_now = now + datetime.timedelta(weeks=1)
    query = urllib.parse.urlencode({
        "key": api_key,
        "singleEvents": True,
        "q": "Office Hours",
        "timeMin": now.isoformat(),
        "timeMax": week_from_now.isoformat(),
        "orderBy": "startTime"
    })
    full_url = f"{events_url}?{query}"
    return requests.get(full_url).json()


def timestamp_to_half_hour_idx(timestamp):
    return timestamp.hour * 2 + (0 if timestamp.minute < 30 else 1)


def form_schedule(events):
    items = events['items']
    oh_sessions = filter(
        lambda x: x['status'] != 'cancelled' and 'Office Hours' in x['summary'], items)
    oh_sessions = list(oh_sessions)
    oh_sessions = [{
        "summary": x['summary'],
        "start": datetime.datetime.strptime(x['start']['dateTime'], "%Y-%m-%dT%H:%M:%S%z"),
        "end": datetime.datetime.strptime(x['end']['dateTime'], "%Y-%m-%dT%H:%M:%S%z")}
        for x in oh_sessions]
    schedule = [["c" for j in range(48)] for i in range(7)]
    for event in oh_sessions:
        start = timestamp_to_half_hour_idx(event['start'])
        end = timestamp_to_half_hour_idx(event['end'])
        # OH queue goes Sunday-Saturday
        day = (event['start'].weekday() + 1) % 7
        schedule[day][start:end] = ["o" for i in range(end - start)]
    return ["".join(x) for x in schedule]


def put_schedule(oh_queue_id, oh_session, schedule):
    base_url = "https://eecsoh.eecs.umich.edu/api/queues"
    headers = {
        "Cookie": f"session={oh_session}",
        "Content-Type": "text/plain;charset=UTF-8"
    }
    r = requests.put(f"{base_url}/{oh_queue_id}/schedule",
                     headers=headers, json=schedule)


def put_groups(oh_queue_id, oh_session, groups):
    base_url = "https://eecsoh.eecs.umich.edu/api/queues"
    headers = {
        "Cookie": f"session={oh_session}",
        "Content-Type": "text/plain;charset=UTF-8"
    }
    r = requests.put(f"{base_url}/{oh_queue_id}/groups",
                     headers=headers, json=groups)


def get_schedule(oh_queue_id, oh_session):
    base_url = "https://eecsoh.eecs.umich.edu/api/queues"
    headers = {
        "Cookie": f"session={oh_session}"
    }
    r = requests.get(f"{base_url}/{oh_queue_id}/schedule", headers=headers)
    return r.json()


def get_groups(oh_queue_id, oh_session):
    base_url = "https://eecsoh.eecs.umich.edu/api/queues"
    headers = {
        "Cookie": f"session={oh_session}"
    }
    r = requests.get(f"{base_url}/{oh_queue_id}/groups", headers=headers)
    return r.json()


def main():
    api_key = os.environ.get("GOOGLE_CALENDAR_API_KEY")  # From eecs485.org
    cal_id = os.environ.get("GOOGLE_CALENDAR_ID")  # From eecs485.org
    oh_session = os.environ.get("OH_SESSION")  # From eecsoh
    oh_queue_id = os.environ.get("OH_QUEUE_ID")  # From eecsoh

    events_json = get_calendar_events(api_key, cal_id)
    schedule = form_schedule(events_json)
    put_schedule(oh_queue_id, oh_session, schedule)

    # Pipe input from agio
    groups = json.loads("".join(sys.stdin.readlines()))
    put_groups(oh_queue_id, oh_session, groups)


if __name__ == '__main__':
    main()
