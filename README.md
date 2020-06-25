# docker-template
*A Python Tool to Simplify the Automated Creation of a Dockerfile Using Jinja2 Templates*

**docker-template** hugely simplifies building multi-module Docker images.
It is a Python script allowing to create Dockerfiles from a Jinja2 Template
and a (Python-based) configuration file (`build_configuration.py`).

This is useful for example in the following cases:

* Your Dockerfile contains a lot of repeated statements.
  They can be replaced by a [Jinja2 For Loop][].
* Your Dockerfile depends on a software with different versions
  and you want to simplify/automate switching between them.

### Workflow

```
              docker-template
          & build_configuration.py
                   ↓
                                   (optionally)
Dockerfile.jinja2  🡆  Dockerfile,  Docker image
```

### CLI

```
$ ./docker-template.py --help
usage: docker-template.py [-h] [--template-file TEMPLATE_FILE]
                          [--build-config-file BUILD_CONFIG_FILE]
                          [--registry REGISTRY] [--platform PLATFORM]
                          [--latest LATEST]
                          {list-tags,render,build} ...

Create Dockerfiles from templates

positional arguments:
  {list-tags,render,build}
                        action to be executed
    list-tags           Returns the list of available tags
    render              Render the template
    build               Render the template and build the image

optional arguments:
  -h, --help            show this help message and exit
  --template-file TEMPLATE_FILE, -f TEMPLATE_FILE
                        The Dockerfile template to use.
  --build-config-file BUILD_CONFIG_FILE, -b BUILD_CONFIG_FILE
                        The Python file containing the build configuration.
  --registry REGISTRY, -r REGISTRY
                        Add registry address to image name.
  --platform PLATFORM, -p PLATFORM
                        Build images for given platforms (requires experimental buildx
                        plugin)
  --latest LATEST, -l LATEST
                        Add tag latest when building the image
```

### Original Use Case

The script was originally developed to automate building different configurations
of the control system software EPICS and it's various modules.
Traditionally, those modules were installed by a single shell script with
fixed versions (i.e. synApps), which is bad in the Docker world
as a build failure at the end if it would require rebuilding everything before.

### Authors

* Philipp Klaus, University Frankfurt  
  *initial author*
* Florian Feldbauer, University Bochum  
  *custom registries, support for buildx*

[Jinja2 For Loop]: https://jinja.palletsprojects.com/en/2.11.x/templates/#for
