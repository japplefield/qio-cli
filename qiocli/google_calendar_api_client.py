"""
Google Calendar REST API client, a wrapper around the requests library.

Based on HTTPClient by James Perretta
https://github.com/eecs-autograder/autograder-contrib/
"""
import copy
import os
import json
import sys
from typing import Iterator
from urllib.parse import urljoin, urlencode
import requests


class GoogleCalendarAPIClient:
    """Send authenticated requests to the autograder.io REST API.

    GoogleCalendarAPIClient is a wrapper around the requests library that adds an
    authentication key to the query.  It supports all the arguments
    accepted by the corresponding requests library methods.
    https://requests.readthedocs.io/

    Avoid constructing an GoogleCalendarAPIClient directly.  Instead, use
    GoogleCalendarAPIClient.make_default().

    """

    @staticmethod
    def make_default(
            key_filename='.gcalkey',
            base_url='https://www.googleapis.com/calendar/v3/calendars/',
            debug=False
    ):
        """Create an GoogleCalendarAPIClient instance with API key found in key_filename.

        Key file discovery works as follows:
        - If key_filename is just a filename (no path information),
        the current directory and every upward directory until the home
        directory will be searched for a file with that name.
        - If key_filename is an absolute path or a relative path that
        contains at least one directory, that file will be opened and
        the key read to it.

        base_url will be prepended to all URLs passed to the client's
        request methods and defaults to https://www.googleapis.com/calendar/v3/calendars/.
        """
        return GoogleCalendarAPIClient(get_api_key(key_filename), base_url, debug)

    def __init__(self, api_key, base_url, debug=False):
        """Create an GoogleCalendarAPIClient instance using a raw api_key.

        Most users should use GoogleCalendarAPIClient.make_default() instead.
        """
        self.api_key = api_key
        self.base_url = base_url
        self.debug = debug

    def get(self, path, *args, **kwargs):
        """Call requests.get with authentication headers and base URL."""
        return self.do_request(requests.get, path, *args, **kwargs)

    def do_request(self, method_func, path, *args, **kwargs):
        """Add authentication, base URL, call method, parse JSON.

        - Append path to Google Calendar API base URL
        - Add key query arg
        - Call method_func
        - Check HTTP status code
        - Parse JSON
        """
        # Append path to base URL
        url = urljoin(self.base_url, path)

        query = copy.deepcopy(kwargs.pop('query', {}))
        query['key'] = self.api_key
        query = urlencode(query)

        url = f"{url}?{query}"

        # Print request method and url
        if self.debug:
            method = method_func.__name__.upper()
            print(f"{method} {url}")

        # Call the underlying requests library function
        response = method_func(
            url, *args, headers=kwargs.pop('headers', {}), **kwargs)

        # Print the response
        if self.debug:
            print_response(response)

        # Check response status code
        if not response.ok:
            sys.exit(
                f"Error: {response.status_code} {response.reason} "
                f"for url {response.url}"
            )

        # Decode JSON
        if "Content-Type" not in response.headers:
            sys.exit(f"Error: no Content-Type from: {response.url}")
        elif 'application/json' in response.headers['Content-Type']:
            try:
                return response.json()
            except json.JSONDecodeError:
                sys.exit(
                    f"Error: JSON decoding failed for url {response.url}\n"
                    f"{response.text}"
                )
        else:
            sys.exit(
                "Error: Unknown Content-Type "
                f"'{response.headers['Content-Type']}' for url {response.url}"
            )


def get_api_key(key_filename: str) -> str:
    """Search for autograder.io key.

    Key file discovery works as follows:
    - If key_filename is just a filename (no path information), the current
      directory and every upward directory until the home directory will be
      searched for a file with that name.
    - If key_filename is an absolute path or a relative path that contains
      at least one directory, that file will be opened and the key read.
    """
    # Key filename provided and it does not exist
    if os.path.dirname(key_filename) and not os.path.isfile(key_filename):
        raise KeyFileNotFound("Key file does not exist: {key_filename}")

    # Make sure that we're starting in a subdir of the home directory
    curdir = os.path.abspath(os.curdir)
    if os.path.expanduser('~') not in curdir:
        raise KeyFileNotFound(f"Invalid search path: {curdir}")

    # Search, walking up the directory structure from PWD to home
    for dirname in walk_up_to_home_dir():
        filename = os.path.join(dirname, key_filename)
        if os.path.isfile(filename):
            with open(filename, encoding="utf8") as keyfile:
                return keyfile.read().strip()

    # Didn't find a key file
    raise KeyFileNotFound(
        f"Key file not found: {key_filename}."
    )


def walk_up_to_home_dir() -> Iterator[str]:
    """Iterate up the directory structure from pwd to home directory."""
    current_dir = os.path.abspath(os.curdir)
    home_dir = os.path.expanduser('~')

    while current_dir != home_dir:
        yield current_dir
        current_dir = os.path.dirname(current_dir)

    yield home_dir


def print_response(response):
    """Print a response object."""
    try:
        parsed = response.json()
    except json.JSONDecodeError:
        print(response.text)
    else:
        formatted = json.dumps(parsed, indent=4)
        print(formatted)


class KeyFileNotFound(Exception):
    """Exception type indicating failure to locate user key file."""
