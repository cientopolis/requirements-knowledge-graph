# Ontoscen generator

Ontoscen generator is a Python tool that builds an Ontoscen graph out of a json file.

## Structure

✨ [`data/input.json`](gen-ontoscen/data/input.json) is a file containing requirement
specification in the form of Scenarios. You can replace it with any file
that follows the same format.

✨ [`Ontoscen`](gen-ontoscen/src/ontoscen.py) represents an
RDF graph with the Ontoscen ontology.

✨ [`JSONParser`](gen-ontoscen/src/jsonparser.py) helps extract the data from the
JSON file.

✨ [`Requirement`](gen-ontoscen/src/requirement.py) models a scenario.

## Installing

```bash
# Clone the repo
git clone https://github.com/cientopolis/requirements-knowledge-graph \
  && cd requirements-knowledge-graph \
  && cd gen-ontoscen

# If you don't have `make` installed, fall back to bash
make setup || if python -m venv .venv && source .venv/bin/activate; then
  python -m pip install --upgrade pip
  pip install -r requirements.txt
fi
```

## Usage

```help
$ python main.py -h

usage: main.py [-h] [-i INPUT] [-o OUTPUT] [--format {xml,n3,turtle,nt,pretty-xml,trix,trig,nquads}]

Generate an Ontoscen graph from a JSON file.

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        Specify an input file containing a JSON list of scenarios (defaults to 'data/input.json').
  -o OUTPUT, --output OUTPUT
                        Specify the output file for the Ontoscen graph (defaults to 'data/output')
  --format {xml,n3,turtle,nt,pretty-xml,trix,trig,nquads}
                        Set the format of the output file (defaults to 'turtle')
```

Example:

```bash
python main.py --input data/input.json --output data/output.ttl --format turtle
```

Remember to get inside the virtual environment:

```bash
$ source .venv/bin/activate
```

## Test

From `gen-ontoscen/` run:

```bash
$ make test
```

Or, if you prefer not to use `make`:

```bash
$ python -m unittest discover test -b
```
