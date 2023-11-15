# Spatrem Parser

More documentation to come.

## Building and Installing

Requirements:

Python 3.11
Poetry >= 1.6

To install, clone this repository, then run Poetry install:

``` shell
git clone git@github.com:cwulfman/spatrem_parser.git spatrem_parser
cd spatrem_parser
poetry install
```

There are two scripts, one for building graphs from translation spreadsheets and one for translator spreadsheets.

``` shell
poetry run python process_translations_file.py --help
poetry run python process_translators_file.py --help
```
