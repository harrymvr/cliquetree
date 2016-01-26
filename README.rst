================================
Dynamic Clique Tree
================================

|docs| |travis| |coveralls|
    
Given a chordal graph, this package provides functions to update the graph
ensuring its chordality. It is based on the first of the two implementations 
described in

::
    Ibarra, Louis. 
    "Fully dynamic algorithms for chordal graphs and split graphs"
    ACM Transactions on Algorithms (TALG) (2008).

The ``add_edge`` and ``update_insertable(v)`` operations costs O(n), where n is 
the number of nodes in the graph.

Installation
------------

You can install the *cliquetree* package by executing the following command in a terminal.

::

   pip install git+https://github.com/harrymvr/cliquetree#Egg=cliquetree

Documentation
-------------

For instructions on how to use the package, consult `its documentation`__.

__ https://cliquetree.readthedocs.org/

Development
-----------

To run all the tests for the code, you will need tox_ -- check its webpage for instructions on how to install it.

.. _tox: https://testrun.org/tox/latest/

Once tox_ is installed, use your terminal to enter the directory with the local copy of the code (here it's named '*absorbing-centrality*') and simply type the following command.

::

    cliquetree $ tox

If everything goes well, you'll receive a congratulatory message. 


Note that the code is distributed under the Open Source Initiative (ISC) license.
For the exact terms of distribution, see the LICENSE_.

.. _LICENSE: ./LICENSE

::

   Copyright (c) 2016, cliquetree contributors,
   Charalampos Mavroforakis <cmav@bu.edu>

    
.. |docs| image:: https://readthedocs.org/projects/cliquetree/badge/?version=latest
    :target: https://cliquetree.readthedocs.org/en/latest/
    :alt: Documentation Status

.. |travis| image:: https://travis-ci.org/harrymvr/cliquetree.svg?branch=master
    :alt: Travis-CI Build Status
    :target: https://travis-ci.org/harrymvr/cliquetree

.. |requires| image:: https://requires.io/github/harrymvr/cliquetree/requirements.svg?branch=master
    :alt: Requirements Status
    :target: https://requires.io/github/harrymvr/cliquetree/requirements/?branch=master


.. |coveralls| image:: https://coveralls.io/repos/harrymvr/cliquetree/badge.svg?branch=master&service=github
    :alt: Coverage Status
    :target: https://coveralls.io/github/harrymvr/cliquetree?branch=master


.. |version| image:: https://img.shields.io/pypi/v/cliquetree.svg?style=flat
    :alt: PyPI Package latest release
    :target: https://pypi.python.org/pypi/cliquetree

.. |downloads| image:: https://img.shields.io/pypi/dm/cliquetree.svg?style=flat
    :alt: PyPI Package monthly downloads
    :target: https://pypi.python.org/pypi/cliquetree

.. |wheel| image:: https://img.shields.io/pypi/wheel/cliquetree.svg?style=flat
    :alt: PyPI Wheel
    :target: https://pypi.python.org/pypi/cliquetree

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/cliquetree.svg?style=flat
    :alt: Supported versions
    :target: https://pypi.python.org/pypi/cliquetree

.. |supported-implementations| image:: https://img.shields.io/pypi/implementation/cliquetree.svg?style=flat
    :alt: Supported imlementations
    :target: https://pypi.python.org/pypi/cliquetree

