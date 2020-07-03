# docker-template
*A Python Tool to Simplify the Automated Creation of a Dockerfile Using Jinja2 Templates*

**docker-template** hugely simplifies building multi-module Docker images.
It is a Python script allowing to create Dockerfiles from a Jinja2 Template
with the help of a configuration file (`build_configuration.py`).

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

Dockerfile.jinja2  🡆  Dockerfile
```

### How it compares to other templating tools

By using a Python file to provide the context for the template, much more
flexibility is possible than with a simple solution such as jinja2-cli or j2cli.
They allow to use files such as YAML, INI or JSON as input for variables.

A Python script - however - can also simply define a dictionary like structure
for the context. In many ways very similar to a JSON file.
But it can also ease complicated tasks such as dependency management.
As an elaborate example of such a use case, have a look at
[this](https://github.com/pklaus/docker-epics/tree/master/epics_contapps),
where I use a custom class in the `build_configuration.py` and further code
to validate the resulting context.

### CLI

```
usage: docker-template [-h] [--build-config-file BUILD_CONFIG_FILE]
                       {list-tags,render} ...

Create Dockerfiles from templates

positional arguments:
  {list-tags,render}    action to be executed
    list-tags           Returns the list of available tags
    render              Render the template

optional arguments:
  -h, --help            show this help message and exit
  --build-config-file BUILD_CONFIG_FILE, -b BUILD_CONFIG_FILE
                        The Python file containing the build
                        configuration.
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
  *further improvements*

[Jinja2 For Loop]: https://jinja.palletsprojects.com/en/2.11.x/templates/#for
