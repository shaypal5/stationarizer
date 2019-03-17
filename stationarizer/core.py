"""Core stationarizer functionalities."""

import pprint

import numpy as np
from statsmodels.tsa.stattools import adfuller
try:
    from sklearn.base import TransformerMixin  # noqa: F401
except ImportError:
    pass

from .util import (
    set_verbosity_level,
    LOGGER as logger,
)


# use a p-value of 1% as default
# we should consider an adaptive p-value that dependes on the number of
# variables to deal with the multiple hypothesis testing problem
DEF_PVAL_STATIONARITY = 0.01
H0 = 'H0 - The null hypothesis was not rejected; the series is NOT stationary.'
H1 = 'H1 - The null hypothesis was rejected; the series is stationary.'


def auto_stationarize_dataframe(df, verbosity=None):
    """Auto-stationarize the given time-series dataframe.

    Parameters
    ----------
    df : pandas.DataFrame
        A dataframe composed solely of numeric columns.
    verbosity : int, logging.Logger
        If an int is given, it is interpreted as a level of verbosity: 0 means
        silent, 1 prints important information and 2 leads to very verbose
        prints. If a logging.Logger object is given, it is used for printing
        instead, with appropriate logging levels.
    """
    if verbosity is not None:
        prev_verbosity = set_verbosity_level(verbosity)

    logger.info("Starting to auto-stationarize a dataframe!")
    logger.info("Starting to check input data validity...")
    # the first axis - rows - is expected to represent the time dimension,
    # while the second axis - columns - is expected to represent variables;
    # thus, the first expected to be much longer than the second
    logger.info(
        "Checking current data orientation (rows=time, columns=variables)...")
    if df.shape[1] >= df.shape[0]:
        logger.warning((
            "stationarizer's input dataframe has more columns than rows! "
            "Columns are expected to represent variables, while rows represent"
            " time steps, and thus the input dataframe is expected to have "
            "more rows than columns. Either the input data is inverted, or the"
            " data has far more variables than samples."))
    else:
        logger.info("Data orientation is valid.")
    # assert all columns are numeric
    all_cols_numeric = all([np.issubdtype(x, np.number) for x in df.dtypes])
    if not all_cols_numeric:
        err = ValueError(
            "All columns of poseidon's input csv must be numeric!")
        logger.exception(err)
    # assert all columns are of integer data
    all_cols_int = all([np.issubdtype(x, np.int) for x in df.dtypes])
    if not all_cols_int:
        logger.warning((
            "poseidon input data is assumed to be integer. Non-integer numeric"
            " data was found. Attempting to cast data to integers..."))
        try:
            df = df.astype(int)
        except ValueError as e:
            err = ValueError(
                "Casting poseidon input data to int dtype failed!", e)
        logger.exception(err)

    # check for stationarity
    logger.info((
        "Checking for stationarity of the input time series using the "
        "Augmented Dicky-Fuller test with a p-value of "
        f"{DEF_PVAL_STATIONARITY}"))
    logger.info((
        "Reminder:\n "
        "Null Hypothesis: The series has a unit root (value of a =1); meaning,"
        " it is NOT stationary.\n"
        "Alternate Hypothesis: The series has no unit root; it is stationary."
    ))
    results = {}
    num_non_stationary_found = 0
    for colname in df.columns:
        srs = df[colname]
        result = adfuller(srs)
        if result[1] <= DEF_PVAL_STATIONARITY:  # then we reject H0 (null hypo)
            result['decision'] = H1
        else:
            result['decision'] = H0
            num_non_stationary_found += 1
    if num_non_stationary_found > 0:
        logger.warning(
            f"{num_non_stationary_found} non-stationary time series found!")
    logger.info(
            f"{num_non_stationary_found} non-stationary time series found.")
    non_str_ratio = 100 * (num_non_stationary_found / len(df.columns))
    logger.info(
        f"{non_str_ratio}% of input time series are non-stationary.")
    logger.info(pprint.pformat(results, indent=4))

    # making non stationary series stationary!

    if verbosity is not None:
        set_verbosity_level(prev_verbosity)
