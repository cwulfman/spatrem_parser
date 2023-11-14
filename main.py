from pathlib import Path
import typer
from spatrem.importer import Importer




app = typer.Typer(help="Spatrem CV parser")


@app.command()
def process_translations_file(filename: str, outdirname: str) -> None:
    infile = Path(filename)
    outdir = Path(outdirname)

    importer = Importer()
    importer.import_translations_file(infile)
    importer.export(outdir)

@app.command()
def process_translators_file(filename: str, outdirname: str) -> None:
    infile = Path(filename)
    outdir = Path(outdirname)

    importer = Importer()
    importer.import_translators_file(infile)
    importer.export(outdir)



if __name__ == "__main__":
    app()
