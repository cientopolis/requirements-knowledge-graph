import sys
sys.path.append("..")
from src.analyzer import Analyzer
from src.jsonparser import JSONParser
import unittest

from rdflib.term import URIRef


class TestAnalyzer(unittest.TestCase):
    SCENARIO = JSONParser('input.json').requirements()[0]
    ANALYZER = Analyzer()

    def test_detect_actors(self):
        '''
        Ensures that each actor of the scenario has been added (both detected and specified)
        '''
        actors = set()
        for episode in self.SCENARIO.episodes:
            actors.add(self.ANALYZER.analyze_for_actors(episode))
        actors = list(actors)
        self.assertTrue(all(
            actor in ['gardener', 'solution', 'agricultural engineer'] for actor in actors))

    def test_detect_resources(self):
        '''
        Ensures that each resource of the scenario has been added (both detected and specified)
        Asked resources for command line should be accepted
        '''
        
        all_detected_resources = list()
        for episode in self.SCENARIO.episodes:
            all_detected_resources += self.ANALYZER.analyze_for_resources(
                episode,
                URIRef(
                    'http://sw.cientopolis.org/scenarios_ontology/0.1/scenarios.ttl#scenario0'),
                self.SCENARIO.resources
            )

        self.assertTrue(
            all(resource in ['result of soil analysis', 'solution', 'agricultural lime', 'soil', 'magnesium']
                for resource in all_detected_resources
                )
        )


if __name__ == '__main__':
    unittest.main()
