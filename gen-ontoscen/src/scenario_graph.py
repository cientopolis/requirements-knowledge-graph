from rdflib.namespace import RDF, RDFS
from rdflib import Namespace, Graph, Literal


class ScenarioGraph(Graph):

    iri = Namespace(
        "http://sw.cientopolis.org/scenarios_ontology/0.1/scenarios.ttl#"
    )

    def addLabel(self, individual, label):
        self.add((individual, RDFS.label, Literal(label)))

    def addContext(self, individual, cont):
        self.add((individual, self.iri["hasContext"], cont))

    def addDependence(self, dependence, individual):
        self.add((dependence, self.iri["dependsOn"], individual))

    def addResource(self, individual, resource):
        self.add((individual, self.iri["hasResource"], resource))

    def addGoal(self, individual, goal):
        self.add((individual, self.iri["hasGoal"], goal))

    def addActor(self, individual, actor):
        self.add((individual, self.iri["hasActor"], actor))

    def addEpisode(self, individual, episode):
        self.add((individual, self.iri["hasEpisode"], episode))

    def addType(self, individual, type):
        self.add((individual, RDF.type, self.iri[type]))
