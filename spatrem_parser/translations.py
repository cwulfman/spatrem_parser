"""Functions to parse Spatrem translation tables into graphs.

A translation is a Spatrem-specific sub-class, or collection of
subclasses, that represent(s) the data from Spatrem's spreadsheets
as a graph.
"""

from csv import DictReader
from pydantic import BaseModel
from pathlib import Path
from typing import Optional, List
from rdflib import Graph
from rdflib.term import URIRef, Literal
import spatrem_parser.datamodels as dm
from spatrem_parser.mag_models import Journal, Issue, Author

# Translator and Translation are Pydantic classes that validate rows
# from the spreadsheets.


class Translator(BaseModel):
    """A Pydantic model for a row in the translators csv tables"""

    Surname_Name: str
    Pseudonyms: Optional[str]
    Year_Birth: str
    Year_Death: str
    Nationality: str
    Gender: str
    Journals: Optional[str]
    Notes: str


class Translation(BaseModel):
    """A Pydantic model for a row in the translations csv tables"""

    Journal: str
    Year: str
    Issue_ID: str
    Vol: str
    No: str
    Listed_Translator: str
    Translator: str
    Author: str
    Title: str
    Genre: str
    SL: str
    TL: str
    Notes: str


class TranslationWork(dm.Work):
    def __init__(self, label: Optional[str] = None) -> None:
        super().__init__(label)


class TranslationExpression(dm.Expression):
    def __init__(self, label: Optional[str] = None) -> None:
        super().__init__(label)


# class Translation(dm.Work):
#     def __init__(self, label: Optional[str] = None) -> None:
#         super().__init__(label)


def create_translation_graph(row: Translation) -> Graph:
    g = dm.BaseGraph().graph

    tr_expr = dm.Expression(f"tr_expr of {row.Title}")
    tr_creation = dm.ExpressionCreation(f"creation of tr of {row.Title}")
    tr_creation.has_type("translation")
    tr_creation.created(tr_expr)
    tr_expr.was_created_by(tr_creation)

    src_expr = dm.Expression(f"expression of unnamed source of {row.Title}")
    src_creation = dm.ExpressionCreation(f"creation of unnamed source of {row.Title}")
    src_creation.created(src_expr)
    src_expr.was_created_by(src_creation)

    tr_creation.used(src_expr)
    src_expr.was_used_for(tr_creation)

    # short cut
    tr_expr.is_derivative_of(src_expr)

    # authors & translators
    if row.Translator and row.Translator != "NONE":
        translator = Author(row.Translator)
        translator.performed(tr_creation)
        g += translator.graph

    if row.Author and row.Author != "NONE":
        author = Author(row.Author)
        author.performed(src_creation)
        g += author.graph

    # languages
    if row.SL:
        source_language = dm.Language(row.SL)
        g += source_language.graph
        src_expr.has_language(source_language)

    if row.TL:
        translation_language = dm.Language(row.TL)
        g += translation_language.graph
        tr_expr.has_language(translation_language)

    for entity in [
        tr_expr,
        tr_creation,
        src_expr,
        src_creation,
        translator,
        author,
    ]:
        g += entity.graph

    return g


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
        expr_creation: dm.ExpressionCreation = dm.ExpressionCreation(
            f"creation of {title}"
        )
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


# def create_translation_old(data: dm.Translation) -> Graph:
#     g = dm.BaseGraph().graph
#     journal: Journal = Journal(data.Journal)
#     issue: Issue = Issue(journal, data.Issue_ID)
#     author: Author = Author(data.Author)
#     translator: Author = Author(data.Translator)
#     SL = dm.Language(data.SL)
#     TL = dm.Language(data.TL)
#     date = dm.TimeSpan(data.Year)

#     original_work: dm.Work = create_authored_work(f"{data.Title}_original", author, SL)
#     translation: dm.Work = create_authored_work(
#         f"{data.Title}_translation", translator, TL
#     )
#     translation.is_derivative_of(original_work)

#     constituent: Constituent = Constituent(issue, translation)

#     manifestation: dm.Manifestion = dm.Manifestion(
#         label=f"{journal.label}_{issue.label}_manifestation", time_span=date
#     )
#     if issue.expression:
#         manifestation.embodies(issue.expression)
#         issue.expression.is_embodied_in(manifestation)

#     for entity in [
#         journal,
#         issue,
#         author,
#         translator,
#         SL,
#         TL,
#         date,
#         original_work,
#         translation,
#         constituent,
#         manifestation,
#     ]:
#         g += entity.graph

#     if issue.expression:
#         g += issue.expression.graph

#     return g
