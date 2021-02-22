from graph import Graph, primary_color
from algorithm.util import shuffled


def chromatic_balls(graph: Graph): # 6 (D_max - 1) - Approximation
    is_clustered = {node: False for node in graph.nodes()}
    clustering = []
    for u, v in shuffled(graph.edges()):
        if u == v:
            continue
        if is_clustered[u] or is_clustered[v]:
            continue
        edge_color = graph.edges[(u,v)]['color']
        cluster = [u,v]
        is_clustered[u] = True
        is_clustered[v] = True
        for w in graph.neighbors(v):
            if is_clustered[w]:
                continue
            if not graph.has_edge(w,u):
                continue
            if graph.edges[(v,w)]['color'] == graph.edges[(u,w)]['color'] and graph.edges[(v,w)]['color'] == edge_color:
                cluster.append(w)
                is_clustered[w] = True
        clustering.append((cluster, edge_color))
    for node in graph.nodes():
        if is_clustered[node] == False:
            clustering.append(([node], 0))
    return clustering