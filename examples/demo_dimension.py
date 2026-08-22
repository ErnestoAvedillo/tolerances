from pytolerance.dimension import Dimension
from pytolerance.hystogram import Hystogram
SAMPLES = 100000
cota1 = Dimension(nominal=10,
                  tol_sup=0.5,
                  tol_inf=0,
                  CP=2,
                  number_samples=SAMPLES)
cota2 = Dimension(nominal=11,
                  tol_sup=0,
                  tol_inf=-0.5,
                  CP=2,
                  number_samples=SAMPLES)

result = cota1 - cota2
print(f"Mean: {result.mean:.4f} mm")
print(f"Sigma: {result.sigma:.4f} mm")

hist = Hystogram(
    dimension=result,
    bins=50,
    xlabel="Dimension (mm)",
    ylabel="Density",
    title="Distribution with Tolerance Limits"
)
hist.show_plot()
