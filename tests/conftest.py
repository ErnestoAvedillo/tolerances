"""Shared test configuration.

Force a non-interactive matplotlib backend so histogram tests never try to
open a window under CI / headless environments.
"""
import matplotlib

matplotlib.use("Agg")
