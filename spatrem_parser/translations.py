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
        expr_creation: dm.ExpressionCreation = dm.ExpressionCreation(f"creation of {title}")
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
    date = dm.TimeSpan(data.Year)

    original_work: dm.Work = create_authored_work(f"{data.Title}_original", author, SL)
    translation: dm.Work = create_authored_work(
        f"{data.Title}_translation", translator, TL
    )
    translation.is_derivative_of(original_work)

    constituent: Constituent = Constituent(issue, translation)

    manifestation: dm.Manifestion = dm.Manifestion(
        label=f"{journal.label}_{issue.label}_manifestation", time_span=date
    )
    if issue.expression:
        manifestation.embodies(issue.expression)
        issue.expression.is_embodied_in(manifestation)

    for entity in [
        journal,
        issue,
        author,
        translator,
        SL,
        TL,
        date,
        original_work,
        translation,
        constituent,
        manifestation,
    ]:
        g += entity.graph

    if issue.expression:
        g += issue.expression.graph

    return g
