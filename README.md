# Spatrem Compiler
This repository contains models and utilities developed for the
Spatrem project.  It comprises Python models of LRMoo classes and
properties and code that uses those models to process tabular data
files into RDF representations and serialize them into files that may
be loaded into an RDF graph database like GraphDB or Jena and queried
with SPARQL.

A single command-line script, *compile_rdf.py*, takes a pair of
semicolon-separated tabular data files, one of translator records and
one of translation records, and builds an internal graph of unique
nodes representing authors, translators, names, magazines, languages, issues,
genres, originals, and translations, which are then exported to files.
The files are in the Turtle format, which is easier to read than other
RDF serializations.

## Notes
The compiler processes the translations file first. It proceeds record
by record, cleaning the data where necessary and tracking the creation
of new nodes to prevent duplication. Special attention is given to the 
"Anon." translator: a new node is created for each appearance of this
token, even though the same name (Nomen) is attached to it.  When all
the translations have been processed, the translator file is
processed, and the demographic data captured in it are added to the
translator graphs.

The graph model (or schema, or ontology), is primarily LRMoo, with
identifiers coming from the dcterms vocabulary. The following
Spatrem-specific classes have been introduced:

- volume 
- number
- language_area
- gender
- genre
- nationality
- pubDate
- year_birth
- year_death

Introducing the Spatrem-specific property *pubDate* makes it possible
to eliminate the complex graphs of expressions, which are unneeded by
Spatrem's application. 

## Identifiers
Nodes are generated in several namespaces. UUIDs are used to guarantee
uniqueness, at the price of human legibility.


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

## Running
There is a command-line script building graphs from translation and
translator spreadsheets.  Command-line help is available:

``` shell
poetry run python compile_rdf.py --help
```

### An Example: the German Dataset

For example, to process the German translations file into RDF, type
the following at the command line, replacing the filepaths as appropriate:

```shell
poetry run python compile_rdf.py ~/spatrem/Datasets/translators/DE_Translators.csv \
~/spatrem/Datasets/translations/DE_Translations.csv \
~/spatrem/knowledge_graphs/rdf/DE
```

