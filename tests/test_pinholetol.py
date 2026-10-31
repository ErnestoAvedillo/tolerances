"""Tests for the PinHoleTol fit analysis."""
import pytest

from pytolerance.convert import ureg
from pytolerance.dimension import Dimension
from pytolerance.PinHoleTol import PinHoleTol


def test_clearance_fit():
    # hole always larger than pin -> guaranteed clearance
    ph = PinHoleTol(pin_nominal=10, pin_tol_sup=-0.005, pin_tol_inf=-0.025,
                    hole_nominal=10, hole_tol_sup=0.025, hole_tol_inf=0.001)
    summary = ph.get_summary()
    assert summary["fit"]["fit_type"].startswith("Clearance")
    assert summary["fit"]["min_clearance"] > 0 * ureg.mm
    assert summary["fit"]["max_clearance"] > 0 * ureg.mm


def test_interference_fit():
    # pin always larger than hole -> interference
    ph = PinHoleTol(pin_nominal=10, pin_tol_sup=0.05, pin_tol_inf=0.02,
                    hole_nominal=10, hole_tol_sup=0.01, hole_tol_inf=0.0)
    summary = ph.get_summary()
    assert summary["fit"]["fit_type"].startswith("Interference")
    assert summary["fit"]["max_clearance"] < 0 * ureg.mm


def test_transition_fit():
    # ranges overlap zero -> transition
    ph = PinHoleTol(pin_nominal=10, pin_tol_sup=0.02, pin_tol_inf=-0.02,
                    hole_nominal=10, hole_tol_sup=0.02, hole_tol_inf=-0.02)
    summary = ph.get_summary()
    assert summary["fit"]["fit_type"].startswith("Transition")


def test_worst_case_limits():
    ph = PinHoleTol(pin_nominal=10, pin_tol_sup=0, pin_tol_inf=-0.025,
                    hole_nominal=10, hole_tol_sup=0.025, hole_tol_inf=0)
    s = ph.get_summary()
    assert s["pin"]["max"].magnitude == pytest.approx(10.0)
    assert s["pin"]["min"].magnitude == pytest.approx(9.975)
    assert s["hole"]["max"].magnitude == pytest.approx(10.025)
    assert s["hole"]["min"].magnitude == pytest.approx(10.0)
    # max_clearance = max_hole - min_pin ; min_clearance = min_hole - max_pin
    assert s["fit"]["max_clearance"].magnitude == pytest.approx(0.05)
    assert s["fit"]["min_clearance"].magnitude == pytest.approx(0.0)


def test_gap_result_is_dimension():
    ph = PinHoleTol(pin_nominal=10, pin_tol_sup=0, pin_tol_inf=-0.025,
                    hole_nominal=10, hole_tol_sup=0.025, hole_tol_inf=0)
    assert isinstance(ph.gap_result, Dimension)
