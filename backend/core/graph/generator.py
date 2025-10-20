#Heres where the graph generation code is gonna go
import networkx as nx
import random
from shared.schemas.graph_schema import FullGraph, NodeData, EdgeData

current_networkx_graph: nx.Graph = None

def generate_new_game_graph(num_nodes: int = 20) -> FullGraph: #returns a FullGraph method
    
    global current_networkx_graph

    #Generate and prepare graph
    G = None
    while G is None or not nx.is_connected(G):
        G = nx.fast_gnp_random_graph(n = num_nodes, p = 0.2, seed=random.randint(1, 1000))
    
    G = nx.relabel_nodes(G, {i:str(i) for i in range(num_nodes)})
    current_networkx_graph = G #we're storing the raw graph object here

    #Select source and target and compute features
    nodes_list = list(G.nodes)
    source_id, target_id = random.sample(nodes_list, 2)
    degree_map = nx.degree_centrality(G)
    betweenness_map = nx.betweenness_centrality(G)

    #building pydantic response
    node_data_list = []
    for node_id in nodes_list:
        node_data_list.append(NodeData(
            id = node_id,
            label=f"P{node_id}",
            degree_centrality=degree_map.get(node_id, 0.0),
            betweenness_centrality=betweenness_map.get(node_id, 0.0),
            is_source=(node_id == source_id),
            is_target=(node_id == target_id)
        ))

    edge_data_list = [EdgeData(source=u, target=v) for u, v in G.edges]

    return FullGraph(
        nodes = node_data_list,
        edges= edge_data_list,
        metadata={
            "source_id": source_id,
            "target_id": target_id,
            "tokens_left": 3,
            "status": "Defence_Phase"
        }
    )