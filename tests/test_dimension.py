"""Tests for the core Dimension model and its arithmetic operators."""
import pytest

from pytolerance.convert import ureg
from pytolerance.dimension import (
    Dimension,
    DimensionOperator,
    GausianDimensionGenerator,
    SkewedDimensionGenerator,
)

SAMPLES = 40000


def test_mean_and_sigma_from_symmetric_tolerance():
    d = Dimension(nominal=10, tol_sup=0.5, tol_inf=-0.5, CP=2,
                  number_samples=SAMPLES)
    # midpoint of the tolerance band
    assert d.mean.magnitude == pytest.approx(10.0)
    # sigma = (tol_sup - tol_inf) / 6 / CP
    assert d.sigma.magnitude == pytest.approx((0.5 - -0.5) / 6 / 2)


def test_mean_from_asymmetric_tolerance():
    d = Dimension(nominal=10, tol_sup=0.4, tol_inf=-0.2, CP=1,
                  number_samples=SAMPLES)
    assert d.mean.magnitude == pytest.approx(10 + (0.4 - 0.2) / 2)


def test_sampled_statistics_match_analytic():
    d = Dimension(nominal=10, tol_sup=0.6, tol_inf=-0.6, CP=1,
                  number_samples=SAMPLES)
    assert d.vector_samples.mean() == pytest.approx(d.mean.magnitude, abs=0.02)
    assert d.vector_samples.std() == pytest.approx(d.sigma.magnitude, rel=0.05)


def test_plain_number_inputs_coerced_to_mm():
    d = Dimension(nominal=5, tol_sup=0.1, tol_inf=-0.1, number_samples=100)
    assert d.nominal.units == ureg.mm


class TestOperators:
    def _dims(self):
        a = Dimension(nominal=10, tol_sup=0.5, tol_inf=0.0, CP=2,
                      number_samples=SAMPLES)
        b = Dimension(nominal=11, tol_sup=0.0, tol_inf=-0.5, CP=2,
                      number_samples=SAMPLES)
        return a, b

    def test_add_nominal_and_tolerances(self):
        a, b = self._dims()
        s = a + b
        assert s.nominal.magnitude == pytest.approx(21)
        # regression: tolerances must land on tol_sup/tol_inf, not tol_*_sum
        assert s.tol_sup.magnitude == pytest.approx(0.5)
        assert s.tol_inf.magnitude == pytest.approx(-0.5)

    def test_add_samples_are_summed(self):
        a, b = self._dims()
        s = a + b
        expected = (a.vector_samples + b.vector_samples).mean()
        assert s.vector_samples.mean() == pytest.approx(expected)

    def test_sub_swaps_tolerances(self):
        a, b = self._dims()
        r = a - b
        assert r.nominal.magnitude == pytest.approx(-1)
        # tol_sup_sub = self.tol_sup - other.tol_inf = 0.5 - (-0.5)
        assert r.tol_sup.magnitude == pytest.approx(1.0)
        # tol_inf_sub = self.tol_inf - other.tol_sup = 0 - 0
        assert r.tol_inf.magnitude == pytest.approx(0.0)

    def test_truediv_by_scalar(self):
        a, _ = self._dims()
        r = a / 2
        assert r.nominal.magnitude == pytest.approx(5)
        assert r.tol_sup.magnitude == pytest.approx(0.25)

    def test_add_non_dimension_returns_notimplemented(self):
        a, _ = self._dims()
        with pytest.raises(TypeError):
            _ = a + 3

    def test_truediv_non_scalar_returns_notimplemented(self):
        a, b = self._dims()
        with pytest.raises(TypeError):
            _ = a / b

    def test_dimension_operator_helpers(self):
        a, b = self._dims()
        assert DimensionOperator.add(a, b).nominal.magnitude == pytest.approx(21)
        assert (DimensionOperator.subtract(a, b).nominal.magnitude
                == pytest.approx(-1))


