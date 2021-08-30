from os import remove
from numpy import pi
import spacy
from spacy.matcher import Matcher
from rdflib import URIRef

from collections import Counter

NLP = spacy.load("en_core_web_sm")

MATCHER = Matcher(NLP.vocab)


class Analyzer:
    def _getVerbPosition(self, sentence):
        pos = 0
        for token in sentence:
            relation = self._getRelation(sentence)
            if token.text == relation:
                return pos
            pos += 1

    def _getRelation(self, sentence):
        for token in sentence:
            if token.pos_ == "VERB":
                return token.text

    def _counter_of_matches(self, matches):
        return Counter(map(lambda match: match[0], matches))

    def _select_matches_from_candidates(
        self, match_id, matches, candidate_list
    ):
        # if it matches with match_id and it has more than one match is bc it is matching with the modifiers and without it
        # it should get the most complete match
        if self._counter_of_matches(matches)[NLP.vocab.strings[match_id]] > 1:
            return max(candidate_list, key=len)
        elif len(candidate_list) == 1:
            return candidate_list[0]

    def _get_actor(self, episode) -> str:
        episode = NLP(episode)

        matches = MATCHER(
            episode[0 : self._getVerbPosition(episode)], as_spans=True
        )

        return str(matches[0])

    def _remove_unnecessary_matches(
        self, candidate_resources, candidate_resources_of
    ):
        with_modifier = list(
            filter(lambda r: self._has_modifier(r), candidate_resources)
        )
        simples = list(
            filter(lambda r: r not in with_modifier, candidate_resources)
        )
        simples_that_matter = list(
            filter(
                lambda s: not self.is_substring_of_any(s, with_modifier),
                simples,
            )
        )

        # breakpoint()
        return candidate_resources_of + list(
            filter(
                lambda r: not self.is_substring_of_any(
                    r, candidate_resources_of
                ),
                simples_that_matter + with_modifier,
            )
        )

    def _get_lemmatized_resources(self, episode):
        episode = NLP(episode)

        matches = MATCHER(episode)

        candidate_resources = set()
        candidate_resources_simple_od = list()
        candidate_resources_of = list()

        for match_id, start, end in matches:
            match = " ".join(
                [t.lemma_ for t in episode[start:end] if t.dep_ != "det"]
            )
            if NLP.vocab.strings[match_id] == "with":
                candidate_resources.add(match.replace("with", "").strip())
            elif NLP.vocab.strings[match_id] == "of":
                candidate_resources_of.append(match)
            elif NLP.vocab.strings[match_id] == "simple_od":
                candidate_resources_simple_od.append(match)

        candidate_resources = list(candidate_resources)
        candidate_resources += self._remove_unnecessary_matches(
            candidate_resources_simple_od, candidate_resources_of
        )

        # occurrence_on_of= self._select_matches_from_candidates(
        #     "of", matches, candidate_resources_of
        # )

        return candidate_resources

    def is_substring_of_any(self, simple, lista_compuestos):
        return any(simple in c for c in lista_compuestos)

    def _has_modifier(self, resource):
        return " " in resource

    def _add_rules_for_actors(self):
        MATCHER.add(
            "nominal_subject",
            [
                [
                    {"DEP": {"IN": ["compound", "amod"]}, "OP": "?"},
                    {
                        "POS": "NOUN",
                        "DEP": {
                            "IN": ["nsubj", "nsubjpass", "compound", "ROOT"]
                        },
                    },
                ],
            ],
        )

    def _remove_rules_for_actors(self):
        MATCHER.remove("nominal_subject")

    def _add_rules_for_resources(self):
        MATCHER.add(
            "with",
            [
                [
                    {"ORTH": "with"},  # with
                    {"DEP": "det", "OP": "?"},  # the
                    {"DEP": {"IN": ["amod", "compound"]}, "OP": "?"},  # tomato
                    {"DEP": {"IN": ["dobj", "pobj"]}},  # plant
                ],
            ],
        )
        MATCHER.add(
            "of",
            [
                [
                    {"DEP": {"IN": ["amod", "compound"]}, "OP": "?"},  # great
                    {"DEP": "dobj"},  # results
                    {"ORTH": "of"},  # of
                    {"DEP": "det", "OP": "?"},  # the
                    {"DEP": {"IN": ["amod", "compound"]}, "OP": "?"},  # soil
                    {"DEP": {"IN": ["dobj", "pobj", "poss"]}},  # analysis
                ]
            ],
        )

        MATCHER.add(
            "simple_od",
            [
                [
                    {"DEP": {"IN": ["amod", "compound"]}, "OP": "?"},  # tomato
                    {"POS": "NOUN", "DEP": "dobj"},  # plant
                ]
            ],
        )

    def _remove_rules_for_resources(self):
        MATCHER.remove("of")
        MATCHER.remove("with")
        MATCHER.remove("simple_od")

    def analyze_for_actors(self, episode) -> str:
        self._add_rules_for_actors()
        actor = self._get_actor(episode)
        self._remove_rules_for_actors()
        return actor

    def _get_resources(self, episode, resources):
        # this method is just necessary bc is needed to ask the user for adding some resources, and we don't want to ask twice
        # when delete it, modify analyze_for_resources to just add all resources found as in get_actor method
        # remove resources parameter too
        lista = list()
        for resource in self._get_lemmatized_resources(episode):
            if resource not in resources:
                lista.append(resource)

        return lista

    def analyze_for_actions(self, episode) -> str:
        action = ""
        ok = False
        episode = NLP(episode)
        for i in episode:
            if i.pos_ == "VERB":
                ok = True
            if ok:
                action = action + i.text + " "
            if i.dep_ == "dobj":
                ok = False
        return action.strip()

    def analyze_for_resources(
        self, episode: str, scenario: URIRef, resources: list[str]
    ) -> list[str]:
        self._add_rules_for_resources()
        resources_not_included = self._get_resources(episode, resources)
        result = list()
        if len(resources_not_included) > 1:
            print(
                f"The following resources are not defined for scenario {scenario}."
                "Select the number/s of the resource/s you want to include, or press Enter to skip.",
                sep="\n",
            )

            for index, resource_not_included in enumerate(
                resources_not_included
            ):
                print(str(index) + ")", resource_not_included)

            indexes = input("Options: ").replace("\n", " ").split()
            for index in indexes:
                if int(index) < len(resources_not_included):
                    result.append(resources_not_included[int(index)])
        elif len(resources_not_included) == 1:
            result.append(resources_not_included[0])

        self._remove_rules_for_resources()
        return result
