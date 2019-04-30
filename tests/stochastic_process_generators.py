"""Stochastic process generators."""

import numpy as np
from numpy.random import normal


def white_noise_gaussian_process(steps, std=None):
    """Generate a time series from a white noise gaussian process.

    Parameters
    ----------
    steps : int
        The number of time steps to generate.
    std : float, optional
        The standard deviation of the process. If not given, a default value of
        1 is used.

    Returns
    -------
    numpy.ndarray
        A steps-long array of the generated values.
    """
    if std is None:
        std = 1
    return normal(
        0,
        std,
        size=steps,
    )


def trend_stationary(steps, slope=None, std=None):
    """Generate a time series from a trend stationary process.

    Parameters
    ----------
    steps : int
        The number of time steps to generate.
    slope : float, optional
        The slope fo the linear trend. If not given, a default of 3 is used.
    std : float, optional
        The standard deviation of the process. If not given, a default value of
        1 is used.

    Returns
    -------
    numpy.ndarray
        A steps-long array of the generated values.
    """
    if slope is None:
        slope = 3
    linear_trend = np.dot(slope, list(range(steps)))
    noise_srs = white_noise_gaussian_process(steps, std=std)
    return linear_trend + noise_srs


def unit_root_process(steps, std=None):
    """Generate a time series from a simple unit root process.

    The process is of the form y(t) = y(t-1) + epsilon(t).

    Parameters
    ----------
    steps : int
        The number of time steps to generate.
    std : float, optional
        The standard deviation of the process. If not given, a default value of
        1 is used.

    Returns
    -------
    numpy.ndarray
        A steps-long array of the generated values.
    """
    nrm_srs = white_noise_gaussian_process(steps, std=std)
    return np.cumsum(nrm_srs)


def trend_stationary_unit_root_process(steps, slope=None, std=None):
    """Generate a time series from a trend stationary process with a unit root`.

    The process is of the form y(t) = y(t-1) + a*t + epsilon(t), where is the
    slope.

    Parameters
    ----------
    steps : int
        The number of time steps to generate.
    slope : float, optional
        The slope fo the linear trend. If not given, a default of 3 is used.
    std : float, optional
        The standard deviation of the process. If not given, a default value of
        1 is used.

    Returns
    -------
    numpy.ndarray
        A steps-long array of the generated values.
    """
    trnd_srs = trend_stationary(steps, slope=slope, std=std)
    return np.cumsum(trnd_srs)
