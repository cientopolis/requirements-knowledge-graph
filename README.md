# Ontoscen generator - DEV

Ontoscen generator is a Python tool that provides support for building an ontology in turtle format

## Structure
✨ ```src/tomatoScenarios``` is the JSON file with a requirement specification made using Scenarios. You can replace it by another one following the same format

✨ ``` ScenarioGraph ``` class builds each Scenario specification 

✨ ``` Parser``` class extract the necessary data from the json object, making some changes like avoid whitespaces between words that will be used in the iri


## Dependencies

You must have the following libraries installed in your OS: pandas, rdflib

## Running

```python
py main.py src/tomatoScenarios.json
```