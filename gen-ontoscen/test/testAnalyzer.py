import unittest
from src.jsonparser import JSONParser
from src.analyzer import Analyzer

class TestOntoscen(unittest.TestCase):
    SCENARIO= JSONParser('test/input.json').requirements()[0] 
    ANALYZER= Analyzer()

    def test_detect_actors(self):
        actors=set()
        for episode in self.SCENARIO.episodes:
            actors.add(self.ANALYZER.analyze_for_actors(episode))
        actors=list(actors)
        self.assertTrue(all(actor in ['gardener', 'solution', 'agricultural engineer'] for actor in actors))

if __name__ == '__main__':
    unittest.main()