#Data contract
#we'll have the pydantic model for data here 

from pydantic import BaseModel, Field
from typing import List, Dict, Union

class NodeData(BaseModel):
    id: str = Field(..., description="Unique ID")
    label:str
    degree_centrality: float = 0.0
    betweenness_centrality: float = 0.0
    is_source: bool = False
    is_target: bool = False
    is_firewall: bool = False

class EdgeData(BaseModel):
    source: str
    target: str

class FullGraph(BaseModel):
    nodes: List[NodeData]
    edges: List[EdgeData]
    metadata: Dict[str, Union[int, str]] = Field(..., description="Game State (tokens, S/T IDs).")