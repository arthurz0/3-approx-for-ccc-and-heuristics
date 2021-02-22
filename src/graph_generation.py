from random import random, randrange, randint, shuffle
from graph import Graph

class GraphGenerator:
    def __init__(self, **kwargs):
        self.arguments = kwargs
    
    def generate(self):
        return self.generate_graph(**self.arguments)
    
    def generate_graph(self):
        pass

    def name(self):
        return type(self).__name__

    def summary(self):
        return {
            'name': self.name(),
            'arguments': self.arguments
        }
    
#k = #cluster, p = mutation rate, f = #colors

class GilbertGraph(GraphGenerator):
    def generate_graph(self, n, p, f):
        graph = Graph()
        graph.add_nodes_from(range(n))
        for i, j in graph.node_pairs():
            if random() < p:
                graph.add_edge(i, j, color = randrange(f))
        return graph


class UniformClusterGraph(GraphGenerator):
    def generate_graph(self, n, k, f):
        graph = Graph()
        graph.add_nodes_from(range(n))
        
        shuf = [*range(n)]
        shuffle(shuf)
        cluster = [0 for i in range(k)]
        clustered = 0
        clustering = [([],0) for i in range(k)]
        for i in range(n):
            x = randrange(k)
            cluster[x]+=1
        for i in range(k):
            c = cluster[i]
            cf = randrange(f)
            clustering[i] = (clustering[i][0], cf)
            for x in range(clustered,clustered+c):
                clustering[i][0].append(shuf[x])
                for y in range(x+1,clustered+c):
                    graph.add_edge(shuf[x], shuf[y], color = cf)
            clustered += c
        return graph, clustering

class MutatedUniformClusterGraph(GraphGenerator):
    def generate_graph(self, n, k, p, f):
        graph1, clustering = UniformClusterGraph(n=n, k=k, f=f).generate()
        graph2 = GilbertGraph(n=n, p=p, f=f).generate()
        for i, j in graph2.edges():
            if not i < j: continue
            if graph1.has_edge(i,j) and graph1.color_of(i,j) == graph2.color_of(i,j):
                graph1.remove_edge(i,j)
            else:
                graph1.add_edge(i,j, color=graph2.color_of(i,j))
        return graph1, clustering
