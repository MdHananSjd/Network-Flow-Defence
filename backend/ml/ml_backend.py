"""
ML Backend Integration Module for Network Flow Defense
======================================================
This module provides the complete ML backend for predicting critical nodes.

Usage:
------
from ml_backend import predict_critical_nodes, extract_node_features, label_critical_nodes

# For new graph prediction:
predictions = predict_critical_nodes(G, source, target, top_k=5)

# For training data generation:
features = extract_node_features(G, source, target)
labels = label_critical_nodes(G, source, target)
"""

import networkx as nx
import numpy as np
import pandas as pd
import pickle
import warnings
import os
warnings.filterwarnings('ignore')

# Load trained models


# Get the directory where this file is located
current_dir = os.path.dirname(__file__)

# Load models from the models folder
with open(os.path.join(current_dir, 'models', 'random_forest_model.pkl'), 'rb') as f:
    rf_model = pickle.load(f)

with open(os.path.join(current_dir, 'models', 'gradient_boosting_model.pkl'), 'rb') as f:
    gb_model = pickle.load(f)


print("✓ ML Backend models loaded successfully!")

def extract_node_features(G, source, target):
    """Extract comprehensive node features from a graph."""
    features = pd.DataFrame(index=sorted(G.nodes()))
    
    # Centrality measures
    degree_cent = nx.degree_centrality(G)
    features['degree_centrality'] = [degree_cent[node] for node in features.index]
    
    betweenness_cent = nx.betweenness_centrality(G)
    features['betweenness_centrality'] = [betweenness_cent[node] for node in features.index]
    
    closeness_cent = nx.closeness_centrality(G)
    features['closeness_centrality'] = [closeness_cent[node] for node in features.index]
    
    # Distance features
    try:
        dist_from_source = nx.single_source_shortest_path_length(G, source)
        features['dist_from_source'] = [dist_from_source.get(node, 999) for node in features.index]
    except:
        features['dist_from_source'] = 999
    
    try:
        dist_to_target = nx.single_source_shortest_path_length(G, target)
        features['dist_to_target'] = [dist_to_target.get(node, 999) for node in features.index]
    except:
        features['dist_to_target'] = 999
    
    # Shortest path feature
    try:
        all_shortest_paths = list(nx.all_shortest_paths(G, source, target))
        nodes_on_shortest_path = set()
        for path in all_shortest_paths:
            nodes_on_shortest_path.update(path)
        features['on_shortest_path'] = [1 if node in nodes_on_shortest_path else 0 for node in features.index]
    except:
        features['on_shortest_path'] = 0
    
    # Additional features
    features['raw_degree'] = [G.degree(node) for node in features.index]
    
    clustering = nx.clustering(G)
    features['clustering_coefficient'] = [clustering[node] for node in features.index]
    
    return features

def label_critical_nodes(G, source, target):
    """Label critical nodes using minimum node cut algorithm."""
    try:
        min_cut_nodes = nx.minimum_node_cut(G, source, target)
        
        try:
            all_shortest_paths = list(nx.all_shortest_paths(G, source, target))
            nodes_on_all_paths = set(all_shortest_paths[0])
            for path in all_shortest_paths[1:]:
                nodes_on_all_paths &= set(path)
            nodes_on_all_paths.discard(source)
            nodes_on_all_paths.discard(target)
        except:
            nodes_on_all_paths = set()
        
        critical_nodes = min_cut_nodes | nodes_on_all_paths
        
        labels = {}
        for node in G.nodes():
            if node == source or node == target:
                labels[node] = -1
            elif node in critical_nodes:
                labels[node] = 1
            else:
                labels[node] = 0
        
        return labels
    
    except Exception as e:
        betweenness = nx.betweenness_centrality(G)
        threshold = np.percentile(list(betweenness.values()), 80)
        
        labels = {}
        for node in G.nodes():
            if node == source or node == target:
                labels[node] = -1
            elif betweenness[node] >= threshold:
                labels[node] = 1
            else:
                labels[node] = 0
        
        return labels

def predict_critical_nodes(G, source, target, top_k=None, model_type='hybrid'):
    """
    Predict critical nodes for a given graph.
    
    Parameters:
    -----------
    G : networkx.Graph
        Input graph
    source : int
        Source node (Patient Zero)
    target : int
        Target node (Critical Patient)
    top_k : int, optional
        Number of top critical nodes to return
    model_type : str
        'rf', 'gb', or 'hybrid' (default)
    
    Returns:
    --------
    list : List of tuples (node_id, criticality_score)
    """
    features = extract_node_features(G, source, target)
    X = features.values
    
    if model_type == 'rf':
        proba = rf_model.predict_proba(X)[:, 1]
    elif model_type == 'gb':
        proba = gb_model.predict_proba(X)[:, 1]
    else:  # hybrid
        proba_rf = rf_model.predict_proba(X)[:, 1]
        proba_gb = gb_model.predict_proba(X)[:, 1]
        proba = 0.4 * proba_rf + 0.6 * proba_gb
    
    results = []
    for i, node in enumerate(features.index):
        if node != source and node != target:
            results.append((node, float(proba[i])))
    
    results.sort(key=lambda x: x[1], reverse=True)
    
    if top_k:
        return results[:top_k]
    return results

# Example usage when run as main script
if __name__ == "__main__":
    # Create a test graph
    G = nx.gnm_random_graph(20, 35, seed=42)
    source, target = 0, 10
    
    # Get predictions
    top_nodes = predict_critical_nodes(G, source, target, top_k=5)
    
    print("\n" + "="*60)
    print("TEST: Top 5 Critical Nodes")
    print("="*60)
    for rank, (node, score) in enumerate(top_nodes, 1):
        print(f"{rank}. Node {node}: {score:.4f}")
    print("="*60)
