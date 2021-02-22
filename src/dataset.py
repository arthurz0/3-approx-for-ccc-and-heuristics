import pandas as pd
from graph import Graph
from multigraph import MultiGraph
import os
from os.path import isfile, join
import networkx as nx
import random

def read_dataset(name: str):
    if name in ['facebook', 'twitter', 'microsoft_academic','facebook_multilabel', 'twitter_multilabel', 'microsoft_academic_multilabel']:
        return map(remove_self_loops, read_small_dataset(name))
    data_dict = {
        'dblp': (lambda : read_dblp()),
        'dblp_multilabel': (lambda : read_dblp(multilabel = True)),
        'string': (lambda : read_string()),
        'string_multilabel': (lambda : read_string(multilabel = True)),
        'legacy_dblp': (lambda : read_legacy('DBLP_ALL.csv')),
        'legacy_string': (lambda : read_legacy('STRING_ALL.csv')),
        'cooking': (lambda : read_hyperedge('Cooking_majority.csv')),
        'cooking_multilabel': (lambda : read_hyperedge('Cooking_majority.csv', multilabel = True)),
        'dawn': (lambda : read_hyperedge('DAWN_majority.csv')),
        'dawn_multilabel': (lambda : read_hyperedge('DAWN_majority.csv', multilabel = True)),\
    }
    if name not in data_dict:
        raise Exception('Unknown Dataset')
    return map(remove_self_loops, data_dict[name]())

def remove_self_loops(graph):
    for node in graph.nodes():
        if graph.has_edge(node, node):
            graph.remove_edge(node, node)
    return graph

def read_social_circles(path, multilabel = False):
    graph = None
    if multilabel:
        graph = nx.read_edgelist(join(path, 'combined.txt'), nodetype = int, create_using = MultiGraph, comments = '#')
    else:
        graph = nx.read_edgelist(join(path, 'combined.txt'), nodetype=int, create_using = Graph,comments ='#')
    circle_path = join(path, 'circles')
    circle_files = [f for f in os.listdir(circle_path) if isfile(join(circle_path, f))]
    circles_of = {}
    circle_id = 0
    for circle_file in circle_files:
        with open(join(circle_path, circle_file), 'r') as file:
            ego = os.path.basename(circle_file).split('.')[0]
            for line in file.readlines():
                circle = [int(a) for a in line.split()[1:]]
                circle.append(ego)
                for node in circle:
                    if not node in circles_of:
                        circles_of[node] = set()
                    circles_of[node].add(circle_id)
                circle_id += 1
    random_edges = 0
    semi_random_edges = 0
    useless_nodes = [node for node in graph.nodes() if node not in circles_of]
    graph.remove_nodes_from(useless_nodes)
    for a, b in graph.edges():
        shared_circles = circles_of[a].intersection(circles_of[b])
        edge_color = None
        if multilabel:
            if len(shared_circles) == 0:
                shared_circles = [random.randrange(circle_id)]
                random_edges += 1  
            graph.edges[(a,b)]['colors'] = list(shared_circles)
        else:
            if shared_circles:
                edge_color = random.choice(list(shared_circles))
                if len(shared_circles) > 1: semi_random_edges += 1
            else:
                edge_color = random.randrange(circle_id)   
                random_edges += 1      
            graph.edges[(a, b)]['color'] = edge_color
    return [graph]
                
def read_microsoft_academic(multilabel = False):
    data_path = './data/microsoft_academic/'
    labels = []
    with open(join(data_path,'hyperedge-labels.txt')) as file:
        for line in file.readlines():
            labels.append(int(line)-1)
    edge_candidates = {}
    with open(join(data_path,'hyperedges.txt')) as file:
        for index, line in enumerate(file.readlines()):
            label = labels[index]
            authors = [int(i) for i in line.split()]
            for a in range(len(authors)):
                for b in range(a+1, len(authors)):
                    adrian = authors[a]
                    bdrian = authors[b]
                    edge = (min(adrian, bdrian), max(adrian, bdrian))
                    if edge not in edge_candidates:
                        edge_candidates[edge] = {}
                    edge_candidates[edge][label] = edge_candidates[edge].get(label, 0) + 1
    graph = MultiGraph() if multilabel else Graph()
    for edge, potential_topics in edge_candidates.items():
        if multilabel:
            graph.add_edge(edge[0], edge[1], colors = list(potential_topics.keys()))
        else:
            most_frequent_topic = max(potential_topics, key = potential_topics.get)
            graph.add_edge(edge[0], edge[1], color = most_frequent_topic)
    return [graph]


def spliturl(url):
    splitted = url.split('/')
    if len(splitted) >= 3:
        return splitted[2]
    else:
        return None

def generate_dblp():
    data_path = './data/dblp/'
    publication_types = ['output_article', 'output_inproceedings']
    for publication_type in publication_types:
        print(publication_type)
        headername = publication_type + '_header.csv'
        df_header = pd.read_csv(join(data_path, headername), sep =';')
        column_names = ([i.split(':')[0] for i in df_header.columns])
        if 'url' not in column_names:
            print('does not have a url: ', column_names)
            continue
        filename = publication_type + '.csv'
        column_types = {name:str for name in column_names}
        df = pd.read_csv(join(data_path, filename), sep = ';', header = None, names = column_names, dtype=column_types)
        df = df[['author', 'url']]
        print(df.shape)
        df = df.dropna()
        df['url'] = df['url'].apply(spliturl)
        df = df.dropna()
        print(df.shape)
        df.to_csv(join(data_path, publication_type + '_dataset.csv'))
        print(df.head())

