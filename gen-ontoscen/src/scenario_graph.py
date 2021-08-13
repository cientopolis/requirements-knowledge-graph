from rdflib.namespace import RDF, RDFS
from rdflib import Namespace, Graph, Literal

from src.parser import Parser


class ScenarioGraph(Graph):
    
    iri = Namespace(
        "http://sw.cientopolis.org/scenarios_ontology/0.1/scenarios.ttl#"
    )
    scenarioID= 2
    conditionID=3
    episodeID= 7
        

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

    def createScenario(self, jsonObject):
        scenario = self.iri["sc"+str(self.scenarioID)]
        self.scenarioID+=1
        self.addType(scenario, "Scenario")
        self.addLabel(scenario, Parser.getScenario(jsonObject))

        context = self.iri["c"+str(self.conditionID)]
        self.conditionID+=1
        self.addType(context, "Condition")
        self.addLabel(context, Parser.getContext(jsonObject))
        self.addContext(scenario, context)

        goal = self.iri["c"+str(self.conditionID)]
        self.conditionID+=1
        self.addType(goal, "Condition")
        self.addLabel(goal, Parser.getGoal(jsonObject))
        self.addGoal(scenario, goal)

        actors = Parser.getActors(jsonObject)
        for each in actors:
            actor = self.iri[each]
            self.addType(actor, "Actor")
            self.addLabel(actor, each)
            self.addActor(scenario, actor)

        resources = Parser.getResources(jsonObject)
        for each in resources:
            resource= self.iri[each]
            self.addType(resource, "Resource")
            self.addLabel(resource, each)
            self.addResource(scenario, resource)
        
        episodes = Parser.getEpisodes(jsonObject)
        for each in episodes:
            episode = self.iri["ep"+str(self.episodeID)]
            self.episodeID+=1
            self.addType(episode, "Episode")
            self.addLabel(episode, each)
            self.addEpisode(scenario, episode)