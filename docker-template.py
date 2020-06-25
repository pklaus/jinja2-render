#!/usr/bin/env python3


def main():
    import argparse, sys, os, subprocess

    ## Command Line Argument Parsing
    parser = argparse.ArgumentParser(description="Create Dockerfiles from templates")
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

    # ACTION build
    parser_build = subparsers.add_parser("build", help="Render the template and build the image")

    # ACTION buildx
    parser_buildx = subparsers.add_parser("buildx", help="Render the template and build the image using buildx")
    parser_buildx.add_argument("--platform", "-p", help="Build images for given platforms")

    # render, build, buildx ACTIONs: additional arguments
    for sub_parser in (parser_render, parser_build, parser_buildx):
        sub_parser.add_argument(
            "build_config_tag", help="Tag to select from the build configuration file.",
        )
        sub_parser.add_argument(
            "--template-file", "-f", default="Dockerfile.jinja2", help="The Dockerfile template to use."
        )

    # build, buildx ACTIONs: additional arguments
    for sub_parser in (parser_build, parser_buildx):
        sub_parser.add_argument(
            "--tag", "-t", nargs="*", help="Name of the image and optionally a tag in the 'name:tag' format"
        )
        sub_parser.add_argument(
            "--dry",
            action="store_true",
            help="Dry run: don't render the Dockerfile, only print the resulting build command.",
        )
        sub_parser.add_argument(
            "--additional-args",
            "-a",
            default=("--pull --push" if sub_parser == parser_buildx else "--pull"),
            help="Additional options/arguments for the `docker build` / `docker buildx build` command.",
        )

    try:
        import jinja2
    except ImportError:
        parser.error("Please install the Python package jinja2 to make this script work.")

    args = parser.parse_args()

    ## load build_configuration.py from workdir
    if sys.version_info[0:3] < (3, 6):
        parser.error("Minimum Python version is 3.6 - Exiting.")

    import importlib.util

    try:
        spec = importlib.util.spec_from_file_location("buildconfig", os.path.abspath(args.build_config_file))
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
    if args.action == "render" or (args.action in ("build", "buildx") and not args.dry):
        loader = jinja2.FileSystemLoader(".")
        env = jinja2.Environment(loader=loader, trim_blocks=True, lstrip_blocks=True)
        template = env.get_template(args.template_file)

        with open("Dockerfile", "w") as f:
            f.write(template.render(BUILDS[args.build_config_tag]))

    ## build / buildx
    if args.action not in ("build", "buildx"):
        sys.exit(0)
    tags = " ".join(f"-t {tag}" for tag in args.tag)
    if args.action == "build":
        cmd = f"docker build {args.additional_args} {tags} ."
    if args.action == "buildx":
        cmd = f"docker buildx build --platform={args.platform} {args.additional_args} {tags} ."
    if args.dry:
        print("DRY RUN - resulting command line call would be:")
        print(cmd)
        sys.exit(0)
    sys.exit(subprocess.run(cmd, shell=True).returncode)


if __name__ == "__main__":
    main()
