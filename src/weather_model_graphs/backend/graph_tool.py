"""
Is a very hastily generated (with github co-pilot) wrapper around graph_tool's
Graph class to make it behave like a networkx DiGraph.

NB: This doesn't currently work, but demonstrates the concept
"""
from graph_tool.all import Graph

class GraphToolDiGraph:
    def __init__(self):
        self.graph = Graph(directed=True)
        self.node_map = {}

    def add_node(self, node, **attr):
        if node not in self.node_map:
            v = self.graph.add_vertex()
            self.node_map[node] = v
            for key, value in attr.items():
                self.graph.vp[key] = self.graph.new_vertex_property("object")
                self.graph.vp[key][v] = value

    def add_edge(self, u, v, **attr):
        if u not in self.node_map:
            self.add_node(u)
        if v not in self.node_map:
            self.add_node(v)
        edge = self.graph.add_edge(self.node_map[u], self.node_map[v])
        for key, value in attr.items():
            self.graph.ep[key] = self.graph.new_edge_property("object")
            self.graph.ep[key][edge] = value

    def nodes(self):
        return list(self.node_map.keys())

    def edges(self):
        return [(u, v) for u, v in self.graph.edges()]

    def neighbors(self, node):
        if node in self.node_map:
            return [self.graph.vertex_index[v] for v in self.node_map[node].out_neighbors()]
        return []

    def degree(self, node):
        if node in self.node_map:
            return self.node_map[node].out_degree()
        return 0

    def __getitem__(self, node):
        if node in self.node_map:
            return self.node_map[node]
        raise KeyError(f"Node {node} not found in graph")

    def __contains__(self, node):
        return node in self.node_map

    def __len__(self):
        return len(self.node_map)

    def __iter__(self):
        return iter(self.node_map.keys())