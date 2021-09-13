# Installation

It's recomended some kind of virtualenv for package installation

```sh
pip install -r requirements.txt
spacy download en_core_web_sm
```

## Usage

- In _data/input.txt_ it's specified the input text for the Natural Language Processing
  tool.

- After the analysis of the text, a knowledge graph is created containing all the
  objects and it's relations found.

- Next we run a script that fetches **broader** and **narrower** concepts found in
  [Agrovoc](https://agrovoc.fao.org/browse/agrovoc/en/) if there is a concept
  in the ontology with the same label.

- The output is written in **Turtle** format in _data/output.ttl_

- Finally we print to screen the final Graph using matplotlib
