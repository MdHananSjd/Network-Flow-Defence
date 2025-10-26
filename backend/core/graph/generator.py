import networkx as nx
import random
from shared.schemas.graph_schema import FullGraph, NodeData, EdgeData 
from backend.core.state import current_networkx_graph 

def generate_new_game_graph(num_nodes: int = 20):
    """Generates a random connected graph, selects S/T, and computes features."""
    global current_networkx_graph # points to the object in state.py
    
    G = None
    while G is None or not nx.is_connected(G):
        G = nx.fast_gnp_random_graph(n=num_nodes, p=0.2, seed=random.randint(1, 1000))
        
    G = nx.relabel_nodes(G, {i: str(i) for i in range(num_nodes)})
    current_networkx_graph = G # Write the new object to global state
    
    nodes_list = list(G.nodes)
    source_id, target_id = random.sample(nodes_list, 2) 
    degree_map = nx.degree_centrality(G)
    betweenness_map = nx.betweenness_centrality(G)
    # Compute clean layout positions to declutter frontend
    # Using spring layout provides aesthetically pleasing spacing
    pos = nx.spring_layout(G, seed=random.randint(1, 1000), k=None)
    
    node_data_list = []
    for node_id in nodes_list:
        x, y = pos.get(node_id, (0.0, 0.0))
        node_data_list.append(NodeData(
            id=node_id,
            label=f"P{node_id}",
            degree_centrality=degree_map.get(node_id, 0.0),
            betweenness_centrality=betweenness_map.get(node_id, 0.0),
            is_source=(node_id == source_id),
            is_target=(node_id == target_id),
            pos_x=float(x),
            pos_y=float(y)
        ))
        
    edge_data_list = [EdgeData(source=u, target=v) for u, v in G.edges]
    
    pydantic_graph = FullGraph(
        nodes=node_data_list,
        edges=edge_data_list,
        metadata={
            "source_id": source_id,
            "target_id": target_id,
            "tokens_left": 3,
            "status": "Defence_Phase"
        }
    )
    
    return pydantic_graph, G