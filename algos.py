
"""
initial version
"""
def algo1(adj_list : list[list[int]]) -> dict[Coord]:
    # find longest path (from all in-degree 0 nodes)
    # place nodes within longest path as the first relative reference point
    # mark all nodes within the longest path as placed 
    # and therefore no longer exist with the graph
    # Repeat until no more nodes:
    #   Find LP from all in-degree 0 nodes
    #   Get the longest path
    #   place that path between x-displacements of the nodes it starts and ends
    #   wrt to the reference line
    nodeid_to_coord : dict[int, Coord] = {}
    row_list : collections.deque[list[int]] = collections.deque() # to defer y displacements till the end

    while len(nodeid_to_coord) < len(adj_list): # while we haven't placed all nodes
        longest_path : list[int] = solve_longest_path(adj_list, nodeid_to_coord) # index 0 is the root node we need to iterate from?
        assert(len(longest_path) > 0) # we need to add at least one more node
        
        # either root has no parent
        # or root's parent is in placed_nodes
        parents_of_root : list[int] = parents_of(adj_list, longest_path[0])
        assert(all(p in nodeid_to_coord for p in parents_of_root) or len(parents_of_root) == 0)
        # pick one non None parent

        xleft_bound = 0 if len(parents_of_root) == 0 else max([nodeid_to_coord[p].x for p in parents_of_root]) # use the rightmost node as leftbound

        single_row_placement : list[Coord] = place_nodes(longest_path, xleft_bound + 2)
        assert(len(longest_path) == len(single_row_placement))
        for idx in range(len(longest_path)):
            assert(longest_path[idx] not in nodeid_to_coord)
            nodeid_to_coord[longest_path[idx]] = Coord(single_row_placement[idx], 0)
        row_list.append(longest_path)
    
    # now settle y displacements
    y_displacement = 0
    for row in row_list:
        for node in row:
            nodeid_to_coord[node].y = y_displacement
        y_displacement += y_spacing

    return nodeid_to_coord
