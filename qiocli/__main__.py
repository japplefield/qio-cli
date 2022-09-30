import requests
import os
import urllib
import datetime
import sys
import json
import click
from qiocli import GoogleCalendarAPIClient, QueueAPIClient

# GCAL_BASE_URL
# OH_BASE_URL


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option()
@click.option("-d", "--debug", is_flag=True, help="Debug output")
@click.pass_context
def main(ctx, debug):
    """Queue command line interface."""
    # Pass global flags to subcommands via Click context
    # https://click.palletsprojects.com/en/latest/commands/#nested-handling-and-contexts
    ctx.ensure_object(dict)
    ctx.obj["DEBUG"] = debug


@main.command()
@click.option("-g", "--google-calendar", "gcal_id", nargs=1, help="Google Calendar ID")
@click.argument("queue", required=True)
@click.pass_context
def schedule(ctx, gcal_id, queue):
    """Schedule."""
    if not gcal_id:
        sys.exit("schedule without -g is not yet implemented.")
    gcal_client = GoogleCalendarAPIClient.make_default()
    path = f"{gcal_id}/events"
    now = datetime.datetime.now(datetime.timezone.utc)
    week_from_now = now + datetime.timedelta(weeks=1)
    query = {
        "singleEvents": True,
        "q": "Office Hours",
        "timeMin": now.isoformat(),
        "timeMax": week_from_now.isoformat(),
        "orderBy": "startTime"
    }
    events_json = gcal_client.get(path, query=query)
    schedule = form_schedule(events_json)

    queue_client = QueueAPIClient.make_default()
    path = f"{queue}/schedule"
    queue_client.put(path, json=schedule)


@main.command()
@click.option("-f", "--filename", help="File containing list of groups")
@click.argument("queue", required=True)
@click.pass_context
def groups(ctx, queue, filename):
    """Groups.

    QUEUE is the specific queue id.
    """

    with open(filename) as fh:
        groups_input = json.load(fh)
    base_url = "https://eecsoh.eecs.umich.edu/api/queues"
    headers = {
        "Cookie": f"session={oh_session}",
        "Content-Type": "text/plain;charset=UTF-8"
    }
    r = requests.put(f"{base_url}/{oh_queue_id}/groups",
                     headers=headers, json=groups)
    breakpoint()
    print("Groups called")
    pass


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


def old_main():
    api_key = os.environ.get("GOOGLE_CALENDAR_API_KEY")  # From eecs485.org
    cal_id = os.environ.get("GOOGLE_CALENDAR_ID")  # From eecs485.org
    oh_session = os.environ.get("OH_SESSION")  # From eecsoh
    oh_queue_id = os.environ.get("OH_QUEUE_ID")  # From eecsoh

    events_json = get_calendar_events(api_key, cal_id)
    schedule = form_schedule(events_json)
    put_schedule(oh_queue_id, oh_session, schedule)


if __name__ == '__main__':
    # These errors are endemic to click
    # pylint: disable=no-value-for-parameter,unexpected-keyword-arg
    main(obj={})
