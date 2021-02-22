from typing import Set, List, Tuple

def similarity(true_cluster: Set[int], cluster: Set[int]) -> float:
    intersection = cluster.intersection(true_cluster)
    if len(intersection) == 0:
        return 0
    precision = len(intersection) / len(cluster)
    recall = len(intersection) / len(true_cluster)
    return (2 * precision * recall) / (precision + recall)

def f_measure(true_clustering: List[Tuple[List[int], int]], clustering: List[Tuple[List[int], int]]) -> float:
    true_clustering = [set(clust) for clust, col in true_clustering]
    clustering = [set(clust) for clust, col in clustering]
    n = sum(map(len, clustering))
    result = 0
    for true_cluster in true_clustering:
        max_similarity = 0
        for cluster in clustering:
            max_similarity = max(max_similarity, similarity(true_cluster, cluster))
        result += max_similarity * len(true_cluster)
    return result / n