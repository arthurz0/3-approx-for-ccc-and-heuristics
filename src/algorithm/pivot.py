from random import shuffle, random, choices, randrange
from graph import Graph
from algorithm.util import most_frequent_color, shuffled
import queue as Q

def pivot(graph: Graph): # 3-Approximation
    clustering = []
    is_clustered = dict((i, False) for i in graph.nodes())
    for center in shuffled(graph.nodes()):
        if is_clustered[center]: continue
        is_clustered[center] = True
        cluster = [center]
        for a in graph.neighbors(center):
            if is_clustered[a]: continue
            is_clustered[a] = True
            cluster.append(a)
        cluster_color = most_frequent_color(graph, cluster)
        clustering.append((cluster, cluster_color))
    return clustering

def reduce_and_cluster(graph:Graph): # 5-Approximation
    graph = graph.primary_edge_graph()
    return pivot(graph)



