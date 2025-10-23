from ml_backend import predict_critical_nodes
import networkx as nx

# Create a test graph
G = nx.gnm_random_graph(25, 40, seed=123)
source = 0
target = 15

# Get predictions
predictions = predict_critical_nodes(G, source, target, top_k=5, model_type='hybrid')

print("Top 5 Critical Nodes to Block:")
for rank, (node, score) in enumerate(predictions, 1):
    print(f"  {rank}. Node {node}: Criticality Score = {score:.4f}")
