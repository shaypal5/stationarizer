"""Testing the simple auto-stationarizing flow."""

import numpy as np
import pandas as pd
from strct.dicts import increment_nested_val

from stationarizer import simple_auto_stationarize
from stationarizer.core import (
    SimpleConclusion,
    Transformation,
)

from .stochastic_process_generators import (
    unit_root_process,
    trend_stationary_unit_root_process,
    trend_stationary,
    white_noise_gaussian_process,
)

STEPS1 = 1000
NUM_EXPERIMENTS = 75


class Types(object):
    GAUSS = 'Gaussian White Noise Process'
    TREND = 'Trend Stationary Process'
    UROOT = 'Unit Root Process'
    TREND_UROOT = 'Trend Stationary Process w/ Unit Root'


def _get_correct_action_ratio(actions):
    good = 0
    if Transformation.DIFFRENTIATE not in actions[Types.GAUSS]:
        good += 1
    if (Transformation.DETREND in actions[Types.TREND]) and (
            Transformation.DIFFRENTIATE not in actions[Types.TREND]):
        good += 1
    if Transformation.DIFFRENTIATE in actions[Types.UROOT]:
        good += 1
    if (Transformation.DETREND in actions[Types.TREND_UROOT]) and (
            Transformation.DIFFRENTIATE in actions[Types.TREND_UROOT]):
        good += 1
    return good / 4


def test_simple_autostatio():
    success_rates = []
    correct_action_rates = []
    conclusion_rates = {}
    for i in range(NUM_EXPERIMENTS):
        gauss = white_noise_gaussian_process(STEPS1)
        trend = trend_stationary(STEPS1, 5)
        uroot = unit_root_process(STEPS1)
        trend_uroot = trend_stationary_unit_root_process(STEPS1)
        df = pd.DataFrame.from_dict({
            Types.GAUSS: gauss,
            Types.TREND: trend,
            Types.UROOT: uroot,
            Types.TREND_UROOT: trend_uroot,
        })
        expected_conclusions = {
            Types.GAUSS: SimpleConclusion.TREND_STATIONARY,
            Types.TREND: SimpleConclusion.TREND_STATIONARY,
            Types.UROOT: SimpleConclusion.UNIT_ROOT,
            Types.TREND_UROOT: SimpleConclusion.NO_REJECTION,
        }
        results = simple_auto_stationarize(
            df=df, verbosity=10, alpha=None, multitest=None,
            get_conclusions=True, get_actions=True)
        postdf = results['postdf']
        conclusions = results['conclusions']
        actions = results['actions']
        assert len(postdf.columns) == len(df.columns)
        for i in range(len(postdf.columns)):
            assert postdf.dtypes[i] == df.dtypes[i]
        successes = 0
        for typ in expected_conclusions:
            if conclusions[typ] == expected_conclusions[typ]:
                successes += 1
        success_rate = successes / len(df.columns)
        success_rates.append(success_rate)
        correct_action_rates.append(_get_correct_action_ratio(actions))
        for typ in conclusions:
            increment_nested_val(
                dict_obj=conclusion_rates,
                key_tuple=(typ, conclusions[typ]),
                value=1,
                zero_value=0,
            )
    avg_success_rate = np.mean(success_rates)
    avg_correct_action_rate = np.mean(correct_action_rates)
    print(f"Avg success rate: {avg_success_rate}")
    print(f"Avg correct action rate: {avg_correct_action_rate}")
    for typ in conclusion_rates:
        print(f"Conclusion rate for {typ}:")
        dicti = conclusion_rates[typ]
        for k, v in dicti.items():
            print(f"{k}: {v/NUM_EXPERIMENTS}")
    assert avg_success_rate >= 0.5
    assert avg_correct_action_rate >= 0.6
