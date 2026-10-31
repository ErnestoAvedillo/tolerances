"""Tests for SquaredPosition and PositionedHole."""
import numpy as np
import pytest

from pytolerance.dimension import Dimension
from pytolerance.position import SquaredPosition
from pytolerance.positioned_hole import PositionedHole

SAMPLES = 20000


def test_position_generates_two_sample_vectors():
    p = SquaredPosition(nominal_x=1, nominal_y=2, tol=0.5,
                        number_samples=SAMPLES)
    assert p.vector_x.shape == (SAMPLES,)
    assert p.vector_y.shape == (SAMPLES,)
    assert p.vector_x.mean() == pytest.approx(1, abs=0.02)
    assert p.vector_y.mean() == pytest.approx(2, abs=0.02)


def test_position_add():
    p1 = SquaredPosition(nominal_x=1, nominal_y=1, tol=0.5,
                         number_samples=SAMPLES)
    p2 = SquaredPosition(nominal_x=2, nominal_y=3, tol=0.3,
                         number_samples=SAMPLES)
    r = p1 + p2
    assert r.nominal_x.magnitude == pytest.approx(3)
    assert r.nominal_y.magnitude == pytest.approx(4)
    assert r.tol.magnitude == pytest.approx(0.8)


def test_position_sub():
    p1 = SquaredPosition(nominal_x=5, nominal_y=5, tol=0.5,
                         number_samples=SAMPLES)
    p2 = SquaredPosition(nominal_x=2, nominal_y=1, tol=0.3,
                         number_samples=SAMPLES)
    r = p1 - p2
    assert r.nominal_x.magnitude == pytest.approx(3)
    assert r.nominal_y.magnitude == pytest.approx(4)
    # tolerances add on subtraction (worst case)
    assert r.tol.magnitude == pytest.approx(0.8)


def test_position_add_wrong_type():
    p = SquaredPosition(nominal_x=0, nominal_y=0, tol=0.5, number_samples=100)
    assert p.__add__(42) is NotImplemented


def test_get_dimension_is_radial_distance():
    p = SquaredPosition(nominal_x=3, nominal_y=4, tol=0.1,
                        number_samples=SAMPLES)
    d = p.get_dimension()
    assert isinstance(d, Dimension)
    # centred at (3,4) -> distance ~5
    assert d.mean.magnitude == pytest.approx(5, abs=0.05)


def test_calc_dpmo_reflects_capability():
    # sigma = (tol/2)/3/CP, so the failure boundary sits at 3*CP sigmas.
    # CP=1 -> 3 sigma per axis -> a few thousand DPMO across two axes;
    # CP=2 -> 6 sigma -> essentially zero.
    low_cp = SquaredPosition(nominal_x=0, nominal_y=0, tol=1.0, CP=1,
                             number_samples=SAMPLES)
    high_cp = SquaredPosition(nominal_x=0, nominal_y=0, tol=1.0, CP=2,
                              number_samples=SAMPLES)
    assert low_cp.calc_dpmo() > high_cp.calc_dpmo()
    assert high_cp.calc_dpmo() < 100


class TestPositionedHole:
    def _holes(self):
        pos1 = SquaredPosition(nominal_x=0, nominal_y=0, tol=0.5,
                               number_samples=SAMPLES)
        pos2 = SquaredPosition(nominal_x=0, nominal_y=0, tol=0.2,
                               number_samples=SAMPLES)
        dia1 = Dimension(nominal=7.5, tol_sup=0.1, tol_inf=-0.1, CP=3,
                         number_samples=SAMPLES)
        dia2 = Dimension(nominal=7.45, tol_sup=0.1, tol_inf=-0.1, CP=3,
                         number_samples=SAMPLES)
        return (PositionedHole(position=pos1, diameter=dia1),
                PositionedHole(position=pos2, diameter=dia2))

    def test_diameter_evolv_computed(self):
        h1, _ = self._holes()
        # nominal - tol_inf - position_tol
        expected = 7.5 - (-0.1) - 0.5
        assert h1.diameter_evolv.magnitude == pytest.approx(expected)

    def test_subtraction_returns_positioned_hole(self):
        # cross-registry regression: Dimension + SquaredPosition must share
        # a single pint UnitRegistry, otherwise this raises.
        h1, h2 = self._holes()
        gap = h1 - h2
        assert isinstance(gap, PositionedHole)
        assert gap.diameter.vector_samples.shape == (SAMPLES,)
        assert np.all(gap.diameter.vector_samples >= 0)
