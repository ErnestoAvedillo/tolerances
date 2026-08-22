from typing import Optional
from .convert import ureg
from .dimension import Dimension, GausianDimensionGenerator


class PinHoleTol:
    """Calculate pin/hole tolerance and fit analysis.

    All inputs are plain numbers interpreted as millimetres. The clearance is
    computed from the worst-case combination of pin and hole limits:

    * ``max_clearance = max_hole - min_pin``
    * ``min_clearance = min_hole - max_pin``
    """

    def __init__(self,
                 pin_nominal: float,
                 pin_tol_sup: float,
                 pin_tol_inf: float,
                 hole_nominal: float,
                 hole_tol_sup: float,
                 hole_tol_inf: float):
        self.pin: GausianDimensionGenerator = GausianDimensionGenerator(
            nominal=pin_nominal * ureg.mm,
            tol_sup=pin_tol_sup * ureg.mm,
            tol_inf=pin_tol_inf * ureg.mm,
        )
        self.hole: GausianDimensionGenerator = GausianDimensionGenerator(
            nominal=hole_nominal * ureg.mm,
            tol_sup=hole_tol_sup * ureg.mm,
            tol_inf=hole_tol_inf * ureg.mm,
        )
        self.gap_result: Optional[Dimension] = None
        self.fit_type: str = ""
        self._calculate_fit()

    # -- worst-case limits -------------------------------------------------
    @property
    def max_pin(self):
        return self.pin.nominal + self.pin.tol_sup

    @property
    def min_pin(self):
        return self.pin.nominal + self.pin.tol_inf

    @property
    def max_hole(self):
        return self.hole.nominal + self.hole.tol_sup

    @property
    def min_hole(self):
        return self.hole.nominal + self.hole.tol_inf

    @property
    def max_clearance(self):
        return self.max_hole - self.min_pin

    @property
    def min_clearance(self):
        return self.min_hole - self.max_pin

    def _calculate_fit(self):
        """Determine the fit type from the clearance limits."""
        self.gap_result = self.hole - self.pin

        zero = 0 * ureg.mm
        if self.max_clearance < zero and self.min_clearance < zero:
            self.fit_type = "Interference (Apriete)"
        elif self.max_clearance > zero and self.min_clearance > zero:
            self.fit_type = "Clearance (Juego)"
        else:
            self.fit_type = "Transition (Ajuste de Transición)"
        return self

    def get_summary(self) -> dict:
        """Return a summary of the pin-hole tolerance calculation."""
        return {
            "pin": {
                "nominal": self.pin.nominal,
                "tolerance_sup": self.pin.tol_sup,
                "tolerance_inf": self.pin.tol_inf,
                "max": self.max_pin,
                "min": self.min_pin,
            },
            "hole": {
                "nominal": self.hole.nominal,
                "tolerance_sup": self.hole.tol_sup,
                "tolerance_inf": self.hole.tol_inf,
                "max": self.max_hole,
                "min": self.min_hole,
            },
            "fit": {
                "max_clearance": self.max_clearance,
                "min_clearance": self.min_clearance,
                "fit_type": self.fit_type,
            }
        }
