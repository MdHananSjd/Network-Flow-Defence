import networkx as nx
from typing import Dict, Any
from backend.core.state import current_networkx_graph #safe import from state

def calculate_min_cut_value(source_id: str, target_id: str) -> Dict[str, Any]:
    """Calculates the minimum nodes to remove to disconnect S from T."""
    
    G = current_networkx_graph
    
    if G is None:
        return {"min_cut_value": 0, "status": "Graph not loaded."}
        
    try:
        min_cut_value = nx.node_connectivity(G, source_id, target_id) 
    except Exception as e:
        return {"min_cut_value": 0, "status": f"Error calculating cut: {e}"}

    return {
        "min_cut_value": min_cut_value,
        "status": "Ready for ML integration."
    }