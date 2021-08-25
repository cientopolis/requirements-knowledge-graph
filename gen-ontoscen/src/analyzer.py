from itertools import chain
from os import read
from typing import List
from numpy import mat
import spacy
from spacy.matcher import Matcher

from src.jsonparser import JSONParser

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
        ocurrences_of_match_id= list()
        [ocurrences_of_match_id.append(match_id) for match_id, start, end in matches]
        return Counter(ocurrences_of_match_id)

    def _select_matches_from_candidates(self, match_id, matches, candidate_resources, candidate_list):
        #if it matches with match_id and it has more than one match is bc it is matching with the modifiers and without it
        #it should get the most complete match
        if (self._counter_of_matches(matches)[NLP.vocab.strings[match_id]] > 1):        
            candidate_resources.add(max(candidate_list, key=len))
        elif len(candidate_list)==1:
            candidate_resources.add(candidate_list[0])
    
    def _get_action(self, episode):
            accion = ""
            ok = False
            episode= NLP(episode)
            for i in episode:
                if i.pos_ == "VERB":
                    ok = True
                if ok:
                    accion = accion +i.text +" "
                if i.dep_ == "dobj":
                    ok = False
            return accion.strip()

    def _get_actor(self, episode):
        episode= NLP(episode)

        matches = MATCHER(episode[0:self._getVerbPosition(episode)], as_spans=True)
        return matches[0] 

    def _get_resources(self, episode): 
        episode= NLP(episode)    
        matches=MATCHER(episode)   

        candidate_resources= set()
        candidate_resources_simple_od= list()  
        candidate_resources_of = list()  

        for match_id, start, end in matches:
            match= " ".join([t.lemma_ for t in episode[start:end] if t.dep_ != "det"])
            if (NLP.vocab.strings[match_id]=='with'):
                candidate_resources.add(match.replace('with','').strip())
            elif (NLP.vocab.strings[match_id]=='of'):
                candidate_resources_of.append(match)
            elif (NLP.vocab.strings[match_id]=='simple_od'):
                candidate_resources_simple_od.append(match)
       
        self._select_matches_from_candidates('simple_od', matches, candidate_resources, candidate_resources_simple_od)
        self._select_matches_from_candidates('of', matches, candidate_resources, candidate_resources_of)   

        return candidate_resources

    def _addRulesForActors(self):
        MATCHER.add(
        "nominal_subject",
        [
            [
                {'DEP': 'amod', 'OP': '?'},
                {'POS': 'NOUN', 'DEP': {"IN": ["nsubj", "nsubjpass", "compound", "ROOT"]}}
            ],
        ]
        )

    def _removeRulesForActors(self):
        MATCHER.remove("nominal_subject")

    def _addRulesForActions(self):
        MATCHER.add(
        "action",
        [
            [
                {'POS': 'VERB', 'DEP':'ROOT'},
            ],
            [
                {'POS':'ADJ','DEP':{'IN': ['amod', 'compound']}, 'OP':'?'},
                {'POS':{'IN':['ADJ', 'NOUN']} ,'DEP': {'IN': ['amod', 'compound', 'dobj']}},
                {'DEP': 'prep', 'OP':'?'},
                {'DEP':'det', 'OP':'?'},
                {'DEP': 'compound', 'OP':'?'},
                {'DEP': {'IN': ['pobj','dobj', 'appos']}},
                {'POS':'NOUN', 'OP':'?'}
                
            ],
            [
                {'POS': 'NOUN', 'DEP': {"IN": ["dobj", "pobj"]}}
            ]
        ]
        )      
   
    def _removeRulesForActions(self):
        MATCHER.remove("action")

    def _addRulesForResources(self):
        MATCHER.add(
            'with',
            [
                [
                    {'ORTH':'with'},
                    {'DEP':'det', 'OP':'?'},
                    {'DEP':{'IN': ['amod', 'compound']}, 'OP':'?'},
                    {'DEP': {"IN": ['dobj', 'pobj']}}
                ],
            ]
        )
        MATCHER.add(
            'of',
            [
                [
                    {'DEP':{'IN': ['amod', 'compound']}, 'OP':'?'},
                    {'DEP': 'dobj'},
                    {'ORTH':'of'},
                    {'DEP':'det', 'OP':'?'},
                    {'DEP':{'IN': ['amod', 'compound']}, 'OP':'?'},
                    {'DEP': {"IN": ["dobj", "pobj", "poss"]}}
                ]
            ]
        )
        MATCHER.add(
            'simple_od',
            [
                [
                    {'DEP':{'IN': ['amod', 'compound']}, 'OP':'?'},
                    {'POS': 'NOUN','DEP':'dobj'}
                ]
            ]            
        )
    
    def _removeRulesForResources(self):
        MATCHER.remove('of')
        MATCHER.remove('with')
        MATCHER.remove('simple_od')

    def analyzeForActors(self,episode, actors, scenario) -> str:
        self._addRulesForActors()
        actor= self._getActor(episode)
        if str(actor) not in actors:
            answer= input(f"The actor {actor} is not defined for scenario {scenario}. Add it? Y/n ")
            if (answer.lower()=="y"):
                self._removeRulesForActors()
                return actor
        self._removeRulesForActors()

    def analyzeForActions(self, episode) -> List:
        self._addRulesForActions()
        action= self._get_action(episode)
        
        self._removeRulesForActions()
        return action 

    def _get_lemma_from_included_resources(self, resources):
        lemmatized_resources=list()
        for resource in resources:
            resource= NLP(resource)
            lemmatized_resources.append(" ".join([r.lemma_ for r in resource]))
        return lemmatized_resources

    def _get_resoruces_not_defined_in_scenario(self, episode, resources):
        resources_not_included= list()
        for candidate_resource in self._get_resources(episode): 
            if candidate_resource not in self._get_lemma_from_included_resources(resources):
                resources_not_included.append(candidate_resource)

        return resources_not_included

    def analyzeForResources(self,episode, resources, scenario) -> List:

        self._addRulesForResources()
        resources_not_included= self._get_resoruces_not_defined_in_scenario(episode, resources)     
        
        resources=list()
        if (resources_not_included):
            print(f"The following resources are not defined for scenario {scenario}. \nSelect numbers separated by space if you want to include some of them")
        
            for index, resource_not_included in enumerate(resources_not_included):
                print(str(index)+')', resource_not_included)
            
            indexes= input("Options: ").split(' ')
            if (indexes[0]):
                [resources.append(resources_not_included[int(index)]) for index in indexes]
            
        self._removeRulesForResources()
        return resources

        
