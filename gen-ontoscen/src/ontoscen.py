from __future__ import annotations
from functools import reduce
from typing import Optional, Union

from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF, RDFS

from .requirement import Requirement

from src.analyzer import Analyzer

class Ontoscen(Graph):
    """An RDF graph that respects the Ontoscen ontology.

    Class attributes:
        IRI (URIRef): Identifier for the Ontoscen ontology.
    """
    ANALYZER = Analyzer()

    IRI: Namespace = Namespace(
        "http://sw.cientopolis.org/scenarios_ontology/0.1/scenarios.ttl#"
    )

    def __init__(self, requirements: Optional[list[Requirement]] = None):
        """Constructor for the Ontoscen class.

        Arguments:
            requirements (list[Requirement] - optional): list of
                requirements to be added.
        """
        super().__init__()

        self.parse("data/ontoscen.ttl", format="turtle", encoding="utf-8")

        if requirements:
            self.add_requirements(requirements)

    def add_requirements(self, requirements: list[Requirement]) -> Ontoscen:
        """Add a list of Requirements to the graph.

        Arguments:
            requirements (list[str]): scenarios to be added.
        """
        for requirement in requirements:
            self.add_requirement(requirement)
        return self

    def add_requirement(self, requirement: Requirement) -> Ontoscen:
        """Add a single Requirement to the graph.

        Arguments:
            requirement (str): scenario to be added.
        """
        # TODO: move most of this to Requirement or remove the class
        #   altogether
        scenario = self._add_scenario(requirement.scenario)
        self._add_goal(scenario, requirement.goal)
        self._add_context(scenario, requirement.context)
        for actor in requirement.actors:
            self._add_actor(scenario, actor)
        for resource in requirement.resources:
            self._add_resource(scenario, resource)
        self._add_episodes(
            scenario,
            requirement.episodes,
            requirement.resources,
        )
        return self

    def count_individuals_of_type(self, a_type: str) -> int:
        """Count the amount of individuals belonging to a certain type

        Arguments:
            a_type (str): The RDF class whose individuals are to be
                counted.

        Returns:
            counter (int): Amount of individuals of `a_type`.
        """
        return len(list(self.triples((None, RDF.type, self.IRI[a_type]))))

    def _exists_individual_with(self, type: str, label: str) -> bool:
        """Check in the graph for an individual of type `type` and label
            `label`.

        Arguments:
            type (str): An RDF class.
            label (str): A description of the individual.

        Returns:
            exists (bool): Is there such an individual in Ontoscen?
        """
        return (None, RDF.type, self.IRI[type]) in self and (
            None,
            RDFS.label,
            Literal(label),
        ) in self

    def get_individual(self, label: str) -> Union[URIRef|bool]:
        """Retrieve the individual of RDFS.label
            `label` or False if not found

        Arguments:
            type (str): An RDF class.
            label (str): A description of the individual.

        Returns:
            individual (URIRef): An subject linked with RDFS.label `label`.

        """
        return next(
            self.subjects(RDFS.label, Literal(label)), False
        )

    def _add_scenario(self, scenario: str) -> URIRef:
        return self._add_individual("Scenario", scenario)

    def _add_condition(self, condition: str) -> URIRef:
        return self._add_individual("Condition", condition)

    def _add_goal(self, scenario: URIRef, goal: str) -> URIRef:
        individual: URIRef = self._add_condition(goal)
        self.add((scenario, self.IRI["hasGoal"], individual))
        return individual

    def _add_context(self, scenario: URIRef, context: str) -> URIRef:
        individual: URIRef = self._add_condition(context)
        self.add((scenario, self.IRI["hasContext"], individual))
        return individual

    def _add_actor(self, scenario: URIRef, actor: str) -> URIRef:
        individual: URIRef = self._add_individual("Actor", self.ANALYZER.lemmatize(actor))
        self.add((scenario, self.IRI["hasActor"], individual))
        return individual

    def _add_resource(self, scenario: URIRef, resource: str) -> URIRef:
        individual: URIRef = self._add_individual("Resource", self.ANALYZER.lemmatize(resource))
        self.add((scenario, self.IRI["hasResource"], individual))
        return individual

    def _add_episodes(
        self, scenario: URIRef, episodes: list[str], resources
    ) -> None:
        reduce(
            self._add_dependency,
            map(
                lambda ep: self._add_episode(scenario, ep, resources),
                episodes,
            ),
            scenario,
        )

    def _add_action(self, episode, action):
        individual: URIRef = self._add_individual("Action", action)
        self.add((episode, self.IRI["hasAction"], individual))
        return individual

    def _add_dependency(self, required: URIRef, dependent: URIRef) -> URIRef:
        self.add((dependent, self.IRI["dependsOn"], required))
        self.add((required, self.IRI["requiredBy"], dependent))
        return dependent

    def _add_episode(
        self, scenario: URIRef, episode: str, resources
    ) -> URIRef:
        individual: URIRef = self._add_individual("Episode", episode)
        self.add((scenario, self.IRI["hasEpisode"], individual))
        self._analyze_episode(scenario, episode, individual, resources)
        return individual

    def _analyze_episode_for_actors(self, episode: str, episode_individual: URIRef):
        actor = self.ANALYZER.analyze_for_actors(episode)
        if self._exists_individual_with("Resource", actor):
            #if actor exists in the graph as Resource, then append it to scenario with role "Actor"
            #TODO: inconsistency detected here
            self._add_actor(episode_individual, actor)
        else:
            #actor not already exists, or actor is an Actor
            self._add_actor(episode_individual, actor)

    def _analyze_episode_for_actions(self, episode: str, episode_individual: URIRef):
        action = self.ANALYZER.analyze_for_actions(episode)
        if action:
            self._add_action(episode_individual, action)

    def _analyze_episode_for_resources(self, scenario: URIRef, episode: str, episode_individual: URIRef, resources: list[str]):
        
        for resource in self.ANALYZER.analyze_for_resources(episode, scenario, resources):
            if self._exists_individual_with("Actor", resource):
                #if resource exists in the graph as Actor, then append it to scenario with role "Resource"
                #TODO: inconsistency detected here
                
                self._add_resource(episode_individual, resource)
            else:
                #resource not already exists, or resource is a Resource
                self._add_resource(episode_individual, resource)            
            resources.append(resource)
            
    def _analyze_episode(
        self,
        scenario: URIRef,
        episode: str,
        episode_individual: URIRef,
        resources: list[str],
    ):
        self._analyze_episode_for_actors(episode, episode_individual)
        self._analyze_episode_for_actions(episode, episode_individual)
        self._analyze_episode_for_resources(scenario, episode, episode_individual, resources)

    def _add_individual(self, type: str, label: str) -> URIRef:
        """Add an individual to Ontoscen if it doesn't exist.

        If the individual doesn't exist:
            Add it to Ontoscen.
        If the individual already exists:
            Return it.

        Arguments:
            a_type (str): The RDF class whose individuals are to be
                counted.

        Returns:
            individual (URIRef): A node with triples defining its class
                and label.
        """
        if self._individual_exists(label):
            return self.get_individual(label)

        individual: URIRef = self.IRI[
            type.lower() + str(self.count_individuals_of_type(type))
        ]

        self._add_type(individual, type)
        self._add_label(individual, label)

        return individual

    def _individual_exists(self, label):
        return (None,
                RDFS.label,
                Literal(label),
                ) in self

    def _add_label(self, individual, label):
        self.add((individual, RDFS.label, Literal(label)))

    def _add_type(self, individual, type):
        self.add((individual, RDF.type, self.IRI[type]))

    