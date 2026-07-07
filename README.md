# pytol

## 🎯 Description

Python library designed for Tolerance Stack-up analysis using Monte Carlo simulation, allowing you to predict dimensional variability in mechanical assemblies. The dimension class also calculates absolute tolerances, enabling direct comparison with your Monte Carlo simulation results.

## 🚀 Key Features

Monte Carlo Simulation: Statistical precision for non-linear distributions.
Distribution Support: Supports various distributions (e.g., Normal, Uniform, Triangular, etc.).
Sensitivity Analysis: Identify which tolerances have the greatest impact on your results.
Lightweight & Fast: Optimized for iterative calculations.

## 📦 Installation

    pip install pytol

## 🛠️ Quick Start

## 📏 Define your dimensions

    from dimension import Dimension

    SAMPLES = 100000

    diemsion1 = Dimension(nominal=10,
                                    tol_sup=0.5,
                                    tol_inf=0,
                                    CP=2,
                                    number_samples=SAMPLES)

    dimension2 = Dimension(nominal=11,
                                    tol_sup=0,
                                    tol_inf=-0.5,
                                    CP=2,
                                    number_samples=SAMPLES)

## 📊 Perform the operation

    result = dimension1 - dimension2

## 📊 Visualize results

    print(f"Mean: {result.mean:.4f} mm")
    print(f"Sigma: {result.std:.4f} mm")

    from hystogram import Hystogram

    hist = Hystogram(
        dimension=result,
        bins=50,
        xlabel="Dimension (mm)",
        ylabel="Density",
        title="Distribution with Tolerance Limits"
    )
    hist.show_plot()

![Sample of image to be shown](./images/Hystogram.png)

⚙️ Technical Requirements

    Python 3.11

    Main dependencies: numpy.

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