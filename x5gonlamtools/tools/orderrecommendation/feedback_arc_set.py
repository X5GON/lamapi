
""" Define functions using the theory of feedback arc set to generate a sequence coherent with the ordering (input graph)"""

def proba_fail(origin, next_ids, graph):
    """ Return the probability that the origin should be predicted before all the next_ids (supposing independency)"""
    prod = 1
    for next_id in next_ids:
        if next_id in graph[origin]:
            prod *= graph[origin][next_id]
        else:
            prod *= 1-graph[next_id][origin]
    return prod

def nb_fails(origin, next_ids, graph):
    """ Return the number of bad prediction if origin is put before the next_ids"""
    return sum([1 for i in next_ids if origin in graph[i]])

def inverse_lexicographic_lt(c1, c2):
    return c1[1] < c2[1] or (c1[1] == c2[1] and c1[0] < c2[0])

def recursive_feedback(allowed_set, current_val, current_seq, best_val, best_seq, graph, comparison=lambda x,y: x<y):
    """ Given a set of vertices to order, a current and best value and sequence, and the graph, return the best value and the best sequence. If increasing the current solution makes the solution worse than the best_val, best_seq is returned"""
    if len(allowed_set) == 0:
        if not comparison(current_val,best_val):
            raise ValueError("It should not be possible be at the leaf of the recursion tree with a worse solution")
        return current_val, current_seq
    for _nb_nei,current in sorted([(len(graph[i]),i) for i in allowed_set],reverse=True):
        allowed_set.remove(current)
        nb_errors = nb_fails(current, allowed_set, graph)
        proba_errors = proba_fail(current, allowed_set, graph)
        updated_current_val = (current_val[0]+nb_errors, current_val[1]*proba_errors)
        updated_current_seq = current_seq + [current]
        if comparison(updated_current_val,best_val):
            best_val, best_seq = recursive_feedback(allowed_set, updated_current_val, updated_current_seq, best_val, best_seq, graph)
        allowed_set.add(current)
    return best_val, best_seq

def generate_sequence_from_feedback_arc_set(graph):
    """ Return a sequence (containing all the nodes in the graph) that minimizes the number of back edges, and the probability of having a bad prediction"""
    return recursive_feedback(set(graph), (0,-1), [], (len(graph)**2, 0), [], graph)[1]

if __name__ == '__main__':
    print(generate_sequence_from_feedback_arc_set({0:{1:0.8,2:0.6},1:{2:0.9,3:0.7},2:{3:0.8},3:{0:0.53}}))
    








            
