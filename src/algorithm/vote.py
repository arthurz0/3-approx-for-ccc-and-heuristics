from graph import Graph, primary_color
from typing import List
from random import random
from algorithm.util import most_frequent_color, shuffled

def vote(graph: Graph):
    graph = graph.primary_edge_graph()
    cluster_of = {}
    clustering = []
    cluster_colors = []
    for node in shuffled(graph.nodes()):
        connectivity = {}
        for u in graph.neighbors(node):
            if u not in cluster_of: continue
            cluster = cluster_of[u]
            connectivity[cluster] = connectivity.get(cluster, 0) + 1
        best_cluster = max(connectivity, key = lambda id: 2*connectivity[id] - len(clustering[id]) + random()*0.42) if connectivity else None
        if best_cluster is not None and 2*connectivity[best_cluster] - len(clustering[best_cluster]) > 0:
            clustering[best_cluster].append(node)
            cluster_of[node] = best_cluster
        else:
            clustering.append([node])
            cluster_colors.append(primary_color(graph, node))
            cluster_of[node] = len(clustering) - 1
    return list(zip(clustering, cluster_colors))