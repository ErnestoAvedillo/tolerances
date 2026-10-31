# pytolerance

## 🎯 Description

Python library designed for Tolerance Stack-up analysis using Monte Carlo simulation, allowing you to predict dimensional variability in mechanical assemblies. The dimension class also calculates absolute tolerances, enabling direct comparison with your Monte Carlo simulation results.

## 🚀 Key Features

Monte Carlo Simulation: Statistical precision for non-linear distributions.
Distribution Support: Currently supports Gaussian and Skewed distributions, with Uniform and Triangular planned.
Sensitivity Analysis: Identify which tolerances have the greatest impact on your results.
Pin/Hole Fit Analysis: Worst-case clearance/interference calculation for cylindrical fits.
Positional Tolerance Stack-up: Model hole position and diameter together to work out evolved free gaps.
Lightweight & Fast: Optimized for iterative calculations.

## 📦 Installation

    pip install pytolerance

## 🛠️ Quick Start

### 📏 Define your dimensions

    from pytolerance.dimension import Dimension

    SAMPLES = 100000

    dimension1 = Dimension(nominal=10,
                           tol_sup=0.5,
                           tol_inf=0,
                           CP=2,
                           number_samples=SAMPLES)

    dimension2 = Dimension(nominal=11,
                           tol_sup=0,
                           tol_inf=-0.5,
                           CP=2,
                           number_samples=SAMPLES)

