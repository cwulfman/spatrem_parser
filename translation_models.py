"""Functions to parse Spatrem translation tables into graphs.

A translation is a Spatrem-specific sub-class, or collection of
subclasses, that represent(s) the data from Spatrem's spreadsheets
as a graph.
"""

from pydantic import BaseModel
from typing import Literal, Optional
from rdflib import Graph
from rdflib.namespace._RDFS import RDFS
import rdflib.term
import lrm_models as lrm
from mag_models import Author

# Translator and Translation are Pydantic classes that validate rows
# from the spreadsheets.


class Translator(BaseModel):
    """A Pydantic model for a row in the translators csv tables"""

    Surname_Name: str
    Pseudonyms: Optional[str] = None
    Year_Birth: Optional[str] = None
    Year_Death: Optional[str] = None
    Nationality: Optional[str] = None
    Gender: Optional[str] = None
    Journals: Optional[str] = None
    Notes: Optional[str] = None


class Translation(BaseModel):
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
        translators = [n.strip() for n in row.Translator.split(";")]
        for name in translators:
            key = None
            if name != "Anon.":
                key = name
            translator = Author(key)
            if name == "Anon.":
                nomen: lrm.Nomen = lrm.Nomen("Anon.")
                translator.has_appellation(nomen)
                nomen.is_appellation_of(translator)
                translator.graph.add((translator.id, RDFS.label, rdflib.term.Literal("Anon.")))
            translator.performed(tr_creation)
            tr_creation.carried_out_by(translator)
            g += translator.graph

    if row.Author and row.Author != "NONE":
        authors = [n.strip() for n in row.Author.split(";")]
        for name in authors:
            author = Author(name)
            author.performed(src_creation)
            src_creation.carried_out_by(author)
            g += author.graph

    # languages
    if row.SL:
        languages = [l.strip() for l in row.SL.split(";")]
        for language in languages:
            source_language = lrm.Language(language)
            g += source_language.graph
            src_expr.has_language(source_language)

    if row.TL:
        languages = [l.strip() for l in row.TL.split(";")]
        for language in languages:
            translation_language = lrm.Language(language)
            g += translation_language.graph
            tr_expr.has_language(translation_language)

    # for entity in [
    #     tr_expr,
    #     tr_creation,
    #     src_expr,
    #     src_creation,
    #     translator,
    #     author,
    # ]:
    #     g += entity.graph
        
    for entity in [
        tr_expr,
        tr_creation,
        src_expr,
        src_creation,
    ]:
        g += entity.graph
        
    return g


def create_magazine_graph(row: Translation) -> Graph:
    g = lrm.BaseGraph().graph

    journal = lrm.SerialWork(row.Journal)

    issue_label = f"{row.Journal}_{row.Issue_ID}"

    issue_work = lrm.Work(issue_label)
    journal.has_part(issue_work)
    issue_work.is_part_of(journal)

    # Create Volume, if one is specified
    if row.Vol:
        vol_label = f"{row.Journal}_v_{row.Vol}"
        volume_work = lrm.Work(vol_label)
        volume_work.is_part_of(journal)
        
        journal.has_part(volume_work)
        issue_work.is_part_of(volume_work)
        volume_work.has_part(issue_work)
    else:
        volume_work = None

    issue_pub_expr = lrm.Expression(f"{issue_label}_pub_expr")
    issue_work.is_realised_by(issue_pub_expr)
    issue_pub_expr.realises(issue_work)

    tr_expr = lrm.Expression(f"tr_expr of {row.Title}")
    constituent_work = lrm.Work(row.Title)
    constituent_work.is_part_of(issue_work)
    if row.Genre:
        constituent_work.has_type(row.Genre)
    issue_work.has_part(constituent_work)

    constituent_work.is_realised_by(tr_expr)
    tr_expr.realises(constituent_work)

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
    if row.Year:
        time_span = lrm.TimeSpan(row.Year)
        mf_creation.has_time_span(time_span)
    else:
        time_span = None
    issue_manifestation.was_created_by(mf_creation)
    mf_creation.created(issue_manifestation)

    issue_manifestation.embodies(issue_pub_expr)
    issue_pub_expr.is_embodied_in(issue_manifestation)

    for entity in [
        journal,
        issue_work,
        issue_pub_expr,
        tr_expr,
        constituent_work,
        issue_ed_expr,
        issue_manifestation,
        mf_creation,
    ]:
        g += entity.graph
    if volume_work:
        g += volume_work.graph
    if time_span:
        g += time_span.graph
    return g


def create_translator_graph(row: Translator) -> Graph:
    """Create a graph from a row in a translators table.

    This function assumes the functions above have already
    been run on a translations table, and that the person
    has already been established.
    """

    person = Author(row.Surname_Name)
    if row.Year_Birth and row.Year_Birth != "Missing":
        person.has_birthdate(row.Year_Birth)

    if row.Year_Death and row.Year_Death != "Missing":
        person.has_deathdate(row.Year_Death)

    if row.Gender and row.Gender != "Missing":
        person.has_gender(row.Gender)

    if row.Nationality and row.Nationality != "Missing":
        person.has_nationality(row.Nationality)

    return person.graph
