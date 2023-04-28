from typing import Optional
from rdflib.term import URIRef, Literal
import spatrem_parser.datamodels as dm
import spatrem_parser.lrm_classes as lrm
import spatrem_parser.journal_classes as mag
from spatrem_parser.spatrem import SpatremClass

class Translator(SpatremClass):
    def __init__(
        self, id: URIRef, data: dm.Translation, **kwargs: Optional[dict]
    ) -> None:
        super().__init__(id, **kwargs)
        self.data: dm.Translation = data


class Translation(SpatremClass):
    def __init__(self, data: dm.Translation) -> None:
        super().__init__()
        title = data.Title
        self.id: URIRef = self.uri_ref("translation", self.clean_name(data.Title))
        self.data: dm.Translation = data
        self.create_graph()

    def create_graph(self):
        name: str = self.data.Journal
        journal: mag.Journal = mag.Journal(self.data.Journal)
        self.graph += journal.graph

        issue: mag.Issue = mag.Issue(self.data.Journal, self.data.Issue_ID)
        self.graph += issue.graph
