import json
import collections
import matplotlib.pyplot as plt
# going to take g as an adjacency list?

x_spacing = 2 # 2 units of spacing?
y_spacing = 2 # 2 units of spacing?


class Coord:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __repr__(self):
        return F"<{self.x}, {self.y}>"

class SolnPair:
    def __init__(self, child, length):
        self.child = child
        self.length = length

# slow for now but whatever
def parents_of(adj_list : list[list[int]], node : int) -> list[int]:
    parent_list = []
    for p in range(len(adj_list)):
        if node in adj_list[p]:
            parent_list.append(p)
    return parent_list

def solve_longest_path(adj_list, deadends) -> list[int]:
    def helper(adj_list : list[list[int]], deadends, curr_node : int, soln : dict[int, SolnPair]) -> int:
        
        if curr_node in soln:
            return soln[curr_node].length
        
        soln_child = None
        max_so_far = 0
        for neighbour in adj_list[curr_node]:
            if neighbour in deadends:
                continue # skip the deadends
            neighbour_length = helper(adj_list, deadends, neighbour, soln) + 1
            if neighbour_length > max_so_far:
                soln_child = neighbour
                max_so_far = neighbour_length

        soln[curr_node] = SolnPair(soln_child, max_so_far)
        return max_so_far

    # try all in-degree 0 nodes
    soln_table : dict[int, SolnPair] = dict()
    for node_idx in range(len(adj_list)):
        if node_idx in deadends:
            continue # skip the deadends
        helper(adj_list, deadends, node_idx, soln_table)
    # now find the the key that has max SolnPair
    max_root : int = max(soln_table, key=lambda s : soln_table[s].length)
    # now solution recovery
    longest_path = []
    curr_node : int = max_root
    while curr_node != None:
        longest_path.append(curr_node)
        curr_node = soln_table[curr_node].child
    return longest_path

def place_nodes(longest_path, xleft_bound):
    # something simple for now
    single_row_placement = [xleft_bound + x_spacing * i for i in range(len(longest_path))]
    return single_row_placement

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

def display(nodeid_to_coord : dict[int, Coord], adj_list : list[list[int]]):
    print(nodeid_to_coord)

    for coord in nodeid_to_coord.values():
        print(coord)
    
    square_list = [plt.Rectangle((coord.x, coord.y), 1, 1) for coord in nodeid_to_coord.values() ]
    for square in square_list:
        plt.gca().add_patch(square)

    for from_idx in range(len(adj_list)):
        for to_idx in adj_list[from_idx]:
            plt.arrow(nodeid_to_coord[from_idx].x + 0.5, nodeid_to_coord[from_idx].y + 0.5, nodeid_to_coord[to_idx].x - nodeid_to_coord[from_idx].x, nodeid_to_coord[to_idx].y - nodeid_to_coord[from_idx].y, head_width=0.2)

    plt.axis('scaled')
    plt.show()

if __name__ == "__main__":
    with open("graph1.json", "r") as f:
        data = json.load(f)

    print(data)
    # print()
    display(algo1(data), data)


