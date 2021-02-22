from algorithm import chromatic_balls, deep_cluster, greedy_expansion, pivot, rmm, vote
from statistics import mean, median
from log import log_real_world
import inspect
from graph import Graph
from dataset import read_dataset
import queue as Q
from time import process_time

def clean_source_code_line(line):
    cleaned = line.split(':', maxsplit = 1)[1].split('#', maxsplit=1)[0].strip()
    if cleaned[-1] == ',':
        return cleaned[:-1].strip()
    return cleaned

def approx_errors(runs, graph, cluster_generator):
    result = {
        'errors': [],
        'cluster_counts': [],
        'wall_clock_times': []
    }
    for _ in range(runs):
        start_time = process_time()
        clustering = cluster_generator(graph)
        end_time = process_time()
        result['errors'].append(graph.error_of(clustering))
        result['cluster_counts'].append(len(clustering))
        result['wall_clock_times'].append(end_time - start_time)
        print('#', end = '',flush=True)
    print(end='\r')
    return result

def remove_nodes_with_low_degree(graph: Graph, min_degree):
    if min_degree == 0:
        return
    deleted = set()
    pq = Q.PriorityQueue()
    for node in graph.nodes():
        pq.put((graph.degree[node],node))
    while not pq.empty():
        degree, node = pq.get()
        if node in deleted: continue
        if degree >= min_degree:
            return
        for neig in graph.neighbors(node):
            pq.put((graph.degree[neig]-1, neig))
        graph.remove_node(node)
        deleted.add(node)

def run_real_world_experiment(dataset_name, algorithms, algorithm_names, runs, minimum_degree = 0):
    print(f"Reading dataset: {dataset_name}")
    dataset = read_dataset(dataset_name)
    if minimum_degree > 0:
        dataset_name = dataset_name + f"_min_degree_{minimum_degree}"
    summaries = []
    for i in range(len(algorithms)+1):
        summary = {}
        summary['runs'] = runs
        summary['number_of_nodes'] = 0
        summary['number_of_edges'] = 0
        summary['number_of_colors'] = 0
        summary['dataset'] = dataset_name
        summary['errors'] = [0]*summary['runs']
        summary['wall_clock_times'] = [0]*summary['runs']
        summary['number_of_clusters'] = [0]*summary['runs']
        summary['algorithm'] = algorithm_names[algorithms[i]].split('.', maxsplit=1)[1] if i < len(algorithms) else 'primary_edge_graph'
        summaries.append(summary)
    summaries[-1]['runs'] = 10
    summaries[-1]['wall_clock_times'] = [0]*summaries[-1]['runs']
    summaries[-1]['dataset'] = dataset_name

    for graph_number, graph in enumerate(dataset):
        print(f'part {graph_number}')
        if minimum_degree > 0:
            remove_nodes_with_low_degree(graph, minimum_degree)

        # measure time of to create primary_edge_graph(), we generally cache it to speed up the experiments
        for i in range(summaries[-1]['runs']):
            if hasattr(graph, 'primary_graph'):
                delattr(graph, 'primary_graph')
            start_time = process_time()
            graph.primary_edge_graph()
            end_time = process_time()
            summaries[-1]['wall_clock_times'][i] += end_time - start_time
        
        results_by_algorithm = {}
        for i in range(len(algorithms)):
            summary = summaries[i]
            alg = algorithms[i]
            summary['number_of_nodes'] += graph.number_of_nodes()
            summary['number_of_edges'] += graph.number_of_edges()
            summary['number_of_colors'] = max(summary['number_of_colors'], len(graph.colors()))
            measurements = approx_errors(summary['runs'], graph, alg)
            for i in range(summary['runs']):
                summary['errors'][i] += measurements['errors'][i]
                summary['number_of_clusters'][i] += measurements['cluster_counts'][i]
                summary['wall_clock_times'][i] += measurements['wall_clock_times'][i]
            results_by_algorithm[algorithm_names[alg]] = mean(measurements['errors'])
            print("{0:65} mean: {1:8}     median: {2:8}     wct all runs: {3:8} seconds".format(summary['algorithm'], round(mean(measurements['errors'])), round(median(measurements['errors'])), round(sum(measurements['wall_clock_times']), 2)))
        print()

    for i in range(len(algorithms)+1):
        summary = summaries[i]
        log_real_world(summary)

def run_real_world_experiment_on_all_algorithms_and_datasets(): 
    print("run_real_world_experiment")      
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
    small_datasets = ['facebook', 'twitter', 'microsoft_academic', 'cooking', 'dawn']
    large_datasets = ['dblp', 'string']
    legacy_datasets = ['legacy_string', 'legacy_dblp']
    for dataset_name in small_datasets + large_datasets:
        run_real_world_experiment(dataset_name, algorithms, algorithm_names, runs = 50)
        run_real_world_experiment(dataset_name + '_multilabel', algorithms[:-1], algorithm_names, runs = 50)
    for dataset_name in legacy_datasets:
        run_real_world_experiment(dataset_name, algorithms, algorithm_names, runs = 50, minimum_degree=10)
        
run_real_world_experiment_on_all_algorithms_and_datasets()