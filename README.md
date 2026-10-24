# 🚆 Railway Route Finder System — DAA Mini Project

A graph-based **Railway Route Optimization System** built in Python for the **Design and Analysis of Algorithms (DAA)** course. This project models an Indian Railway network as an **Undirected Weighted Graph** and compares **Breadth-First Search (BFS)** and **Dijkstra's Greedy Algorithm** across multiple optimization criteria: **Minimum Stops**, **Shortest Distance (km)**, **Fastest Travel Time**, and **Cheapest Ticket Fare (₹)**.

---

## 📌 1. Problem Formulation (Graph Theory)

The railway network is represented mathematically as an undirected weighted graph $G = (V, E)$:
* **Vertices ($V$):** Railway Junctions / Stations (12 major Indian junctions including `BRC`, `ADI`, `ST`, `MMCT`, `NDLS`, etc.).
* **Edges ($E$):** Direct bi-directional railway tracks connecting pairs of stations (18 tracks).
* **Edge Weights ($w(u, v)$):** A multi-attribute weight vector for each track:
  * $w_{\text{dist}}(u, v)$: Distance in kilometers (km)
  * $w_{\text{time}}(u, v)$: Travel duration in minutes
  * $w_{\text{cost}}(u, v)$: Ticket fare in INR (₹)

### Why Adjacency List over Adjacency Matrix?
Real-world railway networks are **sparse graphs** ($E \ll V^2$), because each station only connects directly to a few neighboring junctions.
* **Adjacency Matrix Space Complexity:** $O(V^2)$ — wastes memory storing `0` or `∞` for non-existent tracks.
* **Adjacency List Space Complexity (Used Here):** $O(V + E)$ — optimal memory utilization and $O(\text{degree}(u))$ neighbor traversal.

---

## ⚙️ 2. Algorithms Implemented & Complexity Analysis

| Algorithm | Design Paradigm | Optimization Objective | Data Structure Used | Time Complexity | Space Complexity |
| :--- | :--- | :--- | :--- | :---: | :---: |
| **Breadth-First Search (BFS)** | Level-Order Traversal | Minimum Intermediate Stops (Unweighted) | FIFO Queue (`collections.deque`) | $O(V + E)$ | $O(V)$ |
| **Dijkstra's Algorithm (Distance)** | Greedy Approach | Shortest Total Distance (km) | Min-Heap Priority Queue (`heapq`) | $O((V + E) \log V)$ | $O(V)$ |
| **Dijkstra's Algorithm (Time)** | Greedy Approach | Fastest Total Travel Time (mins) | Min-Heap Priority Queue (`heapq`) | $O((V + E) \log V)$ | $O(V)$ |
| **Dijkstra's Algorithm (Cost)** | Greedy Approach | Cheapest Total Ticket Fare (₹) | Min-Heap Priority Queue (`heapq`) | $O((V + E) \log V)$ | $O(V)$ |

### Edge Relaxation Formula (Dijkstra's Algorithm)
For every adjacent station $v$ of the currently extracted station $u$:
$$\text{if } d[u] + w(u, v) < d[v] \implies d[v] = d[u] + w(u, v)$$

---

## 📊 3. DAA Comparative Benchmark (Sample Case: Surat `ST` $\rightarrow$ New Delhi `NDLS`)

This benchmark demonstrates why unweighted traversal (BFS) and weighted greedy relaxation (Dijkstra) produce different optimal routes:

| Algorithm & Criteria | Optimal Route Found | Intermediate Stops | Total Distance | Total Time | Total Fare |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **BFS (Minimum Stops)** | `ST -> NGP -> BPL -> NDLS` | **2** | 1,835 km | 25h 10m | ₹1,460 |
| **Dijkstra (Shortest Distance)** | `ST -> BRC -> RTM -> KOTA -> NDLS` | 3 | **1,123 km** | **14h 25m** | **₹1,025** |
| **Dijkstra (Fastest Time)** | `ST -> BRC -> RTM -> KOTA -> NDLS` | 3 | **1,123 km** | **14h 25m** | **₹1,025** |
| **Dijkstra (Cheapest Fare)** | `ST -> BRC -> RTM -> KOTA -> NDLS` | 3 | **1,123 km** | **14h 25m** | **₹1,025** |

> **Key Takeaway:** BFS minimizes station count (**2 stops**) by taking longer long-haul hops via Nagpur and Bhopal (`1,835 km`), whereas Dijkstra's algorithm performs edge relaxation on track weights to find a route that is **712 km shorter** and **10 hours 45 minutes faster**, even though it passes through **3 intermediate stops**.

---

## 📂 4. Project Directory Structure

```text
railway-route-finder-daa/
├── data/
│   └── stations.json       # Graph dataset (12 Stations, 18 Weighted Tracks)
├── src/
│   ├── __init__.py         # Package initializer
│   ├── graph.py            # RailwayGraph class (Adjacency List representation)
│   └── algorithms.py       # BFS and Dijkstra's Algorithm with metric tracking
├── main.py                 # Interactive CLI & DAA side-by-side benchmark runner
├── requirements.txt        # Python dependencies (rich)
└── README.md               # Project documentation & complexity analysis