"""Generates rdf file from csv file"""

from pathlib import Path
from sys import stdout
from csv import DictReader
from typing import Optional
import typer
from lrm_models import BaseGraph
from translation_models import Translator, create_translator_graph


app = typer.Typer(help="Spatrem translators csv parser")


@app.command()
def generate_translators_graph(infile: Path, outfile: Optional[Path] = None) -> None:
    """generates rdf file from input csv file."""

    translators = BaseGraph().graph
    with open(infile, mode="r", encoding="utf-8-sig") as data:
        reader: DictReader = DictReader(data, delimiter=";")
        for row in reader:
            record = Translator(**row)
            translator = create_translator_graph(record)
            translators += translator

    if outfile is None:
        stdout.write(translators.serialize())
    else:
        with open(outfile, mode="w", encoding="utf-8-sig") as out:
            out.write(translators.serialize())


if __name__ == "__main__":
    app()
