"""Queue CLI build and install configuration."""
import os
import io
import setuptools


# Read the contents of README file
PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))
with io.open(os.path.join(PROJECT_DIR, "README.md"), encoding="utf-8") as f:
    LONG_DESCRIPTION = f.read()


setuptools.setup(
    name="qiocli",
    description="A command line interface to eecsoh.eecs.umich.edu",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    version="0.1.0",
    author="Justin Applefield",
    author_email="jmapple@umich.edu",
    url="https://github.com/japplefield/qio-cli/",
    license="MIT",
    packages=["qiocli"],
    keywords=[
        "queue", "office hours", "office hours queue",
        "qio", "eecsoh", "eecsoh.eecs.umich.edu", "qio-cli",
    ],
    install_requires=[
        "click",
        "requests",
    ],
    extras_require={
        "dev": [
            "pdbpp",
            "twine",
            "tox",
        ],
        "test": [
            "check-manifest",
            "freezegun",
            "pycodestyle",
            "pydocstyle",
            "pylint",
            "pytest",
            "pytest-cov",
            "pytest-mock",
            "requests-mock",
        ],
    },
    python_requires='>=3.7',
    entry_points={
        "console_scripts": [
            "qio = qiocli.__main__:main",
        ]
    },
)
