import pandas as pd
from graph import Graph
from datetime import datetime
import os.path
from statistics import mean

LOG_PATHS = {
    'synthetic' :  'measurements/synthetic_log.csv',
    'real_world' : 'measurements/real_world_log.csv'
}

def write_to(df, file_path):
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)
    if os.path.isfile(file_path):
        df.to_csv(file_path, header=False, mode='a', index=False)
    else:
        df.to_csv(file_path, index=False)

def log_real_world(result, file_path=LOG_PATHS['real_world']):
    entry = {
        'timestamp': [datetime.now()],
        'algorithm': [result['algorithm']],
        'mean_approx_error': [mean(result['errors'])],
        'approx_errors': [result['errors']],
        'number_of_clusters': [result['number_of_clusters']],
        'wall_clock_times': [result['wall_clock_times']],
        'avg_wct': [mean(result['wall_clock_times'])],
        'runs': [result['runs']],
        'number_of_nodes': [result['number_of_nodes']],
        'number_of_edges': [result['number_of_edges']],
        'number_of_colors': [result['number_of_colors']],
        'dataset': [result['dataset']]
    }
    write_to(pd.DataFrame(entry), file_path)

def log_synthetic(result, file_path=LOG_PATHS['synthetic']):
    entry = {
        'timestamp': [datetime.now()],
        'algorithm': [result['algorithm']],
        'mean_error': [mean(result['errors'])],
        'number_of_clusters':[result['number_of_clusters']],
        'wall_clock_times': [result['wall_clock_times']],
        'avg_wct': [mean(result['wall_clock_times'])],
        'f_score':[result['f_scores']],
        'errors': [result['errors']],
        'graphs_generated': [result['graphs_generated']],
        'runs_per_graph': [result['runs_per_graph']],
        'graph_generator': [result['generator'].summary()]
    }
    write_to(pd.DataFrame(entry), file_path)