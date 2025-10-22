from shared.schemas.graph_schema import FullGraph
import networkx as nx

# Global state for the Pydantic model
current_fastapi_game_state: FullGraph = None 

# Global state for the raw NetworkX object
current_networkx_graph: nx.Graph = None