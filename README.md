Queue CLI
=========================

Queue (Q) CLI (`qio`) is a command line interface to [eecsoh.eecs.umich.edu](https://eecsoh.eecs.umich.edu), i.e. the Office Hours Queue (Q).

## Quick start
TODO

## Usage

Make sure you have a session stored in `.ohsession` or `~/.ohsession`. You can obtain this by signing in to the [queue](https://eecsoh.eecs.umich.edu) and finding the cookie called `session` in your browser's memory. Note that these sessions have a TTL of one month so this file will need to be updated monthly.

### Groups

Use `agio` to download a list of groups.

```console
$ agio groups --list-json --course <COURSE_NAME> --project <PROJECT> > groups.json
```

Use `qio` to upload the downloaded groups.

```console
$ qio groups put <QUEUE_ID> -f groups.json
```

Example:

```console
$ agio groups --list-json --course eecs485f23 --project p2 > groups.json
$ qio groups put 1gpzfffFeITHiGHBSvCaF106XfC -f groups.json
```

### Schedule

Make sure you have a Google Calendar key stored in `.gcalkey` or `~/.gcalkey`.

Use `qio` to download groups from Google Calendar and upload them.

```console
$ qio schedule put <QUEUE_ID> -g <GOOGLE_CALENDAR_ID>
```

Example:

```console
$ qio groups put 1gpzfffFeITHiGHBSvCaF106XfC -g c_vf0mfqo3skg16fka7aspdv97ts@group.calendar.google.com
```

## Contributing
See the guide for [guide for contributing](CONTRIBUTING.md).

## Acknowledgements
Q CLI is written by Justin Applefield <jmapple@umich.edu> and inspired by [Autograder.io CLI](https://pypi.org/project/agiocli/)