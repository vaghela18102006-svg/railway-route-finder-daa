import json
from typing import Dict, List, Any


class RailwayGraph:
    """
    Represents the Railway Network as an Undirected Weighted Graph
    using an Adjacency List data structure.
    Space Complexity: O(V + E) where V = Stations, E = Railway Tracks.
    """

    def __init__(self) -> None:
        # Dictionary mapping station_code -> {name, city}
        self.stations: Dict[str, Dict[str, str]] = {}
        # Adjacency List: station_code -> list of neighbor dicts
        self.adj_list: Dict[str, List[Dict[str, Any]]] = {}
        self.num_edges: int = 0

    def add_station(self, code: str, name: str, city: str) -> None:
        """Adds a vertex (station) to the graph in O(1) time."""
        code = code.upper()
        if code not in self.stations:
            self.stations[code] = {"name": name, "city": city}
            self.adj_list[code] = []

    def add_route(self, u: str, v: str, distance: int, time: int, cost: int) -> None:
        """
        Adds an undirected weighted edge (track) between station u and station v
        in O(1) time.
        """
        u, v = u.upper(), v.upper()
        if u not in self.adj_list or v not in self.adj_list:
            raise ValueError(f"Station {u} or {v} does not exist in the graph.")

        # Undirected graph: add edge in both directions
        self.adj_list[u].append({
            "station": v,
            "distance": distance,
            "time": time,
            "cost": cost
        })
        self.adj_list[v].append({
            "station": u,
            "distance": distance,
            "time": time,
            "cost": cost
        })
        self.num_edges += 1

    def get_neighbors(self, code: str) -> List[Dict[str, Any]]:
        """Returns all adjacent stations and edge weights in O(1) lookup time."""
        return self.adj_list.get(code.upper(), [])

    def get_station_name(self, code: str) -> str:
        """Helper to format 'CODE (Station Name)'."""
        code = code.upper()
        if code in self.stations:
            return f"{self.stations[code]['name']} ({code})"
        return code

    @classmethod
    def load_from_json(cls, filepath: str) -> "RailwayGraph":
        """Loads vertices and edges from a JSON file in O(V + E) time."""
        graph = cls()
        with open(filepath, "r", encoding="utf-8") as file:
            data = json.load(file)

        for code, info in data.get("stations", {}).items():
            graph.add_station(code, info["name"], info["city"])

        for route in data.get("routes", []):
            graph.add_route(
                route["from"],
                route["to"],
                route["distance"],
                route["time"],
                route["cost"]
            )
        return graph