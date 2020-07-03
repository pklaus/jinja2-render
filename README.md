# docker-template
*A Python Tool to Simplify the Automated Creation of a Dockerfile Using Jinja2 Templates*

**docker-template** hugely simplifies building Docker images with repetitive sections.
It is a Python script allowing to create Dockerfiles from a Jinja2 Template
with the help of a configuration file defining different contexts (`contexts.py`)

This is useful for example in the following cases:

* Your Dockerfile contains a lot of repeated statements.
  They can be replaced by a [Jinja2 For Loop][].
* Your Dockerfile depends on a software with different versions
  and you want to simplify/automate switching between them.

### Workflow

```
               docker-template
               (& contexts.py)
                     ↓

Dockerfile.jinja2    🡆    Dockerfile
```

### Synopsis

```
usage: docker-template [-h] [-c CONTEXTS] [-f TEMPLATE]
                       [-o OUTPUT]
                       [which]

Render Dockerfiles from Jinja2 templates

positional arguments:
  which        Which context to choose. Omit for a list of
               contexts defined in the context configuration
               provided with parameter -c. (default: None)

optional arguments:
  -h, --help   show this help message and exit
  -c CONTEXTS  The Python file defining the contexts to
               render the template. (default: ./contexts.py)
  -f TEMPLATE  The Jinja2 template to use. (default:
               Dockerfile.jinja2)
  -o OUTPUT    The output file to write to. (default:
               Dockerfile)
```

### Minimal Example

Content of `Dockerfile.jinja2`:

```Dockerfile
FROM {{ base_img }}

RUN apt-get update \
 && apt-get install -yq {{ packages | join(' ') }}

RUN echo "Done!"

```

Content of `context_configuration.py`:

```python
CONTEXTS = {
    "v1.0": {
        "base_img": "debian:10-slim",
        "packages": ["glibc-devel", "turboshutdown"],
    }
}

```

Call to `docker-template`:

```sh
docker-template v1.0
```

Resulting in the following rendered Dockerfile:

```Dockerfile
FROM debian:10-slim

RUN apt-get update \
 && apt-get install -yq glibc-devel turboshutdown

RUN echo "Done!"
```

### The Context Configuration File

The configuration file (defaults to `./context_config.py`) contains
one ore multiple context definitions to render the template.
This includes variables to be substituted, lists to render for loops, etc.

* The context configuration file **must** contain a global `CONTEXTS = {}`
  with keys corresponding to different contexts that can be selected.
  (*Pro Tip™*: Instead of a dictionary, this CONTEXTS object could also
  be a class that derives from dict.)
* The items in `CONTEXTS` are the actual context handed over to
  [jinja2.Template.render()](https://jinja.palletsprojects.com/en/2.11.x/api/#jinja2.Template.render).
  Usually this would also be a dictionary.

### Original Use Case

The script was originally developed to automate building different configurations
of the control system software EPICS and it's various modules.
Traditionally, those modules were installed by a single shell script with
fixed versions (i.e. synApps), which is bad in the Docker world
as a build failure at the end if it would require rebuilding everything before.

### How it compares to other templating tools

By using a Python file to provide the context for the template, much more
flexibility is possible than with a simple solution such as jinja2-cli or j2cli.
They allow to use files such as YAML, INI or JSON as input for variables.

A Python script can - however - in addition to defining static information
ease additional tasks tasks such as dependency management.
As an elaborate example of such a use case, have a look at
[this](https://github.com/pklaus/docker-epics/tree/master/epics_contapps),
where I use a custom class in the `contexts.py` along with additional code
to validate the resulting context.

### Authors

* Philipp Klaus, University Frankfurt  
  *initial author*
* Florian Feldbauer, University Bochum  
  *further improvements*

[Jinja2 For Loop]: https://jinja.palletsprojects.com/en/2.11.x/templates/#for
