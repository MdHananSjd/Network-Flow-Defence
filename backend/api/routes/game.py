#Heres where all the game APIs will live

# backend/api/routes/game.py

import asyncio
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from shared.schemas.graph_schema import FullGraph
from backend.core.graph.generator import generate_new_game_graph

# --- Import your new logic files ---
from backend.core.infection.simulator import bfs_infection_simulator
from backend.core.scoring.scorer import (
    get_ai_prediction, 
    run_full_simulation, 
    _prepare_simulation_data
)

# Global state that you (gohul) will read and modify
current_fastapi_game_state: FullGraph = None 

router = APIRouter(tags=["Game"])

# --- hanan's ENDPOINT (Leave this unchanged) ---
@router.get("/api/graph/new", response_model=FullGraph)
async def get_new_game():
    """Generates a new graph and returns the initial game state."""
    global current_fastapi_game_state
    
    new_graph = generate_new_game_graph()
    current_fastapi_game_state = new_graph # Store the mutable state
    return new_graph

# --- gohul's ENDPOINTS (Replace placeholders with this) -----  

@router.post("/api/defense/{node_id}", response_model=FullGraph)
async def place_firewall_token(node_id: str):
    """
    (Gohul's logic)
    Places a firewall on a node if tokens are available.
    """
    global current_fastapi_game_state
    if not current_fastapi_game_state:
        raise HTTPException(status_code=404, detail="No active game. Create a new graph first.")

    # Safely get and convert tokens
    tokens_raw = current_fastapi_game_state.metadata.get("tokens_left", 0)
    try:
        tokens = int(tokens_raw)
    except ValueError:
        tokens = 0
    
    if tokens <= 0:
        raise HTTPException(status_code=400, detail="No defense tokens left.")

    node_found = False
    for node in current_fastapi_game_state.nodes:
        if node.id == node_id:
            if node.is_source or node.is_target:
                raise HTTPException(status_code=400, detail="Cannot place firewall on source or target.")
            if not node.is_firewall:
                node.is_firewall = True
                current_fastapi_game_state.metadata["tokens_left"] = str(tokens - 1) # Store as string
            node_found = True
            break
            
    if not node_found:
        raise HTTPException(status_code=404, detail="Node not found.")
        
    return current_fastapi_game_state

@router.websocket("/ws/simulate")
async def websocket_simulation(websocket: WebSocket):
    """
    (Gohul's logic)
    Handles real-time simulation stream.
    """
    global current_fastapi_game_state
    await websocket.accept()
    
    if not current_fastapi_game_state:
        await websocket.send_json({"status": "error", "message": "No active game."})
        await websocket.close()
        return

    start_node = str(current_fastapi_game_state.metadata["source_id"])
    
    # Use the helper function to prepare data for the simulation
    adj_list, firewalls = _prepare_simulation_data(current_fastapi_game_state)
    current_fastapi_game_state.metadata["status"] = "Simulation_Phase"

    try:
        gen = bfs_infection_simulator(adj_list, start_node, firewalls)
        for step, infected_wave in enumerate(gen):
            await websocket.send_json({
                "step": step,
                "newly_infected": list(infected_wave)
            })
            await asyncio.sleep(0.75) # Pause for animation
        
        await websocket.send_json({"status": "complete"})

    except WebSocketDisconnect:
        print("Client disconnected.")
    except Exception as e:
        print(f"Simulation error: {e}")
        await websocket.send_json({"status": "error", "message": str(e)})
    finally:
        current_fastapi_game_state.metadata["status"] = "Scoring_Phase"
        print("WebSocket closed.")

@router.get("/api/score/final")
async def get_final_score():
    """
    (Gohul's logic)
    Handles final scoring integration.
    """
    global current_fastapi_game_state
    if not current_fastapi_game_state or current_fastapi_game_state.metadata["status"] != "Scoring_Phase":
        raise HTTPException(status_code=400, detail="Game not in scoring phase.")

    start_node = str(current_fastapi_game_state.metadata["source_id"])
    total_nodes = len(current_fastapi_game_state.nodes)

    # 1. Calculate User's Score
    user_infected_count = run_full_simulation(current_fastapi_game_state, start_node, custom_firewalls=None)
    user_nodes_saved = total_nodes - user_infected_count

    # 2. Calculate AI's Score
    ai_firewalls = get_ai_prediction(current_fastapi_game_state)
    ai_infected_count = run_full_simulation(current_fastapi_game_state, start_node, custom_firewalls=ai_firewalls)
    ai_nodes_saved = total_nodes - ai_infected_count

    return {
        "results": {
            "user": {
                "nodes_saved": user_nodes_saved,
                "nodes_infected": user_infected_count
            },
            "ai": {
                "firewalls_placed": list(ai_firewalls),
                "nodes_saved": ai_nodes_saved,
                "nodes_infected": ai_infected_count
            }
        },
        "total_nodes_in_graph": total_nodes
    }
