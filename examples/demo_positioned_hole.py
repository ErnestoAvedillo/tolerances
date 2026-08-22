from pytolerance.dimension import Dimension
from pytolerance.position import SquaredPosition
from pytolerance.positioned_hole import PositionedHole
from pytolerance.hystogram import Hystogram

SAMPLES = 100000
Hole_position_1 = SquaredPosition(nominal_x=0,
                                  nominal_y=0,
                                  tol=0.5,
                                  number_samples=SAMPLES)
Hole_position_2 = SquaredPosition(nominal_x=0,
                                  nominal_y=0,
                                  tol=0.2,
                                  number_samples=SAMPLES)
Diameter1 = Dimension(nominal=7.5,
                      tol_sup=0.1,
                      tol_inf=-0.1,
                      CP=3,
                      number_samples=SAMPLES)
Diameter2 = Dimension(nominal=7.45,
                      tol_sup=0.1,
                      tol_inf=-0.1,
                      CP=3,
                      number_samples=SAMPLES)
hole1 = PositionedHole(position=Hole_position_1, diameter=Diameter1)
hole2 = PositionedHole(position=Hole_position_2, diameter=Diameter2)
Evold_free_gap = hole1 - hole2
Pin = Dimension(nominal=7.2, tol_inf=-0.1, tol_sup=0.1, number_samples=SAMPLES)
Gap = Evold_free_gap.diameter - Pin
print("Printing values form Evolved Free Gap")
print(Evold_free_gap.diameter)
print("Printing values form Pin")
print(Pin)
print("Printing values form resultant Gap pin evolved free gap")
print(Gap)

hyst = Hystogram(dimension=Gap,
                 bins=100,
                 xlabel="Free Gap Diameter (mm)",
                 ylabel="Density",
                 title="Hystogram of Free Gap Diameter")
hyst.show_plot()
impult = input("Press Enter to continue...")
