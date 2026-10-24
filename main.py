import os
import sys
from typing import Dict, Any, List
from src.graph import RailwayGraph
from src.algorithms import bfs_min_stops, dijkstra_shortest_path

# Try importing 'rich' for styled tables; fallback to clean standard output if not installed
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    RICH_AVAILABLE = True
    console = Console()
except ImportError:
    RICH_AVAILABLE = False


def format_duration(minutes: int) -> str:
    """Converts total minutes into 'Xh Ym' format."""
    hrs = minutes // 60
    mins = minutes % 60
    return f"{hrs}h {mins}m"


def display_stations(graph: RailwayGraph) -> None:
    """Displays all available stations in the railway network."""
    if RICH_AVAILABLE:
        table = Table(title="Indian Railway Network Stations (Vertices)", show_lines=True)
        table.add_column("Station Code", style="bold cyan", justify="center")
        table.add_column("Station Name", style="white")
        table.add_column("City", style="green")
        table.add_column("Direct Connections (Degree)", style="yellow", justify="center")

        for code, info in sorted(graph.stations.items()):
            neighbors = [n["station"] for n in graph.get_neighbors(code)]
            table.add_row(
                code,
                info["name"],
                info["city"],
                f"{len(neighbors)} ({', '.join(neighbors)})"
            )
        console.print(table)
    else:
        print("\n=== INDIAN RAILWAY NETWORK STATIONS ===")
        print(f"{'CODE':<6} | {'STATION NAME':<25} | {'CITY':<12} | CONNECTIONS")
        print("-" * 70)
        for code, info in sorted(graph.stations.items()):
            neighbors = ", ".join(n["station"] for n in graph.get_neighbors(code))
            print(f"{code:<6} | {info['name']:<25} | {info['city']:<12} | {neighbors}")
        print("-" * 70)


def display_single_result(graph: RailwayGraph, result: Dict[str, Any]) -> None:
    """Prints detailed route breakdown and DAA metrics for a single algorithm run."""
    if not result["found"]:
        print("\n[!] No valid route found between the selected stations.")
        return

    route_str = " -> ".join(result["path"])
    full_names_str = " -> ".join(graph.get_station_name(c) for c in result["path"])

    if RICH_AVAILABLE:
        summary = (
            f"[bold cyan]Algorithm:[/bold cyan] {result['algorithm']}\n"
            f"[bold cyan]Optimization Goal:[/bold cyan] {result['criteria']}\n"
            f"[bold green]Optimal Route:[/bold green] {route_str}\n"
            f"[dim]{full_names_str}[/dim]\n\n"
            f"[bold yellow]Route Summary:[/bold yellow]\n"
            f"  • Intermediate Stops : {result['stops']}\n"
            f"  • Total Distance     : {result['total_distance']} km\n"
            f"  • Total Travel Time  : {format_duration(result['total_time'])} ({result['total_time']} mins)\n"
            f"  • Total Ticket Fare  : ₹{result['total_cost']}\n\n"
            f"[bold magenta]DAA Performance Metrics:[/bold magenta]\n"
            f"  • Nodes Visited      : {result['nodes_visited']} / {len(graph.stations)} vertices\n"
            f"  • Execution Time     : {result['execution_time_ms']} ms\n"
            f"  • Time Complexity    : {result['time_complexity']}\n"
            f"  • Space Complexity   : {result['space_complexity']}"
        )
        console.print(Panel(summary, title="Route & Algorithm Analysis", expand=False))

        seg_table = Table(title="Track-by-Track Edge Breakdown", show_lines=True)
        seg_table.add_column("Step", justify="center")
        seg_table.add_column("From Station", style="cyan")
        seg_table.add_column("To Station", style="green")
        seg_table.add_column("Distance (km)", justify="right")
        seg_table.add_column("Time", justify="right")
        seg_table.add_column("Fare (₹)", justify="right")

        for idx, seg in enumerate(result["segments"], start=1):
            seg_table.add_row(
                str(idx),
                graph.get_station_name(seg["from"]),
                graph.get_station_name(seg["to"]),
                f"{seg['distance']} km",
                format_duration(seg["time"]),
                f"₹{seg['cost']}"
            )
        console.print(seg_table)
    else:
        print("\n" + "=" * 65)
        print(f"ALGORITHM         : {result['algorithm']}")
        print(f"OPTIMIZATION GOAL : {result['criteria']}")
        print(f"OPTIMAL ROUTE     : {route_str}")
        print("-" * 65)
        print(f"Intermediate Stops: {result['stops']}")
        print(f"Total Distance    : {result['total_distance']} km")
        print(f"Total Travel Time : {format_duration(result['total_time'])} ({result['total_time']} mins)")
        print(f"Total Ticket Fare : INR {result['total_cost']}")
        print("-" * 65)
        print(f"Nodes Visited     : {result['nodes_visited']} / {len(graph.stations)}")
        print(f"Execution Time    : {result['execution_time_ms']} ms")
        print(f"Time Complexity   : {result['time_complexity']}")
        print(f"Space Complexity  : {result['space_complexity']}")
        print("=" * 65)


