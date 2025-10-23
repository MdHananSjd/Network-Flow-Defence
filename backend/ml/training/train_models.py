"""
ML Backend Training Pipeline for Network Flow Defense
======================================================
This script trains Random Forest and Gradient Boosting models to predict
critical nodes in network graphs for infection spread prevention.

Run this script ONCE to generate model files (.pkl) for deployment.

Author: ML Backend Team
Date: October 2025
"""

# =====================================
# IMPORTS
# =====================================

import networkx as nx
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (classification_report, confusion_matrix, 
                             accuracy_score, precision_score, recall_score, f1_score)
import pickle
import json
import warnings
warnings.filterwarnings('ignore')

print("="*70)
print("ML BACKEND TRAINING PIPELINE - NETWORK FLOW DEFENSE")
print("="*70)
print("\n✓ All libraries imported successfully!\n")

# =====================================
# STEP 1: FEATURE EXTRACTION FUNCTION
# =====================================

def extract_node_features(G, source, target):
    """
    Extract comprehensive node features from a graph.
    
    Parameters:
    -----------
    G : networkx.Graph
        The input graph
    source : int
        Source node (Patient Zero)
    target : int
        Target node (Critical Patient)
    
    Returns:
    --------
    pd.DataFrame : Features for all nodes
    """
    
    features = pd.DataFrame(index=sorted(G.nodes()))
    
    # 1. Degree Centrality (normalized by max possible degree)
    degree_cent = nx.degree_centrality(G)
    features['degree_centrality'] = [degree_cent[node] for node in features.index]
    
    # 2. Betweenness Centrality (how often node appears on shortest paths)
    betweenness_cent = nx.betweenness_centrality(G)
    features['betweenness_centrality'] = [betweenness_cent[node] for node in features.index]
    
    # 3. Closeness Centrality (how close to all other nodes)
    closeness_cent = nx.closeness_centrality(G)
    features['closeness_centrality'] = [closeness_cent[node] for node in features.index]
    
    # 4. Distance from Source (BFS-based)
    try:
        dist_from_source = nx.single_source_shortest_path_length(G, source)
        features['dist_from_source'] = [dist_from_source.get(node, 999) for node in features.index]
    except:
        features['dist_from_source'] = 999
    
    # 5. Distance to Target (BFS-based)
    try:
        dist_to_target = nx.single_source_shortest_path_length(G, target)
        features['dist_to_target'] = [dist_to_target.get(node, 999) for node in features.index]
    except:
        features['dist_to_target'] = 999
    
    # 6. Is on Shortest Path (Binary feature)
    try:
        all_shortest_paths = list(nx.all_shortest_paths(G, source, target))
        nodes_on_shortest_path = set()
        for path in all_shortest_paths:
            nodes_on_shortest_path.update(path)
        features['on_shortest_path'] = [1 if node in nodes_on_shortest_path else 0 for node in features.index]
    except:
        features['on_shortest_path'] = 0
    
    # 7. Raw Degree (number of connections)
    features['raw_degree'] = [G.degree(node) for node in features.index]
    
    # 8. Clustering Coefficient (how connected are neighbors)
    clustering = nx.clustering(G)
    features['clustering_coefficient'] = [clustering[node] for node in features.index]
    
    return features

print("✓ STEP 1: Feature extraction function created")


# =====================================
# STEP 2: LABELING FUNCTION (MIN-CUT)
# =====================================

def label_critical_nodes(G, source, target):
    """
    Label critical nodes using minimum node cut algorithm.
    
    Parameters:
    -----------
    G : networkx.Graph
        The input graph
    source : int
        Source node (Patient Zero)
    target : int
        Target node (Critical Patient)
    
    Returns:
    --------
    dict : Dictionary mapping node to label (1=critical, 0=non-critical)
    """
    
    try:
        # Find minimum node cut (nodes that if removed disconnect source from target)
        min_cut_nodes = nx.minimum_node_cut(G, source, target)
        
        # Also include nodes on all shortest paths as potentially critical
        try:
            all_shortest_paths = list(nx.all_shortest_paths(G, source, target))
            nodes_on_all_paths = set(all_shortest_paths[0])
            for path in all_shortest_paths[1:]:
                nodes_on_all_paths &= set(path)
            # Remove source and target from critical set
            nodes_on_all_paths.discard(source)
            nodes_on_all_paths.discard(target)
        except:
            nodes_on_all_paths = set()
        
        # Combine both approaches
        critical_nodes = min_cut_nodes | nodes_on_all_paths
        
        # Create labels dictionary
        labels = {}
        for node in G.nodes():
            if node == source or node == target:
                labels[node] = -1  # Special label for source/target (exclude from training)
            elif node in critical_nodes:
                labels[node] = 1  # Critical node
            else:
                labels[node] = 0  # Non-critical node
        
        return labels
    
    except Exception as e:
        # If min-cut fails, use betweenness as fallback
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

