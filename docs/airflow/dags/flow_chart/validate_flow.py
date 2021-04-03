from collections import defaultdict


class ValidateFlow(object):
    def __init__(self, nodes):
        self.graph = defaultdict(list)
        self.nodes = nodes

    def add_edge(self, from_node, to_node):
        self.graph[from_node].append(to_node)

    def is_cyclic_util(self, v, visited, rec_stack):

        # Mark current node as visited and
        # adds to recursion stack
        visited[v] = True
        rec_stack[v] = True

        # Recur for all neighbours
        # if any neighbour is visited and in
        # recStack then graph is cyclic
        for neighbour in self.graph[v]:
            if not visited[neighbour]:
                if self.is_cyclic_util(neighbour, visited, rec_stack):
                    return True
            elif rec_stack[neighbour]:
                return True

        # The node needs to be poped from
        # recursion stack before function ends
        rec_stack[v] = False
        return False

    # Returns true if graph is cyclic else false
    def is_cyclic(self):
        visited = {node: False for node in self.nodes}
        rec_stack = {node: False for node in self.nodes}
        for node in self.nodes:
            if not visited[node]:
                if self.is_cyclic_util(node, visited, rec_stack):
                    return True
        return False
