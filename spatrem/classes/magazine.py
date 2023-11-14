from typing import Optional
from rdflib.term import Literal
from rdflib.namespace._RDF import RDF
from spatrem.classes import LRM, CRM, SCHEMA, DCTERMS, SPATREM
from spatrem.classes.base_graph import BaseGraph, Type
import spatrem.classes.lrm as lrm
import spatrem.classes.crm as crm
from spatrem.classes.lrm import SerialWork, Work, Expression, Manifestation, ManifestationCreation, TimeSpan, WorkCreation
from spatrem.classes.crm import Person

types = { 'journal': Type('journal'),
          'issue': Type('issue'),
          'constituent': Type('constituent'),
          'translation': Type('translation'),
          'original': Type('original'),
          'author': Type('author'),
          'translator': Type('translator'),
    }



# is this used?
class Kb():
    def __init__(self) -> None:
        self.graph = BaseGraph()
        self.journals = []
        self.issues = []
        self.translators = []

    def add_journal(self, journal):
        self.journals.append(journal)
        self.graph = self.graph + journal.graph


class Journal(lrm.SerialWork):
    def __init__(self, label:str) -> None:
        super().__init__(label)
        self.graph.add((self.id, DCTERMS.identifier, Literal(label)))
        self.issues = []
        self.has_type(types['journal'])
        
    def publishes(self, issue: "Issue", year: str) -> None:
        self.issues.append(issue)

        # manifestation_creation = ManifestationCreation()
        # pubDate = lrm.TimeSpan(year)
        # manifestation_creation.has_time_span(pubDate)
        
        # issue_manifestation = Manifestation()
        # manifestation_creation.created(issue_manifestation)
        # issue_manifestation.was_created_by(manifestation_creation)

        # issue_manifestation.embodies(issue.pub_expr)
        # issue.pub_expr.is_embodied_in(issue_manifestation)
        # issue.graph += issue.pub_expr.graph

        # issue.graph.add((issue.id, SPATREM.pubDate, Literal(year)))

        self.has_part(issue)
        issue.is_part_of(self)

        # self.graph += manifestation_creation.graph
        # self.graph += issue_manifestation.graph
        # self.graph += pubDate.graph
        


class Issue(lrm.Work):
    def __init__(self, identifier: str,
                 volume: Optional[str] = None,
                 number: Optional[str] = None,
                 pubDate: Optional[str] = None,
                 language_area: Optional[str] = None) -> None:
        super().__init__(identifier)
        self.constituents = []
        self.has_type(types['issue'])
        self.graph.add((self.id, DCTERMS.identifier, Literal(identifier)))
        if volume:
            self.graph.add((self.id, SPATREM.volume, Literal(volume)))

        if number:
            self.graph.add((self.id, SPATREM.number, Literal(number)))

        if pubDate:
            self.graph.add((self.id, SPATREM.pubDate, Literal(pubDate)))

        if language_area:
            self.has_language_area(language_area)

        # self.ed_expr = Expression()
        # self.pub_expr = Expression()

        # self.is_realised_by(self.pub_expr)
        # self.pub_expr.realises(self)
        # self.pub_expr.incorporates(self.ed_expr)
        # self.ed_expr.is_incorporated_in(self.pub_expr)

        # self.graph += self.ed_expr.graph
        # self.graph += self.pub_expr.graph


    def includes(self, constituent) -> None:
        self.constituents.append(constituent)
        self.has_part(constituent)
        constituent.is_part_of(self)

    def has_language_area(self, language_area:str) -> None:
        self.graph.add((self.id, SPATREM.language_area, Literal(language_area)))

        


class Constituent(lrm.Work):
    def __init__(self, title: Optional[str] = None) -> None:
        super().__init__(title)
        self.has_type(types['constituent'])
        # self.expression_creation = lrm.ExpressionCreation()
        # self.expression = lrm.Expression()

        # self.expression_creation.created(self.expression)
        # self.expression.was_created_by(self.expression_creation)

        self.work_creation = WorkCreation()
        self.was_created_by(self.work_creation)

        # self.graph += self.expression_creation.graph
        # self.graph += self.expression.graph
        self.graph += self.work_creation.graph


    

    def written_by(self, person: Person) -> None:
        self.work_creation.carried_out_by(person)
        self.graph += self.work_creation.graph

    def has_genre(self, genre:str) -> None:
        # self.has_type(genre)
        self.graph.add((self.id, SPATREM.genre, Literal(genre)))


class Translation(Constituent):
    def __init__(self, title: str) -> None:
        super().__init__(title)
        self.has_type(types['translation'])

    def has_original(self, original:"Original") -> None:
        # self.creation.used(original.expression)
        # self.expression.is_derivative_of(original.expression)
        self.graph.add((self.id, LRM.R68_is_inspired_by, original.id))
        self.graph.add((original.id, LRM.R68_is_inspiration_for, self.id))
        # self.graph += self.creation.graph
        # self.graph += self.expression.graph


class Original(Constituent):
    def __init__(self, title: Optional[str] = None) -> None:
        super().__init__(title)
        self.has_type(types['original'])
        

class Writer(Person):
    def __init__(self, key:str, persName:str) -> None:
        super().__init__(key, persName)
        self.graph.add((self.id, RDF.type, CRM.E39_Actor))

    def wrote(self, work:Constituent) -> None:
        self.performed(work.work_creation)



class Author(Writer):
    def __init__(self, key:str, persName:str) -> None:
        super().__init__(key, persName)
        self.has_type(types['author'])


class Translator(Writer):
    def __init__(self, key: str, persName:str) -> None:
        super().__init__(key, persName)
        self.has_type(types['translator'])

    def has_birth_year(self, year:str) -> None:
        self.graph.add((self.id, SPATREM.year_birth, Literal(year)))

    def has_death_year(self, year:str) -> None:
        self.graph.add((self.id, SPATREM.year_death, Literal(year)))

    def has_nationality(self, nationality:str) -> None:
        self.graph.add((self.id, SPATREM.nationality, Literal(nationality)))

    def has_gender(self, gender:str) -> None:
        self.graph.add((self.id, SPATREM.gender, Literal(gender)))

    def has_language_area(self, language_area:str) -> None:
        self.graph.add((self.id, SPATREM.language_area, Literal(language_area)))


# class Genre(Type):
#     def __init__(self, name: str) -> None:
#         super().__init__(name)
#         self.graph.add((self.id, RDF.type, CRM.E55_Type))
