# backend/core/infection/simulator.py

from collections import deque

def bfs_infection_simulator(graph: dict, start_node: str, firewalls: set):
    """
    A generator that simulates infection spread using BFS, yielding each step.

    Args:
        graph (dict): The network graph as an adjacency list.
        start_node (str): The node where the infection begins.
        firewalls (set): A set of nodes that block the infection.

    Yields:
        set: The set of newly infected nodes at each step of the simulation.
    """
    if start_node in firewalls:
        return

    queue = deque([start_node])
    infected = {start_node}

    yield {start_node}

    while queue:
        nodes_in_current_wave = len(queue)
        newly_infected_this_wave = set()

        for _ in range(nodes_in_current_wave):
            current_node = queue.popleft()
            for neighbor in graph.get(current_node, []):
                if neighbor not in infected and neighbor not in firewalls:
                    infected.add(neighbor)
                    newly_infected_this_wave.add(neighbor)
                    queue.append(neighbor)
        
        if newly_infected_this_wave:
            yield newly_infected_this_wave