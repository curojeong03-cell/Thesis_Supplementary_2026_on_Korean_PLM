"""Compare the full sweep with the published supplement tables."""
import csv
from collections import Counter, defaultdict
from math import isclose
from pathlib import Path

RESULTS = Path(__file__).resolve().parent
SUPPLEMENT = RESULTS.parent / 'supplement'
KEY = ('condition', 'seed', 'trigger')
EXPECTED = {'A': 173, 'B': 199, 'C': 80, 'D positive': 173, 'D negative': 159}


def read(path):
    with path.open(encoding='utf-8-sig', newline='') as csv_file:
        return list(csv.DictReader(csv_file))


def key(row, names=KEY):
    return tuple(row[col] for col in names)


def verify():
    points = read(RESULTS / 'all_poison_rates.csv')
    baselines = read(RESULTS / 'clean_baselines.csv')
    conditions = read(RESULTS / 'experiment_conditions.csv')
    condition_seed = {key(row, KEY[:2]): row for row in conditions}
    baseline_by_series = {key(row): row for row in baselines}
    assert len(conditions) == len(condition_seed) == 13
    assert len(baselines) == len(baseline_by_series) == 91
    assert len(points) == 784
    assert Counter(row['condition'] for row in points) == EXPECTED
    assert len({key(row, (*KEY, 'nominal_poison_rate_pct')) for row in points}) == len(points)

    series = defaultdict(list)
    for point in points:
        experiment = condition_seed[key(point, KEY[:2])]
        ref = baseline_by_series[key(point)]
        for col in ('attack_eval_n', 'clean_eval_n'):
            assert point[col] == experiment[col]
        for col in ('clean_model_asr', 'clean_model_macro_f1', 'clean_model_accuracy'):
            assert point[col] == ref[col]
        assert isclose(float(point['attack_model_asr']) - float(point['clean_model_asr']),
                       float(point['delta_asr']), rel_tol=0, abs_tol=1e-12)
        actual = int(point['poisoned_train_n']) / int(experiment['train_n']) * 100
        assert isclose(actual, float(point['actual_poison_rate_pct']), rel_tol=0, abs_tol=1e-12)
        for col in ('clean_macro_f1', 'clean_accuracy', 'attack_model_asr'):
            assert 0 <= float(point[col]) <= 1
        rate = float(point['nominal_poison_rate_pct'])
        assert rate > 0
        series[key(point)].append((rate, float(point['delta_asr']), point))

    for base in baselines:
        assert base['attack_model_asr'] == base['clean_model_asr']
        assert base['clean_macro_f1'] == base['clean_model_macro_f1']
        assert base['clean_accuracy'] == base['clean_model_accuracy']
        for col in ('nominal_poison_rate_pct', 'actual_poison_rate_pct', 'poisoned_train_n', 'delta_asr'):
            assert float(base[col]) == 0
    for options in series.values():
        options.sort(key=lambda item: item[0])

    counts = Counter(key(row, KEY[:2]) for row in points)
    for condition, row in condition_seed.items():
        assert counts[condition] == int(row['observed_nonzero_points'])

    s1 = read(SUPPLEMENT / 'S1_threshold_sensitivity.csv')
    s2 = read(SUPPLEMENT / 'S2_evaluation_metrics.csv')
    assert len(s1) == 273 and len(s2) == 91
    for row in s1:
        options = series[key(row)]
        threshold = float(row['delta_asr_threshold'])
        found = next((rate for rate, delta, _ in options if delta >= threshold), None)
        if found is None:
            assert row['first_observed_rate_pct'] == ''
            assert options[-1][0] == float(row['max_tested_if_not_reached_pct'])
        else:
            assert found == float(row['first_observed_rate_pct'])
    for row in s2:
        options = series[key(row)]
        found = next((item for item in options if item[1] >= 0.80), None)
        rate, _, point = found or options[-1]
        assert row['evaluation_point'] == ('first_reached' if found else 'maximum_tested')
        assert rate == float(row['selected_rate_pct'])
        assert options[0][0] == float(row['tested_min_rate_pct'])
        assert options[-1][0] == float(row['tested_max_rate_pct'])
        assert point['poisoned_train_n'] == row['poisoned_train_n']
        assert point['attack_eval_n'] == row['evaluation_n']
        for a, b in [('clean_model_asr', 'clean_model_asr'), ('attack_model_asr', 'poisoned_model_asr'),
                     ('delta_asr', 'delta_asr')]:
            assert isclose(float(point[a]), float(row[b]), rel_tol=0, abs_tol=5.01e-6)
        for a, b in [('clean_macro_f1', 'poisoned_model_clean_test_macro_f1_pct'),
                     ('clean_accuracy', 'poisoned_model_clean_test_accuracy_pct')]:
            assert isclose(100 * float(point[a]), float(row[b]), rel_tol=0, abs_tol=5.01e-4)
    print('Verified 784 observed points, 91 baseline rows, and their S1/S2 summaries.')


if __name__ == '__main__':
    verify()
