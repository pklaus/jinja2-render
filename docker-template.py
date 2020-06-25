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

    subparsers = parser.add_subparsers(dest="action")
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

    ## no action chosen
    if not args.action:
        parser.error("Please choose an action.")

    ## load build_configuration.py from workdir
    ## https://stackoverflow.com/a/67692
    if sys.version_info[0] >= 3 and sys.version_info[1] >= 5:
        try:
            import importlib.util

            spec = importlib.util.spec_from_file_location("buildconfig", os.path.abspath(args.build_config_file))
            build_configuration = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(build_configuration)
        except FileNotFoundError:
            parser.error("Cannot find file {}".format(os.path.abspath(args.build_config_file)))

    elif sys.version_info[0] >= 3 and sys.version_info[1] in (3, 4):
        try:
            from importlib.machinery import SourceFileLoader

            build_configuration = SourceFileLoader(
                "buildconfig", os.path.abspath(args.build_config_file)
            ).load_module()
        except FileNotFoundError:
            parser.error("Cannot find file {}".format(os.path.abspath(args.build_config_file)))

    else:
        parser.error("Couldn't detect python version.")

    BUILDS = build_configuration.BUILDS

    ## list-tags
    if args.action == "list-tags":
        for tag in BUILDS.keys():
            print(tag)
        sys.exit(0)

    ## render
    if args.action in ("render", "build"):
        from jinja2 import FileSystemLoader, Environment

        loader = FileSystemLoader(".")
        env = Environment(loader=loader, trim_blocks=True, lstrip_blocks=True)
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
                        "docker buildx build --pull -t {name}:{tag1} -t {name}:{tag2} -t {name}:latest --platform={platform} --push .".format(
                            name=name, tag1=tag_end, tag2=shorttag, platform=args.platform
                        ),
                        shell=True,
                    )
                else:
                    subprocess.run(
                        "docker buildx build --pull -t {name}:{tag1} --platform={platform} --push .".format(
                            name=name, tag1=tag_end, platform=args.platform
                        ),
                        shell=True,
                    )
            else:
                if args.latest is not None:
                    subprocess.run(
                        "docker build --pull --rm -t {name}:{tag1} -t {name}:{tag2} -t {name}:latest .".format(
                            name=name, tag1=tag_end, tag2=shorttag
                        ),
                        shell=True,
                    )
                else:
                    subprocess.run(
                        "docker build --pull --rm -t {name}:{tag1} .".format(name=name, tag1=tag_end), shell=True
                    )


if __name__ == "__main__":
    main()
