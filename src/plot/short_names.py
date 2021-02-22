def remove_alg_prefix(alg):
    return alg.split('.', maxsplit = 1)[1] if len(alg.split('.')) > 1 else alg

algorithm_short_names = {
    'pivot(graph)':'Pivot',
    'chromatic_balls(graph)': 'CB',
    'reduce_and_cluster(graph)': 'RC',
    'deep_cluster(graph)': 'DC',
    'vote(graph)': 'Vote',
    'random_maximum_merging(graph)': 'RMM',
    'random_maximum_merging(graph, delete_secondary = False)': 'RMM_S',
    'greedy_expansion(graph)': 'GE',
    'greedy_expansion(graph.primary_edge_graph())': 'GER',
    
    'primary_edge_graph':'primary_edge_graph',  # logs time required to delete secondary edges
}

dataset_short_names = {
    'facebook': 'Facebook', 
    'twitter': 'Twitter', 
    'microsoft_academic': 'MAG',
    'string': 'String',
    'legacy_string_min_degree_10': 'String_S',
    'legacy_dblp_min_degree_10': 'DBLP_S',
    'cooking': 'cooking', 
    'dawn': 'DAWN',
    'dblp': 'DBLP'
}
for key, val in list(dataset_short_names.items()):
    dataset_short_names[key + '_multilabel'] = val
