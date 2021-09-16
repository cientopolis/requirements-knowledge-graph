from argparse import ArgumentParser

from src.jsonparser import JSONParser
from src.ontoscen import Ontoscen
from src.wikilink import Wikilink


def main():
    args = set_arguments().parse_args()
    Wikilink().enrich(
        Ontoscen(JSONParser(args.input).requirements())
    ).serialize(args.output, format=args.format, encoding="utf-8")


def set_arguments():
    parser = ArgumentParser(
        description="Generate an Ontoscen graph from a JSON file.",
    )
    parser.add_argument(
        "-i",
        "--input",
        default="data/input.json",
        help="Specify an input file containing a JSON list of scenarios "
        "(defaults to 'data/input.json').",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="data/output.ttl",
        help="Specify the output file for the Ontoscen graph (defaults to "
        "'data/output')",
    )

    parser.add_argument(
        "--format",
        choices=[
            "xml",
            "n3",
            "turtle",
            "nt",
            "pretty-xml",
            "trix",
            "trig",
            "nquads",
        ],
        default="turtle",
        help="Set the format of the output file (defaults to 'turtle')",
    )

    return parser


if __name__ == "__main__":
    main()
