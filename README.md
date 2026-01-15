# Heterograph

**heterograph** is a Python library for building, querying, and visualizing *heterogeneous directed graphs* ("heterographs") on top of [`graph-tool`](https://graph-tool.skewed.de/). It provides a convenient, Pythonic API for managing vertices, edges, and their properties, supports common graph traversals, and includes rich visualization tools for notebooks and the web.

> The project is designed for exploratory graph modeling and analysis, especially when you need structured metadata on vertices and edges and interactive inspection of graph topology.

---

## Key Features

* **Heterogeneous directed graphs**

  * Vertices and edges with arbitrary, typed properties
  * Explicit in-/out-neighbour management

* **Graph algorithms**

  * Depth-first search (DFS) traversal utilities
  * Topology and neighbourhood queries

* **Visualization**

  * Interactive **web-based viewer** (Flask + D3)
  * Notebook-friendly display helpers
  * Optional Graphviz export for static diagrams

* **Extensible design**

  * Custom initialization hooks for graphs, vertices, and edges
  * Property system (`HGraphProps`) for clean metadata handling

---

## Project Structure

```
heterograph/
├── heterograph/
│   ├── hgraph.py          # Core HGraph implementation
│   ├── hgraph_props.py    # Property handling for graphs, vertices, edges
│   ├── webview.py         # Flask-based interactive web viewer
│   ├── utils/             # Notebook & display helpers
│   └── assets/            # Static JS/CSS assets for visualization
├── tests/                 # Pytest test suite
├── environment.yml        # Conda environment definition
├── pyproject.toml         # Build & packaging configuration
├── LICENSE
└── README.md
```

---

## Installation

### Create the Conda environment (recommended)

```bash
conda env create -f environment.yml
conda activate heterograph
```

---

## Quick Start

### Creating a graph

```python
from heterograph import *

# Create an empty heterograph
g = HGraph()

# Add vertices
v1 = g.add_vx()
v2 = g.add_vx()

# Add an edge
e = g.add_edge(v1, v2)
```

### Working with properties

```python
# Set vertex properties
g.pmap[v1]["label"] = "Source"
g.pmap[v2]["label"] = "Target"

# Set edge properties
g.pmap[e]["weight"] = 1.0

# set graph properties
g['name'] = 'my graph'
```

---

## Visualization

### Web-based viewer

```python
from heterograph import *

g = HGraph()

# Add vertices
v1 = g.add_vx()
v2 = g.add_vx()
g.add_edge(v1, v2)
g.view()

```

This launches a local Flask server with an interactive graph UI (pan, zoom, inspect vertices/edges).

---

## Testing

Run the full test suite with:

```bash
pytest
```

Tests cover:

* Vertex and edge creation
* Neighbour queries
* DFS traversal
* Graph initialization and topology

---

See `environment.yml` for the full dependency list.

---

## License

This project is licensed under the terms of the **MIT License**. See `LICENSE` for details.

---

## Acknowledgements

* Built on top of the excellent [`graph-tool`](https://graph-tool.skewed.de/) library
* Visualization powered by Flask and D3.js