class TestDpmo:
    def test_centered_high_capability_is_near_zero(self):
        d = Dimension(nominal=10, tol_sup=0.5, tol_inf=-0.5, CP=2,
                      number_samples=SAMPLES)
        # ~8 sigma to each limit -> essentially zero defects
        assert d.dpmo < 1.0

    def test_low_capability_has_many_defects(self):
        d = Dimension(nominal=10, tol_sup=0.05, tol_inf=-0.05, CP=0.5,
                      number_samples=SAMPLES)
        assert d.dpmo > 10_000

    def test_higher_cp_lowers_dpmo(self):
        # The model always centres the mean in the tolerance band, so DPMO is
        # governed by the process capability CP (band half-width in sigmas).
        low_cp = Dimension(nominal=10, tol_sup=0.3, tol_inf=-0.3, CP=1,
                           number_samples=SAMPLES)
        high_cp = Dimension(nominal=10, tol_sup=0.3, tol_inf=-0.3, CP=1.67,
                            number_samples=SAMPLES)
        assert high_cp.dpmo < low_cp.dpmo

    def test_cp_one_is_three_sigma(self):
        # CP=1 => limits at +/-3 sigma => ~2700 DPMO (both tails)
        d = Dimension(nominal=10, tol_sup=0.3, tol_inf=-0.3, CP=1,
                      number_samples=SAMPLES)
        assert d.dpmo == pytest.approx(2700, abs=50)

    def test_zero_sigma_in_spec(self):
        d = Dimension(nominal=10, tol_sup=0.5, tol_inf=-0.5, CP=1,
                      number_samples=100)
        d.sigma = 0.0 * ureg.mm
        assert d.calc_dpmo() == 0.0

    def test_zero_sigma_out_of_spec(self):
        d = Dimension(nominal=10, tol_sup=0.5, tol_inf=-0.5, CP=1,
                      number_samples=100)
        d.mean = 20.0 * ureg.mm
        d.sigma = 0.0 * ureg.mm
        assert d.calc_dpmo() == 1_000_000.0


class TestGenerators:
    def test_gaussian_generator_sets_dpmo(self):
        d = GausianDimensionGenerator(nominal=10, tol_sup=0.5, tol_inf=-0.5,
                                      CP=2, number_samples=SAMPLES)
        assert isinstance(d.dpmo, float)
        assert d.dpmo < 1.0

    def test_skew_generator_mean_is_band_midpoint(self):
        d = SkewedDimensionGenerator(nominal=10, tol_sup=0.5, tol_inf=-0.1,
                                     CP=2, number_samples=SAMPLES, skewness=4)
        assert d.mean.magnitude == pytest.approx(10 + (0.5 - 0.1) / 2)

    def test_skew_generator_actually_skews_samples(self):
        from scipy.stats import skew
        d = SkewedDimensionGenerator(nominal=10, tol_sup=0.5, tol_inf=-0.5,
                                     CP=2, number_samples=SAMPLES, skewness=8)
        assert skew(d.vector_samples) > 0.2

    def test_chained_operations(self):
        d1 = GausianDimensionGenerator(nominal=10, tol_sup=0.5, tol_inf=-0.5,
                                       CP=2, number_samples=SAMPLES)
        d2 = GausianDimensionGenerator(nominal=15, tol_sup=0.3, tol_inf=-0.3,
                                       CP=2, number_samples=SAMPLES)
        d3 = GausianDimensionGenerator(nominal=5, tol_sup=0.2, tol_inf=-0.2,
                                       CP=2, number_samples=SAMPLES)
        result = (d1 + d2) - d3
        assert result.nominal.magnitude == pytest.approx(20)
        assert result.vector_samples is not None


def test_str_contains_key_fields():
    d = Dimension(nominal=10, tol_sup=0.5, tol_inf=-0.5, number_samples=100)
    text = str(d)
    assert "nominal" in text and "dpmo" in text
