"""Functions to parse Spatrem translation tables into graphs.

A translation is a Spatrem-specific sub-class, or collection of
subclasses, that represent(s) the data from Spatrem's spreadsheets
as a graph.
"""

from pydantic import BaseModel
from typing import Optional
from rdflib import Graph
import lrm_models as lrm
from mag_models import Author

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


class TranslationWork(lrm.Work):
    def __init__(self, label: Optional[str] = None) -> None:
        super().__init__(label)


class TranslationExpression(lrm.Expression):
    def __init__(self, label: Optional[str] = None) -> None:
        super().__init__(label)


def create_publication_graph(row: Translation) -> Graph:
    g = lrm.BaseGraph().graph
    issue_label = f"{row.Journal}_{row.Issue_ID}"

    # the translation expression
    tr_expr = lrm.Expression(f"tr_expr of {row.Title}")

    # the editorial expression
    issue_ed_expr = lrm.Expression(f"{issue_label}_ed_expr")

    # the publication expression
    issue_pub_expr = lrm.Expression(f"{issue_label}_pub_expr")

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
    g = lrm.BaseGraph().graph

    tr_expr = lrm.Expression(f"tr_expr of {row.Title}")
    tr_creation = lrm.ExpressionCreation(f"creation of tr of {row.Title}")
    tr_creation.has_type("translation")
    tr_creation.created(tr_expr)
    tr_expr.was_created_by(tr_creation)

    src_expr = lrm.Expression(f"expression of unnamed source of {row.Title}")
    src_creation = lrm.ExpressionCreation(f"creation of unnamed source of {row.Title}")
    src_creation.created(src_expr)
    src_expr.was_created_by(src_creation)

    tr_creation.used(src_expr)
    src_expr.was_used_for(tr_creation)

    # short cut
    tr_expr.is_derivative_of(src_expr)

    # authors & translators
    if row.Translator and row.Translator != "NONE":
        translators = row.Translator.split(";")
        for name in translators:
            translator = Author(name)
            translator.performed(tr_creation)
            g += translator.graph

    if row.Author and row.Author != "NONE":
        authors = row.Author.split(";")
        for name in authors:
            author = Author(name)
            author.performed(src_creation)
            g += author.graph

    # languages
    if row.SL:
        languages = row.SL.split(";")
        for language in languages:
            source_language = lrm.Language(language)
            g += source_language.graph
            src_expr.has_language(source_language)

    if row.TL:
        for language in row.TL.split(";"):
            translation_language = lrm.Language(language)
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
    g = lrm.BaseGraph().graph

    issue_label = f"{row.Journal}_{row.Issue_ID}"

    journal = lrm.SerialWork(row.Journal)
    issue_work = lrm.Work(issue_label)
    journal.has_member(issue_work)
    issue_work.is_member_of(journal)

    issue_pub_expr = lrm.Expression(f"{issue_label}_pub_expr")
    issue_work.is_realised_by(issue_pub_expr)
    issue_pub_expr.realises(issue_work)

    # the editorial expression
    issue_ed_expr = lrm.Expression(f"{issue_label}_ed_expr")

    # the editorial expresion is incorporated by the publication expression
    issue_pub_expr.incorporates(issue_ed_expr)
    issue_ed_expr.is_incorporated_in(issue_pub_expr)

    # representing the activity of publication

    # break this out into the creation and the entity to avoid overlap and duplication
    # issue_manifestation = lrm.Manifestion(f"{issue_label}_issue", lrm.TimeSpan(row.Year))
    issue_manifestation = lrm.Manifestion(f"manifestation of {issue_label}")
    mf_creation = lrm.ManifestationCreation(f"creation of {issue_label}")
    time_span = lrm.TimeSpan(row.Year)
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


def create_translator_graph(row: Translator) -> Graph:
    """Create a graph from a row in a translators table.

    This function assumes the functions above have already
    been run on a translations table, and that the person
    has already been established.
    """

    person = lrm.Person(row.Surname_Name)
    if row.Year_Birth != "Missing":
        person.has_birthdate(row.Year_Birth)

    if row.Year_Death != "Missing":
        person.has_deathdate(row.Year_Death)

    if row.Gender != "Missing":
        person.has_gender(row.Gender)

    if row.Nationality != "Missing":
        person.has_nationality(row.Nationality)

    return person.graph