def read_dblp_slow(multilabel = False):
    data_path = './data/dblp_original/'
    publication_types = ['output_article', 'output_inproceedings']
    authors_by_name = {}
    journals_by_name = {}
    author_id_counter = 0
    journal_id_counter = 0
    edge_candidates = {}
    for publication_type in publication_types:
        print(publication_type)
        filename = join(data_path, publication_type + '_dataset.csv')
        with open(filename, 'r', encoding='utf-8') as file: 
            line = file.readline() #header
            line = file.readline()
            while line:
                authors = line.split(',')[1].split('|')
                journal = line.split(',')[2]
                if journal not in journals_by_name:
                    journals_by_name[journal] = journal_id_counter
                    journal_id_counter+= 1
                for author in authors:
                    if author not in authors_by_name:
                        authors_by_name[author] = author_id_counter
                        author_id_counter+= 1
                journal_id = journals_by_name[journal]
                for i in range(len(authors)):
                    for j in range(i+1, len(authors)):
                        idA = authors_by_name[authors[i]]
                        idB = authors_by_name[authors[j]]
                        if idA == idB:
                            continue
                        edge = (min(idA, idB), max(idA, idB))
                        if edge not in edge_candidates:
                            edge_candidates[edge] = {}
                        if not journal_id in edge_candidates[edge]:
                            edge_candidates[edge][journal_id] = 0
                        edge_candidates[edge][journal_id] += 1
                line = file.readline()        
    graph = MultiGraph() if multilabel else Graph()
    for edge, potential_topics in edge_candidates.items():
        if multilabel:
            graph.add_edge(edge[0], edge[1], colors = potential_topics.keys())
        else:
            most_frequent_topic = max(potential_topics, key = potential_topics.get)
            graph.add_edge(edge[0], edge[1], color = most_frequent_topic)
    return [graph]

def read_dblp(multilabel = False):
    graph = None
    if multilabel:
        filename = "./data/dblp/dblp_multilabel.edgelist"
        graph = MultiGraph()
        with open(filename) as file:
            for index, line in enumerate(file.readlines()):
                parts = line.split(' ', maxsplit = 2)
                a = int(parts[0])
                b = int(parts[1])
                color_list = parts[2].split('[', maxsplit = 1)[1][:-3]
                colors = set(int(i) for i in color_list.split(','))
                graph.add_edge(a,b, colors = colors)
    else:
        graph = nx.read_edgelist("dblp.edgelist", create_using = Graph,nodetype =int, data=(("color", int),))
    return [graph]

def read_string(multilabel = False):
    def read_graph(path):
        graph = Graph() if not multilabel else MultiGraph()
        with open(path) as file:
            line = file.readline()
            line = file.readline()
            while line:
                elems = [int(x) for x in line.strip().split(',')]
                u = elems[0]
                v = elems[1]
                graph.add_edge(u, v)
                if not multilabel:
                    graph[u][v]['color'] = elems[2]
                else:
                    graph[u][v]['colors'] = set(elems[2:])
                line = file.readline()
        return graph

    directory = './data/string_protein'
    return (read_graph(os.path.join(directory, filename)) for filename in os.listdir(directory))

def read_hyperedge(filename, multilabel = False):
    def read_graph(path):
        graph = Graph() if not multilabel else MultiGraph()
        with open(path) as file:
            line = file.readline()
            while line:
                elems = [int(x) for x in line.strip().split(',')]
                u = elems[0]
                v = elems[1]
                graph.add_edge(u, v)
                if not multilabel:
                    graph[u][v]['color'] = elems[2]
                else:
                    graph[u][v]['colors'] = set(elems[2:])
                line = file.readline()
        return graph

    path = './data/hyperedge/' + filename
    return [read_graph(path)]

def read_legacy(filename):
    def read_graph(path):
        return nx.read_edgelist(path, comments='#', delimiter=' ', create_using=Graph,nodetype =int, data=[('color', int)])

    directory = './data/legacy'
    return [read_graph(os.path.join(directory, filename))]

def read_small_dataset(filename):
    def read_graph(path, multilabel = False):
        if multilabel:
            graph = MultiGraph()
            with open(path) as file:
                for index, line in enumerate(file.readlines()):
                    parts = line.split(' ', maxsplit = 2)
                    a = int(parts[0])
                    b = int(parts[1])
                    color_list = parts[2].split('[', maxsplit = 1)[1].split(']', maxsplit=1)[0]
                    colors = set(int(i) for i in color_list.split(','))
                    graph.add_edge(a,b, colors = colors)
            return graph
        return nx.read_edgelist(path, comments='#', delimiter=' ', create_using=Graph,nodetype =int, data=[('color', int)])

    directory = './data/small_datasets'
    multilabel = filename.endswith('_multilabel')
    return [read_graph(os.path.join(directory, filename+'.edgelist'), multilabel=multilabel)]

