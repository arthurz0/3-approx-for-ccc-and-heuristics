from typing import List, Tuple, Set
from graph import Graph

class MultiGraph(Graph):
    def is_multilabel_graph(self):
        return True

    def colors_of(self, a: int, b: int) -> Set[int]:
        return self.edges[(a,b)]['colors']

    def colors(self) -> Set[int]:
        colors = set()
        for edge in self.edges:
            colors = colors.union(self.edges[edge]['colors'])
        return colors

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
                        if color not in self.colors_of(u,v):
                            color_errors += 1
        return remaining_edges + non_edge_errors + color_errors
