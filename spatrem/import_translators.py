from pathlib import Path
from csv import DictReader
from pydantic import BaseModel


from rdflib import Graph
from typing import Dict, Optional
from rdflib.term import Literal
from rdflib.namespace._RDF import RDF
from rdflib.namespace._RDFS import RDFS
from rdflib.namespace._XSD import XSD
from rdflib import Namespace

LRM = Namespace("http://iflastandards.info/ns/lrm/lrmer/")
CRM = Namespace("http://www.cidoc-crm.org/cidoc-crm/")
SCHEMA = Namespace("http://schema.org/")
DCTERMS = Namespace("http://purl.org/dc/terms/")
SPATREM = Namespace("http://spacesoftranslation.org/ns/spatrem/")
NAMES = Namespace("http://spacesoftranslation.org/ns/names/")
LANGUAGES = Namespace("http://spacesoftranslation.org/ns/languages/")
TYPES = Namespace("http://spacesoftranslation.org/ns/types/")
PEOPLE = Namespace("http://spacesoftranslation.org/ns/people/")


class TranslatorRecord(BaseModel):
    Language_area: Optional[str] = None
    Surname_Name: Optional[str] = None
    Pseudonyms: Optional[str] = None
    Year_Birth: Optional[str] = None
    Year_Death: Optional[str] = None
    Nationality: Optional[str] = None
    Gender: Optional[str] = None
    Journals: Optional[str] = None
    Notes: Optional[str] = None

datafile = Path("/Users/wulfmanc/projects/sm/spatrem/SpaTrEM_Database/Datasets/translations/DE_Translations.csv")
tfile = Path("/Users/wulfmanc/Desktop/DE/translators.ttl")
nfile = Path("/Users/wulfmanc/Desktop/DE/names.ttl")

class Importer:
    def __init__(self, datafile: Path, tfile: Path, nfile: Path) -> None:
        self. graph = Graph()
        self.records: list[TranslatorRecord] = []

        with open(datafile, 'r', encoding='utf-8-sig') as data:
            reader: DictReader = DictReader(data, delimiter=";")
            for row in reader:
                self.records.append(TranslatorRecord(**row))

        self.graph.parse(tfile)
        self.graph.parse(nfile)
        

i = Importer(datafile, tfile, nfile)
names = list(i.graph.subjects((RDF.type, CRM.E21_Person)))
print(len(names))
