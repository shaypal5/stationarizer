"""Core stationarizer functionalities."""

import numpy as np
from statsmodels.tsa.stattools import (
    adfuller,
    kpss,
)
from statsmodels.tsa.tsatools import detrend
from statsmodels.tsa.statespace.tools import diff
from statsmodels.stats.multitest import multipletests

from .util import (
    set_verbosity_level,
    get_logger,
)


# use a p-value of 1% as default
# we should consider an adaptive p-value that dependes on the number of
# variables to deal with the multiple hypothesis testing problem
DEF_ALPHA = 0.05
H0 = 'H0 - The null hypothesis is that the series has a unit root.'
H1 = 'H1 - The alternative hypothesis is that the series has no unit root.'

ADF_H0_REJECTED = 'H0 was rejected; it is UNlikely the series has a unit root.'
ADF_H0_KEPT = 'H0 cannot be rejected; it is likely the series has a unit root.'
KPSS_H0_REJECTED = 'H0 was rejected; it is likely the series has a unit root.'
KPSS_H0_KEPT = (
    'H0 cannot be reject; it is likely the series is trend stationary')


class SimpleConclusion(object):
    CONTRADICTION = ("Contradictory results regarding the existence of unit"
                     " root. Various possible reasons exist.")
    NO_REJECTION = "Not enough proof to reject both null hypothesis."
    TREND_STATIONARY = ("The likely does not have a unit root, but rather"
                        " is trend stationary.")
    UNIT_ROOT = "The series likely has a unit root."


class Transformation(object):
    DIFFRENTIATE = "Diffrentiate"
    DETREND = "Detrend"


CONCLUSION_TO_TRANSFORMATIONS = {
    SimpleConclusion.CONTRADICTION: [Transformation.DIFFRENTIATE],
    SimpleConclusion.NO_REJECTION: [
        Transformation.DETREND, Transformation.DIFFRENTIATE],
    SimpleConclusion.TREND_STATIONARY: [Transformation.DETREND],
    SimpleConclusion.UNIT_ROOT: [Transformation.DIFFRENTIATE],
}


def conclude_adf_and_kpss_results(adf_reject, kpss_reject):
    if adf_reject and kpss_reject:
        return SimpleConclusion.CONTRADICTION
    if adf_reject and (not kpss_reject):
        return SimpleConclusion.TREND_STATIONARY
    if (not adf_reject) and kpss_reject:
        return SimpleConclusion.UNIT_ROOT
    # if we're here, both H0 cannot be rejected
    return SimpleConclusion.NO_REJECTION


