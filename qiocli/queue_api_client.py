"""
Queue REST API client, a wrapper around the requests library.

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


class QueueAPIClient:
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
        """Create an QueueAPIClient instance with API session found in session_filename.

        Session file discovery works as follows:
        - If session_filename is just a filename (no path information),
        the current directory and every upward directory until the home
        directory will be searched for a file with that name.
        - If session_filename is an absolute path or a relative path that
        contains at least one directory, that file will be opened and
        the session read to it.

        base_url will be prepended to all URLs passed to the client's
        request methods and defaults to https://eecsoh.eecs.umich.edu/api/queues/.
        """
        return QueueAPIClient(get_api_session(session_filename), base_url, debug)

    def __init__(self, api_session, base_url, debug=False):
        """Create an QueueAPIClient instance using a raw api_session.

        Most users should use QueueAPIClient.make_default() instead.
        """
        self.api_session = api_session
        self.base_url = base_url
        self.debug = debug

    def get(self, path, *args, **kwargs):
        """Call requests.get with authentication headers and base URL."""
        return self.do_request(requests.get, path, *args, **kwargs)

    def put(self, path, *args, **kwargs):
        """Call requests.put with authentication headers and base URL."""
        return self.do_request(requests.put, path, *args, **kwargs)

    def do_request(self, method_func, path, *args, **kwargs):
        """Add authentication, base URL, call method, parse JSON.

        - Append path to OH Queue API base URL
        - Add session query arg
        - Call method_func
        - Check HTTP status code
        - Parse JSON
        """
        # Append path to base URL
        url = urljoin(self.base_url, path)

        headers = copy.deepcopy(kwargs.pop('headers', {}))
        headers['Cookie'] = f"session={self.api_session}"

        # Print request method and url
        if self.debug:
            method = method_func.__name__.upper()
            print(f"{method} {url}")

        # Call the underlying requests library function
        response = method_func(
            url, *args, headers=headers, **kwargs)

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
        if 'Content-Type' in response.headers and 'application/json' in response.headers['Content-Type']:
            try:
                return response.json()
            except json.JSONDecodeError:
                sys.exit(
                    f"Error: JSON decoding failed for url {response.url}\n"
                    f"{response.text}"
                )


def get_api_session(session_filename: str) -> str:
    """Search for eecsoh.eecs.umich.edu session.

    Session file discovery works as follows:
    - If session_filename is just a filename (no path information), the current
      directory and every upward directory until the home directory will be
      searched for a file with that name.
    - If session_filename is an absolute path or a relative path that contains
      at least one directory, that file will be opened and the session read.
    """
    # Session filename provided and it does not exist
    if os.path.dirname(session_filename) and not os.path.isfile(session_filename):
        raise SessionFileNotFound(
            "Session file does not exist: {session_filename}")

    # Make sure that we're starting in a subdir of the home directory
    curdir = os.path.abspath(os.curdir)
    if os.path.expanduser('~') not in curdir:
        raise SessionFileNotFound(f"Invalid search path: {curdir}")

    # Search, walking up the directory structure from PWD to home
    for dirname in walk_up_to_home_dir():
        filename = os.path.join(dirname, session_filename)
        if os.path.isfile(filename):
            with open(filename, encoding="utf8") as sessionfile:
                return sessionfile.read().strip()

    # Didn't find a session file
    raise SessionFileNotFound(
        f"Session file not found: {session_filename}."
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


class SessionFileNotFound(Exception):
    """Exception type indicating failure to locate user session file."""
