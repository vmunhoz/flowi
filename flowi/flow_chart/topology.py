from collections import defaultdict


# Class to represent a graph
class Topology(object):
    def __init__(self, nodes: list):
        self.graph: defaultdict = defaultdict(list)  # dictionary containing adjacency List
        self.nodes: list = nodes

    def add_edge(self, node_from, node_to):
        self.graph[node_from].append(node_to)

    def _topological_sort_util(self, node, visited, stack):
        visited[node] = True

        for i in self.graph[node]:
            if not visited[i]:
                self._topological_sort_util(i, visited, stack)

        stack.insert(0, node)

    def topological_sort(self) -> list:
        visited = {node: False for node in self.nodes}
        stack = []

        for node in self.nodes:
            if not visited[node]:
                self._topological_sort_util(node, visited, stack)

        return stack
