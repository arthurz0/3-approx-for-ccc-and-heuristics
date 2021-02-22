from typing import List, Tuple, Set
import networkx as nx

def print_cluster_head(cluster,n):
    if len(cluster) <= n:
        print("Cluster is ", cluster)
        return
    print("Cluster is ",cluster[:n], f"... (size {len(cluster)})")


def primary_color(graph, node: int):
    count = {}
    for _, v in graph.edges(node):
        for color in graph.colors_of(node, v):
            count[color] = count.get(color, 0) + 1
    if not count:
        return 0
    return max(count, key=count.get)

class Graph(nx.Graph):
    def is_multilabel_graph(self):
        return False
    
    def without_secondary_edges(self):
        edited_graph = Graph()
        edited_graph.add_nodes_from(self.nodes())
        primary_colors = dict([(i, primary_color(self, i)) for i in self.nodes()])
        for u, v in self.edges():
            if primary_colors[u] == primary_colors[v] and primary_colors[u] in self.colors_of(u, v):
                edited_graph.add_edge(u, v, color=primary_colors[u])
        return edited_graph
        
    def primary_edge_graph(self):
        if not hasattr(self, 'primary_graph'):
            self.primary_graph = self.without_secondary_edges()
        return self.primary_graph

    def colors_of(self, a: int, b: int) -> List[int]:
        return [self.color_of(a, b)]
    
    def color_of(self, a: int, b: int) -> int:
        return self.edges[(a,b)]['color']

    def colors(self) -> Set[int]:
        if not hasattr(self, 'color_set'):
            colors = set()
            for edge in self.edges:
                colors.add(self.edges[edge]['color'])
            self.color_set = colors
        return self.color_set

    def node_pairs(self) -> List[Tuple[int, int]]:
        return [(a, b) for a in self.nodes for b in self.nodes if a < b]
    
    def is_valid_clustering(self, clustering: List[Tuple[List[int], int]]) -> bool:
        cluster_nodes = set()
        for cluster, col in clustering:
            if not isinstance(col, int):
                print(f"Cluster col {col} is not an integer.")
                print_cluster_head(cluster, 20)
                return False
            for node in cluster:
                if node in cluster_nodes:
                    print(f"{node} is already clustered in some other cluster.")
                    print_cluster_head(cluster, 20)
                    return False
                cluster_nodes.add(node)
        if cluster_nodes.symmetric_difference(set(self.nodes())):
            print(f"Set of clustered nodes is not equal to set of nodes.")
            print(f"{len(cluster_nodes)} were clustered, {len(self.nodes())} nodes in this graph.")
            print(f"{len(cluster_nodes.symmetric_difference(set(self.nodes())))} nodes in difference.")
            return False
        return True

    def error_of(self, clustering: List[Tuple[List[int], int]]) -> int:
        if not self.is_valid_clustering(clustering):
            raise Exception('Clustering is not valid')
        remaining_edges = self.number_of_edges()
        color_errors = 0
        non_edge_errors = 0
        for cluster, color in clustering:
            for v in cluster:
                for u in cluster:
                    if u <= v: continue
                    if not self.has_edge(u, v):
                        non_edge_errors += 1
                    else:
                        remaining_edges -= 1
                        if self.color_of(u,v) != color:
                            color_errors += 1
        return remaining_edges + non_edge_errors + color_errors