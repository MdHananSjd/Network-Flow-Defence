import networkx as nx
from typing import Dict, Any
from backend.core.graph.generator import current_networkx_graph

#function to calculate the minimum number of nodes to remove to disconnect S fromt T

def calculate_min_cut_value(source_id: str, target_id: str) -> Dict[str, Any]:
    G = current_networkx_graph
    if G is None:
        return {
            'min_cut_value': 0,
            "status": "Graph not found"
        }
    try:
        min_cut_value = nx.node_connectivity(G, source_id, target_id)
    except Exception as e:
        return {
            "min_cut_value": 0,
            "status": f"Error when calculating the cut: {e}"
        }
    return {
        "min_cut_value": min_cut_value,
        "status": "Ready for ML Integration"
    }
