from neo4j import GraphDatabase
from functools import reduce
from typing import List, Optional
from .requirement import Requirement
from .analyzer import Analyzer


class Neo4jOntoscen:
    """ A basic class that populates a neo4j graph database,
        respecting the Ontoscen ontology.
    """

    ANALYZER = Analyzer()

    def __init__(self, requirements: Optional[List[Requirement]] = None):
        """Constructor for the Neo4jOntoscen class.

        Arguments:
            requirements (list[Requirement] - optional): list of
                requirements to be added.

        """
        super().__init__()
        url = "neo4j://your-server-adress-probably-localhost:7687"
        user = "an_user"
        pw = "a_pass"
        self.driver = GraphDatabase.driver(url, auth=(user, pw))

        with self.driver.session() as session:
            session.run("match (n) detach delete n")

        if requirements:
            self.add_requirements(requirements)

    def add_requirements(self, requirements: List[Requirement]):
        """Add a list of Requirements to the graph database.

        Arguments:
            requirements (list[str]): scenarios to be added.
        """
        for requirement in requirements:
            self.add_requirement(requirement)
        return self

    def add_requirement(self, req: Requirement):
        """Add a single req to the graph database.

        Arguments:
            req (str): scenario to be added.
        """

        with self.driver.session() as s:

            s.write_transaction(self._add_scenario, req.scenario)
            s.write_transaction(self._add_goal, req.scenario, req.goal)
            s.write_transaction(self._add_context, req.scenario, req.context)
            s.write_transaction(self._add_actors, req.scenario, req.actors)

            for resource in req.resources:
                s.write_transaction(self._add_resource,
                                    req.scenario, self.ANALYZER.lemmatize(resource))

            for episode in req.episodes:
                s.write_transaction(self._add_episode, req.scenario, episode)
                self._analyze_episode(
                    req.scenario, episode, episode, req.resources)  # episode_individual=episode

        self._add_episodes(req.scenario, req.episodes, req.resources)

        return self

    @staticmethod
    def _add_scenario(tx, scenario: str):
        query = (
            "optional match (a { label: $scenario }) "
            "call apoc.do.when(a is not null, "
            "'', "
            "'merge (b:Scenario { label: $scenario })', "
            "{ a:a, scenario:$scenario }) yield value return null ")
        return tx.run(query, scenario=scenario)

    @staticmethod
    def _add_condition(tx, condition: str):
        query = ("optional match (a { label: $condition }) "
                 "call apoc.do.when(a is not null, "
                 "'', "
                 "'merge (b:Condition { label: $condition })', "
                 "{ a:a, condition:$condition }) yield value return null ")
        return tx.run(query, condition=condition)

    @staticmethod
    def _add_goal(tx, scenario: str, goal: str):
        query = ("match (e{ label: $scenario }) "
                 "optional match (a { label: $goal }) "
                 "call apoc.do.when(a is not null, "
                 "'merge (e)-[:hasGoal]->(a)', "
                 "'merge (b:Condition { label: $goal }) "
                 "merge (e)-[:hasGoal]->(b)', "
                 "{ a:a,e:e,goal:$goal }) yield value return null")
        return tx.run(query, scenario=scenario, goal=goal)

    @staticmethod
    def _add_context(tx, scenario: str, context: str):
        query = ("match (e{ label: $scenario }) "
                 "optional match (a { label: $context }) "
                 "call apoc.do.when(a is not null, "
                 "'merge (e)-[:hasContext]->(a)', "
                 "'merge (b:Condition { label: $context }) "
                 "merge (e)-[:hasContext]->(b)', "
                 "{ a:a,e:e,context:$context }) yield value return null")
        return tx.run(query, context=context, scenario=scenario)

    @staticmethod
    def _add_actors(tx, scenario: str, actors):
        query = ("match (e{ label: $scenario }) "
                 "unwind $actors as actor "
                 "optional match (a { label:actor }) "
                 "call apoc.do.when(a is not null, "
                 "'merge (e)-[:hasActor]->(a)', "
                 "'merge (b:Actor { label:actor }) "
                 "merge (e)-[:hasActor]->(b)', "
                 "{ a:a,e:e,actor:actor }) yield value return null")
        return tx.run(query, scenario=scenario, actors=actors)

    @staticmethod
    def _add_resource(tx, scenario: str, resource: str):
        query = ("match (e{ label: $scenario }) "
                 "optional match (a { label: $resource }) "
                 "call apoc.do.when(a is not null, "
                 "'merge (e)-[:hasResource]->(a)', "
                 "'merge (b:Resource { label: $resource }) "
                 "merge (e)-[:hasResource]->(b)', "
                 "{ a:a,e:e,resource:$resource }) yield value return null")
        return tx.run(query, scenario=scenario, resource=resource)

    def _add_episodes(
        self, scenario: str, episodes: List[str], resources
    ):
        reduce(  # me gustaria que las dependencias se hagan todas juntas, en una misma transacción
            # si yo se que las dependencias entre episodios son intrinsecas, y no tengo que evaluar nada
            # para qué tomar el riesgo? (si se interrumpe la herramienta por ejemplo)
            self.add_dependency,
            map(
                lambda ep: self.add_episode(scenario, ep, resources),
                episodes,
            ),
            scenario,
        )

    @staticmethod
    def _add_action(tx, episode, action):
        query = ("match (e:Episode{ label: $episode }) "
                 "optional match (a { label: $action }) "
                 "call apoc.do.when(a is not null, "
                 "'merge (e)-[:hasAction]->(a)', "
                 "'merge (b:Action{ label: $action }) "
                 "merge (e)-[:hasAction]->(b)', "
                 "{ e:e,a:a,action:$action }) yield value return null")
        return tx.run(query, episode=episode, action=action)

    def add_dependency(self, required: str, dependent: str):
        with self.driver.session() as session:
            session.write_transaction(
                self._add_dependency, required, dependent)
        return dependent

    @staticmethod
    def _add_dependency(tx, required, dependent):
        query = ("match (a{ label: $required }) "
                 "match (b{ label: $dependent }) "
                 "merge (a)-[:requiredBy]->(b) "
                 "merge (b)-[:dependsOn]->(a)")
        tx.run(query, required=required, dependent=dependent)

    def add_episode(self, scenario: str, episode: str, resources):
        with self.driver.session() as session:
            session.write_transaction(self._add_episode, scenario, episode)

        self._analyze_episode(scenario, episode, episode, resources)
        return episode

    @staticmethod
    def _add_episode(tx, scenario: str, episode: str):
        query = ("match (e{ label: $scenario }) "
                 "optional match (a { label: $episode }) "
                 "call apoc.do.when(a is not null, "
                 "'merge (e)-[:hasEpisode]->(a)', "
                 "'merge (b:Episode{ label: $episode }) "
                 "merge (e)-[:hasEpisode]->(b)', "
                 "{ e:e,a:a,episode:$episode }) yield value return null")
        tx.run(query, scenario=scenario, episode=episode)

    def analyze_episode_for_actors(self, episode: str, episode_individual: str):
        actor = self.ANALYZER.analyze_for_actors(episode)
        with self.driver.session() as session:
            session.write_transaction(
                self._analyze_episode_for_actors, episode_individual, actor)

    @staticmethod
    def _analyze_episode_for_actors(tx, episode, actor):
        query = ("match (e:Episode{ label: $episode }) "
                 "optional match (r: Resource{ label: $actor }) "
                 "call apoc.do.when(r is not null, "
                 "'merge (e)-[:hasActor]->(r)', "
                 "'merge (b:Actor{ label: $actor }) "
                 "merge (e)-[:hasActor]->(b)', "
                 "{ e:e,r:r,actor:$actor }) yield value return null")
        tx.run(query, episode=episode, actor=actor)

    def analyze_episode_for_actions(
            self, episode: str, episode_individual: str):
        action = self.ANALYZER.analyze_for_actions(episode)
        if action:
            with self.driver.session() as session:
                session.write_transaction(
                    self._add_action, episode_individual, action)

    def analyze_episode_for_resources(
        self,
        scenario: str,
        episode: str,
        resources: List[str]
    ):
        with self.driver.session() as session:
            for resource in self.ANALYZER.analyze_for_resources(
                episode, scenario, resources
            ):
                session.write_transaction(
                    self._analyze_episode_for_resources, episode, resource)
                resources.append(resource)

    @staticmethod
    def _analyze_episode_for_resources(tx, episode, resource):
        query = ("match (e:Episode{ label: $episode }) "
                 "optional match (a:Actor{ label: $resource }) "
                 "call apoc.do.when(a is not null, "
                 "'merge (e)-[:hasResource]->(a)', "
                 "'merge (b:Resource{ label: $resource }) "
                 "merge (e)-[:hasResource]->(b)', "
                 "{ e:e,a:a,resource:$resource }) yield value return null")
        tx.run(query, episode=episode, resource=resource)

    def _analyze_episode(
        self,
        scenario: str,
        episode: str,
        episode_individual: str,
        resources: List[str],
    ):

        self.analyze_episode_for_actors(episode, episode_individual)
        self.analyze_episode_for_actions(episode, episode_individual)
        self.analyze_episode_for_resources(
            scenario, episode, resources)
