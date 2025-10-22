import pandas as pd
import networkx as nx
import random
import os
import sys

# Everything u might need to change has been comented with "VERIFY" u can use find to find them.

# To the other person who will see this code there are dummy functions if u want to test it individually
# change this variable below to switch from test to final mode.

# VERIFY
final = True # <---- THIS ONE

if final:
    # MAKE SURE THE PATH AND FUNCTION NAMES ARE CORRECT OR ELSE IT WILL BREAK (obviously)
    # RECHECK THIS BEFORE RUNNING

    script_dir = os.path.dirname(__file__) # VERIFY
    backend_dir = os.path.abspath(os.path.join(script_dir, '..', '..')) # VERIFY
    sys.path.append(backend_dir) # VERIFY

    from core.graph.generation import create_game_graph # VERIFY
    from ml.features.extraction import extract_graph_features # VERIFY
    from ml.training.labeling import get_critical_nodes # VERIFY


def dummy_generate_graph():
    """
    Generates a simple random graph.
    """
    G = nx.erdos_renyi_graph(n=random.randint(20, 25), p=0.15)
    
    if not nx.is_connected(G):
        components = list(nx.connected_components(G))

        if len(components) > 1:

            for i in range(len(components) - 1):
                node1 = random.choice(list(components[i]))
                node2 = random.choice(list(components[i+1]))
                G.add_edge(node1, node2)
                
    nodes = list(G.nodes())
    source = random.choice(nodes)
    target = random.choice([n for n in nodes if n != source])
    
    G.graph['source'] = source
    G.graph['target'] = target
    
    return G

def dummy_get_features(G):
    """
    Placeholder for Harshit's feature extraction function
    Generates fake feature data for each node.
    The real function should be in: backend/ml/features/ as said in the project structure
    WILL NOT WORK IF THE PATH IS DIFFRENT
    """
    node_features = {}
    for node in G.nodes():
        node_features[node] = {
            'degree_centrality': random.random(),
            'betweenness_centrality': random.random(),
            'closeness_centrality': random.random(),
            'is_source': 1 if node == G.graph['source'] else 0,
            'is_target': 1 if node == G.graph['target'] else 0
        }
    return node_features

def dummy_get_labels(G):
    """
    Placeholder for Harshit's labeling function
    Generates fake labels (critical(1) or not-critical(0)) for each node.
    """
    node_labels = {}
    for node in G.nodes():
        # just creats a random 0 or 1 label for now
        node_labels[node] = {
            'is_critical': random.choice([0, 1]) 
        }
    return node_labels

# Data Pipeline Script
# Most of the stuff above is for testing purpose and will not affect the main code
def generate_training_data(num_graphs=500):
    """
    Generates many graphs.
    For each graph, gets features and labels for all nodes.
    Combines all data into one big list.
    Converts to a DataFrame and saves as a CSV.
    """
    print(f"Starting data generation for {num_graphs} graphs...")
    
    all_nodes_data = [] # all node data from all graphs

    for i in range(num_graphs):
        if not final:
            graph = dummy_generate_graph()
            features_dict = dummy_get_features(graph)
            labels_dict = dummy_get_labels(graph)
        else:
            graph = create_game_graph() # VERIFY
            features_dict = extract_graph_features(graph) # VERIFY
            labels_dict = get_critical_nodes(graph) # VERIFY
        
        # data merging
        for node in graph.nodes():
            node_data = {
                'graph_id': i,
                'node_id': node
            }
            node_data.update(features_dict[node])
            node_data.update(labels_dict[node])
            
            all_nodes_data.append(node_data)
            
        if (i + 1) % 50 == 0: # print every 50 for nice loding screen effect :)
            print(f"Processed graph... {i + 1}/{num_graphs}")

    print("All graphs processed. Converting to DataFrame...")
    
    df = pd.DataFrame(all_nodes_data)
    
    if final:
        output_dir = os.path.join(backend_dir, 'data')
    else:
        # In test mode, just goes up two folders from this script's location
        script_dir = os.path.dirname(__file__)
        output_dir = os.path.abspath(os.path.join(script_dir, '..', '..', 'data'))
    
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'training_dataset.csv')
    
    # VERIFY
    df.to_csv(output_path, index=False) #Location is based on the project structure
    
    print("Dataset Training Complete")
    print(f"Training dataset saved to: {output_path}")
    print(f"Nodes processed: {len(df)}")
    print("\nSample data:")
    print(df.head())


if __name__ == "__main__":
    # VERIFY
    n = 10 # Run with a small number to test ex 10 increase as requiered
    if final:
        print(f"Analysis with {n} graphs")
    else:
        print(f"Testing with {n} graphs")
    generate_training_data(num_graphs=n)