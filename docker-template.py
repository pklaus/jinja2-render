#!/usr/bin/env python3


def main():
    import argparse, sys, os, subprocess

    parser = argparse.ArgumentParser(description="Create Dockerfiles from templates")
    parser.add_argument(
        "--template-file", "-f", default="Dockerfile.jinja2", help="The Dockerfile template to use."
    )
    parser.add_argument(
        "--build-config-file",
        "-b",
        default="./build_configuration.py",
        help="The Python file containing the build configuration.",
    )
    parser.add_argument("--registry", "-r", help="Add registry address to image name.")
    parser.add_argument(
        "--platform", "-p", help="Build images for given platforms (requires experimental buildx plugin)"
    )
    parser.add_argument("--latest", "-l", help="Add tag latest when building the image")

    subparsers = parser.add_subparsers(dest="action", help="action to be executed")
    subparsers.required = True
    subparsers.add_parser("list-tags", help="Returns the list of available tags")
    parser_render = subparsers.add_parser("render", help="Render the template")
    parser_build = subparsers.add_parser("build", help="Render the template and build the image")

    for template_parser in parser_render, parser_build:
        template_parser.add_argument("tag", help="The tag to build (implies the base image to derive from).")

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
    if args.action in ("render", "build"):
        loader = jinja2.FileSystemLoader(".")
        env = jinja2.Environment(loader=loader, trim_blocks=True, lstrip_blocks=True)
        template = env.get_template(args.template_file)

        name, tag_end = args.tag.split(":")
        if args.registry is not None:
            name = "{}/{}".format(args.registry, name)
        shorttag = tag_end.split(".")[0]

        with open("Dockerfile", "w") as f:
            f.write(template.render(BUILDS[tag_end]))

        ## build
        if args.action == "build":
            if args.platform is not None:
                if args.latest is not None:
                    subprocess.run(
                        f"docker buildx build --pull -t {name}:{tag_end} -t {name}:{shorttag} -t {name}:latest --platform={args.platform} --push .",
                        shell=True,
                    )
                else:
                    subprocess.run(
                        f"docker buildx build --pull -t {name}:{tag_end} --platform={args.platform} --push .",
                        shell=True,
                    )
            else:
                if args.latest is not None:
                    subprocess.run(
                        f"docker build --pull --rm -t {name}:{tag_end} -t {name}:{shorttag} -t {name}:latest .",
                        shell=True,
                    )
                else:
                    subprocess.run(f"docker build --pull --rm -t {name}:{tag_end} .", shell=True)


if __name__ == "__main__":
    main()
