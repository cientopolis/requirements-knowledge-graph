import json
from sys import argv

from src.scenario_graph import ScenarioGraph


def analyzeSentences(scenarios):
    graph = ScenarioGraph()
    # graph.parse("data/template.ttl", format="turtle", encoding="utf-8")
    for scenario in scenarios:
        print(scenario)
        graph.createScenario(scenario)

    file = open("output.txt", mode="w")
    file.write(graph.serialize(format="turtle"))

def loadSentencesFromJSON(fileName):
    file = open(fileName)
    scenarios = json.load(file)
    file.close()
    return scenarios


def main():
    if len(argv) != 2:
        print("Ingresar nombre de archivo")
        exit
    else:
        analyzeSentences(loadSentencesFromJSON(argv[1]))


main()
