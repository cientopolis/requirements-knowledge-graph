import pandas as pd

class Parser:
    @staticmethod
    def getScenario(jsonObject):
        return jsonObject['scenario']

    @staticmethod
    def getContext(jsonObject):
        return jsonObject['context']
    
    @staticmethod
    def getGoal(jsonObject):
        return jsonObject['goal']

    @staticmethod
    def getActors(jsonObject):
        return map(lambda x: x.replace(' ', '_'), jsonObject['actors'])

    @staticmethod
    def getEpisodes(jsonObject):
        return jsonObject['episodes']

    @staticmethod
    def getResources(jsonObject):
        return map(lambda x: x.replace(' ', '_'), jsonObject['resources'])