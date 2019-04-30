stationarizer ෴
###############
|PyPI-Status| |PyPI-Versions| |Build-Status| |Codecov| |LICENCE|

Smart, automatic detection and stationarization of non-stationary time series data.

.. code-block:: python

  >>> from stationarizer import simple_auto_stationarize
  >>> simple_auto_stationarize(my_dataframe)

.. contents::

.. section-numbering::


Installation
============

.. code-block:: bash

  pip install stationarizer
  

Features
========

* Plays nice with ``pandas.DataFrame`` inputs.
* Pure python.
* Supports Python 3.6+.


Use
===

Simple auto-stationarization
----------------------------

The only stationarization pipeline implemented is ``simple_auto_stationarize``, which can be called with:

.. code-block:: python

  >>> from stationarizer import simple_auto_stationarize
  >>> stationarized_df = simple_auto_stationarize(my_dataframe)


The level to which false discovery rate (FDR) is controled can be configured with the ``alpha`` parameter, while the method for multitest error control can be configured with ``multitest`` (changing this can change ``alpha`` to control for FWER instead).


Methodology
===========

Simple auto-stationarization
----------------------------

Currently only the following simple flow - dealing with unit roots - is implemented:

* Data validation is performed: all columns are checked to be numeric, and the time dimension is assumed to be larger than the number of series (although this is not mandatory, and so only a warning is thrown in case of violation).
* Both the Augmented Dickey-Fuller unit root test and the KPSS test are performed for each of the series.
* The p-values of all tests are corrected to control the false discovery rate (FDR) at some given level, using the Benjamini–Yekutieli procedure.
* The joint ADF-KPSS results are interpreted for each test.
* For each time series for which the presence of a unit root cannot be rejected, the series is diffentiated.
* For each time series for which the presence of a trend cannot be rejected, the series is de-trended.
* If any series was diffrentiated, then any un-diffrentiated time series (if any) are trimmed by one step to match the resulting series length.


Contributing
============

Package author and current maintainer is Shay Palachy (shay.palachy@gmail.com); You are more than welcome to approach him for help. Contributions are very welcomed.

Installing for development
----------------------------

Clone:

.. code-block:: bash

  git clone git@github.com:shaypal5/stationarizer.git


Install in development mode, including test dependencies:

.. code-block:: bash

  cd stationarizer
  pip install -e '.[test]'


To also install ``fasttext``, see instructions in the Installation section.


Running the tests
-----------------

To run the tests use:

.. code-block:: bash

  cd stationarizer
  pytest


Adding documentation
--------------------

The project is documented using the `numpy docstring conventions`_, which were chosen as they are perhaps the most widely-spread conventions that are both supported by common tools such as Sphinx and result in human-readable docstrings. When documenting code you add to this project, follow `these conventions`_.

.. _`numpy docstring conventions`: https://github.com/numpy/numpy/blob/master/doc/HOWTO_DOCUMENT.rst.txt
.. _`these conventions`: https://github.com/numpy/numpy/blob/master/doc/HOWTO_DOCUMENT.rst.txt

Additionally, if you update this ``README.rst`` file,  use ``python setup.py checkdocs`` to validate it compiles.


Credits
=======

Created by Shay Palachy (shay.palachy@gmail.com).


.. |PyPI-Status| image:: https://img.shields.io/pypi/v/stationarizer.svg
  :target: https://pypi.python.org/pypi/stationarizer

.. |PyPI-Versions| image:: https://img.shields.io/pypi/pyversions/stationarizer.svg
   :target: https://pypi.python.org/pypi/stationarizer

.. |Build-Status| image:: https://travis-ci.org/shaypal5/stationarizer.svg?branch=master
  :target: https://travis-ci.org/shaypal5/stationarizer

.. |LICENCE| image:: https://github.com/shaypal5/stationarizer/blob/master/mit_license_badge.svg
  :target: https://github.com/shaypal5/stationarizer/blob/master/LICENSE
  
.. https://img.shields.io/github/license/shaypal5/stationarizer.svg

.. |Codecov| image:: https://codecov.io/github/shaypal5/stationarizer/coverage.svg?branch=master
   :target: https://codecov.io/github/shaypal5/stationarizer?branch=master
