import logging

from bs4 import BeautifulSoup
from rdflib import Graph, OWL, SKOS
import requests as rq

from consts import AGROVOC_PREFIX, BASE_AGROVOC_URL, LOCAL_GRAPH_PREFIX as PREFIX
from utils import normalize_resource


def extend_with_agrovoc(g, concept):
    """
    Recives a concept/word and if found returns agrovoc's broader and narrower concepts
    """

    normalized_concept = normalize_resource(concept)

    # Prevent further requests if it's already processed
    if (PREFIX[normalized_concept], OWL.sameAs, None) in g:
        return

    concept_URI = search_agrovoc_concept(concept)
    if not concept_URI:
        return

    logging.info(f'Concept "{concept}" found in agrovoc, extracting data...')
    graph = create_remote_graph(concept_URI)

    # Remove the URL prefix from the ID, wich has a length of 47 chars
    # https://agrovoc.fao.org/browse/agrovoc/en/page/<ID>
    concept_ID = concept_URI[47:]
    g.add(
        (
            PREFIX[normalized_concept],
            OWL.sameAs,
            AGROVOC_PREFIX[concept_ID],
        )
    )

    agrovoc_data = get_related_triplets(graph, concept_ID)
    for triplet in agrovoc_data:
        g.add(triplet)


def search_agrovoc_concept(concept):
    response = rq.get(f"{BASE_AGROVOC_URL}agrovoc/en/search?clang=en&q={concept}")
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    anchors = soup.findAll("a", class_="conceptlabel")
    if anchors:
        URI = BASE_AGROVOC_URL + anchors[0].attrs["href"]
        return URI
    else:
        return None


def create_remote_graph(URI):
    response = rq.get(URI)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    turtle_anchors = soup.select("span.versal.concept-download-links > a:nth-child(1)")
    link = turtle_anchors[0].attrs["href"]
    g = Graph()
    g.parse(BASE_AGROVOC_URL + link)

    return g


def get_related_triplets(g, subject_id):
    broader_concepts = g.triples((AGROVOC_PREFIX[subject_id], SKOS.narrower, None))
    narrower_concepts = g.triples((AGROVOC_PREFIX[subject_id], SKOS.broader, None))
    return list(broader_concepts) + list(narrower_concepts)
