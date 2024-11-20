import networkx as nx
from .graph_tool import GraphToolDiGraph

DEFAULT_DIGRAPH_CLASS = nx.DiGraph
DiGraph = DEFAULT_DIGRAPH_CLASS


class GraphToolBackendContextManager:
    def __enter__(self):
        global DiGraph
        DiGraph = GraphToolDiGraph

    def __exit__(self, exc_type, exc_value, traceback):
        global DiGraph
        DiGraph = DEFAULT_DIGRAPH_CLASS
        
def use_graph_tool_backend():
    return GraphToolBackendContextManager()
    
def relabel_nodes(G, mapping, copy=True):
    if copy:
        H = G.__class__()
        H.add_nodes_from((mapping.get(n, n), d.copy()) for n, d in G.nodes(data=True))
        H.add_edges_from((mapping.get(u, u), mapping.get(v, v), d.copy()) for u, v, d in G.edges(data=True))
        H.graph.update(G.graph)
        return H
    else:
        for n in list(G.nodes):
            if n in mapping:
                nx.relabel.relabel_nodes(G, {n: mapping[n]}, copy=False)
        return G

def compose(G1, G2):
    H = G1.__class__()
    H.add_nodes_from(G1.nodes(data=True))
    H.add_nodes_from(G2.nodes(data=True))
    H.add_edges_from(G1.edges(data=True))
    H.add_edges_from(G2.edges(data=True))
    H.graph.update(G1.graph)
    H.graph.update(G2.graph)
    return H

def grid_2d_graph(m, n):
    G = DiGraph()
    for i in range(m):
        for j in range(n):
            G.add_node((i, j))
            if i > 0:
                G.add_edge((i-1, j), (i, j))
                G.add_edge((i, j), (i-1, j))
            if j > 0:
                G.add_edge((i, j-1), (i, j))
                G.add_edge((i, j), (i, j-1))
    return G

def is_empty(G):
    return len(G.edges()) == 0

def compose_all(graphs):
    if not graphs:
        return GraphToolDiGraph()
    H = list(graphs)[0].__class__()
    for G in graphs:
        H.add_nodes_from(G.nodes(data=True))
        H.add_edges_from(G.edges(data=True))
    return H