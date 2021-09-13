import logging

from rdflib import Graph
import spacy

from agrovoc_matcher import extend_with_agrovoc
from consts import AGROVOC_PREFIX, LOCAL_GRAPH_PREFIX as PREFIX
import sentence_extractor as sente
from utils import normalize_triplet, print_rdflib_graph


def build_graph(triplets):
    g = Graph()
    g.namespace_manager.bind("agrovoc", AGROVOC_PREFIX)
    g.namespace_manager.bind("local", PREFIX)

    for triplet in triplets:
        subject, relation, _object = normalize_triplet(triplet)
        g.add((PREFIX[subject], PREFIX[relation], PREFIX[_object]))

        raw_subject, _, raw_object = triplet
        extend_with_agrovoc(g, raw_subject)
        extend_with_agrovoc(g, raw_object)

    return g


def main():
    logging.basicConfig(level=logging.INFO)
    nlp = spacy.load("en_core_web_sm")  # English tokenizer

    with open("../data/input.txt") as file:
        text = file.read()

    logging.info("Reading data from input file...")
    doc = nlp(text)

    logging.info("Detecting resources and relations...")
    triplets = sente.findSVOs(doc)
    logging.info("Building graph with detected resources")
    agroGraph = build_graph(triplets)

    agroGraph.serialize("../data/output.ttl", format="turtle", encoding="utf-8")
    print_rdflib_graph(agroGraph)


if __name__ == "__main__":
    main()
