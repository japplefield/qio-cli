"""
Queue REST API client, a wrapper around the requests library.

Based on HTTPClient by James Perretta
https://github.com/eecs-autograder/autograder-contrib/
"""
import os
import json
import sys
from typing import Iterator
from urllib.parse import urljoin, urlencode
import requests


class APIClient:
    """Base class for sending authenticated requests to a REST API.

    Don't actually use this.
    """

    def __init__(self, base_url, debug=False):
        """Construct an API Client.

        Don't actually use this.
        """
        self.base_url = base_url
        self.debug = debug

    def get(self, path, *args, **kwargs):
        """Call requests.get with authentication headers and base URL."""
        return self.do_request(requests.get, path, *args, **kwargs)

    def put(self, path, *args, **kwargs):
        """Call requests.put with authentication headers and base URL."""
        return self.do_request(requests.put, path, *args, **kwargs)

    def prepare_auth(self, path, *args, **kwargs):
        """Modify request to add authentication."""
        raise NotImplementedError

    def do_request(self, method_func, path, *args, **kwargs):
        """Add authentication, base URL, call method, parse JSON.

        - Append path to OH Queue API base URL
        - Add session query arg
        - Call method_func
        - Check HTTP status code
        - Parse JSON
        """
        self.prepare_auth(path, *args, **kwargs)

        # Append path to base URL
        url = urljoin(self.base_url, path)

        # Append query to URL
        query = urlencode(kwargs.pop('query', {}))
        url = f"{url}?{query}"

        # Print request method and url
        if self.debug:
            method = method_func.__name__.upper()
            print(f"{method} {url}")

        # Call the underlying requests library function
        response = method_func(url, *args, **kwargs)

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
        if 'Content-Type' in response.headers and \
                'application/json' in response.headers['Content-Type']:
            try:
                return response.json()
            except json.JSONDecodeError:
                sys.exit(
                    f"Error: JSON decoding failed for url {response.url}\n"
                    f"{response.text}"
                )

        return None  # Stop Pylint from complaining?


class QueueAPIClient(APIClient):
    """Send authenticated requests to the eecsoh.eecs.umich.edu REST API.

    QueueAPIClient is a wrapper around the requests library that adds a
    session cookie to the query.  It supports all the arguments
    accepted by the corresponding requests library methods.
    https://requests.readthedocs.io/

    Avoid constructing an QueueAPIClient directly.  Instead, use
    QueueAPIClient.make_default().

    """

    @staticmethod
    def make_default(
            session_filename='.ohsession',
            base_url='https://eecsoh.eecs.umich.edu/api/queues/',
            debug=False
    ):
        """Create an QueueAPIClient instance with API session.

        base_url will be prepended to all URLs passed to the client's
        request methods and defaults to
        https://eecsoh.eecs.umich.edu/api/queues/.
        """
        return QueueAPIClient(get_auth(session_filename), base_url, debug)

    def __init__(self, api_session, base_url, debug=False):
        """Create an QueueAPIClient instance using a raw api_session.

        Most users should use QueueAPIClient.make_default() instead.
        """
        super().__init__(base_url, debug)
        self.api_session = api_session

    def prepare_auth(self, path, *args, **kwargs):
        kwargs['headers']['Cookie'] = f"session={self.api_session}"


class GoogleCalendarAPIClient(APIClient):
    """Send authenticated requests to the Google Calendar API.

    GoogleCalendarAPIClient is a wrapper around the requests library that adds
    an authentication key to the query.  It supports all the arguments
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
        """Create an GoogleCalendarAPIClient instance with API key.

        base_url will be prepended to all URLs passed to the client's
        request methods and defaults to
        https://www.googleapis.com/calendar/v3/calendars/.
        """
        return GoogleCalendarAPIClient(get_auth(key_filename), base_url, debug)

    def __init__(self, api_key, base_url, debug=False):
        """Create an GoogleCalendarAPIClient instance using a raw api_key.

        Most users should use GoogleCalendarAPIClient.make_default() instead.
        """
        super().__init__(base_url, debug)
        self.api_key = api_key

    def prepare_auth(self, path, *args, **kwargs):
        kwargs['query']['key'] = self.api_key


def get_auth(filename: str) -> str:
    """Search for auth file.

    Session file discovery works as follows:
    - If filename is just a filename (no path information), the current
    directory and every upward directory until the home directory will be
    searched for a file with that name.
    - If filename is an absolute path or a relative path that contains
    at least one directory, that file will be opened and the session read.
    """
    # Session filename provided and it does not exist
    if os.path.dirname(filename) and not os.path.isfile(filename):
        raise AuthFileNotFound(
            "Session file does not exist: {session_filename}")

    # Make sure that we're starting in a subdir of the home directory
    curdir = os.path.abspath(os.curdir)
    if os.path.expanduser('~') not in curdir:
        raise AuthFileNotFound(f"Invalid search path: {curdir}")

    # Search, walking up the directory structure from PWD to home
    for dirname in walk_up_to_home_dir():
        filename = os.path.join(dirname, filename)
        if os.path.isfile(filename):
            with open(filename, encoding="utf8") as sessionfile:
                return sessionfile.read().strip()

    # Didn't find a session file
    raise AuthFileNotFound(
        f"Session file not found: {filename}."
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


class AuthFileNotFound(Exception):
    """Exception type indicating failure to locate user session file."""