print("✓ STEP 2: Labeling function created")


# =====================================
# STEP 3: GRAPH GENERATION (FOR TESTING)
# =====================================

def generate_training_graph(n_nodes=25, edge_prob=0.2, seed=None):
    """
    Generate a random connected graph for training.
    
    Parameters:
    -----------
    n_nodes : int
        Number of nodes
    edge_prob : float
        Probability of edge creation
    seed : int
        Random seed for reproducibility
    
    Returns:
    --------
    tuple : (Graph, source, target)
    """
    
    if seed:
        np.random.seed(seed)
    
    # Generate random graph
    G = nx.erdos_renyi_graph(n_nodes, edge_prob, seed=seed)
    
    # Ensure connectivity
    if not nx.is_connected(G):
        # Add edges to make it connected
        components = list(nx.connected_components(G))
        for i in range(len(components) - 1):
            node1 = list(components[i])[0]
            node2 = list(components[i+1])[0]
            G.add_edge(node1, node2)
    
    # Select source and target (far apart)
    nodes = list(G.nodes())
    source = np.random.choice(nodes)
    
    # Find node farthest from source
    distances = nx.single_source_shortest_path_length(G, source)
    target = max(distances.items(), key=lambda x: x[1])[0]
    
    return G, source, target

print("✓ STEP 3: Graph generation function created")


# =====================================
# STEP 4: TEST FEATURE EXTRACTION & LABELING
# =====================================

print("\n" + "="*70)
print("STEP 4: Testing feature extraction and labeling on sample graph")
print("="*70)

test_G, test_source, test_target = generate_training_graph(n_nodes=20, seed=42)
print(f"\nTest graph: {test_G.number_of_nodes()} nodes, {test_G.number_of_edges()} edges")
print(f"Source: {test_source}, Target: {test_target}")

# Extract features
test_features = extract_node_features(test_G, test_source, test_target)
print(f"\n✓ Features extracted! Shape: {test_features.shape}")
print("\nFirst 5 rows:")
print(test_features.head())

# Generate labels
test_labels = label_critical_nodes(test_G, test_source, test_target)
labels_series = pd.Series(test_labels)
print(f"\n✓ Labels generated!")
print(f"\nLabel distribution:")
print(labels_series.value_counts())
print("  -1: Source/Target (excluded)")
print("   0: Non-critical nodes")
print("   1: Critical nodes")


# =====================================
# STEP 5: GENERATE TRAINING DATASET
# =====================================

def generate_training_dataset(n_graphs=500, n_nodes_range=(20, 30), edge_prob=0.2):
    """
    Generate multiple graphs and extract features + labels for training.
    
    Parameters:
    -----------
    n_graphs : int
        Number of graphs to generate
    n_nodes_range : tuple
        Range of nodes (min, max)
    edge_prob : float
        Edge probability
    
    Returns:
    --------
    tuple : (X_train, y_train, metadata)
    """
    
    all_features = []
    all_labels = []
    metadata = []
    
    print(f"\nGenerating {n_graphs} training graphs...")
    
    for i in range(n_graphs):
        if (i + 1) % 100 == 0:
            print(f"  Progress: {i + 1}/{n_graphs} graphs...")
        
        # Random number of nodes
        n_nodes = np.random.randint(n_nodes_range[0], n_nodes_range[1] + 1)
        
        # Generate graph
        G, source, target = generate_training_graph(n_nodes=n_nodes, edge_prob=edge_prob, seed=i)
        
        # Extract features
        features = extract_node_features(G, source, target)
        
        # Generate labels
        labels = label_critical_nodes(G, source, target)
        
        # Add to dataset (exclude source and target nodes)
        for node in G.nodes():
            if labels[node] != -1:  # Exclude source/target
                all_features.append(features.loc[node].values)
                all_labels.append(labels[node])
                metadata.append({
                    'graph_id': i,
                    'node_id': node,
                    'source': source,
                    'target': target,
                    'n_nodes': n_nodes
                })
    
    X = np.array(all_features)
    y = np.array(all_labels)
    
    print(f"\n✓ Dataset generation complete!")
    print(f"  Total samples: {len(y)}")
    print(f"  Feature dimensions: {X.shape[1]}")
    print(f"  Class distribution: Non-critical={np.sum(y == 0)}, Critical={np.sum(y == 1)}")
    
    return X, y, metadata

print("\n" + "="*70)
print("STEP 5: Generating training dataset (300 graphs)")
print("="*70)

X_train_full, y_train_full, metadata = generate_training_dataset(n_graphs=300, n_nodes_range=(20, 25))


# =====================================
# STEP 6: TRAIN-TEST SPLIT
# =====================================

print("\n" + "="*70)
print("STEP 6: Splitting data into train and test sets")
print("="*70)

