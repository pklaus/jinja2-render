#!/usr/bin/env python3

import argparse, os, subprocess, sys
import importlib.util
from contextlib import contextmanager


@contextmanager
def add_to_path(p):
    old_path = sys.path
    sys.path = sys.path[:]
    sys.path.insert(0, p)
    try:
        yield
    finally:
        sys.path = old_path

def main():
    ## Command Line Argument Parsing
    parser = argparse.ArgumentParser(
        description="Render a Jinja2 template from the command line.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-c",
        dest="contexts",
        default="./contexts.py",
        help="The Python file defining the contexts to render the template.",
    )
    parser.add_argument("-f", default="Dockerfile.jinja2", dest="template", help="The Jinja2 template to use.")
    parser.add_argument(
        "-o", default="Dockerfile", dest="output", help="The output file to write to.",
    )
    parser.add_argument(
        "which",
        nargs="?",
        help="Context to choose. Omit for a list of contexts available in the contexts file (-c).",
    )

    try:
        import jinja2
    except ImportError:
        parser.error("Python package jinja2 is missing.")

    args = parser.parse_args()

    if sys.version_info[0:3] < (3, 6):
        parser.error("Minimum Python version is 3.6 - Exiting.")


    try:
        contexts_file = os.path.abspath(args.contexts)
        with add_to_path(os.path.dirname(contexts_file)):
            spec = importlib.util.spec_from_file_location("contexts", contexts_file)
            contexts = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(contexts)
    except FileNotFoundError:
        parser.error("Cannot find file {}".format(os.path.abspath(args.contexts)))

    CONTEXTS = contexts.CONTEXTS

    if args.which is None:
        print("No context to render the template was provided. Please choose from:", file=sys.stderr)
        for tag in CONTEXTS:
            print(tag)
        sys.exit(0)

    if args.which not in CONTEXTS:
        print(f"Invalid context {args.which}. Available contexts are:", file=sys.stderr)
        for tag in CONTEXTS:
            print(tag, file=sys.stderr)
        sys.exit(1)

    loader = jinja2.FileSystemLoader(".")
    j2_env = jinja2.Environment(loader=loader, trim_blocks=True, lstrip_blocks=True)
    template = j2_env.get_template(args.template)

    with open(args.output, "wt") as f:
        f.write(template.render(CONTEXTS.get(args.which)))


if __name__ == "__main__":
    main()
