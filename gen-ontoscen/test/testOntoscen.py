import unittest
import sys

from rdflib import namespace
sys.path.append("..")
from src.jsonparser import JSONParser
from src.ontoscen import Ontoscen
from rdflib import URIRef, Literal, graph
from rdflib.namespace import RDFS, RDF, Namespace

class TestOntoscen(unittest.TestCase):
    IRI: namespace = Namespace(
        "http://sw.cientopolis.org/scenarios_ontology/0.1/scenarios.ttl#"
    )
    graph= Ontoscen(JSONParser('input.json').requirements()) 

    actor= IRI.Actor
    resource= IRI.Resource
    action= IRI.Action

    hasActor= IRI.hasActor
    hasResource= IRI.hasResource
    hasAction= IRI.hasAction

    gardener= graph.get_individual("gardener")
    agricultural_engineer= graph.get_individual("agricultural engineer")

    solution= graph.get_individual("solution")
    results_of_soil_analysis= graph.get_individual("result of soil analysis")
    agricultural_lime = graph.get_individual("agricultural lime")
    soil = graph.get_individual("soil")
    magnesium = graph.get_individual("magnesium")
    
    def test_detect_actors(self):   

        self.assertTrue((self.IRI.episode0, self.hasActor, self.agricultural_engineer) in self.graph)
        self.assertTrue((self.IRI.episode1, self.hasActor, self.agricultural_engineer) in self.graph)
        self.assertTrue((self.IRI.episode2, self.hasActor, self.gardener) in self.graph)
        self.assertTrue((self.IRI.episode3, self.hasActor, self.solution) in self.graph)

        self.assertTrue((self.solution, RDF.type, self.resource) in self.graph)
        self.assertFalse((self.solution, RDF.type, self.actor) in self.graph)

    def test_detect_resources(self):
        self.assertTrue((self.IRI.scenario0, self.hasResource, self.magnesium) in self.graph)


        self.assertTrue((self.IRI.episode0, self.hasResource, self.results_of_soil_analysis) in self.graph)
        self.assertTrue((self.IRI.episode1, self.hasResource, self.solution) in self.graph)
        self.assertTrue((self.IRI.episode1, self.hasResource, self.agricultural_lime) in self.graph)
        # self.assertTrue((self.IRI.episode1, self.hasResource, self.magnesium) in self.graph)
        self.assertTrue((self.IRI.episode2, self.hasResource, self.solution) in self.graph)
        # self.assertTrue((self.IRI.episode2, self.hasResource, self.soil) in self.graph)
        self.assertTrue((self.IRI.episode3, self.hasResource, self.soil) in self.graph)

        self.assertTrue((self.solution, RDF.type, self.resource) in self.graph)
        self.assertFalse((self.solution, RDF.type, self.actor) in self.graph)

    def test_detect_action(self):
        self.assertTrue((self.IRI.episode5, self.hasActor, self.gardener) in self.graph)
        self.assertTrue((self.IRI.episode5, self.hasResource, self.graph.get_individual("pruning plier")) in self.graph)
        self.assertTrue((self.IRI.episode5, self.hasResource, self.graph.get_individual("infected branch of tomato plant")) in self.graph)
        self.assertTrue((self.IRI.episode5, self.hasResource, self.graph.get_individual("withered branch of tomato plant")) in self.graph)        
        self.assertTrue((self.IRI.episode5, self.hasAction, self.graph.get_individual("uses to prune")) in self.graph)



if __name__ == '__main__':
    unittest.main()