X_train, X_test, y_train, y_test = train_test_split(
    X_train_full, y_train_full, 
    test_size=0.2, 
    random_state=42,
    stratify=y_train_full
)

print(f"\nTraining set: {len(y_train)} samples")
print(f"  Critical: {np.sum(y_train == 1)} ({np.sum(y_train == 1)/len(y_train)*100:.1f}%)")
print(f"  Non-critical: {np.sum(y_train == 0)} ({np.sum(y_train == 0)/len(y_train)*100:.1f}%)")

print(f"\nTest set: {len(y_test)} samples")
print(f"  Critical: {np.sum(y_test == 1)} ({np.sum(y_test == 1)/len(y_test)*100:.1f}%)")
print(f"  Non-critical: {np.sum(y_test == 0)} ({np.sum(y_test == 0)/len(y_test)*100:.1f}%)")


# =====================================
# STEP 7: TRAIN RANDOM FOREST MODEL
# =====================================

print("\n" + "="*70)
print("STEP 7: Training Random Forest model")
print("="*70)

rf_model = RandomForestClassifier(
    n_estimators=100,
    max_depth=10,
    min_samples_split=10,
    min_samples_leaf=5,
    class_weight='balanced',
    random_state=42,
    n_jobs=-1
)

print("\nTraining in progress...")
rf_model.fit(X_train, y_train)

y_pred_rf = rf_model.predict(X_test)
y_pred_proba_rf = rf_model.predict_proba(X_test)[:, 1]

print("\n✓ Random Forest Training Complete!\n")
print("RANDOM FOREST PERFORMANCE:")
print(f"  Accuracy:  {accuracy_score(y_test, y_pred_rf):.4f}")
print(f"  Precision: {precision_score(y_test, y_pred_rf):.4f}")
print(f"  Recall:    {recall_score(y_test, y_pred_rf):.4f}")
print(f"  F1-Score:  {f1_score(y_test, y_pred_rf):.4f}")


# =====================================
# STEP 8: TRAIN GRADIENT BOOSTING MODEL
# =====================================

print("\n" + "="*70)
print("STEP 8: Training Gradient Boosting model")
print("="*70)

gb_model = GradientBoostingClassifier(
    n_estimators=100,
    learning_rate=0.1,
    max_depth=5,
    min_samples_split=10,
    min_samples_leaf=5,
    subsample=0.8,
    random_state=42
)

print("\nTraining in progress...")
gb_model.fit(X_train, y_train)

y_pred_gb = gb_model.predict(X_test)
y_pred_proba_gb = gb_model.predict_proba(X_test)[:, 1]

print("\n✓ Gradient Boosting Training Complete!\n")
print("GRADIENT BOOSTING PERFORMANCE:")
print(f"  Accuracy:  {accuracy_score(y_test, y_pred_gb):.4f}")
print(f"  Precision: {precision_score(y_test, y_pred_gb):.4f}")
print(f"  Recall:    {recall_score(y_test, y_pred_gb):.4f}")
print(f"  F1-Score:  {f1_score(y_test, y_pred_gb):.4f}")


# =====================================
# STEP 9: HYBRID ENSEMBLE MODEL
# =====================================

print("\n" + "="*70)
print("STEP 9: Creating Hybrid Ensemble (RF 40% + GB 60%)")
print("="*70)

weight_rf = 0.4
weight_gb = 0.6

y_pred_proba_ensemble = weight_rf * y_pred_proba_rf + weight_gb * y_pred_proba_gb
y_pred_ensemble = (y_pred_proba_ensemble >= 0.5).astype(int)

print("\n✓ Hybrid Ensemble Complete!\n")
print("HYBRID ENSEMBLE PERFORMANCE:")
print(f"  Accuracy:  {accuracy_score(y_test, y_pred_ensemble):.4f}")
print(f"  Precision: {precision_score(y_test, y_pred_ensemble):.4f}")
print(f"  Recall:    {recall_score(y_test, y_pred_ensemble):.4f}")
print(f"  F1-Score:  {f1_score(y_test, y_pred_ensemble):.4f}")


# =====================================
# STEP 10: MODEL COMPARISON
# =====================================

print("\n" + "="*70)
print("STEP 10: Model Comparison")
print("="*70)

comparison_df = pd.DataFrame({
    'Model': ['Random Forest', 'Gradient Boosting', 'Hybrid Ensemble'],
    'Accuracy': [
        accuracy_score(y_test, y_pred_rf),
        accuracy_score(y_test, y_pred_gb),
        accuracy_score(y_test, y_pred_ensemble)
    ],
    'Precision': [
        precision_score(y_test, y_pred_rf),
        precision_score(y_test, y_pred_gb),
        precision_score(y_test, y_pred_ensemble)
    ],
    'Recall': [
        recall_score(y_test, y_pred_rf),
        recall_score(y_test, y_pred_gb),
        recall_score(y_test, y_pred_ensemble)
    ],
    'F1-Score': [
        f1_score(y_test, y_pred_rf),
        f1_score(y_test, y_pred_gb),
        f1_score(y_test, y_pred_ensemble)
    ]
})

