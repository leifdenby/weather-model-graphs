import tempfile

import pytest
from loguru import logger

import tests.utils as test_utils
import weather_model_graphs as wmg
from weather_model_graphs.save import HAS_PYG, split_into_neural_lam_subgraphs


@pytest.mark.parametrize("kind", ["graphcast", "keisler", "oskarsson_hierarchical"])
def test_save_to_pyg_neural_lam(kind):
    if not HAS_PYG:
        logger.warning(
            "Skipping test_save_to_pyg because weather-model-graphs[pytorch] is not installed."
        )
        return

    is_hierarchical = kind == "oskarsson_hierarchical"
    if is_hierarchical:
        list_from_attribute = "level"
    else:
        list_from_attribute = None

    xy = test_utils.create_fake_xy(N=64)
    fn_name = f"create_{kind}_graph"
    fn = getattr(wmg.create.archetype, fn_name)
    graph = fn(coords=xy)

    graph_components = split_into_neural_lam_subgraphs(
        graph=graph, is_hierachical=is_hierarchical
    )

    with tempfile.TemporaryDirectory(suffix=f"__{kind}") as tmpdir:
        for name, graph in graph_components.items():
            wmg.save.to_pyg(
                graph=graph,
                output_directory=tmpdir,
                name=name,
                list_from_attribute=list_from_attribute,
            )
