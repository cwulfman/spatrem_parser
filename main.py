from typing import Optional
from sys import stdout
from pathlib import Path
from csv import DictReader
from rdflib import Graph
import typer
from lrm_models import BaseGraph
from translation_models import (
    Translation,
    create_magazine_graph,
    create_publication_graph,
    create_translation_graph,
)


app = typer.Typer(help="Spatrem CSV translator")


@app.command()
def generate_graph(infile: Path, outfile: Optional[Path] = None) -> None:
    graphs: Graph = BaseGraph().graph
    with open(infile, mode="r", encoding="utf-8-sig") as csvfile:
        reader: DictReader = DictReader(csvfile, delimiter=";")
        for row in reader:
            record = Translation(**row)
            graphs += create_magazine_graph(record)
            if record.Translator != "NONE":
                graphs += create_translation_graph(record)
                graphs += create_publication_graph(record)

    if outfile is None:
        stdout.write(graphs.serialize())
    else:
        with open(outfile, mode="w", encoding="utf-8-sig") as out:
            out.write(graphs.serialize())


if __name__ == "__main__":
    app()