`nominal`, `tol_sup` and `tol_inf` accept plain numbers (assumed to be millimetres) or [pint](https://pint.readthedocs.io/) quantities/strings, e.g. `"10 mm"`. `CP` is the process capability index used to derive sigma from the tolerance band, and `number_samples` controls the size of the Monte Carlo sample vector generated in `vector_samples`.

### 📊 Perform the operation

    result = dimension1 - dimension2

`Dimension` overloads `+`, `-` and `/` (by a scalar). Each operation combines the nominal values and tolerances analytically **and** combines the underlying Monte Carlo sample vectors, so `result.vector_samples` reflects the true simulated distribution of the stack-up.

### 📊 Visualize results

    print(f"Mean: {result.mean:.4f} mm")
    print(f"Sigma: {result.sigma:.4f} mm")
    print(f"DPMO: {result.dpmo:.2f}")

    from pytolerance.hystogram import Hystogram

    hist = Hystogram(
        dimension=result,
        bins=50,
        xlabel="Dimension (mm)",
        ylabel="Density",
        title="Distribution with Tolerance Limits"
    )
    hist.show_plot()

![Sample of image to be shown](./images/Screenshot%20from%202026-07-07%2007-23-19.png)

## 📚 More Examples

Runnable versions of every example below live in the [`examples/`](./examples) folder.

### Gaussian dimension generator

`GausianDimensionGenerator` builds the Monte Carlo sample vector from a normal distribution derived from the nominal value, tolerances and `CP` ([`examples/demo_dimension.py`](./examples/demo_dimension.py)):

    from pytolerance.dimension import GausianDimensionGenerator

    dim = GausianDimensionGenerator(
        nominal=10,
        tol_sup=0,
        tol_inf=-0.5,
        CP=1.33,
        number_samples=100000
    )

    print(f"Mean: {dim.mean:.4f}")
    print(f"Sigma: {dim.sigma:.6f}")
    print(f"Upper limit: {(dim.nominal + dim.tol_sup).magnitude:.4f}")
    print(f"Lower limit: {(dim.nominal + dim.tol_inf).magnitude:.4f}")

### Skewed dimension generator

`SkewedDimensionGenerator` behaves like `Dimension`/`GausianDimensionGenerator` but samples from a skew-normal distribution, useful for modelling processes that are not symmetric around the mean. Pass `skewness` (0 = normal, positive shifts right, negative shifts left) ([`examples/demo_operator_overloading.py`](./examples/demo_operator_overloading.py)):

    from pytolerance.dimension import SkewedDimensionGenerator

    skewed = SkewedDimensionGenerator(
        nominal=10,
        tol_sup=0.5,
        tol_inf=-0.5,
        CP=2,
        number_samples=100000,
        skewness=5
    )

### Operator overloading (`+`, `-`, `/`) and chaining

Dimensions of any generator flavor can be combined directly with Python operators, and the results can be chained ([`examples/demo_operator_overloading.py`](./examples/demo_operator_overloading.py)):

    from pytolerance.dimension import GausianDimensionGenerator

    dim1 = GausianDimensionGenerator(nominal=10, tol_sup=0.5, tol_inf=-0.5, CP=2, number_samples=100000)
    dim2 = GausianDimensionGenerator(nominal=15, tol_sup=0.3, tol_inf=-0.3, CP=2, number_samples=100000)
    dim3 = GausianDimensionGenerator(nominal=5, tol_sup=0.2, tol_inf=-0.2, CP=2, number_samples=100000)

    dim_sum = dim1 + dim2          # nominal/tolerances add, sample vectors add
    dim_sub = dim1 - dim2          # tol_sup/tol_inf swap sign for the subtracted term
    result = (dim1 + dim2) - dim3  # operations chain naturally
    half = dim1 / 2                # divide by a scalar

### `DimensionOperator` static helpers

The same `+`/`-` behaviour is also available as static methods, handy when composing operations programmatically ([`examples/demo_dimension_operator.py`](./examples/demo_dimension_operator.py)):

    from pytolerance.dimension import GausianDimensionGenerator, DimensionOperator

    dim1 = GausianDimensionGenerator(nominal=10, tol_sup=0.5, tol_inf=-0.5, CP=2, number_samples=100000)
    dim2 = GausianDimensionGenerator(nominal=15, tol_sup=0.3, tol_inf=-0.3, CP=2, number_samples=100000)

    dim_sum = DimensionOperator.add(dim1, dim2)
    dim_sub = DimensionOperator.subtract(dim1, dim2)

### Histograms

`Hystogram` renders the Monte Carlo sample vector of a `Dimension`, with reference lines for the mean, nominal value, tolerance limits and the ±4σ USL/LSL band ([`examples/demo_hystogram.py`](./examples/demo_hystogram.py)):

    from pytolerance.dimension import Dimension
    from pytolerance.hystogram import Hystogram

    result = Dimension(nominal=10, tol_sup=0.5, tol_inf=0, CP=2) - \
             Dimension(nominal=11, tol_sup=0, tol_inf=-0.5, CP=2)

    hist = Hystogram(
        dimension=result,
        bins=50,
        xlabel="Dimension (mm)",
        ylabel="Density",
        title="Distribution with Tolerance Limits"
    )

    hist.plot()          # build the matplotlib figure without displaying it
    hist.show_plot()     # build (if needed) and display the figure
    png_base64 = hist.plot_to_base64_png()  # render to a base64-encoded PNG, e.g. for a web report

### Pin/hole fit analysis

`PinHoleTol` performs a worst-case clearance/interference calculation for a cylindrical pin/hole pair and classifies the fit type ([`examples/demo_pinholetol.py`](./examples/demo_pinholetol.py)):

    from pytolerance.PinHoleTol import PinHoleTol

    pin_hole = PinHoleTol(
        pin_nominal=10,
        pin_tol_sup=0,
        pin_tol_inf=-0.025,
        hole_nominal=10,
        hole_tol_sup=0.025,
        hole_tol_inf=0
    )

    summary = pin_hole.get_summary()
    print(f"Pin max/min: {summary['pin']['max']} / {summary['pin']['min']}")
    print(f"Hole max/min: {summary['hole']['max']} / {summary['hole']['min']}")
    print(f"Max clearance: {summary['fit']['max_clearance']}")
    print(f"Min clearance: {summary['fit']['min_clearance']}")
    print(f"Fit type: {summary['fit']['fit_type']}")  # Clearance / Transition / Interference (here: Transition)

`pin_hole.gap_result` also exposes the full `Dimension` (with its Monte Carlo sample vector) of the hole/pin gap, so it can be fed straight into `Hystogram`.

### Positional tolerance stack-up (`SquaredPosition` + `PositionedHole`)

`SquaredPosition` models the 2D positional tolerance of a hole (square tolerance zone), and `PositionedHole` combines that position with a diameter `Dimension`. Subtracting two `PositionedHole`s computes the evolved free gap between the holes, taking into account both their positions and diameters ([`examples/demo_positioned_hole.py`](./examples/demo_positioned_hole.py)):

    from pytolerance.dimension import Dimension
    from pytolerance.position import SquaredPosition
    from pytolerance.positioned_hole import PositionedHole
    from pytolerance.hystogram import Hystogram

    SAMPLES = 100000

    position1 = SquaredPosition(nominal_x=0, nominal_y=0, tol=0.5, number_samples=SAMPLES)
    position2 = SquaredPosition(nominal_x=0, nominal_y=0, tol=0.2, number_samples=SAMPLES)

    diameter1 = Dimension(nominal=7.5, tol_sup=0.1, tol_inf=-0.1, CP=3, number_samples=SAMPLES)
    diameter2 = Dimension(nominal=7.45, tol_sup=0.1, tol_inf=-0.1, CP=3, number_samples=SAMPLES)

    hole1 = PositionedHole(position=position1, diameter=diameter1)
    hole2 = PositionedHole(position=position2, diameter=diameter2)

    evolved_free_gap = hole1 - hole2   # PositionedHole with the resulting gap diameter

    pin = Dimension(nominal=7.2, tol_inf=-0.1, tol_sup=0.1, number_samples=SAMPLES)
    gap = evolved_free_gap.diameter - pin

    hist = Hystogram(dimension=gap, bins=100,
                     xlabel="Free Gap Diameter (mm)",
                     ylabel="Density",
                     title="Hystogram of Free Gap Diameter")
    hist.show_plot()

`SquaredPosition` also overloads `+`/`-` on its own (combining nominal x/y and worst-case tolerance), and exposes `get_dimension()` to turn the 2D position into a radial-distance `Dimension`, and `calc_dpmo()` to estimate the defect rate for the square tolerance zone.

⚙️ Technical Requirements

    Python 3.11

    Main dependencies: numpy, scipy, pint, pydantic, matplotlib.

## 🤝 Contributing

To contribute to this project, please visit my GitHub repository:
https://github.com/ErnestoAvedillo/tolerances/

## 📜 License

Copyright (c) 2026 Ernesto Avedillo Carretero

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
