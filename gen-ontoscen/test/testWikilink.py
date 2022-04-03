import unittest
from unittest.mock import patch

from rdflib.namespace import Namespace, OWL

from src.jsonparser import JSONParser
from src.ontoscen import Ontoscen
from src.wikilink import Wikilink

WD: Namespace = Namespace("http://www.wikidata.org/entity/")
SCHEMA: Namespace = Namespace("https://schema.org/")


class TestWikilink(unittest.TestCase):

    graph = Ontoscen(JSONParser("test/data/wikilink.json").requirements())

    OSC = graph.IRI

    soil = (graph.get_individual("soil"), WD.Q36133)

    resources: dict[str, tuple] = {
        "tomato plant": (graph.get_individual("tomato plant"), WD.Q23501),
        "agricultural lime": (
            graph.get_individual("agricultural lime"),
            WD.Q3550861,
        ),
        "magnesium": (graph.get_individual("magnesium"), WD.Q660),
        "solution": (graph.get_individual("solution"), WD.Q5447188),
        "environmental property": (
            graph.get_individual("environmental property"),
            WD.Q62580461,
        ),
    }

    actors: dict[str, tuple] = {
        "gardener": (graph.get_individual("gardener"), WD.Q758780),
        "agricultural engineer": (
            graph.get_individual("agricultural engineer"),
            WD.Q18926350,
        ),
    }

    egraph: Ontoscen

    @classmethod
    def setUpClass(cls):
        super(TestWikilink, cls).setUpClass()
        cls.egraph = cls.create_enriched_graph()

    def test_subjects_get_enriched(self):
        "Test if subjects get related with Wikidata's concepts"

        concepts: list = [*self.resources.values(), *self.actors.values()]
        concepts.append(self.soil)

        for osc_in, wd_in in concepts:
            self.assertIn((osc_in, OWL.sameAs, wd_in), self.egraph)

    @classmethod
    @patch("src.wikilink.get_user_input", return_value="1")
    def create_enriched_graph(cls, *_):
        """Create an enriched graph without taking input (automatically
        selecting the first option instead)"""

        return Wikilink().enrich(cls.graph)
