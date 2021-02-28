""" Generate the minimum spanning tree of a graph, and computes many different representations"""

def ordered_edges_mst_graph_indexed(adj_graph):
    """Return a list of edges in the order they were added in the maximum spanning tree.
    Each edge is a triple (weight, (i, j), (c1,c2)) where c1 and c2 are the two classes that are merged during the mst computation.
    We suppose that the graph is not directed"""
    n = len(adj_graph)
    sorted_edges = sorted([(adj_graph[j][i],(j,i)) for i in range(n) for j in range(i)])
    node_class = [i for i in range(n)]
    current_edge_index = 0
    edges = []
    for iterations in range(n-1):
        current_edge = sorted_edges[current_edge_index]
        while node_class[current_edge[1][0]] == node_class[current_edge[1][1]]:
            current_edge_index += 1
            current_edge = sorted_edges[current_edge_index]
        changed_classes = [node_class[current_edge[1][0]], node_class[current_edge[1][1]]]
        min_class,max_class = min(changed_classes), max(changed_classes)
        edges.append((current_edge[0],current_edge[1],(min_class,max_class)))
        node_class = [min_class if node_class[i] == max_class else node_class[i] for i in range(n)]
    return edges

def ordered_edges_mst(adj_graph):
    """Return the mst with information where the adj_graph is not necessarily indexed from 0 to n-1""" 
    ids_to_names = list(adj_graph)
    names_to_ids = {ids_to_names[i]:i for i in range(len(ids_to_names))}
    graph_indexed = {names_to_ids[name]:{names_to_ids[name2]:dist for name2, dist in adj_graph[name].items()} for name in adj_graph}
    edges = ordered_edges_mst_graph_indexed(graph_indexed)
    return [(c[0], (ids_to_names[c[1][0]],ids_to_names[c[1][1]]), (ids_to_names[c[2][0]], ids_to_names[c[2][1]])) for c in edges]

def max_edge_mst(adj_graph):
    """Return a couple (weight, (u,v)) representing the maximum weight edge in the mst of the given graph"""
    return min([(c[0],c[1]) for c in ordered_edges_mst(adj_graph)])

def sum_edges_mst(adj_graph):
    """Return the sum of the weights of the edges present in the MST of the graph"""
    return sum([c[0] for c in ordered_edges_mst(adj_graph)])
