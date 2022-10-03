"""A CLI for the Office Hours Queue."""
import sys
import json
import click
from qiocli import GoogleCalendarAPIClient, QueueAPIClient, utils


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
@click.argument("operation", required=True)
@click.argument("queue", required=True)
@click.option("-g", "--google-calendar", "gcal_id",
              nargs=1, help="Google Calendar ID")
@click.pass_context
def schedule(ctx, operation, queue, gcal_id):
    """Interact with queue Schedule.

    OPERATION is GET or PUT.
    QUEUE is the specific queue id.
    """
    queue_client = QueueAPIClient.make_default(debug=ctx["DEBUG"])

    if operation.lower() == 'get':
        print(queue_client.get(f"{queue}/schedule"))
        return

    if operation.lower() != 'put':
        sys.exit("Operation must be GET or PUT.")

    if not gcal_id:
        sys.exit("schedule without -g is not yet implemented.")

    gcal_client = GoogleCalendarAPIClient.make_default(debug=ctx["DEBUG"])
    path = f"{gcal_id}/events"

    events_json = gcal_client.get(
        path, query=utils.form_gcal_office_hours_search())
    schedule_json = utils.form_schedule(events_json)

    path = f"{queue}/schedule"
    queue_client.put(path, json=schedule_json)


@main.command()
@click.argument("operation", required=True)
@click.argument("queue", required=True)
@click.option("-f", "--filename", help="File containing list of groups")
@click.pass_context
def groups(ctx, operation, queue, filename):
    """Interact with queue Groups.

    OPERATION is GET or PUT.
    QUEUE is the specific queue id.
    """
    queue_client = QueueAPIClient.make_default(debug=ctx["DEBUG"])

    if operation.lower() == 'get':
        print(queue_client.get(f"{queue}/groups"))
        return

    if operation.lower() != 'put':
        sys.exit("Operation must be GET or PUT.")

    with open(filename, 'r', encoding='utf-8') as groups_file:
        groups_input = json.load(groups_file)

    path = f"{queue}/groups"
    queue_client.put(path, json=groups_input)


if __name__ == '__main__':
    # These errors are endemic to click
    # pylint: disable=no-value-for-parameter,unexpected-keyword-arg
    main(obj={})
