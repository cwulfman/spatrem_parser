from typing import Optional, List
from sys import stdout
from pathlib import Path
from csv import DictReader
from rdflib import Graph
import typer
import spatrem_parser.datamodels as dm
from spatrem_parser.spatrem import spatrem_graph
from spatrem_parser.translations import Translation



app = typer.Typer(help="Spatrem CSV translator")

@app.command()
def generate_graph(infile: Path, outfile: Optional[Path] = None)->None:
    translations: Graph = spatrem_graph()
    with open(infile, mode="r", encoding="utf-8-sig") as csvfile:
        reader: DictReader = DictReader(csvfile, delimiter=";")
        for row in reader:
            dm_tr = dm.Translation(**row)
            tr = Translation(dm_tr)
            translations += tr.graph

    if outfile is None:
        stdout.write(translations.serialize())
    else:
        with open(outfile, mode="w", encoding="utf-8-sig") as out:
            out.write(translations.serialize())

if __name__ == "__main__":
    app()
