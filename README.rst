
pyppl_require
=============

Requirement manager for `PyPPL <https://github.com/pwwang/PyPPL>`_.

Installation
------------

It requires `pyppl_annotate <https://github.com/pwwang/pyppl_annotate>`_.

.. code-block:: shell

   pip install pyppl_require

Usage
-----

.. code-block:: shell

   > pyppl require
   Description:
     Process requirement manager

   Usage:
     pyppl require <--pipe AUTO> [OPTIONS]

   Required options:
     -p, --pipe <AUTO>     - The pipeline script.

   Optional options:
     --install <AUTO>      - Install the requirements.
                             You can specify a directory (default: $HOME/bin) to install the \
                             requirements.
                             Default: None
     -h, -H, --help        - Show help message and exit.

To allow your processes to be analyzed, you have to put a section in annotate using ``toml`` format:

.. code-block:: python

   pXXX.config.annotate = """
   @requires:
     [bedtools]
     validate: "bedtools --version"
     install: "conda install -c bioconda bedtools"
     # other annotations
   """

If you want define those commands using process properties and aggrs:

.. code-block:: python

   pXXX.config.annotate = """
   @requires:
     [bedtools]
     validate: "{{args.bedtools}} --version"
     install: "conda install -c bioconda bedtools"
     # other annotations
   """

Install to a specify directory:

.. code-block:: python

   pXXX.config.annotate = """
   @requires:
     [bedtools]
     validate: "{{args.bedtools}} --version"
     install: "conda install -c bioconda bedtools; ln -s $(which bedtools) {{bindir}}/bedtools"
     # other annotations
   """

``{{bindir}}`` will be the directory passed to the command line.

.. code-block:: shell

   pyppl require --pipe <your pipeline> --install </path/to/bin>
