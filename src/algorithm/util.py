from typing import List, Tuple
from graph import Graph
from multigraph import MultiGraph
from random import shuffle

def most_frequent_color(graph: Graph, vertices: List[int]):
    count = {0: 0}
    for a in vertices:
        for b in vertices:
            if not a < b or not graph.has_edge(a, b): continue
            for color in graph.colors_of(a,b):
                count[color] = count.get(color, 0) + 1
    return max(count, key=count.get)

def cluster_ids(clustering: List[Tuple[List[int], int]]):
    cluster_id = {}
    for i, cluster in enumerate(clustering):
        for node in cluster[0]:
            cluster_id[node] = i
    return cluster_id

def intersect_clusterings(clustering_1: List[Tuple[List[int], int]], clustering_2: List[Tuple[List[int], int]]):
    cluster_ids_1 = cluster_ids(clustering_1)
    cluster_ids_2 = cluster_ids(clustering_2)
    clustering = {}
    for node, id1 in cluster_ids_1.items():
        id2 = cluster_ids_2[node]
        if not (id1, id2) in clustering:
            clustering[(id1, id2)] = ([], clustering_1[id1][1])
        clustering[(id1, id2)][0].append(node)
    return list(clustering.values())

def shuffled(collection):
    as_list = [i for i in collection]
    shuffle(as_list)
    return as_list