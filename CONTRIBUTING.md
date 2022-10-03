Contributing to qio-cli
========================

## Install development environment
Set up a development virtual environment.
```console
$ python3 -m venv env
$ source env/bin/activate
$ pip install -e .[dev,test]
```

A `qio` entry point script is installed in your virtual environment.
```console
$ which qio
/Users/jmapple/Developer/qio-cli/env/bin/qio
```

## Testing and code quality
TODO: unit tests

Test code style
```console
$ pycodestyle qiocli setup.py
$ pydocstyle qiocli setup.py
$ pylint qiocli setup.py
$ check-manifest
```

## Release procedure
TODO
