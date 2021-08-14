from sys import argv, exit

from src.ontoscen import Ontoscen
from src.jsonparser import JSONParser

if __name__ == "__main__":
    if len(argv) != 4:
        print("gen-ontoscen: amount of parameters incorrect.")
        print("USAGE: python main.py INPUT_FILE.json OUTPUT_FILE FORMAT")
        exit(1)

    graph = Ontoscen(JSONParser(argv[1]).requirements())
    graph.save(argv[2], argv[3])
