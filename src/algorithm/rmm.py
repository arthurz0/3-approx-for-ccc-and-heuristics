from random import random, choices
from graph import Graph, primary_color
from typing import List, Tuple, Dict
from networkx.utils import UnionFind
from algorithm.util import intersect_clusterings, shuffled
import queue as Q

def merge_dict(d1, d2):
    for key, val in d2.items():
        if key in d1: 
            if type(val) is dict:
                merge_dict(d1[key], val)
            else:
                d1[key] += val
        else: d1[key] = val

class ContractedNodes:
    def __init__(self, representative):
        self.representative = representative
        self.internal_edges_count = {}
        self.node_count = 1
        self.external_edges = {} #{edge_destination:{color:number_of_edges}}
    
    def internal_error(self):
        n = self.node_count
        total = n*(n-1)/2
        if not self.internal_edges_count: return total
        return total - max(self.internal_edges_count.values())
    
    def add_external_edge(self, target, col):
        if not target in self.external_edges:
            self.external_edges[target] = {}
        self.external_edges[target][col] = self.external_edges[target].get(col, 0) + 1

    def get_color(self):
        if not self.internal_edges_count:
            return 0
        return max(self.internal_edges_count, key=self.internal_edges_count.get)

    def merge(self, other, components):
        if not other.representative in self.external_edges:
            self.external_edges[other.representative] = {}
        merge_dict(self.internal_edges_count, other.internal_edges_count)
        merge_dict(self.internal_edges_count, self.external_edges[other.representative])
        other.external_edges[self.representative] = {}
        del other.external_edges[self.representative]
        del self.external_edges[other.representative]
        merge_dict(self.external_edges, other.external_edges)
        for neigh_id in self.external_edges:
            neigh = components[neigh_id]
            if not other.representative in neigh.external_edges:
                continue
            if not self.representative in neigh.external_edges:
                neigh.external_edges[self.representative] = {}
            merge_dict(neigh.external_edges[self.representative], neigh.external_edges[other.representative])
            del neigh.external_edges[other.representative]
        self.node_count += other.node_count
    
    def get_neighbor_representatives(self):
        return self.external_edges.keys()

def merged_error(a: ContractedNodes, b: ContractedNodes):
    edges_between = a.external_edges[b.representative]
    total_edges = {}
    merge_dict(total_edges, edges_between)
    merge_dict(total_edges, a.internal_edges_count)
    merge_dict(total_edges, b.internal_edges_count)
    n = a.node_count + b.node_count
    return n*(n-1)//2 - max(total_edges.values())

def current_error(a: ContractedNodes, b: ContractedNodes):
    edges_between = a.external_edges[b.representative]
    return a.internal_error() + b.internal_error() + sum(edges_between.values())

def contract_edge(a: int, b: int, clusters: UnionFind, components: Dict[int, ContractedNodes]):
    if clusters[a] == clusters[b]:
        return
    rootA = clusters[a]
    rootB = clusters[b]
    componentA = components[rootA]
    componentB = components[rootB]
    clusters.union(a,b)
    newRoot = clusters[a]
    if newRoot == rootA:
        components[newRoot].merge(componentB, components)
    else:
        components[newRoot].merge(componentA, components)

def initiate_components(graph: Graph):
    components = {i:ContractedNodes(i) for i in graph.nodes()}
    for a, b in graph.edges():
        for col in graph.colors_of(a, b):
            components[a].add_external_edge(b, col)
            components[b].add_external_edge(a, col)
    return components

def extract_clustering(components: Dict[int, ContractedNodes], clusters: UnionFind):
    clustering = []
    for cluster in clusters.to_sets():
        clustering.append((list(cluster), components[clusters[next(iter(cluster))]].get_color()))
    return clustering

def random_maximum_merging(graph: Graph, delete_secondary = True):
    if delete_secondary:
        graph = graph.primary_edge_graph()
    clusters = UnionFind(elements = list(graph.nodes()))
    components = initiate_components(graph)
    pq = Q.PriorityQueue() #-benefit, rand, representativeA, representativeB, sizeA, sizeB
    for u,v in graph.edges():
        pq.put((-1,random(),u,v,1,1))
    while not pq.empty():  
        value, _, u, v, sizeA, sizeB = pq.get()
        value = -value
        if clusters[u] == clusters[v]:
            continue
        if value <= 0:
            break
        compA = components[clusters[u]]
        compB = components[clusters[v]]
        if sizeA !=  compA.node_count or sizeB != compB.node_count:
            continue
        contract_edge(u,v,clusters,components)

        newComp = components[clusters[u]]
        newSize = newComp.node_count
        bestBenefit = 0
        for representative in newComp.get_neighbor_representatives():
            otherComp = components[representative]
            otherSize = otherComp.node_count
            benefit = current_error(newComp, otherComp) - merged_error(newComp, otherComp)
            if benefit > 0:
                bestBenefit = max(bestBenefit, benefit)
                pq.put((-benefit, random(), newComp.representative, representative, newSize, otherSize))
    return extract_clustering(components, clusters)