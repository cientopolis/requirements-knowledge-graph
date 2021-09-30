from functools import reduce
from .ontoscen import Ontoscen
from wikibase_api import Wikibase
from rdflib import URIRef, Graph, Literal, Namespace
from rdflib.namespace import OWL, RDFS


SCHEMA = Namespace("https://schema.org/")


class Wikilink:
    """A class to link an Ontoscen graph with information from Wikidata.

    Attributes:
        LIMIT (int): max amount of items to choose from for each
            subject.
    """

    def __init__(self, limit: int = 10):
        self.LIMIT = limit
        self.WB = Wikibase()

    def enrich(self, graph: Ontoscen) -> Ontoscen:
        """Enrich the resources and actors of an Ontoscen graph with
        Wikidata.

        Arguments:
            graph (Ontoscen): an Ontoscen graph.

        Returns:
            graph (Ontoscen): an Ontoscen graph linked with Wikidata.
        """

        return reduce(
            self._enrich_subject,
            graph.get_resources() + graph.get_actors(),
            graph,
        )

    def _enrich_subject(self, ontoscen: Ontoscen, subject: URIRef) -> Ontoscen:

        if self._is_enriched(subject, ontoscen):
            return ontoscen

        label = ontoscen.get_label(subject)
        if not label:
            return ontoscen

        results: list = self._query(label.toPython())

        if not results:
            return ontoscen

        chosen_result: dict = self._take_input(results, subject, label)

        if not chosen_result:
            return ontoscen

        ontoscen.add(
            (subject, OWL.sameAs, URIRef(chosen_result["concepturi"]))
        )
        ontoscen.add((subject, RDFS.label, Literal(chosen_result["label"])))

        if "description" in chosen_result.keys():
            ontoscen.add(
                (
                    subject,
                    SCHEMA.description,
                    Literal(chosen_result["description"]),
                )
            )

        return ontoscen

    def _take_input(
        self, options: list[dict], subject: URIRef, subject_label: str
    ) -> dict:
        print(
            "--------------------------------------------------------------------------------------------------------------------",
            f"The subject '{subject_label}' ({subject}) matches the following wikidata concepts.",
            "Select the most suitable option, or press Enter to skip.",
            "",
            sep="\n",
        )

        index: int = 0
        for option in options:
            index += 1
            item: str = option["concepturi"]
            label: str = option["label"]

            description: str = ""
            if "description" in option.keys():
                description: str = option["description"]

            print(
                f"{index}) {label}:",
                f"ConceptUri: {item}",
                sep="\n",
            )

            if description:
                print(f"Description: {description}")

            print("")

        selection = input("Select: ")
        try:
            return options[int(selection) - 1]
        except:
            return {}

    def _query(self, item_label: str) -> list[dict]:
        return self.WB.entity.search(item_label, "en", limit=self.LIMIT)[
            "search"
        ]

    def _is_enriched(self, subject: URIRef, graph: Graph) -> bool:
        return (subject, OWL.sameAs, None) in graph or (
            None,
            OWL.sameAs,
            subject,
        ) in graph