def compare_all_algorithms(graph: RailwayGraph, source: str, destination: str) -> None:
    """Runs BFS and all 3 Dijkstra variations side-by-side to compare DAA metrics."""
    results: List[Dict[str, Any]] = [
        bfs_min_stops(graph, source, destination),
        dijkstra_shortest_path(graph, source, destination, criteria="distance"),
        dijkstra_shortest_path(graph, source, destination, criteria="time"),
        dijkstra_shortest_path(graph, source, destination, criteria="cost"),
    ]

    if RICH_AVAILABLE:
        table = Table(
            title=f"DAA Comparative Analysis: {source} to {destination}",
            show_lines=True
        )
        table.add_column("Algorithm & Criteria", style="bold cyan")
        table.add_column("Optimal Path", style="green")
        table.add_column("Stops", justify="center")
        table.add_column("Dist (km)", justify="right")
        table.add_column("Time", justify="right")
        table.add_column("Fare (₹)", justify="right")
        table.add_column("Nodes Visited", justify="center", style="yellow")
        table.add_column("Exec Time (ms)", justify="right", style="magenta")
        table.add_column("Time Complexity", justify="center")

        for res in results:
            table.add_row(
                res["algorithm"],
                " -> ".join(res["path"]),
                str(res["stops"]),
                str(res["total_distance"]),
                format_duration(res["total_time"]),
                f"₹{res['total_cost']}",
                f"{res['nodes_visited']}/{len(graph.stations)}",
                f"{res['execution_time_ms']}",
                res["time_complexity"]
            )
        console.print(table)
    else:
        print(f"\n=== DAA COMPARATIVE BENCHMARK: {source} -> {destination} ===")
        for res in results:
            print(
                f"• {res['algorithm']:<32} | Path: {' -> '.join(res['path']):<26} | "
                f"Dist: {res['total_distance']:>4}km | Time: {format_duration(res['total_time']):>7} | "
                f"Fare: INR {res['total_cost']:>4} | Nodes: {res['nodes_visited']} | "
                f"{res['execution_time_ms']} ms | {res['time_complexity']}"
            )


def prompt_station(graph: RailwayGraph, prompt_text: str) -> str:
    """Prompts and validates a station code from the user."""
    while True:
        code = input(prompt_text).strip().upper()
        if code in graph.stations:
            return code
        print(f"  [!] Invalid station code '{code}'. Valid codes: {', '.join(sorted(graph.stations.keys()))}")


def main() -> None:
    data_path = os.path.join(os.path.dirname(__file__), "data", "stations.json")
    if not os.path.exists(data_path):
        print(f"Error: Could not find dataset at {data_path}")
        sys.exit(1)

    graph = RailwayGraph.load_from_json(data_path)

    while True:
        print("\n" + "=" * 55)
        print("   RAILWAY ROUTE FINDER SYSTEM (DAA MINI PROJECT)")
        print(f"   Loaded Network: {len(graph.stations)} Stations (V), {graph.num_edges} Tracks (E)")
        print("=" * 55)
        print("  1. View All Railway Stations & Network Connections")
        print("  2. Find Route: Minimum Stops (BFS Algorithm)")
        print("  3. Find Route: Shortest Distance (Dijkstra's Algorithm)")
        print("  4. Find Route: Fastest Time / Cheapest Fare (Dijkstra's)")
        print("  5. Compare All Algorithms Side-by-Side (DAA Benchmark)")
        print("  6. Exit")
        print("=" * 55)

        choice = input("Select an option (1-6): ").strip()

        if choice == "1":
            display_stations(graph)

        elif choice == "2":
            src = prompt_station(graph, "Enter Source Station Code (e.g., ST, BRC, ADI): ")
            dst = prompt_station(graph, "Enter Destination Station Code (e.g., NDLS, SC): ")
            res = bfs_min_stops(graph, src, dst)
            display_single_result(graph, res)

        elif choice == "3":
            src = prompt_station(graph, "Enter Source Station Code (e.g., ST, BRC, ADI): ")
            dst = prompt_station(graph, "Enter Destination Station Code (e.g., NDLS, SC): ")
            res = dijkstra_shortest_path(graph, src, dst, criteria="distance")
            display_single_result(graph, res)

        elif choice == "4":
            src = prompt_station(graph, "Enter Source Station Code (e.g., ST, BRC, ADI): ")
            dst = prompt_station(graph, "Enter Destination Station Code (e.g., NDLS, SC): ")
            sub = input("Optimize for (T)ime or (C)ost? [T/C]: ").strip().upper()
            crit = "cost" if sub == "C" else "time"
            res = dijkstra_shortest_path(graph, src, dst, criteria=crit)
            display_single_result(graph, res)

        elif choice == "5":
            src = prompt_station(graph, "Enter Source Station Code (e.g., ST, BRC): ")
            dst = prompt_station(graph, "Enter Destination Station Code (e.g., NDLS, SC): ")
            compare_all_algorithms(graph, src, dst)

        elif choice == "6":
            print("Exiting Railway Route Finder. Good luck with your DAA evaluation!")
            break
        else:
            print("  [!] Please enter a valid option between 1 and 6.")


if __name__ == "__main__":
    main()