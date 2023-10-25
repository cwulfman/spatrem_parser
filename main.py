from typing import Optional
from pydantic import BaseModel
from sys import stdout
from pathlib import Path
from csv import DictReader
from rdflib import Graph, Literal
from rdflib.namespace._RDF import RDF
from rdflib.namespace._RDFS import RDFS
import typer
import lrm_models as lrm
from lrm_models import BaseGraph, BaseGraph2
from mag_models import Journal, Issue
from translation_models import (
    Translation,
    Translator,
    create_magazine_graph,
    create_publication_graph,
    create_translation_graph,
    create_translator_graph,
)

class Record(BaseModel):
    """A Pydantic model for a row in the translations csv tables"""

    Language_area: Optional[str] = None
    Journal: Optional[str] = None
    Year: Optional[str] = None
    Issue_ID: Optional[str] = None
    Vol: Optional[str] = None
    No: Optional[str] = None
    Listed_Translator: Optional[str] = None
    Translator: Optional[str] = None
    Author: Optional[str] = None
    Title: Optional[str] = None
    Genre: Optional[str] = None
    SL: Optional[str] = None
    TL: Optional[str] = None
    Notes: Optional[str] = None



app = typer.Typer(help="Spatrem CSV translator")


@app.command()
def generate_translation_graphs(indir: Path, outdir: Optional[Path] = None) -> None:
    for csvfile in indir.iterdir():
        print(f"processing {csvfile}")
        outfile = csvfile.with_suffix(".ttl")
        if outdir:
            outfile = outdir / Path(outfile.name)
        generate_graph(csvfile, outfile)


@app.command()
def generate_translator_graphs(indir: Path, outdir: Optional[Path] = None) -> None:
    for csvfile in indir.iterdir():
        print(f"processing {csvfile}")
        outfile = csvfile.with_suffix(".ttl")
        if outdir:
            outfile = outdir / Path(outfile.name)
        generate_translators_graph(csvfile, outfile)


@app.command()
def generate_graph(infile: Path, outfile: Optional[Path] = None) -> None:
    graphs: Graph = BaseGraph().graph
    with open(infile, mode="r", encoding="utf-8-sig") as csvfile:
        reader: DictReader = DictReader(csvfile, delimiter=";")
        for row in reader:
            record = Translation(**row)
            if record.Journal != None:
                graphs += create_magazine_graph(record)
                graphs += create_publication_graph(record)
            if record.Translator and record.Translator != "NONE":
                graphs += create_translation_graph(record)

    if outfile is None:
        stdout.write(graphs.serialize())
    else:
        with open(outfile, mode="w", encoding="utf-8-sig") as out:
            out.write(graphs.serialize())


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


@app.command()
def generate_magazine_graph(infile: Path, outfile: Optional[Path] = None):
    """generates file of statements about magazines derived from csv file"""

    magazines = BaseGraph().graph

    records: list[Record] = []

    with open(infile, mode="r", encoding="utf-8-sig") as data:
        reader: DictReader = DictReader(data, delimiter=";")
        for row in reader:
            records.append(Record(**row))

    lookup = {}
    for r in records:
        if r.Journal not in lookup:
            lookup[r.Journal] = {}
        lookup[r.Journal][r.Issue_ID] = { "id": f"{r.Journal}.{r.Issue_ID}",
                                          "label": f"{r.Journal}.{r.Issue_ID}",
                                          "vol": r.Vol,
                                          
                                          "no": r.No,
                                          "pubDate": r.Year,
                                          }
    journal_list = []
    for key in lookup.keys():
        journal = BaseGraph2()
        journal.graph.add((journal.id, RDF.type, journal.uri_ref('lrm', "F18_Serial_Work")))
        journal.graph.add((journal.id, RDFS.label, Literal(key)))
        journal.graph.add((journal.id, journal.uri_ref('dcterms', 'identifier'), Literal(key)))
        for i in lookup[key].keys():
            irec = lookup[key][i]
            issue = BaseGraph2()
            journal.graph.add((journal.id, journal.uri_ref("lrm", "R67_has_part"), issue.id))

            issue.graph.add((issue.id, RDF.type, issue.uri_ref('lrm', "F1_Work")))
            issue.graph.add((issue.id, RDFS.label, Literal(irec['label'])))
            
            issue.graph.add((issue.id, issue.uri_ref('dcterms', 'identifier'), Literal(irec['id'])))
            if irec['vol'] and irec['vol'] != 'NONE':
                issue.graph.add((issue.id, issue.uri_ref("spatrem", 'volume'), Literal(irec['vol'])))
            issue.graph.add((issue.id, issue.uri_ref("spatrem", 'number'), Literal(irec['no'])))
            issue.graph.add((issue.id, issue.uri_ref("spatrem", 'pubDate'), Literal(irec['pubDate'])))
            issue.graph.add((issue.id, issue.uri_ref("lrm", 'R67i_is_part_of'), journal.id))

            issue_pub_expr = lrm.Expression(f"{irec['label']}_pub_expr")
            


            journal.graph = journal.graph + issue.graph
        magazines = magazines + journal.graph

    if outfile is None:
        stdout.write(magazines.serialize())
    else:
        with open(outfile, mode="w", encoding="utf-8-sig") as out:
            out.write(magazines.serialize())


if __name__ == "__main__":
    app()
