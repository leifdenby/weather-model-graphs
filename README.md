# weather-model-graphs

[![linting](https://github.com/mllam/weather-model-graphs/actions/workflows/pre-commit.yml/badge.svg)](https://github.com/mllam/weather-model-graphs/actions/workflows/pre-commit.yml) [![Jupyter Book Badge](https://jupyterbook.org/badge.svg)](https://mllam.github.io/weather-model-graphs)

`weather-model-graphs` is a package for creating, visualising and storing message-passing graphs for data-driven weather models.

The package is designed to use `networkx.DiGraph` objects as the primary data structure for the graph representation right until the graph is to be stored on disk into a specific format.
This makes the graph generation process modular (every step outputs a `networkx.DiGraph`), easy to debug (visualise the graph at any step) and allows output to different file-formats and file-structures to be easily implemented. More details are given in the [background](https://mllam.github.io/weather-model-graphs/background.html) and [design](https://mllam.github.io/weather-model-graphs/design.html) section of the online [documentation](https://mllam.github.io/weather-model-graphs/).


## Installation

```
pdm install
```

### pytorch support

cpu only:

```bash
PIP_INDEX_URL=https://download.pytorch.org/whl/cpu pdm install --group pytorch
```

gpu support (see https://pytorch.org/get-started/locally/#linux-pip for older versions of CUDA):


```bash
pdm install --group pytorch
```

# Usage

The best way to understand how to use `weather-model-graphs` is to look at the [notebooks/constructing_the_graph.ipynb](notebooks/constructing_the_graph.ipynb) notebook, to have look at the tests in [tests/](tests/) or simply to read through the source code.
In addition you can read the [background and design](#background-and-design) section below to understand the design principles of `weather-model-graphs`.

## Example, Keisler 2021 flat graph architecture

```python
import numpy as np
import weather_model_graphs as wmg

# define your (x,y) grid coodinates
xy_grid = np.meshgrid(np.linspace(0, 1, 32), np.linspace(0, 1, 32), indexing='ij')

# create the full graph
graph = wmg.create.archetype.create_keisler_graph(xy=xy_grid)

# split the graph by component
graph_components = wmg.split_graph_by_edge_attribute(graph=graph, attr='component')

# save the graph components to disk in pytorch-geometric format
for component, graph in graph_components.items():
    wmg.save.to_pyg(graph=graph, name=component, output_directory=".")
```

# Documentation

The documentation is built using [Jupyter Book](https://jupyterbook.org/intro.html) and can be found at [https://mllam.github.io/weather-model-graphs](https://mllam.github.io/weather-model-graphs). This includes background on graph-based weather models, the design principles of `weather-model-graphs` and how to use it to create your own graph architectures.
