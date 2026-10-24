import heapq
import time
from collections import deque
from typing import Dict, List, Any, Optional
from src.graph import RailwayGraph


def reconstruct_path(
    graph: RailwayGraph,
    parent: Dict[str, Optional[str]],
    source: str,
    destination: str
) -> Dict[str, Any]:
    """
    Backtracks from destination to source using the parent dictionary
    and calculates total distance, travel time, and ticket cost.
    Time Complexity: O(V) in the worst case.
    """
    path: List[str] = []
    curr: Optional[str] = destination

    while curr is not None:
        path.append(curr)
        curr = parent.get(curr)

    path.reverse()

    if not path or path[0] != source:
        return {
            "found": False,
            "path": [],
            "stops": 0,
            "total_distance": 0,
            "total_time": 0,
            "total_cost": 0,
            "segments": []
        }

    total_distance = 0
    total_time = 0
    total_cost = 0
    segments = []

    for i in range(len(path) - 1):
        u, v = path[i], path[i + 1]
        for neighbor in graph.get_neighbors(u):
            if neighbor["station"] == v:
                total_distance += neighbor["distance"]
                total_time += neighbor["time"]
                total_cost += neighbor["cost"]
                segments.append({
                    "from": u,
                    "to": v,
                    "distance": neighbor["distance"],
                    "time": neighbor["time"],
                    "cost": neighbor["cost"]
                })
                break

    return {
        "found": True,
        "path": path,
        "stops": max(0, len(path) - 2),  # Intermediate stations excluding source & dest
        "total_distance": total_distance,
        "total_time": total_time,
        "total_cost": total_cost,
        "segments": segments
    }


def bfs_min_stops(
    graph: RailwayGraph,
    source: str,
    destination: str
) -> Dict[str, Any]:
    """
    Breadth-First Search (BFS) to find the route with the MINIMUM INTERMEDIATE STOPS.
    Paradigm: Level-Order Graph Traversal (Unweighted shortest path)
    Time Complexity: O(V + E)
    Space Complexity: O(V)
    """
    source, destination = source.upper(), destination.upper()
    start_time = time.perf_counter()

    visited = {source}
    queue = deque([source])
    parent: Dict[str, Optional[str]] = {source: None}
    nodes_visited = 0

    while queue:
        current = queue.popleft()
        nodes_visited += 1

        if current == destination:
            break

        for neighbor in graph.get_neighbors(current):
            next_station = neighbor["station"]
            if next_station not in visited:
                visited.add(next_station)
                parent[next_station] = current
                queue.append(next_station)

    exec_time_ms = (time.perf_counter() - start_time) * 1000
    result = reconstruct_path(graph, parent, source, destination)

    result.update({
        "algorithm": "Breadth-First Search (BFS)",
        "criteria": "Minimum Stops",
        "nodes_visited": nodes_visited,
        "execution_time_ms": round(exec_time_ms, 4),
        "time_complexity": "O(V + E)",
        "space_complexity": "O(V)"
    })
    return result


def dijkstra_shortest_path(
    graph: RailwayGraph,
    source: str,
    destination: str,
    criteria: str = "distance"
) -> Dict[str, Any]:
    """
    Dijkstra's Algorithm using a Min-Heap (Priority Queue) to find the optimal route
    based on 'distance' (km), 'time' (mins), or 'cost' (INR).
    Paradigm: Greedy Approach
    Time Complexity: O((V + E) log V)
    Space Complexity: O(V)
    """
    if criteria not in ("distance", "time", "cost"):
        raise ValueError("Criteria must be 'distance', 'time', or 'cost'.")

    source, destination = source.upper(), destination.upper()
    start_time = time.perf_counter()

    # Initialize distances to infinity for all stations
    min_weight: Dict[str, float] = {station: float("inf") for station in graph.stations}
    min_weight[source] = 0.0

    parent: Dict[str, Optional[str]] = {source: None}
    # Priority Queue stores tuples of: (accumulated_weight, station_code)
    pq = [(0, source)]
    visited = set()
    nodes_visited = 0

    while pq:
        current_weight, current_station = heapq.heappop(pq)

        if current_station in visited:
            continue

        visited.add(current_station)
        nodes_visited += 1

        # Early exit optimization once destination is settled
        if current_station == destination:
            break

        # Edge Relaxation step
        for neighbor in graph.get_neighbors(current_station):
            next_station = neighbor["station"]
            edge_weight = neighbor[criteria]

            if next_station not in visited:
                new_weight = current_weight + edge_weight
                if new_weight < min_weight[next_station]:
                    min_weight[next_station] = new_weight
                    parent[next_station] = current_station
                    heapq.heappush(pq, (new_weight, next_station))

    exec_time_ms = (time.perf_counter() - start_time) * 1000
    result = reconstruct_path(graph, parent, source, destination)

    criteria_labels = {
        "distance": "Shortest Distance (km)",
        "time": "Fastest Travel Time (mins)",
        "cost": "Cheapest Ticket Fare (INR)"
    }

    result.update({
        "algorithm": f"Dijkstra's Algorithm ({criteria.capitalize()})",
        "criteria": criteria_labels[criteria],
        "nodes_visited": nodes_visited,
        "execution_time_ms": round(exec_time_ms, 4),
        "time_complexity": "O((V + E) log V)",
        "space_complexity": "O(V)"
    })
    return result