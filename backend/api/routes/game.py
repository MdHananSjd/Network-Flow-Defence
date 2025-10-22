from fastapi import APIRouter, HTTPException, WebSocket
from shared.schemas.graph_schema import FullGraph
from backend.core.graph.generator import generate_new_game_graph

# Global state that gohul has to read and modify
current_fastapi_game_state: FullGraph = None 

router = APIRouter(tags=["Game"])

# --- hanan's ENDPOINT ---
@router.get("/api/graph/new", response_model=FullGraph)
async def get_new_game():
    """Generates a new graph and returns the initial game state."""
    global current_fastapi_game_state
    
    new_graph = generate_new_game_graph()
    current_fastapi_game_state = new_graph # Store the mutable state
    return new_graph

# --- gohul's ENDPOINTS ---

@router.post("/defense/{node_id}", response_model=FullGraph)
async def place_firewall_token(node_id: str):
    """Placeholder for gohul: Handles user defense actions."""
    raise HTTPException(status_code=501, detail="Defense logic not yet implemented (Developer B's task).")

@router.websocket("/ws/simulate")
async def websocket_simulation(websocket: WebSocket):
    """Placeholder for gohul: Handles real-time simulation stream."""
    await websocket.accept()
    await websocket.close() 

@router.get("/score/final")
async def get_final_score():
    """Placeholder for gohul: Handles final scoring integration."""
    raise HTTPException(status_code=501, detail="Scoring logic not yet implemented (Developer B's task).")

