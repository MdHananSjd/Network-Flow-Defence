import networkx as nx
from typing import Generator, Set, List, Dict, Any

from backend.core.state import current_networkx_graph # SAFE IMPORT
from backend.core.state import current_fastapi_game_state # SAFE IMPORT

def run_bfs_simulation(firewall_ids: Set[str]) -> Generator[Dict[str, Any], None, None]:
    """Runs the BFS simulation, yielding newly infected nodes at each step."""
    
    G = current_networkx_graph
    
    if G is None or current_fastapi_game_state is None:
        return

    # Extract necessary data from the global state
    try:
        state_meta = current_fastapi_game_state.metadata
        source_id = state_meta['source_id']
        target_id = state_meta['target_id']
    except (AttributeError, KeyError):
        return 

    # BFS initialization
    infected_queue = [source_id]
    infected_set = {source_id}
    step = 0
    target_hit = False

    while infected_queue and not target_hit:
        step += 1
        newly_infected_in_step = []
        next_queue = []

        for node_id in infected_queue:
            
            for neighbor_id in G.neighbors(node_id):
                
                # Check 1: Not already infected AND 2: Not a firewall
                if neighbor_id not in infected_set and neighbor_id not in firewall_ids:
                    
                    newly_infected_in_step.append(neighbor_id)
                    infected_set.add(neighbor_id)
                    next_queue.append(neighbor_id)
                    
                    if neighbor_id == target_id:
                        target_hit = True
                        break
            
            if target_hit:
                break

        if newly_infected_in_step:
            yield {
                "step": step, 
                "infected_nodes": newly_infected_in_step, 
                "is_target_hit": target_hit
            }
        
        if target_hit or not newly_infected_in_step:
            break

        infected_queue = next_queue