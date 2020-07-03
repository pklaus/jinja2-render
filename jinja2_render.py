#!/usr/bin/env python3


def main():
    import argparse, sys, os, subprocess

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
        help="Context to choose. Omit for a list of contexts available in the configuration file (-c).",
    )

    try:
        import jinja2
    except ImportError:
        parser.error("Python package jinja2 is missing.")

    args = parser.parse_args()

    ## load the context configuration file
    if sys.version_info[0:3] < (3, 6):
        parser.error("Minimum Python version is 3.6 - Exiting.")

    import importlib.util

    try:
        contexts_file = os.path.abspath(args.contexts)
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

    loader = jinja2.FileSystemLoader(".")
    j2_env = jinja2.Environment(loader=loader, trim_blocks=True, lstrip_blocks=True)
    template = j2_env.get_template(args.template)

    with open(args.output, "wt") as f:
        f.write(template.render(CONTEXTS.get(args.which)))


if __name__ == "__main__":
    main()
