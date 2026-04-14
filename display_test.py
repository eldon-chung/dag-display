import json
import collections
import matplotlib.pyplot as plt
from collections import defaultdict, deque
# going to take g as an adjacency list?

x_spacing = 2 # 2 units of spacing?
y_spacing = 2 # 2 units of spacing?


class Coord:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __hash__(self):
        return hash((self.x, self.y))
    
    def __eq__(self, value):
        return self.x == value.x and self.y == value.y

    def __repr__(self):
        return F"<{self.x}, {self.y}>"

class Placement:
    def __init__(self, num_nodes):
        self.num_nodes = num_nodes
        self.nodeid_to_coord : dict[int, Coord] = dict()
        self.coord_to_nodeid : dict[Coord, int] = dict()
        pass

    def __getitem__(self, nodeid : int):
        return self.nodeid_to_coord[nodeid]

    def __setitem__(self, nodeid : int, coord : Coord):
        self.nodeid_to_coord[nodeid] = coord

        if coord in self.coord_to_nodeid.keys():
            del self.coord_to_nodeid[coord]
        self.coord_to_nodeid[coord] = nodeid
    
    def at_coord(self, coord : Coord) -> int | None:
        return self.coord_to_nodeid[coord] if coord in self.coord_to_nodeid else None

    def into_placement(nodeid_to_coord : dict[int, Coord]):
        assert(all(i in nodeid_to_coord for i in range(len(nodeid_to_coord))))
        placement = Placement(len(nodeid_to_coord))
        for i in range(len(nodeid_to_coord)):
            placement[i] = nodeid_to_coord[i]
        return placement
    
    def values(self) -> list[Coord]:
        return self.nodeid_to_coord.values()

# slow for now but whatever
def parents_of(adj_list : list[list[int]], node : int) -> list[int]:
    parent_list = []
    for p in range(len(adj_list)):
        if node in adj_list[p]:
            parent_list.append(p)
    return parent_list

def solve_longest_path(adj_list, deadends) -> list[int]:
    class SolnPair:
        def __init__(self, child, length):
            self.child = child
            self.length = length


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

    # try to remember all the x placements so that we can stack them on top of each other later
    x_to_node_list : dict[int, list[int]] = defaultdict(list)

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
            x_to_node_list[single_row_placement[idx]].append(longest_path[idx])

        row_list.append(longest_path)
    
    # now settle y displacements;
    for stack in x_to_node_list.values():
        y_disp = 0
        for nodeid in stack:
            nodeid_to_coord[nodeid].y = y_disp
            y_disp += 2

    return nodeid_to_coord

def place_all_sources_left(adj_list : list[list[int]], placement : dict[Coord]):
    for node_idx in range(len(adj_list)):
        if len(parents_of(adj_list, node_idx)) == 0: # is a source
            placement[node_idx].x = 0


def nudge_colinear_lines(adj_list : list[list[int]], placement : dict[Coord]):

    # hey isn't this 3SUM?
    def is_colinear(a : int, b : int, c : int, placement : dict[Coord]) -> bool:
        return (placement[a].y - placement[b].y)(placement[a].y - placement[c].y) == (placement[a].x - placement[c].x)(placement[a].y - placement[b].y)

    
    for from_node in range(len(adj_list)):
        for to_node in adj_list[from_node]:
            for middle_node in range(len(adj_list)):
                if is_colinear(from_node, to_node, middle_node, placement):
                    pass # some nudging needed?

def display(nodeid_to_coord : Placement, adj_list : list[list[int]]):

    square_list = [plt.Rectangle((coord.x, coord.y), 1, 1) for coord in nodeid_to_coord.values() ]
    for square in square_list:
        plt.gca().add_patch(square)

    for from_idx in range(len(adj_list)):
        for to_idx in adj_list[from_idx]:
            plt.arrow(nodeid_to_coord[from_idx].x + 0.5, nodeid_to_coord[from_idx].y + 0.5, nodeid_to_coord[to_idx].x - nodeid_to_coord[from_idx].x, nodeid_to_coord[to_idx].y - nodeid_to_coord[from_idx].y, head_width=0.2)

    plt.axis('scaled')
    plt.show()

if __name__ == "__main__":
    with open("graph2.json", "r") as f:
        data = json.load(f)

    print(data)
    # print()
    initial_placement = Placement.into_placement(algo1(data))
    place_all_sources_left(data, initial_placement)
    display(initial_placement, data)


