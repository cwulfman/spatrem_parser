from pathlib import Path
import typer
from spatrem.importer import Importer


app = typer.Typer(help="Spatrem CSV parser")


@app.command()
def compile_rdf(translatorsfilename: str, translationsfilename: str, outdirname: str) -> None:
    translators_file = Path(translatorsfilename)
    translations_file = Path(translationsfilename)
    outdir = Path(outdirname)

    importer = Importer()
    importer.import_translations_file(translations_file)
    importer.import_translators_file(translators_file)
    importer.export(outdir)



if __name__ == "__main__":
    app()
