from csv import DictReader
from pathlib import Path
from typing import Optional, List
from rdflib import Graph
from rdflib.term import URIRef, Literal
import spatrem_parser.datamodels as dm
from spatrem_parser.mag_models import Journal, Issue, Constituent, Author


# class Translator(SpatremClass):
#     def __init__(
#         self, id: URIRef, data: dm.Translation, **kwargs: Optional[dict]
#     ) -> None:
#         super().__init__(id, **kwargs)
#         self.data: dm.Translation = data


class Translation(dm.Work):
    def __init__(self, label: Optional[str] = None) -> None:
        super().__init__(label)


def create_authored_work(
    title: str,
    author: Optional[Author] = None,
    language: Optional[dm.Language] = None,
) -> dm.Work:
    work: dm.Work = dm.Work(title)
    expr: dm.Expression = dm.Expression(f"{title}_expr")
    expr.realises(work)
    work.is_realised_by(expr)
    if author:
        expr_creation: dm.ExpressionCreation = dm.ExpressionCreation()
        author.performed(expr_creation)
        work.was_realised_through(expr_creation)
        expr.was_created_by(expr_creation)
    if language:
        expr.has_language(language)

    work.graph += expr.graph
    if author:
        work.graph += author.graph
        work.graph += expr_creation.graph
    if language:
        work.graph += language.graph

    return work


def create_translation(data: dm.Translation) -> Graph:
    g = dm.BaseGraph().graph
    journal: Journal = Journal(data.Journal)
    issue: Issue = Issue(journal, data.Issue_ID)
    author: Author = Author(data.Author)
    translator: Author = Author(data.Translator)
    SL = dm.Language(data.SL)
    TL = dm.Language(data.TL)

    original_work: dm.Work = create_authored_work(f"{data.Title}_original", author, SL)
    translation: dm.Work = create_authored_work(
        f"{data.Title}_translation", translator, TL
    )
    translation.is_derivative_of(original_work)

    for entity in [
        journal,
        issue,
        author,
        translator,
        SL,
        TL,
        original_work,
        translation,
    ]:
        g += entity.graph

    return g


class TranslationOld(dm.BaseGraph):
    def __init__(self, data: dm.Translation) -> None:
        super().__init__(data.Title)
        self.data: dm.Translation = data
        self.create_graph()

    def create_graph(self):
        name: str = self.data.Journal
        journal: Journal = Journal(self.data.Journal)
        issue: Issue = Issue(journal, self.data.Issue_ID)

        constituent: Constituent = Constituent(issue, self.data.Title)

        self.graph += journal.graph
        self.graph += issue.graph
        self.graph += constituent.graph


t_file = Path("../data/KA_Translations.csv")

with open(t_file, mode='r', encoding='utf-8-sig') as csvfile:
    reader: DictReader = DictReader(csvfile, delimiter=';')
    translations: List[Graph] = []
    for row in reader:
        translations.append(create_translation(dm.Translation(**row)))
