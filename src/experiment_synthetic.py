import graph_generation
from algorithm import chromatic_balls, deep_cluster, greedy_expansion, pivot, rmm, vote
from metric import f_measure
from log import log_synthetic
from random import random
import inspect
from time import process_time

def clean_source_code_line(line):
    cleaned = line.split(':', maxsplit = 1)[1].split('#', maxsplit=1)[0].strip()
    if cleaned[-1] == ',':
        return cleaned[:-1].strip()
    return cleaned

def approx_errors(runs, graph, cluster_generator, ground_truth):
    result = {
        'errors': [],
        'cluster_counts': [],
        'wall_clock_times': [],
        'f_scores': []
    }
    for _ in range(runs):
        start_time = process_time()
        clustering = cluster_generator(graph)
        end_time = process_time()
        result['errors'].append(graph.error_of(clustering))
        result['cluster_counts'].append(len(clustering))
        result['wall_clock_times'].append(end_time - start_time)
        result['f_scores'].append(f_measure(ground_truth, clustering))
    return result


def run_synthetic_experiments(round_counter = 0):
    algorithms = [
        lambda graph: pivot.pivot(graph),
        lambda graph: pivot.reduce_and_cluster(graph),
        lambda graph: deep_cluster.deep_cluster(graph),
        lambda graph: vote.vote(graph),
        lambda graph: rmm.random_maximum_merging(graph),
        lambda graph: greedy_expansion.greedy_expansion(graph),
        lambda graph: greedy_expansion.greedy_expansion(graph.primary_edge_graph()),
        lambda graph: chromatic_balls.chromatic_balls(graph),
    ]
    algorithm_names = {alg:clean_source_code_line(inspect.getsourcelines(alg)[0][0]) for alg in algorithms}
    graph_generators = []
    n = 10000
    GraphGeneratorClass = graph_generation.MutatedUniformClusterGraph
    for k in [10,20,50,100,150,200,250,300,350,400,450,500]:
        graph_generators.append(GraphGeneratorClass(n=n, k=k, p=0.1, f=20))

    for f in [5, 10, 15, 30,2, 1]:
        graph_generators.append(GraphGeneratorClass(n=n, k=100, p=0.1, f=f))

    for p in [0.0,0.01, 0.05,0.15,0.2,0.3,0.4,0.5]:
        graph_generators.append(GraphGeneratorClass(n=n, k=100, p=p, f=20))

    for generator_number, generator in enumerate(graph_generators):
        generator_start = process_time()
        summary = {}
        summary['graphs_generated'] = 10
        summary['runs_per_graph'] = 5
        summary['generator'] = generator
        summary['errors'] = []
        summary['algorithm'] = "ground_truth"
        summary['number_of_clusters'] = []
        summary['f_scores'] = []
        summary['wall_clock_times'] = []
        total_errors = [[] for _ in algorithms]
        cluster_sizes = [[] for _ in algorithms]
        f_scores = [[] for _ in algorithms]
        wall_clock_times = [[] for _ in algorithms]
        for graph_number in range(summary['graphs_generated']):
            graph_start = process_time()
            graph, ground_truth = generator.generate()
            start_t = process_time()
            graph.primary_edge_graph()
            end_t = process_time()
            summary['errors'].append(graph.error_of(ground_truth))
            summary['number_of_clusters'].append(len(ground_truth))
            summary['f_scores'].append(1.0)
            summary['wall_clock_times'].append(end_t - start_t)
            for i in range(len(algorithms)):
                alg = algorithms[i]
                print(f'computing {algorithm_names[alg]}...\t\t\t\t\t\t\t\t\t', end = '',flush=True)
                measurements = approx_errors(summary['runs_per_graph'], graph, alg, ground_truth)
                total_errors[i].extend(measurements['errors'])
                cluster_sizes[i].extend(measurements['cluster_counts'])
                f_scores[i].extend(measurements['f_scores'])
                wall_clock_times[i].extend(measurements['wall_clock_times'])
                print(end='\r')
            graph_end = process_time()
            print(f'round {round_counter}: generator {generator_number}: completed graph {graph_number + 1} of {summary["graphs_generated"]}, {round(graph_end - graph_start, 2)} seconds\t\t\t\t\t\t\t\t\t')
        log_synthetic(summary)
        for i in range(len(algorithms)):
            alg = algorithms[i]
            summary['errors'] = total_errors[i]
            summary['algorithm'] = algorithm_names[alg]
            summary['number_of_clusters'] = cluster_sizes[i]
            summary['f_scores'] = f_scores[i]
            summary['wall_clock_times'] = wall_clock_times[i]
            log_synthetic(summary)
        generator_end = process_time()
        print(f'generator {generator_number} completed, {round(generator_end - generator_start, 2)} seconds')

run_synthetic_experiments()