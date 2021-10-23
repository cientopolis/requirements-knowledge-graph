from functools import reduce
from json import load, dump

from rdflib import Literal, Namespace, URIRef
from rdflib.namespace import OWL, RDFS
from wikibase_api import Wikibase

from .ontoscen import Ontoscen
from .helpers import get_user_input


SCHEMA = Namespace("https://schema.org/")


class Wikilink:
    """A class to link an Ontoscen graph with information from Wikidata.

    Attributes:
        LIMIT (int): max amount of items to choose from for each
            subject.
    """

    def __init__(self, limit: int = 10):
        self.LIMIT: int = limit
        self.WB: Wikibase = Wikibase()
        self.CACHE_FILE: str = "data/cache.json"
        self.CACHE: dict = self.open_cache()

    def enrich(self, graph: Ontoscen) -> Ontoscen:
        """Enrich the resources and actors of an Ontoscen graph with
        Wikidata.

        Arguments:
            graph (Ontoscen): an Ontoscen graph.

        Returns:
            graph (Ontoscen): an Ontoscen graph linked with Wikidata.
        """

        enriched_graph = reduce(
            self._enrich_subject,
            graph.get_resources() + graph.get_actors(),
            graph,
        )
        self.save_cache()
        return enriched_graph

    def open_cache(self) -> dict:
        try:
            with open(self.CACHE_FILE, mode="r", encoding="utf8") as file:
                return load(file)
        except FileNotFoundError:
            return {}

    def save_cache(self) -> None:
        with open(self.CACHE_FILE, "w", encoding="utf-8") as file:
            dump(self.CACHE, file, ensure_ascii=False, indent=4)

    def _enrich_subject(self, ontoscen: Ontoscen, subject: URIRef) -> Ontoscen:

        if ontoscen.is_linked(subject):
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

        selection = get_user_input("Select: ")
        try:
            return options[int(selection) - 1]
        except:
            return {}

    def _query(self, item_label: str) -> list[dict]:
        if not item_label in self.CACHE.keys():
            self.CACHE[item_label] = self.WB.entity.search(
                item_label, "en", limit=self.LIMIT
            )["search"]
        return self.CACHE[item_label]
