# Ontoscen generator

Ontoscen generator is a Python tool that builds an Ontoscen graph out of a json file.

## Structure

✨ [`data/input.json`](./data/input.json) is a file containing requirement specification in the form of Scenarios. You can replace it by another file as long as it follows the same format.

✨ [`Ontoscen`](./src/ontoscen.py) represents an RDF graph with the Ontoscen ontology.

✨ [`JSONParser`](./src/jsonparser.py) helps extract the data from the JSON file.

✨ [`Requirement`](./src/requirement.py) models a scenario.

## Installing

```bash
# Clone the repo
git clone https://github.com/cientopolis/requirements-knowledge-graph \
  && cd requirements-knowledge-graph \
  && git checkout ontoscen

# Setup and activate a virtual environment
if python -m venv .venv && source .venv/bin/activate; then
  # Upgrade pip just in case
  python -m pip install --upgrade pip

  # Get dependencies
  pip install -r requirements.txt
fi
```

## Running

The tool should be used as follows:

```bash
python main.py input_file output_file format
```

Example:

```bash
python main.py data/input.json data/output.ttl turtle
```
