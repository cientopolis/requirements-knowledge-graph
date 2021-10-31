import unittest
from src.jsonparser import JSONParser
from src.ontoscen import Ontoscen
from rdflib.namespace import RDF, Namespace

from unittest.mock import patch


class TestOntoscen(unittest.TestCase):
    @classmethod
    @patch("src.analyzer.get_user_input", return_value="y")
    def create_graph(cls, *_):
        """Create an Ontoscen graph. Instead of asking for input,
        select every option."""

        return Ontoscen(JSONParser("test/data/ontoscen.json").requirements())

    @classmethod
    def setUpClass(cls):
        super(TestOntoscen, cls).setUpClass()

        cls.IRI: Namespace = Namespace(
            "http://sw.cientopolis.org/scenarios_ontology/0.1/scenarios.ttl#"
        )

        cls.graph = cls.create_graph()

        cls.actor = cls.IRI.Actor
        cls.resource = cls.IRI.Resource
        cls.action = cls.IRI.Action

        cls.hasActor = cls.IRI.hasActor
        cls.hasResource = cls.IRI.hasResource
        cls.hasAction = cls.IRI.hasAction

        cls.gardener = cls.graph.get_individual("gardener")
        cls.agricultural_engineer = cls.graph.get_individual(
            "agricultural engineer"
        )

        cls.solution = cls.graph.get_individual("solution")
        cls.results_of_soil_analysis = cls.graph.get_individual(
            "result of soil analysis"
        )
        cls.agricultural_lime = cls.graph.get_individual("agricultural lime")
        cls.soil = cls.graph.get_individual("soil")
        cls.magnesium = cls.graph.get_individual("magnesium")
        cls.tomato_plant = cls.graph.get_individual("tomato plant")
        cls.pruning_plier = cls.graph.get_individual("pruning plier")

    def test_detect_actors(self):

        self.assertTrue(
            (self.IRI.episode0, self.hasActor, self.agricultural_engineer)
            in self.graph
        )
        self.assertTrue(
            (self.IRI.episode1, self.hasActor, self.agricultural_engineer)
            in self.graph
        )
        self.assertTrue(
            (self.IRI.episode2, self.hasActor, self.gardener) in self.graph
        )
        self.assertTrue(
            (self.IRI.episode3, self.hasActor, self.solution) in self.graph
        )

        self.assertTrue((self.solution, RDF.type, self.resource) in self.graph)
        self.assertFalse((self.solution, RDF.type, self.actor) in self.graph)

        self.assertTrue(
            (self.IRI.scenario1, self.hasActor, self.gardener) in self.graph
        )
        self.assertTrue(
            (self.IRI.episode5, self.hasActor, self.gardener) in self.graph
        )

    def test_detect_resources(self):
        self.assertTrue(
            (self.IRI.scenario0, self.hasResource, self.magnesium)
            in self.graph
        )

        self.assertTrue(
            (
                self.IRI.episode0,
                self.hasResource,
                self.results_of_soil_analysis,
            )
            in self.graph
        )
        self.assertTrue(
            (self.IRI.episode1, self.hasResource, self.solution) in self.graph
        )
        self.assertTrue(
            (self.IRI.episode1, self.hasResource, self.agricultural_lime)
            in self.graph
        )
        self.assertTrue(
            (self.IRI.episode2, self.hasResource, self.solution) in self.graph
        )
        # self.assertTrue((self.IRI.episode2, self.hasResource, self.soil) in self.graph)
        self.assertTrue(
            (self.IRI.episode3, self.hasResource, self.soil) in self.graph
        )

        self.assertTrue((self.solution, RDF.type, self.resource) in self.graph)
        self.assertFalse((self.solution, RDF.type, self.actor) in self.graph)

        self.assertTrue(
            (self.IRI.scenario1, self.hasResource, self.tomato_plant)
            in self.graph
        )
        self.assertTrue(
            (self.IRI.scenario1, self.hasResource, self.pruning_plier)
            in self.graph
        )
        self.assertTrue(
            (self.IRI.episode5, self.hasResource, self.pruning_plier)
            in self.graph
        )
        self.assertTrue(
            (
                self.IRI.episode5,
                self.hasResource,
                self.graph.get_individual("infected branch of tomato plant"),
            )
            in self.graph
        )
        self.assertTrue(
            (
                self.IRI.episode5,
                self.hasResource,
                self.graph.get_individual("withered branch of tomato plant"),
            )
            in self.graph
        )

    def test_detect_action(self):
        self.assertTrue(
            (
                self.IRI.episode0,
                self.hasAction,
                self.graph.get_individual("interprets"),
            )
            in self.graph
        )
        self.assertTrue(
            (
                self.IRI.episode1,
                self.hasAction,
                self.graph.get_individual("prepares"),
            )
            in self.graph
        )
        self.assertTrue(
            (
                self.IRI.episode2,
                self.hasAction,
                self.graph.get_individual("applies"),
            )
            in self.graph
        )
        self.assertTrue(
            (
                self.IRI.episode3,
                self.hasAction,
                self.graph.get_individual("improves"),
            )
            in self.graph
        )
        self.assertTrue(
            (
                self.IRI.episode4,
                self.hasAction,
                self.graph.get_individual("identifies"),
            )
            in self.graph
        )
        self.assertTrue(
            (
                self.IRI.episode5,
                self.hasAction,
                self.graph.get_individual("uses to prune"),
            )
            in self.graph
        )


if __name__ == "__main__":

    unittest.main()
