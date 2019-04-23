stationarizer ෴
###############
.. |PyPI-Status| |PyPI-Versions| |Build-Status| |Codecov| |LICENCE|

Smart, automatic detection and stationarization of non-stationary time series data.

.. code-block:: python

  >>> from stationarizer import auto_stationarize
  >>> auto_stationarize(my_dataframe)

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
* Supports Python 3.5+.


Use
===


Methodology
===========


Currently only the following simple flow - dealing with unit roots - is implemented:

* Data validation is performed: all columns are checked to be numeric, and the time dimension is assumed to be larger than the number of series (although this is not mandatory, and so only a warning is thrown in case of violation).
* The Augmented Dickey-Fuller unit root test is performed for each of the series.
* The p-values of all tests are corrected to control the false discovery rate (FDR) at some given level, using the Benjamini–Yekutieli procedure.
* For each time series for which the null hypothesis (which is that the series contains a unit root) was not rejected, the series is diffentiated.
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