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


def create_publication_graph(row: Translation) -> Graph:
    g = dm.BaseGraph().graph

    issue_label = f"{row.Journal}_{row.Issue_ID}"

    # the translation expression
    tr_expr = dm.Expression(f"tr_expr of {row.Title}")

    # the editorial expression
    issue_ed_expr = dm.Expression(f"{issue_label}_ed_expr")

    # the publication expression
    issue_pub_expr = dm.Expression(f"{issue_label}_pub_expr")

    issue_ed_expr.incorporates(tr_expr)
    tr_expr.is_incorporated_in(issue_ed_expr)

    issue_pub_expr.incorporates(issue_ed_expr)
    issue_ed_expr.is_incorporated_in(issue_pub_expr)

    for entity in [
        tr_expr,
        issue_ed_expr,
        issue_pub_expr,
    ]:
        g += entity.graph
    return g


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


def create_magazine_graph(row: Translation) -> Graph:
    g = dm.BaseGraph().graph

    issue_label = f"{row.Journal}_{row.Issue_ID}"

    journal = dm.SerialWork(row.Journal)
    issue_work = dm.Work(issue_label)
    journal.has_member(issue_work)
    issue_work.is_member_of(journal)

    issue_pub_expr = dm.Expression(f"{issue_label}_pub_expr")
    issue_work.is_realised_by(issue_pub_expr)
    issue_pub_expr.realises(issue_work)

    # the editorial expression
    issue_ed_expr = dm.Expression(f"{issue_label}_ed_expr")

    # the editorial expresion is incorporated by the publication expression
    issue_pub_expr.incorporates(issue_ed_expr)
    issue_ed_expr.is_incorporated_in(issue_pub_expr)

    # representing the activity of publication

    # break this out into the creation and the entity to avoid overlap and duplication
    # issue_manifestation = dm.Manifestion(f"{issue_label}_issue", dm.TimeSpan(row.Year))
    issue_manifestation = dm.Manifestion(f"manifestation of {issue_label}")
    mf_creation = dm.ManifestationCreation(f"creation of {issue_label}")
    time_span = dm.TimeSpan(row.Year)
    mf_creation.has_time_span(time_span)
    issue_manifestation.was_created_by(mf_creation)
    mf_creation.created(issue_manifestation)

    issue_manifestation.embodies(issue_pub_expr)
    issue_pub_expr.is_embodied_in(issue_manifestation)

    for entity in [
        journal,
        issue_work,
        issue_pub_expr,
        issue_ed_expr,
        issue_manifestation,
        mf_creation,
        time_span,
    ]:
        g += entity.graph
    return g
