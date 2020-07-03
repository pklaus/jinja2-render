# -*- coding: utf-8 -*-

from setuptools import setup

try:
    import pypandoc
    LDESC = pypandoc.convert_file('README.md', 'rst', format='md')
except (ImportError, IOError, RuntimeError) as e:
    print("Pandoc / pypandoc missing - couldn't create convert README.md to reStructuredText")
    print(str(e))
    LDESC = ''

setup(name='docker-template',
      version = '1.dev',
      description = 'docker-template – A tool to render Jinja2 templates to Dockerfiles',
      long_description = LDESC,
      author = 'Philipp Klaus',
      author_email = 'philipp.l.klaus@web.de',
      url = 'https://github.com/pklaus/docker-template',
      license = 'GPL',
      #packages = ['',],
      py_modules = ['docker_template',],
      entry_points = {
          'console_scripts': [
              'docker-template = docker_template:main',
          ],
      },
      zip_safe = True,
      platforms = 'any',
      install_requires = [
          "jinja2",
      ],
      keywords = 'PySerial Manager',
      classifiers = [
          'Development Status :: 4 - Beta',
          'Operating System :: OS Independent',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python',
          'Programming Language :: Python :: 3',
          'Topic :: System :: Archiving :: Packaging',
      ]
)
