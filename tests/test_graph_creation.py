import tempfile

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pytest

import weather_model_graphs as wmg


def _create_fake_xy(N=10):
    x = np.linspace(0, 1, N)
    y = np.linspace(0, 1, N)
    xy = np.meshgrid(x, y)
    xy = np.stack(xy, axis=0)
    return xy


def _create_rectangular_fake_xy(Nx=10, Ny=20):
    x = np.linspace(0, 1, Nx)
    y = np.linspace(0, 1, Ny)
    xy = np.meshgrid(x, y)
    xy = np.stack(xy, axis=0)
    return xy


def test_create_single_level_mesh_graph():
    xy = _create_fake_xy(N=4)
    mesh_graph = wmg.create.mesh.create_single_level_2d_mesh_graph(xy=xy, nx=5, ny=5)

    pos = {node: mesh_graph.nodes[node]["pos"] for node in mesh_graph.nodes()}
    fig, ax = plt.subplots(1, 1, figsize=(10, 10))
    nx.draw_networkx(ax=ax, G=mesh_graph, pos=pos, with_labels=True, hide_ticks=False)

    ax.scatter(xy[0, ...], xy[1, ...], color="r")
    ax.axison = True

    with tempfile.NamedTemporaryFile(suffix=".png") as f:
        fig.savefig(f.name)


@pytest.mark.parametrize("use_graph_tool", [True, False])
@pytest.mark.parametrize("kind", ["graphcast", "keisler", "oskarsson_hierarchical"])
def test_create_graph_archetype(kind, use_graph_tool):
    xy = _create_fake_xy(N=64)
    fn_name = f"create_{kind}_graph"
    fn = getattr(wmg.create.archetype, fn_name)

    if use_graph_tool:
        with wmg.use_graph_tool_backend():
            fn(xy_grid=xy)
    else:
        fn(xy_grid=xy)


# list the connectivity options for g2m and m2g and the kwargs to test
G2M_CONNECTIVITY_OPTIONS = dict(
    nearest_neighbour=[],
    nearest_neighbours=[dict(max_num_neighbours=4), dict(max_num_neighbours=8)],
    within_radius=[
        dict(max_dist=0.1),
        dict(max_dist=0.2),
        dict(rel_max_dist=0.51),
        dict(rel_max_dist=1.0),
    ],
)
# containing_rectangle option should only be used for m2g
M2G_CONNECTIVITY_OPTIONS = G2M_CONNECTIVITY_OPTIONS.copy()
M2G_CONNECTIVITY_OPTIONS["containing_rectangle"] = [dict()]

# list the connectivity options for m2m and the kwargs to test
M2M_CONNECTIVITY_OPTIONS = dict(
    flat=[],
    flat_multiscale=[
        dict(max_num_levels=3, grid_refinement_factor=3, level_refinement_factor=3),
        dict(max_num_levels=1, grid_refinement_factor=5, level_refinement_factor=5),
    ],
    hierarchical=[
        dict(max_num_levels=3, grid_refinement_factor=3, level_refinement_factor=3),
        dict(max_num_levels=None, grid_refinement_factor=3, level_refinement_factor=3),
    ],
)


@pytest.mark.parametrize("g2m_connectivity", G2M_CONNECTIVITY_OPTIONS.keys())
@pytest.mark.parametrize("m2g_connectivity", M2G_CONNECTIVITY_OPTIONS.keys())
@pytest.mark.parametrize("m2m_connectivity", M2M_CONNECTIVITY_OPTIONS.keys())
def test_create_graph_generic(m2g_connectivity, g2m_connectivity, m2m_connectivity):
    xy = _create_fake_xy(N=32)

    for g2m_kwargs in G2M_CONNECTIVITY_OPTIONS[g2m_connectivity]:
        for m2g_kwargs in M2G_CONNECTIVITY_OPTIONS[m2g_connectivity]:
            for m2m_kwargs in M2M_CONNECTIVITY_OPTIONS[m2m_connectivity]:
                graph = wmg.create.create_all_graph_components(
                    xy=xy,
                    m2m_connectivity=m2m_connectivity,
                    m2m_connectivity_kwargs=m2m_kwargs,
                    g2m_connectivity=g2m_connectivity,
                    g2m_connectivity_kwargs=g2m_kwargs,
                    m2g_connectivity=m2g_connectivity,
                    m2g_connectivity_kwargs=m2g_kwargs,
                )

                assert isinstance(graph, nx.DiGraph)

                graph_components = wmg.split_graph_by_edge_attribute(
                    graph=graph, attr="component"
                )
                assert all(
                    isinstance(graph, nx.DiGraph) for graph in graph_components.values()
                )
                assert set(graph_components.keys()) == {"m2m", "m2g", "g2m"}


@pytest.mark.parametrize("kind", ["graphcast", "keisler", "oskarsson_hierarchical"])
def test_create_rectangular_graph(kind):
    """
    Tests that graphs can be created for non-square areas, both thin and wide
    """
    # Test thin
    xy = _create_rectangular_fake_xy(Nx=20, Ny=64)
    fn_name = f"create_{kind}_graph"
    fn = getattr(wmg.create.archetype, fn_name)
    fn(xy_grid=xy, grid_refinement_factor=2)

    # Test wide
    xy = _create_rectangular_fake_xy(Nx=64, Ny=20)
    fn_name = f"create_{kind}_graph"
    fn = getattr(wmg.create.archetype, fn_name)
    fn(xy_grid=xy, grid_refinement_factor=2)


@pytest.mark.parametrize("grid_refinement_factor", (2, 3))
@pytest.mark.parametrize("level_refinement_factor", (2, 3, 5))
def test_create_exact_refinement(grid_refinement_factor, level_refinement_factor):
    """
    This test is to check that it is possible to create graph hierarchies when
    the refinement factors are an exact multiple of the number of nodes. In these
    situations it should be possible to create multi-level graphs, but it was not
    earlier due to numerical issues.
    """
    N = grid_refinement_factor * (level_refinement_factor**2)
    xy = _create_rectangular_fake_xy(Nx=N, Ny=N)

    # Build hierarchical graph, should have 2 levels and not give error
    wmg.create.archetype.create_oskarsson_hierarchical_graph(
        xy,
        grid_refinement_factor=grid_refinement_factor,
        level_refinement_factor=level_refinement_factor,
    )
