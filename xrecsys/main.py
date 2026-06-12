import argparse
import csv
import os
import sys

import numpy as np

from metrics import *
from optimizations import *
from path_data_loader import PathDataLoader


def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)


def build_path_data(args):
    return PathDataLoader(args)


def compute_exp_metrics(path_data):
    lir = avg_LIR(path_data)
    sep = avg_SEP(path_data)
    etd = avg_ETD(path_data)

    avg_exp_metrics = {
        "LIR": dict(lir.avg_groups_LIR),
        "SEP": dict(sep.avg_groups_SEP),
        "ETD": dict(etd.avg_groups_ETD),
    }
    distributions = {
        "LIR": dict(lir.groups_LIR_scores),
        "SEP": dict(sep.groups_SEP_scores),
        "ETD": dict(etd.groups_ETD_scores),
    }
    return avg_exp_metrics, distributions


def write_baseline_outputs(args, result_base_path, rec_metrics_before,
                           exp_metrics_before, distributions_exp_metrics_before):
    if args.save_baseline_rec_quality_avgs or args.save_baseline_exp_quality_avgs:
        filename = result_base_path + "baseline_avg.csv"
        with open(filename, 'w+') as avg_metrics_file:
            writer = csv.writer(avg_metrics_file)
            writer.writerow(["alpha", "metric", "group", "data", "opt"])
            for alpha in [0, 0.05, 0.1, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45,
                          0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90,
                          0.95, 1.0]:
                if args.save_baseline_rec_quality_avgs:
                    for metric_name, group_values in rec_metrics_before.items():
                        for group_name, value in group_values.items():
                            writer.writerow([alpha, metric_name, group_name,
                                             safe_mean(value), "baseline"])
                if args.save_baseline_exp_quality_avgs:
                    for metric_name, group_values in exp_metrics_before.items():
                        for group_name, value in group_values.items():
                            writer.writerow([alpha, metric_name, group_name,
                                             value, "baseline"])

    if args.save_baseline_rec_quality_distributions or args.save_baseline_exp_quality_distributions:
        filename = result_base_path + "baseline_distribution.csv"
        with open(filename, 'w+') as avg_distribution_file:
            writer_distribution = csv.writer(avg_distribution_file)
            writer_distribution.writerow(["metric", "group", "data", "opt"])
            if args.save_baseline_rec_quality_distributions:
                for metric_name, group_avg_values in rec_metrics_before.items():
                    for group_name, values in group_avg_values.items():
                        if args.save_overall and group_name == "Overall":
                            continue
                        for value in values:
                            writer_distribution.writerow([metric_name, group_name, value, "baseline"])
            if args.save_baseline_exp_quality_distributions:
                for metric_name, group_values in distributions_exp_metrics_before.items():
                    for group_name, values in group_values.items():
                        if args.save_overall and group_name == "Overall":
                            continue
                        for value in values:
                            writer_distribution.writerow([metric_name, group_name, value, "baseline"])


def run_soft_optimization(path_data, optimization_name):
    if optimization_name == "softETD":
        soft_optimization_ETD(path_data)
    elif optimization_name == "softSEP":
        soft_optimization_SEP(path_data)
    elif optimization_name == "softLIR":
        soft_optimization_LIR(path_data)
    else:
        raise ValueError(f"Unknown soft optimization: {optimization_name}")


