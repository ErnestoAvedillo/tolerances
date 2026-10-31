"""Tests for the Hystogram plotting helper (headless via Agg backend)."""
import base64

from pytolerance.dimension import GausianDimensionGenerator
from pytolerance.hystogram import Hystogram


def _dim():
    return GausianDimensionGenerator(nominal=10, tol_sup=0.5, tol_inf=-0.5,
                                     CP=2, number_samples=5000)


def test_plot_builds_figure_and_axes():
    hist = Hystogram(dimension=_dim(), bins=30, title="t")
    hist.plot()
    assert hist.hyst_plot is not None
    assert hist.hyst_axes is not None


def test_plot_to_base64_png_returns_valid_png():
    hist = Hystogram(dimension=_dim(), bins=30)
    encoded = hist.plot_to_base64_png()
    assert isinstance(encoded, str) and len(encoded) > 0
    raw = base64.b64decode(encoded)
    # PNG magic number
    assert raw[:8] == b"\x89PNG\r\n\x1a\n"
