from .ontoscen import Ontoscen
from SPARQLWrapper import SPARQLWrapper, JSON
from time import sleep
from rdflib import URIRef, Graph, Literal
from rdflib.namespace import OWL, RDFS


class Wikilink:
    """A class to link an Ontoscen graph with information from Wikidata.

    Attributes:
        LIMIT (int): max amount of items to choose from for each
            subject.
    """

    def __init__(self, limit: int = 10):
        self.LIMIT = limit

    def enrich(self, graph: Ontoscen) -> Ontoscen:
        """Enrich the resources and actors of an Ontoscen graph with
        Wikidata.

        Arguments:
            graph (Ontoscen): an Ontoscen graph.

        Returns:
            graph (Ontoscen): an Ontoscen graph linked with Wikidata.
        """

        output = graph
        for subject in graph.get_resources() + graph.get_actors():
            output = self._enrich_subject(output, subject)

        return output

    def _enrich_subject(self, ontoscen: Ontoscen, subject: URIRef) -> Ontoscen:

        if self._is_enriched(subject, ontoscen):
            return ontoscen

        label = ontoscen.get_label(subject)
        if not label:
            return ontoscen

        results: list = self._query_wikidata(label.toPython())

        if not results:
            return ontoscen

        chosen_result: dict = self._take_input(results, subject)

        if not chosen_result:
            return ontoscen

        ontoscen.add(
            (subject, OWL.sameAs, URIRef(chosen_result["item"]["value"]))
        )
        ontoscen.add(
            (subject, RDFS.label, Literal(chosen_result["label"]["value"]))
        )

        return ontoscen

    def _take_input(self, options: list[dict], subject: URIRef) -> dict:
        print(
            f"The subject '{subject}' has the following wikidata matches.",
            "Choose the most precise option, or press Enter to skip.",
            sep="\n",
        )

        index: int = 0
        for option in options:
            index += 1
            external_item: str = option["item"]["value"]
            external_label: str = option["label"]["value"]
            print(f"{index}) {external_label}: {external_item}")

        try:
            selection: int = int(input("Select: "))
            return options[selection - 1]
        except:
            return {}

    def _is_enriched(self, subject: URIRef, graph: Graph) -> bool:
        return (subject, OWL.sameAs, None) in graph or (
            None,
            OWL.sameAs,
            subject,
        ) in graph

    def _query_wikidata(self, name: str) -> list[dict]:
        query = """
            SELECT ?item ?label WHERE {
              SERVICE wikibase:mwapi {
                bd:serviceParam wikibase:api "EntitySearch".
                bd:serviceParam wikibase:endpoint "www.wikidata.org".
                bd:serviceParam mwapi:search "%(subject)s".
                bd:serviceParam mwapi:language "en".
                ?item wikibase:apiOutputItem mwapi:item.
              }
            ?item rdfs:label ?label. FILTER( LANG(?label)="en" )
            }
            LIMIT %(limit)s
            """ % {
            "subject": name,
            "limit": self.LIMIT,
        }

        return self._request_query("https://query.wikidata.org/sparql", query)[
            "results"
        ]["bindings"]

    def _request_query(self, url: str, query: str):
        sparql = SPARQLWrapper(url, returnFormat=JSON)
        sparql.setQuery(query)
        try:
            return sparql.queryAndConvert()
        except:
            print("Too many queries were made... please wait a few minutes...")
            sleep(120)
            return sparql.queryAndConvert()

    def _get_subject(self, graph: Graph) -> URIRef:
        query = graph.query(
            """
            SELECT DISTINCT ?subject
            WHERE {
              ?subject ?predicate ?object
            } LIMIT 1
            """
        )
        for subject in query:
            if subject is None:
                raise Exception("Subject not found.")

            return subject[0]

        raise Exception("Subject not found.")