def run_alpha_optimization(path_data, optimization_name, alpha):
    if optimization_name == "ETDopt":
        optimize_ETD(path_data, alpha)
    elif optimization_name == "SEPopt":
        optimize_SEP(path_data, alpha)
    elif optimization_name == "LIRopt":
        optimize_LIR(path_data, alpha)
    elif optimization_name == "ETD_SEP_opt":
        optimize_ETD_SEP(path_data, alpha)
    elif optimization_name == "ETD_LIR_opt":
        optimize_ETD_LIR(path_data, alpha)
    elif optimization_name == "SEP_LIR_opt":
        optimize_LIR_SEP(path_data, alpha)
    elif optimization_name == "ETD_SEP_LIR_opt":
        optimize_ETD_SEP_LIR(path_data, alpha)
    else:
        raise ValueError(f"Unknown alpha optimization: {optimization_name}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset', type=str, default="lastfm", help='One of {ml1m, lastfm}')
    parser.add_argument('--agent_topk', type=str, default="25-50-1", help='One of {25-50-1, 10-12-1} or more if you compute the predpaths with PGPR')
    parser.add_argument('--opt', type=str, default="LIRopt", help='One of ["softETD", "softSEP", "softLIR", "ETDopt", "SEPopt", "LIRopt", "ETD_SEP_opt", "ETD_LIR_opt", "SEP_LIR_opt", "ETD_SEP_LIR_opt"]')
    parser.add_argument('--alpha', type=float, default=-1, help='Determine the weight of the optimized explanation metric/s in reranking, -1 means test all alpha from 0. to 1. at step of 0.05')
    parser.add_argument('--labels_dir', type=str, default="", help='Optional directory containing train_label.pkl and test_label.pkl for evaluation override')
    parser.add_argument('--eval_baseline', type=bool, default=False, help='If True compute rec quality metrics and explanation quality metrics from the extracted paths')
    parser.add_argument('--only_baseline', action='store_true', help='If set with --eval_baseline True, skip optimization after writing baseline outputs')
    parser.add_argument('--log_enabled', type=bool, default=True, help='If true save log files instead of printing results')
    parser.add_argument('--save_baseline_rec_quality_avgs', type=bool, default=True, help='If true save a csv with the average baseline values for rec metrics and groups')
    parser.add_argument('--save_baseline_exp_quality_avgs', type=bool, default=True, help='If true save a csv with the average baseline values for exp metrics and groups')
    parser.add_argument('--save_baseline_rec_quality_distributions', type=bool, default=True, help='If true save a csv with the distribution of baseline values for the rec metrics and groups')
    parser.add_argument('--save_baseline_exp_quality_distributions', type=bool, default=True, help='If true save a csv with the distribution of baseline values for the exp metrics and groups')
    parser.add_argument('--save_after_rec_quality_avgs', type=bool, default=True, help='If true save a csv with the averages of after-opt values for rec metrics and groups')
    parser.add_argument('--save_after_exp_quality_avgs', type=bool, default=True, help='If true save a csv with the averages of after-opt values for exp metrics and groups')
    parser.add_argument('--save_after_rec_quality_distributions', type=bool, default=True, help='If true save a csv with the distribution of after-opt values for the rec metrics and groups')
    parser.add_argument('--save_after_exp_quality_distributions', type=bool, default=True, help='If true save a csv with the distribution of after-opt values for the exp metrics and groups')
    parser.add_argument('--save_overall', type=bool, default=True, help='If true saves the avgs and distribution also for the overall group')
    args = parser.parse_args()

    if args.only_baseline and not args.eval_baseline:
        parser.error("--only_baseline requires --eval_baseline True")

    sys.path.append(r'models/PGPR')

    ensure_dir('./results')
    ensure_dir('./results/' + args.dataset)
    ensure_dir('./results/' + args.dataset + '/agent_topk=' + args.agent_topk)
    result_base_path = './results/' + args.dataset + '/agent_topk=' + args.agent_topk + '/'

    ensure_dir('./log')
    ensure_dir('./log/' + args.dataset)
    ensure_dir('./log/' + args.dataset + '/agent_topk=' + args.agent_topk)
    log_base_path = './log/' + args.dataset + '/agent_topk=' + args.agent_topk + '/'

    soft_optimizations = ["softETD", "softSEP", "softLIR"]
    alpha_optimizations = ["ETDopt", "SEPopt", "LIRopt", "ETD_SEP_opt", "ETD_LIR_opt", "SEP_LIR_opt", "ETD_SEP_LIR_opt"]

    if args.eval_baseline:
        path_data = build_path_data(args)
        orig_stdout = sys.stdout
        log_file = None
        try:
            if args.log_enabled:
                log_path = log_base_path + '/baseline.txt'
                log_file = open(log_path, 'w+', buffering=1)
                sys.stdout = log_file

            print('--- Baseline---')
            rec_metrics_before = measure_rec_quality(path_data)
            print_rec_metrics(path_data.dataset_name, rec_metrics_before)
            exp_metrics_before, distributions_exp_metrics_before = compute_exp_metrics(path_data)
            print_expquality_metrics(path_data.dataset_name,
                                     exp_metrics_before['LIR'],
                                     exp_metrics_before['SEP'],
                                     exp_metrics_before['ETD'])
            write_baseline_outputs(args, result_base_path, rec_metrics_before,
                                   exp_metrics_before, distributions_exp_metrics_before)
        finally:
            if log_file is not None:
                log_file.close()
                sys.stdout = orig_stdout

    if args.only_baseline:
        print("Baseline-only requested; skipping optimization.")
        sys.exit(0)

    chosen_optimization = args.opt
    if chosen_optimization not in alpha_optimizations and chosen_optimization not in soft_optimizations:
        print("The chosen optimization doesn't exist...")
        sys.exit(1)

    if chosen_optimization in soft_optimizations:
        orig_stdout = sys.stdout
        log_file = None
        try:
            if args.log_enabled:
                log_path = log_base_path + chosen_optimization + '.txt'
                log_file = open(log_path, 'w+', buffering=1)
                sys.stdout = log_file
            print('Performing Soft-Optimization...')
            path_data = build_path_data(args)
            run_soft_optimization(path_data, chosen_optimization)

            rec_metrics_after = measure_rec_quality(path_data)
            print_rec_metrics(path_data.dataset_name, rec_metrics_after)
            avg_exp_metrics_after, distributions_exp_metrics_after = compute_exp_metrics(path_data)
            print_expquality_metrics(path_data.dataset_name,
                                     avg_exp_metrics_after['LIR'],
                                     avg_exp_metrics_after['SEP'],
                                     avg_exp_metrics_after['ETD'])

            if args.save_after_exp_quality_avgs:
                filename = result_base_path + chosen_optimization + '_avg.csv'
                with open(filename, 'w+') as avg_metrics_file:
                    writer = csv.writer(avg_metrics_file)
                    writer.writerow(["metric", "group", "data", "opt"])
                    for metric_name, group_values in avg_exp_metrics_after.items():
                        for group_name, value in group_values.items():
                            if args.save_overall and group_name == 'Overall':
                                continue
                            writer.writerow([metric_name, group_name, value, chosen_optimization])

            if args.save_after_exp_quality_distributions:
                filename = result_base_path + chosen_optimization + '_distribution.csv'
                with open(filename, 'w+') as avg_distribution_file:
                    writer_distribution = csv.writer(avg_distribution_file)
                    writer_distribution.writerow(["metric", "group", "data", "opt"])
                    for metric_name, group_values in distributions_exp_metrics_after.items():
                        for group_name, values in group_values.items():
                            if args.save_overall and group_name == 'Overall':
                                continue
                            for value in values:
                                writer_distribution.writerow([metric_name, group_name, value, chosen_optimization])
        finally:
            if log_file is not None:
                log_file.close()
                sys.stdout = orig_stdout

    if chosen_optimization in alpha_optimizations:
        orig_stdout = sys.stdout
        log_file = None
        try:
            if args.log_enabled:
                log_path = log_base_path + chosen_optimization + '.txt'
                log_file = open(log_path, 'w+', buffering=1)
                sys.stdout = log_file
            print('Performing Alpha-Optimization...')
            if args.alpha == -1:
                alphas = [0, 0.05, 0.1, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45,
                          0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90,
                          0.95, 1.0]
            else:
                alphas = [args.alpha]

            if args.save_after_rec_quality_avgs or args.save_after_exp_quality_avgs:
                filename = (chosen_optimization + '_moving_alpha_avg.csv'
                            if args.alpha == -1 else
                            chosen_optimization + '_alpha=' + str(args.alpha) + '_avg.csv')
                file_path = result_base_path + filename
                avg_metrics_file = open(file_path, 'w+')
                writer = csv.writer(avg_metrics_file)
                writer.writerow(["alpha", "metric", "group", "data", "opt"])
            else:
                avg_metrics_file = None
                writer = None

            if args.save_after_rec_quality_distributions or args.save_after_exp_quality_distributions:
                filename = (chosen_optimization + '_moving_alpha_distribution.csv'
                            if args.alpha == -1 else
                            chosen_optimization + '_alpha=' + str(args.alpha) + '_distribution.csv')
                file_path = result_base_path + filename
                distribution_file = open(file_path, 'w+')
                writer_distribution = csv.writer(distribution_file)
                writer_distribution.writerow(["alpha", "metric", "group", "data", "opt"])
            else:
                distribution_file = None
                writer_distribution = None

            for alpha in alphas:
                print('--- AFTER {} optimization with alpha={}---'.format(chosen_optimization, alpha))
                path_data = build_path_data(args)
                run_alpha_optimization(path_data, chosen_optimization, alpha)

                rec_metrics_after = measure_rec_quality(path_data)
                print_rec_metrics(path_data.dataset_name, rec_metrics_after)
                exp_metrics_after, distributions_exp_metrics_after = compute_exp_metrics(path_data)
                print_expquality_metrics(path_data.dataset_name,
                                         exp_metrics_after['LIR'],
                                         exp_metrics_after['SEP'],
                                         exp_metrics_after['ETD'])

                if args.save_after_rec_quality_avgs and writer is not None:
                    for metric_name, group_values in rec_metrics_after.items():
                        for group_name, value in group_values.items():
                            if not args.save_overall and group_name == 'Overall':
                                continue
                            writer.writerow([alpha, metric_name, group_name, safe_mean(value), chosen_optimization])

                if args.save_after_exp_quality_avgs and writer is not None:
                    for metric_name, group_values in exp_metrics_after.items():
                        for group_name, value in group_values.items():
                            if not args.save_overall and group_name == 'Overall':
                                continue
                            writer.writerow([alpha, metric_name, group_name, value, chosen_optimization])

                if args.save_after_rec_quality_distributions and writer_distribution is not None:
                    for metric_name, group_values in rec_metrics_after.items():
                        for group_name, values in group_values.items():
                            if group_name == 'Overall':
                                continue
                            for value in values:
                                writer_distribution.writerow([alpha, metric_name, group_name, value, chosen_optimization])

                if args.save_after_exp_quality_distributions and writer_distribution is not None:
                    for metric_name, group_values in distributions_exp_metrics_after.items():
                        for group_name, values in group_values.items():
                            if group_name == 'Overall':
                                continue
                            for value in values:
                                writer_distribution.writerow([alpha, metric_name, group_name, value, chosen_optimization])
        finally:
            if log_file is not None:
                log_file.close()
                sys.stdout = orig_stdout
            if 'avg_metrics_file' in locals() and avg_metrics_file is not None:
                avg_metrics_file.close()
            if 'distribution_file' in locals() and distribution_file is not None:
                distribution_file.close()
