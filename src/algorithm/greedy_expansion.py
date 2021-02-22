from random import randrange, random
from graph import Graph
from algorithm.util import most_frequent_color, shuffled


def greedy_expansion(graph: Graph, initial_growth_limit = 25):
    clustering = []
    is_clustered = dict((i, False) for i in graph.nodes())
    unclustered_edges = list(graph.edges())
    past_centers = set()
    while unclustered_edges:
        i = randrange(len(unclustered_edges))
        u,v = unclustered_edges[i]
        if is_clustered[u] or is_clustered[v]:
            unclustered_edges[i], unclustered_edges[-1] = unclustered_edges[-1], unclustered_edges[i]
            unclustered_edges.pop()
            continue
        
        past_centers.add(u)
        past_centers.add(v)
        cluster = set()
        internal_edges = {0: 0}
        connectivity = {u: {0:0}}
        edge_connectivity = {u: 0}
        candidates = set([u])

        def remove_node(removed_node):
            cluster.remove(removed_node)
            for color, cardinality in connectivity[removed_node].items():
                internal_edges[color] = internal_edges.get(color, 0) - cardinality
            for node in graph.neighbors(removed_node):
                if is_clustered[node]: continue
                edge_connectivity[node] = edge_connectivity.get(node, 0) - 1
                for color in graph.colors_of(removed_node, node):
                    connectivity[node][color] = connectivity[node].get(color, 0) - 1  
        
        def add_node(added_node):
            candidates.remove(added_node)
            cluster.add(added_node)
            for color, cardinality in connectivity[added_node].items():
                internal_edges[color] = internal_edges.get(color, 0) + cardinality
            for node in graph.neighbors(added_node):
                if is_clustered[node]: continue
                if node not in cluster and node not in candidates: candidates.add(node)
                if node not in connectivity: connectivity[node] = {}
                edge_connectivity[node] = edge_connectivity.get(node, 0) + 1
                for color in graph.colors_of(added_node, node):
                    connectivity[node][color] = connectivity[node].get(color, 0) + 1
       
        add_node(u)
        add_node(v)
        neighbors_u = set(filter(lambda node: not is_clustered[node] and not node in cluster, graph.neighbors(u)))
        neighbors_v = set(filter(lambda node: not is_clustered[node] and not node in cluster, graph.neighbors(v)))
        common_neighborhood = neighbors_u.intersection(neighbors_v)
        exclusive_neighborhood = neighbors_u.symmetric_difference(neighbors_v)
        for node in (shuffled(common_neighborhood)+shuffled(exclusive_neighborhood))[:initial_growth_limit]:
            add_node(node)

        while len(cluster) > 1:
            def removal_gain(removal_candidate):
                n = len(cluster)
                current_error = n*(n-1)//2 - max(internal_edges.values())
                removal_error = (n-1)*(n-2)//2 - max([internal_edges[color] - connectivity[removal_candidate].get(color,0) for color in internal_edges.keys()]) + edge_connectivity[removal_candidate]
                return current_error - removal_error
            removal_candidate = max(cluster, key = lambda removal_candidate: removal_gain(removal_candidate) + random()/1000)
            if removal_gain(removal_candidate) >= 0:
                remove_node(removal_candidate)
            else:
                break
        
        while candidates:
            def candidate_connectivity(candidate):
                strongest_color = max(connectivity[candidate].keys(), key = lambda color: internal_edges.get(color, 0) + connectivity[candidate][color])
                positive_edges = connectivity[candidate][strongest_color]
                neutral_edges = edge_connectivity[candidate] - positive_edges
                return internal_edges.get(strongest_color, 0) + positive_edges + 0.5*neutral_edges
            candidate = max(candidates, key = lambda candidate: candidate_connectivity(candidate) + random()/1000)
            if candidate_connectivity(candidate) - max(internal_edges.values()) <= 0.5*len(cluster):
                break
            add_node(candidate)
        for node in cluster: is_clustered[node] = True
        clustering.append((list(cluster), most_frequent_color(graph, list(cluster))))
    for v in graph.nodes():
        if not is_clustered[v]:
            clustering.append(([v], 0))
    return clustering
