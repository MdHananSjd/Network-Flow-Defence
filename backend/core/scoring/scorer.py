

# backend/core/scoring/scorer.py

import joblib
from shared.schemas.graph_schema import FullGraph
from backend.core.infection.simulator import bfs_infection_simulator

def _prepare_simulation_data(graph_data: FullGraph) -> tuple:
    """
    Converts a FullGraph object into a simple adjacency list and a set of firewalls.
    This is a preprocessing step to make the BFS run efficiently.
    """
    adjacency_list = {node.id: [] for node in graph_data.nodes}
    firewalls = set()
    
    for edge in graph_data.edges:
        adjacency_list[edge.source].append(edge.target)
        adjacency_list[edge.target].append(edge.source) # Assuming undirected spread

    for node in graph_data.nodes:
        if node.is_firewall:
            firewalls.add(node.id)
            
    return adjacency_list, firewalls

def get_ai_prediction(graph_data: FullGraph) -> set:
    """
    Loads the trained ML model and uses it to predict critical nodes.
    It reads the pre-calculated features from Developer A.
    """
    try:
        model = joblib.load("backend/ml/models/trained_model.pkl")
        
        # Prepare features (reading pre-calculated data from Dev A)
        node_order = [node.id for node in graph_data.nodes]
        features = [
            [node.degree_centrality, node.betweenness_centrality] 
            for node in graph_data.nodes
        ]

        predictions = model.predict(features)
        ai_firewalls = {node_order[i] for i, pred in enumerate(predictions) if pred == 1}
        
        print(f"AI prediction successful. Defending: {ai_firewalls}")
        return ai_firewalls
    except FileNotFoundError:
        print("Model file not found. Falling back to mock prediction.")
        fallback_node = next(n.id for n in graph_data.nodes if not n.is_source and not n.is_target)
        return {fallback_node}
    except Exception as e:
        print(f"An error occurred during AI prediction: {e}")
        fallback_node = next(n.id for n in graph_data.nodes if not n.is_source and not n.is_target)
        return {fallback_node}

def run_full_simulation(graph_data: FullGraph, start_node: str, custom_firewalls: set = None) -> int:
    """
    Runs the BFS simulator to completion and returns the total number of infected nodes.
    """
    adj_list, firewalls_from_graph = _prepare_simulation_data(graph_data)
    
    # Use custom firewalls if provided (for AI sim), else use the graph's state (for user sim)
    firewalls_to_use = custom_firewalls if custom_firewalls is not None else firewalls_from_graph
    
    total_infected = set()
    simulation_generator = bfs_infection_simulator(adj_list, start_node, firewalls_to_use)
    for infected_wave in simulation_generator:
        total_infected.update(infected_wave)
    return len(total_infected)
