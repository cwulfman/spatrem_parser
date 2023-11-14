import re
from typing import Optional
from pathlib import Path
from csv import DictReader
from pydantic import BaseModel
from spatrem.classes.crm import Language, Nomen
from spatrem.classes.base_graph import BaseGraph
from spatrem.classes.magazine import Journal, Issue, Translator, Author, Translation, Original, types


class TranslationRecord(BaseModel):
    """A Pydantic model for a row in the translations csv tables"""

    Language_area: Optional[str] = None
    Journal: str
    Year: str
    Issue_ID: str
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

class TranslatorRecord(BaseModel):
    Language_area:str
    Surname_Name: str
    Pseudonyms: str
    Year_Birth: str
    Year_Death: str
    Nationality: str
    Gender: str
    Journals: Optional[str] = None
    Notes: Optional[str] = None
    

def clean_id(dirty_string: str) -> str:
    return re.sub(r"\W", "", dirty_string)
    
class Importer:
    def __init__(self) -> None:
        self.graph = BaseGraph()
        self.translation_records: list[TranslationRecord] = []
        self.translator_records: list[TranslatorRecord] = []
        self.journals: dict = {}
        self.issues: dict = {}
        self.translators: dict = {}
        self.translators[clean_id('Anon')] = []
        self.authors: dict = {}
        self.authors[clean_id('Anon')] = []
        self.languages: dict = {}
        self.nomena: dict = {}
        # self.genres: dict = {}
        self.translations: dict = {}
        self.originals: list = []

        for _,v in types.items():
            self.graph.graph += v.graph

    def import_translations_file(self, infile: Path) -> None:
        with open(infile, mode="r", encoding="utf-8-sig") as data:
            reader: DictReader = DictReader(data, delimiter=";")
            for row in reader:
                self.translation_records.append(TranslationRecord(**row))

        for r in self.translation_records:
            j = r.Journal.strip()
            if j not in self.journals:
                journal = Journal(j)
                journal.has_identifier(j)
                self.journals[j] = journal

            journal: Journal = self.journals[j]
                
            issue_id = journal.label

            volume = None
            if r.Vol and r.Vol.strip() != "NONE":
                volume = r.Vol.strip()
                issue_id = f"{issue_id}_{volume}"

            number = None
            if r.No and r.No.strip() != "NONE":
                number = r.No.strip()
                # clean up badly formed number data like "23; 24".
                # convert it into "23_24" to match other data.
                if ';' in number:
                    number = "_".join([x.strip() for x in number.split(";")])
                issue_id = f"{issue_id}_{number}"

            pubDate = None
            if r.Year and r.Year.strip() != "NONE":
                pubDate = r.Year.strip()

            language_area = None
            if r.Language_area and r.Language_area.strip() != "NONE":
                language_area = r.Language_area.strip()

            if issue_id and issue_id not in self.issues:
                issue: Issue = Issue(identifier=issue_id,
                                     volume=volume,
                                     number=number,
                                     pubDate=pubDate,
                                     language_area=language_area)
                self.issues[issue_id] = issue

            issue: Issue = self.issues[issue_id]
                
            journal.publishes(issue, r.Year.strip())

            translators = []
            if r.Translator:
                stripped = [n.strip() for n in r.Translator.split(";")]
                ids = {clean_id(name): name for name in stripped if name != "NONE"}

                for id,name in ids.items():
                    if id not in self.nomena:
                        self.nomena[id] = Nomen(name)

                    if id in self.translators:
                        if id == "Anon":
                            translator = Translator(key=id, persName=name)
                            translator.is_identified_by(self.nomena[id])
                            self.nomena[id].identifies(translator)
                            self.translators[id].append(translator)
                        else:
                            translator = self.translators[id]
                    else:
                        translator = Translator(key=id, persName=name)
                        translator.is_identified_by(self.nomena[id])
                        self.nomena[id].identifies(translator)
                        if id == "Anon":
                            self.translators["Anon"].append(translator)
                        else:
                            self.translators[id] = translator
                    translators.append(translator)
                        

            
            if r.Listed_Translator:
                id = clean_id(r.Listed_Translator)
                if id != "NONE" and id not in self.nomena:
                    self.nomena[id] = Nomen(r.Listed_Translator)
            
            authors = []                
            if r.Author:
                stripped = [n.strip() for n in r.Author.split(";")]
                ids = {clean_id(name): name for name in stripped if name != "NONE"}

                for id,name in ids.items():
                    if id not in self.nomena:
                        self.nomena[id] = Nomen(name)

                    if id in self.authors:
                        if id == "Anon":
                            author = Author(key=id, persName=name)
                            author.is_identified_by(self.nomena[id])
                            self.nomena[id].identifies(author)
                            self.authors[id].append(author)
                        else:
                            author = self.authors[id]
                    else:
                        author = Author(key=id, persName=name)
                        author.is_identified_by(self.nomena[id])
                        self.nomena[id].identifies(author)
                        if id == "Anon":
                            self.authors["Anon"].append(author)
                        else:
                            self.authors[id] = author
                    authors.append(author)

                
            sl = []
            if r.SL:
                languages = r.SL.split(";")
                languages = [x.strip() for x in languages]
                languages = list(filter(lambda x: x!= "NONE", languages))
                for lang in languages:
                    if lang not in self.languages:
                        language = Language(lang)
                        language.has_identifier(lang)
                        self.languages[lang] = language
                sl = [self.languages[lang] for lang in languages]

                
            tl = []
            if r.TL:
                languages = r.TL.split(";")
                languages = [x.strip() for x in languages]
                languages = list(filter(lambda x: x!= "NONE", languages))
                
                for lang in languages:
                    if lang not in self.languages:
                        language = Language(lang)
                        language.has_identifier(lang)
                        self.languages[lang] = language
                tl = [self.languages[lang] for lang in languages]

                
            if r.Title:
                id = clean_id(r.Title)
                if id not in self.nomena:
                    self.nomena[id] = Nomen(r.Title)

                if id not in self.translations:
                    work = Translation(r.Title)
                    work.is_identified_by(self.nomena[id])

                    
                    for lang in tl:
                        work.has_language(lang)

                    original = Original()
                    self.originals.append(original)

                    work.has_original(original)

                    for lang in sl:
                        original.has_language(lang)

                    if authors:
                        for author in authors:
                            original.written_by(author)
                            author.wrote(original)

                    if translators:
                        for translator in translators:
                            work.written_by(translator)
                            translator.wrote(work)

                    if r.Genre:
                        work.has_genre(r.Genre.strip())
                    

                    self.translations[id] = work

                translation = self.translations[id]
                issue.includes(translation)

                

    def import_translators_file(self, infile: Path) -> None:
        with open(infile, mode="r", encoding="utf-8-sig") as data:
            reader: DictReader = DictReader(data, delimiter=";")
            for row in reader:
                self.translator_records.append(TranslatorRecord(**row))

            for r in self.translator_records:
                name = r.Surname_Name.strip()
                id = clean_id(name)

                if id not in self.translators:
                    print(f"{id} not in translator list but should be.")
                else:
                    tlator = self.translators[id]
                    pseudonyms = []
                    if r.Pseudonyms != "NONE":
                        stripped = [n.strip() for n in r.Pseudonyms.split(";")]
                        pseudonyms = {clean_id(name): name for name in stripped if name != "NONE"}
                        
                        for id, name in pseudonyms.items():
                            if id not in self.nomena:
                                self.nomena[id] = Nomen(name)
                                tlator.is_identified_by(self.nomena[id])
                                self.nomena[id].identifies(tlator)
                                
                                
                   # add spatrem-specific attributes
                    if r.Year_Birth != "Missing":
                        tlator.has_birth_year(r.Year_Birth.strip())
                    if r.Year_Death != "Missing":
                        tlator.has_death_year(r.Year_Death.strip())
                    if r.Nationality != "Missing":
                        nationalities = r.Nationality.split(";")
                        for n in nationalities:
                            tlator.has_nationality(n.strip())
                    if r.Gender != "Missing":
                        genders = r.Gender.split(";")
                        for g in genders:
                            tlator.has_gender(g.strip())
                    if r.Language_area != "Missing":
                        tlator.has_language_area(r.Language_area.strip())
        

                    
    def journal_graph(self) -> BaseGraph:
        g = BaseGraph().graph
        for _,v in self.journals.items():
            g += v.graph
        return g

    def issue_graph(self) -> BaseGraph:
        g = BaseGraph().graph
        for _,v in self.issues.items():
            g += v.graph
        return g

    def translator_graph(self) -> BaseGraph:
        g = BaseGraph().graph
        for _,v in self.translators.items():
            if type(v) is list:
                for translator in v:
                    g += translator.graph
            else:
                g += v.graph
        return g
    
    def author_graph(self) -> BaseGraph:
        g = BaseGraph().graph
        for _,v in self.authors.items():
            if type(v) is list:
                for author in v:
                    g += author.graph
            else:
                g += v.graph
        return g
    

    def language_graph(self) -> BaseGraph:
        g = BaseGraph().graph
        for _,v in self.languages.items():
            g += v.graph
        return g

    def name_graph(self) -> BaseGraph:
        g = BaseGraph().graph
        for _,v in self.nomena.items():
            g += v.graph
        return g

    def translation_graph(self) -> BaseGraph:
        g = BaseGraph().graph
        for _,v in self.translations.items():
            g += v.graph
        return g


    def original_graph(self) -> BaseGraph:
        g = BaseGraph().graph
        for original in self.originals:
            g += original.graph
        return g


    def export(self, directory: Path):
        if not directory.is_dir():
            raise OSError("directory not found")

        self.graph.graph.serialize(destination= directory / Path("types.ttl"))
        self.journal_graph().serialize(destination= directory / Path("journals.ttl"))
        self.issue_graph().serialize(destination= directory / Path("issues.ttl"))
        self.translator_graph().serialize(destination= directory / Path("translators.ttl"))
        self.author_graph().serialize(destination= directory / Path("authors.ttl"))
        # self.genre_graph().serialize(destination= directory / Path("genres.ttl"))
        self.language_graph().serialize(destination= directory / Path("languages.ttl"))
        self.name_graph().serialize(destination= directory / Path("names.ttl"))
        self.translation_graph().serialize(destination= directory / Path("translations.ttl"))
        self.original_graph().serialize(destination= directory / Path("originals.ttl"))

d = Path("/Users/wulfmanc/Desktop/DE")
datafile = Path("/Users/wulfmanc/projects/sm/spatrem/SpaTrEM_Database/Datasets/translations/DE_Translations.csv")
tfile = Path("/Users/wulfmanc/projects/sm/spatrem/SpaTrEM_Database/Datasets/translators/DE_Translators.csv")
i = Importer()
