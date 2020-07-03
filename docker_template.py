#!/usr/bin/env python3


def main():
    import argparse, sys, os, subprocess

    ## Command Line Argument Parsing
    parser = argparse.ArgumentParser(description="Render Dockerfiles from Jinja2 templates")
    parser.add_argument(
        "--build-config-file",
        "-b",
        default="./build_configuration.py",
        help="The Python file containing the build configuration.",
    )

    # subparser for possible actions
    subparsers = parser.add_subparsers(dest="action", help="action to be executed")
    subparsers.required = True

    # ACTION list-tags
    subparsers.add_parser("list-tags", help="Returns the list of available tags")

    # ACTION render
    parser_render = subparsers.add_parser("render", help="Render the template")
    parser_render.add_argument(
        "build_config_tag", help="Tag to select from the build configuration file.",
    )
    parser_render.add_argument(
        "--template-file", "-f", default="Dockerfile.jinja2", help="The Dockerfile template to use."
    )

    try:
        import jinja2
    except ImportError:
        parser.error("Python package jinja2 is missing.")

    args = parser.parse_args()

    ## load build_configuration.py from workdir
    if sys.version_info[0:3] < (3, 6):
        parser.error("Minimum Python version is 3.6 - Exiting.")

    import importlib.util

    try:
        build_config_file = os.path.abspath(args.build_config_file)
        spec = importlib.util.spec_from_file_location("buildconfig", build_config_file)
        build_configuration = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(build_configuration)
    except FileNotFoundError:
        parser.error("Cannot find file {}".format(os.path.abspath(args.build_config_file)))

    BUILDS = build_configuration.BUILDS

    ## list-tags
    if args.action == "list-tags":
        for tag in BUILDS.keys():
            print(tag)
        sys.exit(0)

    ## render
    if args.action == "render":
        loader = jinja2.FileSystemLoader(".")
        env = jinja2.Environment(loader=loader, trim_blocks=True, lstrip_blocks=True)
        template = env.get_template(args.template_file)

        with open("Dockerfile", "w") as f:
            f.write(template.render(BUILDS[args.build_config_tag]))


if __name__ == "__main__":
    main()
