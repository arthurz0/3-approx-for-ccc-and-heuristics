from graph import Graph, primary_color
from algorithm.util import shuffled
import queue as Q

def deep_cluster(graph: Graph):
    graph = graph.primary_edge_graph()
    clustering = []
    is_clustered = dict((i, False) for i in graph.nodes())
    for center in shuffled(graph.nodes()):
        if is_clustered[center]: continue
        is_clustered[center] = True
        cluster = [center]
        neighbors = [neig for neig in graph.neighbors(center) if not is_clustered[neig]]
        cluster.extend(neighbors)
        for neig in neighbors: is_clustered[neig] = True
        for neig in neighbors:
            for candidate in graph.neighbors(neig):
                if is_clustered[candidate]: continue
                internal_edges = len([x for x in cluster if graph.has_edge(candidate, x)])
                external_edges = graph.degree[candidate] - internal_edges
                non_edges = len(cluster) - internal_edges
                if internal_edges > external_edges + non_edges:
                    cluster.append(candidate)
                    is_clustered[candidate] = True
        clustering.append((cluster, primary_color(graph, center)))
    return clustering