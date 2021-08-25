from typing import List
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
        self, match_id, matches, candidate_resources, candidate_list
    ):
        # if it matches with match_id and it has more than one match is bc it is matching with the modifiers and without it
        # it should get the most complete match
        if self._counter_of_matches(matches)[NLP.vocab.strings[match_id]] > 1:
            candidate_resources.add(max(candidate_list, key=len))
        elif len(candidate_list) == 1:
            candidate_resources.add(candidate_list[0])

    def _get_actor(self, episode):
        episode = NLP(episode)

        matches = MATCHER(
            episode[0 : self._getVerbPosition(episode)], as_spans=True
        )
        return matches[0]

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

        self._select_matches_from_candidates(
            "simple_od",
            matches,
            candidate_resources,
            candidate_resources_simple_od,
        )
        self._select_matches_from_candidates(
            "of", matches, candidate_resources, candidate_resources_of
        )

        return candidate_resources

    def _add_rules_for_actors(self):
        MATCHER.add(
            "nominal_subject",
            [
                [
                    {"DEP": "amod", "OP": "?"},
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

    def _is_resource_included(self, candidate_resource, resources):
        return candidate_resource in self._get_lemma_from_included_resources(
            resources
        )

    def _get_resources_not_defined_in_scenario(self, episode: str, resources: list[str]):
        resources_not_included = list()
        for candidate_resource in self._get_lemmatized_resources(episode):
            if not self._is_resource_included(candidate_resource, resources):
                resources_not_included.append(candidate_resource)

        return resources_not_included

    def _get_lemma_from_included_resources(self, resources):
        lemmatized_resources = list()
        for resource in resources:
            resource = NLP(resource)
            lemmatized_resources.append(" ".join([r.lemma_ for r in resource]))
        return lemmatized_resources

    def analyze_for_actors(self, episode, actors, scenario) -> str:
        self._add_rules_for_actors()
        actor = self._get_actor(episode)
        if str(actor) not in actors:
            answer = input(
                f"The actor {actor} is not defined for scenario {scenario}. Add it? Y/n "
            )
            if answer.lower() == "y":
                self._remove_rules_for_actors()
                return actor
        self._remove_rules_for_actors()

    def analyze_for_actions(self, episode) -> str:
        action = ""
        ok = False
        episode= NLP(episode)
        for i in episode:
            if i.pos_ == "VERB":
                ok = True
            if ok:
                action = action +i.text +" "
            if i.dep_ == "dobj":
                ok = False
        return action.strip()

    def analyze_for_resources(self, episode: str, resources: list[str], scenario: URIRef) -> list[str]:
        self._add_rules_for_resources()
        resources_not_included = self._get_resources_not_defined_in_scenario(
            episode, resources
        )

        result = list()
        if resources_not_included:
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
                else:
                    print("Skipped.")

        self._remove_rules_for_resources()
        return result