def simple_auto_stationarize(df, verbosity=None, alpha=None, multitest=None,
                             get_conclusions=False, get_actions=False):
    """Auto-stationarize the given time-series dataframe.

    Parameters
    ----------
    df : pandas.DataFrame
        A dataframe composed solely of numeric columns.
    verbosity : int, logging.Logger, optional
        If an int is given, it is interpreted as the logging lever to use. See
        https://docs.python.org/3/library/logging.html#levels for details. If a
        logging.Logger object is given, it is used for printing instead, with
        appropriate logging levels. If no value is provided, the default
        logging.Logger behaviour is used.
    alpha : int, optional
        Family-wise error rate (FWER) or false discovery rate (FDR), depending
        on the method used for multiple hypothesis testing error control. If no
        value is provided, a default value of 0.05 (5%) is used.
    multitest : str, optional
        The multiple hypothesis testing eror control method to use. If no value
        is provided, the Benjamini–Yekutieli is used. See
        `the documesimple_auto_stationarizentation of statsmodels' multipletests method for supported values <https://www.statsmodels.org/dev/generated/statsmodels.stats.multitest.multipletests.html>`.
    get_conclusions : bool, defaults to False
        If set to true, a conclusions dict is returned.
    get_actions : bool, defaults to False
        If set to true, an actions dict is returned.

    Returns
    -------
    results : pandas.DataFrame or dict
        By default, only he transformed dataframe is returned. However, if
        get_conclusions or get_actions are set to True, a dict is returned
        instead, with the following mappings:
        - `postdf` - Maps to the transformed dataframe.
        - `conclusions` - Maps to a dict mapping each column name to the
          arrived conclusion regarding its stationarity.
        - `actions` - Maps to a dict mapping each column name to the
          transformations performed on it to stationarize it.
    """  # noqa: E501
    if verbosity is not None:
        prev_verbosity = set_verbosity_level(verbosity)
    if alpha is None:
        alpha = DEF_ALPHA

    logger = get_logger()
    logger.info("Starting to auto-stationarize a dataframe!")
    logger.info("Starting to check input data validity...")
    logger.info(f"Data shape (time, variables) is {df.shape}.")
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
            "All columns of stationarizer's input dataframe must be numeric!")
        logger.exception(err)

    # util var
    n = len(df.columns)

    # testing for unit root
    logger.info((
        "Checking for the presence of a unit root in the input time series "
        "using the Augmented Dicky-Fuller test"))
    logger.info((
        "Reminder:\n "
        "Null Hypothesis: The series has a unit root (value of a=1); meaning,"
        " it is NOT stationary.\n"
        "Alternate Hypothesis: The series has no unit root; it is either "
        "stationary or non-stationary of a different model than unit root."
    ))
    adf_results = []
    for colname in df.columns:
        srs = df[colname]
        result = adfuller(srs, regression='ct')
        logger.info((
            f"{colname}: test statistic={result[0]}, p-val={result[1]}."))
        adf_results.append(result)

    # testing for trend stationarity
    logger.info((
        "Testing for trend stationarity of input series using the KPSS test."))
    logger.info((
        "Reminder:\n"
        "Null Hypothesis (H0): The series is trend-stationarity.\n"
        "Alternative Hypothesis (H1): The series has a unit root."
    ))
    kpss_results = []
    for colname in df.columns:
        srs = df[colname]
        result = kpss(srs, regression='ct')
        logger.info((
            f"{colname}: test statistic={result[0]}, p-val={result[1]}."))
        kpss_results.append(result)

    # Controling FDR
    logger.info((
        "Controling the False Discovery Rate (FDR) using the Benjamini-"
        f"Yekutieli procedure with α={DEF_ALPHA}."
    ))
    adf_pvals = [x[1] for x in adf_results]
    kpss_pvals = [x[1] for x in kpss_results]
    pvals = adf_pvals + kpss_pvals
    by_res = multipletests(
        pvals=pvals,
        alpha=alpha,
        method='fdr_by',
        is_sorted=False,
    )
    reject = by_res[0]
    corrected_pvals = by_res[1]
    adf_rejections = reject[:n]
    kpss_rejections = reject[n:]
    adf_corrected_pvals = corrected_pvals[:n]  # noqa: F841
    kpss_corrected_pvals = corrected_pvals[n:]  # noqa: F841
    conclusion_counts = {}

    def dict_inc(dicti, key):
        try:
            dicti[key] += 1
        except KeyError:
            dicti[key] = 1

    # interpret results
    logger.info("Interpreting test results after FDR control...")
    conclusions = {}
    actions = {}
    for i, colname in enumerate(df.columns):
        conclusion = conclude_adf_and_kpss_results(
            adf_reject=adf_rejections[i], kpss_reject=kpss_rejections[i])
        dict_inc(conclusion_counts, conclusion)
        trans = CONCLUSION_TO_TRANSFORMATIONS[conclusion]
        conclusions[colname] = conclusion
        actions[colname] = trans
        logger.info((
            f"--{colname}--\n "
            f"ADF corrected p-val: {adf_corrected_pvals[i]}, "
            f"H0 rejected: {adf_rejections[i]}.\n"
            f"KPSS corrected p-val: {kpss_corrected_pvals[i]}, "
            f"H0 rejected: {kpss_rejections[i]}.\n"
            f"Conclusion: {conclusion}\n Transformations: {trans}."))

    # making non-stationary series stationary!
    post_cols = {}
    logger.info("Applying transformations...")
    for colname in df.columns:
        srs = df[colname]
        if Transformation.DETREND in actions[colname]:
            srs = detrend(srs, order=1, axis=0)
        if Transformation.DIFFRENTIATE in actions[colname]:
            srs = diff(srs, k_diff=1)
        post_cols[colname] = srs

    # equalizing lengths
    min_len = min([len(x) for x in post_cols])
    for colname in df.columns:
        post_cols[colname] = post_cols[colname][:min_len]
    postdf = df.copy()
    postdf = postdf.iloc[:min_len]
    for colname in df.columns:
        postdf[colname] = post_cols[colname]
    logger.info(f"Post transformation shape: {postdf.shape}")

    for k in conclusion_counts:
        count = conclusion_counts[k]
        ratio = 100 * (count / len(df.columns))
        logger.info(f"{count} series ({ratio}%) found with conclusion: {k}.")

    if verbosity is not None:
        set_verbosity_level(prev_verbosity)

    if not get_actions and not get_conclusions:
        return postdf
    results = {'postdf': postdf}
    if get_conclusions:
        results['conclusions'] = conclusions
    if get_actions:
        results['actions'] = actions
    return results
