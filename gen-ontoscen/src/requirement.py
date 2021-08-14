class Requirement:
    """A Python representation of a software requirement specification
    in the form of scenarios.

    Attributes:
        scenario (str): The title of the scenario.
        goal (str): The objective to achieve with the scenario.
        context (str): The prerequisites of the scenario.
        actors (list[str]): The subjects that will do some activity to
            complete the scenario.
        resources (list[str]): The objects that will be used in the
            scenario.
        episodes (list[str]): The steps needed to complete the scenario.
    """

    def __init__(self, req: dict):
        self.scenario = req["scenario"]
        self.goal = req["goal"]
        self.context = req["context"]
        self.episodes = req["episodes"]
        self.actors = req["actors"]
        self.resources = req["resources"]
