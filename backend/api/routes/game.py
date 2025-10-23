from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from shared.schemas.graph_schema import FullGraph 
from backend.core.graph.generator import generate_new_game_graph # Hanan
from backend.core.scoring.scorer import calculate_min_cut_value # Hanan
from backend.core.infection.simulator import run_bfs_simulation # Gohul
from backend.core.state import current_fastapi_game_state # SAFE IMPORT
from backend.ml.ml_backend import predict_critical_nodes
from backend.core.state import current_networkx_graph


router = APIRouter(tags=["Game"])

# --- PRIMARY ENDPOINT (Hanan) ---
@router.get("/graph/new", response_model=FullGraph)
async def get_new_game():
    """Generates a new graph, stores state, and returns the initial game."""
    global current_fastapi_game_state
    
    new_graph = generate_new_game_graph()
    current_fastapi_game_state = new_graph # Store the mutable state
    return new_graph

# --- STATE MUTATION (Gohul) ---
@router.post("/defense/{node_id}", response_model=FullGraph)
async def place_firewall_token(node_id: str):
    """Handles user defense actions, marking the node as a firewall, consuming a token."""
    global current_fastapi_game_state
    
    if not current_fastapi_game_state:
        raise HTTPException(status_code=400, detail="No active game found.")
        
    tokens_left = current_fastapi_game_state.metadata.get('tokens_left', 0)
    if tokens_left <= 0:
        raise HTTPException(status_code=403, detail="No defense tokens left.")

    found_node = False
    for node in current_fastapi_game_state.nodes:
        if node.id == node_id:
            if node.is_firewall:
                raise HTTPException(status_code=400, detail="Node already defended.")
                
            # Mutate State
            node.is_firewall = True
            current_fastapi_game_state.metadata['tokens_left'] = tokens_left - 1
            found_node = True
            break
            
    if not found_node:
        raise HTTPException(status_code=404, detail=f"Node ID {node_id} not found.")
    
    return current_fastapi_game_state 

# --- WEB SOCKET SIMULATION (Gohul) ---
@router.websocket("/ws/simulate")
async def websocket_simulation(websocket: WebSocket):
    """Handles the real-time, step-by-step animation of the infection spread."""
    await websocket.accept()
    
    if current_fastapi_game_state is None:
        await websocket.send_json({"status": "ERROR", "message": "Game not initialized."})
        await websocket.close()
        return

    # Extract necessary data for simulation
    firewall_ids = {n.id for n in current_fastapi_game_state.nodes if n.is_firewall}
    
    try:
        await websocket.receive_text() # Wait for the client to send the START signal
        
        target_hit = False
        
        # Consume the simulation generator step-by-step
        for step_data in run_bfs_simulation(firewall_ids):
            await websocket.send_json(step_data)
            if step_data.get("is_target_hit"):
                target_hit = True
                break
        
        # Send final result
        result = "FAILURE" if target_hit else "SUCCESS"
        await websocket.send_json({"status": "Simulation_Complete", "result": result})
            
    except WebSocketDisconnect:
        print("Client disconnected during simulation.")
    except Exception as e:
        print(f"Simulation Error: {e}")
    finally:
        await websocket.close()

# --- FINAL SCORE ENDPOINT (Gohul, calling Hanan's logic) ---
@router.get("/score/final")
async def get_final_score():
    """Calculates final score metrics based on user defense vs. Min-Cut."""
    
    if not current_fastapi_game_state:
        raise HTTPException(status_code=400, detail="Game not initialized.")
        
    source_id = current_fastapi_game_state.metadata['source_id']
    target_id = current_fastapi_game_state.metadata['target_id']

    # Get Min-Cut Benchmark (Hanan's logic)
    min_cut_data = calculate_min_cut_value(source_id, target_id)
    min_cut_value = min_cut_data.get('min_cut_value', 0)
    
    # Get User Metrics
    tokens_left = current_fastapi_game_state.metadata.get('tokens_left', 3)
    tokens_used = 3 - tokens_left
    
    # Final Payload
    final_payload = {
        "user_tokens_used": tokens_used,
        "optimal_tokens_required": min_cut_value,
        "efficiency_score": 100 * (min_cut_value / max(1, tokens_used)), 
        "status": "Scoring Complete",
        "ml_critical_nodes": ml_critical_ids,           # NEW - ML suggestions
        "ml_alignment_score": ml_alignment_score        # NEW - How well user matched ML
    }
    # --- ML INTEGRATION START ---
try:
    # Get the graph that's already stored in NetworkX format
    G = current_networkx_graph
    source = current_fastapi_game_state.metadata['source_id']
    target = current_fastapi_game_state.metadata['target_id']
    
    # Get ML predictions for top 5 most critical nodes
    ml_predictions = predict_critical_nodes(G, source, target, top_k=5)
    ml_critical_ids = [node for node, score in ml_predictions]
    
    # Calculate how well user's choices matched ML suggestions
    user_firewall_ids = {n.id for n in current_fastapi_game_state.nodes if n.is_firewall}
    matches = len(set(ml_critical_ids) & user_firewall_ids)
    ml_alignment_score = round(100 * matches / max(1, len(ml_critical_ids)), 2)
    
except Exception as e:
    # If something goes wrong, still return a response
    ml_critical_ids = []
    ml_alignment_score = 0
    print(f"ML prediction error: {e}")
# --- ML INTEGRATION END ---

    return final_payload
