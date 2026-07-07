import importlib


def test_pytolerance_imports_work():
    module = importlib.import_module("pytolerance")
    assert module is not None

    dimension_module = importlib.import_module("pytolerance.dimension")
    assert hasattr(dimension_module, "Dimension")

    histogram_module = importlib.import_module("pytolerance.hystogram")
    assert hasattr(histogram_module, "Hystogram")