print("\n" + comparison_df.to_string(index=False))
print("\nRECOMMENDATION: Hybrid Ensemble provides best balance of precision and recall")


# =====================================
# STEP 11: FEATURE IMPORTANCE ANALYSIS
# =====================================

print("\n" + "="*70)
print("STEP 11: Feature Importance Analysis")
print("="*70)

feature_names = [
    'degree_centrality',
    'betweenness_centrality',
    'closeness_centrality',
    'dist_from_source',
    'dist_to_target',
    'on_shortest_path',
    'raw_degree',
    'clustering_coefficient'
]

rf_importance = rf_model.feature_importances_
rf_importance_df = pd.DataFrame({
    'Feature': feature_names,
    'RF_Importance': rf_importance
}).sort_values('RF_Importance', ascending=False)

print("\nRandom Forest Feature Importance:")
print(rf_importance_df.to_string(index=False))

gb_importance = gb_model.feature_importances_
gb_importance_df = pd.DataFrame({
    'Feature': feature_names,
    'GB_Importance': gb_importance
}).sort_values('GB_Importance', ascending=False)

print("\nGradient Boosting Feature Importance:")
print(gb_importance_df.to_string(index=False))


# =====================================
# STEP 12: CREATE PREDICTION FUNCTION
# =====================================

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
        'rf', 'gb', or 'hybrid'
    
    Returns:
    --------
    list : List of tuples (node_id, criticality_score) sorted by score
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

print("\n✓ STEP 12: Prediction function created")


# =====================================
# STEP 13: TEST PREDICTION FUNCTION
# =====================================

print("\n" + "="*70)
print("STEP 13: Testing prediction function on new graph")
print("="*70)

test_graph, test_src, test_tgt = generate_training_graph(n_nodes=25, seed=999)
print(f"\nTest graph: {test_graph.number_of_nodes()} nodes, {test_graph.number_of_edges()} edges")
print(f"Source: {test_src}, Target: {test_tgt}")

top_5_predictions = predict_critical_nodes(test_graph, test_src, test_tgt, top_k=5, model_type='hybrid')

print("\nTop 5 Predicted Critical Nodes:")
for rank, (node, score) in enumerate(top_5_predictions, 1):
    print(f"  {rank}. Node {node}: Score = {score:.4f}")

# Compare with actual min-cut
actual_labels = label_critical_nodes(test_graph, test_src, test_tgt)
actual_critical = [node for node, label in actual_labels.items() if label == 1]

print(f"\nActual critical nodes (min-cut): {actual_critical}")

predicted_nodes = [node for node, _ in top_5_predictions]
matches = set(predicted_nodes) & set(actual_critical)
print(f"\n✓ Correctly identified {len(matches)} out of {len(actual_critical)} critical nodes")
if matches:
    print(f"  Matched nodes: {matches}")


# =====================================
# STEP 14: SAVE MODELS
# =====================================

print("\n" + "="*70)
print("STEP 14: Saving trained models")
print("="*70)

# Save Random Forest
with open('random_forest_model.pkl', 'wb') as f:
    pickle.dump(rf_model, f)
print("\n✓ Saved: random_forest_model.pkl")

# Save Gradient Boosting
with open('gradient_boosting_model.pkl', 'wb') as f:
    pickle.dump(gb_model, f)
print("✓ Saved: gradient_boosting_model.pkl")

# Save feature names and model info
feature_info = {
    'feature_names': feature_names,
    'feature_order': feature_names,
    'n_features': len(feature_names),
    'model_info': {
        'rf_accuracy': float(accuracy_score(y_test, y_pred_rf)),
        'gb_accuracy': float(accuracy_score(y_test, y_pred_gb)),
        'hybrid_accuracy': float(accuracy_score(y_test, y_pred_ensemble)),
        'hybrid_f1': float(f1_score(y_test, y_pred_ensemble)),
        'training_samples': len(y_train),
        'test_samples': len(y_test)
    },
    'hybrid_weights': {
        'rf_weight': 0.4,
        'gb_weight': 0.6
    }
}

with open('model_info.json', 'w') as f:
    json.dump(feature_info, f, indent=2)
print("✓ Saved: model_info.json")

print("\n" + "="*70)
print("🎉 TRAINING PIPELINE COMPLETE!")
print("="*70)
print("\nGenerated files:")
print("  1. random_forest_model.pkl")
print("  2. gradient_boosting_model.pkl")
print("  3. model_info.json")
print("\nNext step: Use ml_backend.py for inference/integration with backend team")
print("="*70)
