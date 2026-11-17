# Heterograph

**heterograph** is a Python library for building, querying, and visualizing *heterogeneous directed graphs* ("heterographs"). It provides a convenient, Pythonic API for managing vertices, edges, and their properties, supports common graph traversals, and includes rich visualization tools for notebooks and the web.

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

### Development environment

Clone this repository, then create the environment from the repository root:

```bash
conda env create -f environment.yml
conda activate heterograph
```

This installs Heterograph in editable mode, so changes to the source are available
in the environment.

### Use the published Conda package

To install Heterograph in a separate environment, create one directly:

```bash
conda create -n my-heterograph -c ckiddo74 -c conda-forge python=3.12 heterograph
conda activate my-heterograph
```

Alternatively, define an `environment.yml` for your project:

```yaml
name: my-heterograph
channels:
  - ckiddo74
  - conda-forge
dependencies:
  - python=3.12
  - heterograph
```

These examples pin Python to version 3.12; choose a version supported by the
published Heterograph builds if needed.

Then create and activate the environment:

```bash
conda env create -f environment.yml
conda activate my-heterograph
```

The published package currently targets Linux x86-64.

### Build and publish the Conda package

See [conda/README.md](conda/README.md) for build and publishing instructions.

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

## Documentation

Read the [Heterograph documentation](https://custom-computing-ic.github.io/heterograph/).
To build the HTML documentation locally, activate the development environment
and run from the repository root:

```bash
cd docs
make html
```

Open `docs/build/html/index.html` in a browser. The build executes the
documentation notebooks and may take some time.

---

See `environment.yml` for the full dependency list.

---

## License

This project is licensed under the terms of the **Apache License 2.0**. See `LICENSE` for details.

---

## Acknowledgements

* Built on top of the excellent [`graph-tool`](https://graph-tool.skewed.de/) library
* Visualization powered by Flask and D3.js
