from .mst import sum_edges_mst

def is_considered_distance(id1, id2, to_consider, distance):
    """A function deciding if the resource should be considered using the distance"""
    main_dist = distance(id1, id2)
    return distance(id1, to_consider) < main_dist and distance(to_consider, id2) < main_dist

def is_considered_order(id1, id2, to_consider, order):
    """A function deciding if the resource should be considered using the order"""
    main_order = order(id1, id2)
    return 0.5 < order(id1, to_consider) and 0.5 < order(to_consider, id2)

def is_considered(id1, id2, to_consider, distance , order):
    """A function deciding if the resource should be considered"""
    return is_considered_distance(id1, id2, to_consider, distance) and is_considered_order(id1, id2, to_consider, order)

def fitness_score_distance(id1, id2, to_consider, distance):
    """A value to choose between two resources considering the distance"""
    return max(distance(id1,to_consider), distance(to_consider, id2))/distance(id1,id2) # We divide to normalize to potentially compare to the order

def fitness_score_order(id1, id2, to_consider, order):
    """A value to choose between two resources considering the order
    Actually not implemented because it takes over the distance"""
    return 0

def fitness_score(id1, id2, to_consider, distance , order):
    """A score to choose between two resources"""
    return max(fitness_score_distance(id1, id2, to_consider, distance), fitness_score_order(id1, id2, to_consider, order))

def recommend_pair(id1, id2, possible, distance, order):
    """Given a pair and candidates, return the resource to insert (or None)"""
    considered_with_scores = [(fitness_score(id1, id2, nei, distance, order),nei) for nei in possible if is_considered_order(id1,id2,nei,order)]
    if len(considered_with_scores) == 0:
        return None
    return min(considered_with_scores)[1]

def recommend_between_sequence(sequence, possible, distance , order):
    """Given a sequence and candidates for each pair, return a list of resources to insert (or None values)"""
    return [recommend_pair(sequence[i],sequence[i+1], possible[i], distance, order) for i in range(len(possible))]
               
def remove_between_sequence(sequence, distance):
    """Return a resource to remove from the sequence, given the distance, or None if no resource seems worthy to remove"""
    id_to_remove = None
    val_to_remove = None
    for i in range(1,len(sequence)-1):
        value_distance = min(distance(sequence[i-1],sequence[i]),distance(sequence[i],sequence[i+1]))/distance(sequence[i-1],sequence[i+1])
        if value_distance > 1 and (val_to_remove == None or val_to_remove < value_distance):
            id_to_remove = sequence[i]
            val_to_remove = value_distance
    return id_to_remove

def generate_adjacency_graph(nodes, distance):
    """Generate an graph given the nodes and the distance function"""
    G = {node:{} for node in nodes}
    for node in nodes:
        for neighbor in nodes:
            if neighbor < node:
                dist = distance(node,neighbor)
                G[node][neighbor] = dist
                G[neighbor][node] = dist
    return G

def remove_from_basket_mst(basket, distance):
    """Return a couple (value, resource) the resource that maximizes the improvement in the mst when removing it"""
    full_graph = generate_adjacency_graph(basket, distance)
    mst_value_full_graph = sum_edges_mst(full_graph)
    all_values = [((mst_value_full_graph - sum_edges_mst(generate_adjacency_graph([i for i in basket if i != u], distance)))/mst_value_full_graph, u) for u in basket]
    print(all_values)
    return max(all_values)

def remove_from_basket_sum_distances(basket, distance):
    """Return a couple (value,resource) to remove from the basket. The choice is made considering the sum of the distances to this resource"""
    sum_all_edges = sum((distance(basket[i], basket[j]) for i in range(len(basket)) for j in range(i)))
    all_values = [(sum([distance(resource, neighbor)/sum_all_edges for neighbor in basket]),resource) for resource in basket]
    print(all_values)
    return max(all_values)

def remove_from_basket(basket, distance):
    """Return a resource to remove from the basket"""
    return max((remove_from_basket_mst(basket,distance),remove_from_basket_sum_distances(basket,distance)))[1]
