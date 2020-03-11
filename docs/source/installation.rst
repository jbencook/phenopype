
Installation
=============


Installing Trackpy
------------------

For Python Novices
^^^^^^^^^^^^^^^^^^

Installation is simple on Windows, OSX, and Linux, even for Python novices.

1. Get Scientific Python
""""""""""""""""""""""""

To get started with Python on any platform, download and install
`Anaconda <https://www.anaconda.com/distribution/>`_. It comes with the
common scientific Python packages built in.

2. Install trackpy
""""""""""""""""""

Open a command prompt. On Windows, you can use the "Anaconda Command Prompt"
installed by Anaconda or Start > Applications > Command Prompt. On a Mac, look
for Applications > Utilities > Terminal. Type these commands:

.. code-block:: bash

   conda update conda
   conda install -c conda-forge trackpy
   conda install -c conda-forge pims

The above installs trackpy and all its requirements, plus the recommended
`PIMS <http://soft-matter.github.io/pims/>`_ package that simplifies image-reading,
and that is used in the trackpy tutorials.