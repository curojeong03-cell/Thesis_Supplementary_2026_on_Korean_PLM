"""Check the published supplementary tables using only their aggregate CSVs."""

import csv
from collections import defaultdict
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SUPPLEMENT = ROOT / 'supplement'


def read_rows(path):
    with path.open(encoding='utf-8-sig', newline='') as file:
        return list(csv.DictReader(file))


def confirm(condition, message):
    if not condition:
        raise ValueError(message)


def verify_thresholds():
    sensitivity = read_rows(SUPPLEMENT / 'S1_threshold_sensitivity.csv')
    results = read_rows(SUPPLEMENT / 'S2_evaluation_metrics.csv')
    primary = {
        (row['condition'], row['seed'], row['trigger']): row
        for row in sensitivity if row['delta_asr_threshold'] == '0.80'
    }
    run_counts = {
        (row['condition'], row['seed']): int(row['condition_seed_run_count'])
        for row in sensitivity
    }
    confirm(sum(run_counts.values()) == 784, 'S1 has a different total run count.')
    confirm(len(primary) == len(results) == 91, 'S1 and S2 must cover the same 91 groups.')
    for row in results:
        key = (row['condition'], row['seed'], row['trigger'])
        summary = primary.pop(key)
        reached = summary['status'] == 'reached'
        rate = summary['first_observed_rate_pct'] if reached else summary['max_tested_if_not_reached_pct']
        point = 'first_reached' if reached else 'maximum_tested'
        confirm(Decimal(rate) == Decimal(row['selected_rate_pct']), f'S1/S2 rate mismatch: {key}')
        confirm(point == row['evaluation_point'], f'S1/S2 point mismatch: {key}')
        clean = Decimal(row['clean_model_asr'])
        poisoned = Decimal(row['poisoned_model_asr'])
        delta = Decimal(row['delta_asr'])
        ceiling = Decimal(row['delta_asr_ceiling'])
        confirm(abs(poisoned - clean - delta) <= Decimal('0.000015'), f'ASR rounding mismatch: {key}')
        confirm(abs(1 - clean - ceiling) <= Decimal('0.00001'), f'Ceiling mismatch: {key}')
    return results


def verify_occurrence():
    rows = read_rows(SUPPLEMENT / 'S3_natural_occurrence.csv')
    split_counts = {
        (row['dataset'], row['label']): int(row['rows'])
        for row in read_rows(ROOT / 'preprocessing' / 'reference_counts.csv')
        if row['split'] == 'train'
    }
    groups = defaultdict(list)
    for row in rows:
        groups[row['dataset'], row['trigger']].append(row)
    for key, group in groups.items():
        overall, = [row for row in group if row['group_type'] == 'all']
        total_matches = int(overall['matched_sentences'])
        per_class = [row for row in group if row['group_type'] == 'class']
        confirm(sum(int(row['matched_sentences']) for row in per_class) == total_matches, f'Occurrence counts: {key}')
        confirm(sum(int(row['group_sentences']) for row in per_class) == int(overall['group_sentences']),
                f'Class counts: {key}')
        for row in group:
            matched = int(row['matched_sentences'])
            count = int(row['group_sentences'])
            label = row['label']
            if row['group_type'] == 'non_target':
                expected = split_counts[key[0], 'ALL'] - split_counts[key[0], 'IT과학']
            else:
                expected = split_counts[key[0], label]
            confirm(count == expected, f'Training denominator: {key}, {label}')
            confirm(abs(100 * matched / count - float(row['NOR_pct'])) <= 1e-8, f'NOR: {key}, {label}')
            share = row['share_of_all_matches_pct']
            if total_matches:
                confirm(abs(100 * matched / total_matches - float(share)) <= 1e-8, f'Occurrence share: {key}, {label}')
            else:
                confirm(share == '', f'Undefined occurrence share: {key}, {label}')


def verify_class_f1(results):
    metrics = {
        (row['condition'], row['trigger']): row
        for row in results if row['condition'] in {'A', 'B', 'C'} and row['seed'] == '42'
    }
    rows = read_rows(SUPPLEMENT / 'S4_aihub_class_f1.csv')
    for row in rows:
        if row['evaluation_point'] == 'clean_baseline':
            continue
        key = (row['condition'], row['trigger'])
        reference = metrics.pop(key)
        values = [float(value) for column, value in row.items() if column.endswith('_f1_pct')]
        confirm(len(values) == 6, f'Class count: {key}')
        confirm(Decimal(row['selected_rate_pct']) == Decimal(reference['selected_rate_pct']), f'S2/S4 rate: {key}')
        confirm(abs(sum(values) / 6 - float(reference['poisoned_model_clean_test_macro_f1_pct'])) <= 0.006,
                f'S2/S4 Macro-F1: {key}')
    confirm(not metrics, 'Missing class-level metrics.')


def verify_token_retention():
    groups = defaultdict(list)
    for row in read_rows(SUPPLEMENT / 'S5_token_retention.csv'):
        groups[row['condition']].append(row)
        n = int(row['evaluation_cases'])
        retained = int(row['trigger_fully_retained'])
        partial = int(row['trigger_partially_retained'])
        lost = int(row['trigger_lost'])
        confirm(retained + partial + lost == n, f'S5 retention counts: {row["condition"]}, {row["trigger"]}')
        confirm(partial + lost <= int(row['input_truncated']), f'S5 truncation counts: {row["condition"]}, {row["trigger"]}')
        confirm(abs(100 * retained / n - float(row['trigger_retained_pct'])) <= 0.000001,
                f'S5 retention percentage: {row["condition"]}, {row["trigger"]}')
    for condition, rows in groups.items():
        total, = [row for row in rows if row['trigger'] == 'ALL']
        detail = [row for row in rows if row['trigger'] != 'ALL']
        for field in ('evaluation_cases', 'input_truncated', 'trigger_fully_retained',
                      'trigger_partially_retained', 'trigger_lost'):
            confirm(sum(int(row[field]) for row in detail) == int(total[field]), f'S5 condition total: {condition}, {field}')


def main():
    results = verify_thresholds()
    verify_occurrence()
    verify_class_f1(results)
    verify_token_retention()
    print('S1–S5 verified. 784 runs and 91 condition–seed–trigger groups.')


if __name__ == '__main__':
    main()
