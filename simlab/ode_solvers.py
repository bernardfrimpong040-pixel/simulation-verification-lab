# =============================================================================
# simlab/ode_solvers.py
# =============================================================================
# PURPOSE
#   Our REFERENCE SOLVERS for ordinary differential equations (ODEs):
#       y'(t) = f(t, y),   y(t0) = y0
#
#   A "reference solution" is the trusted answer you build yourself, then use
#   to judge other answers (an AI's code, a colleague's result). So these
#   functions are written to be simple, readable and checkable, not clever.
#
#   Methods in this file:
#     euler()  - Euler's method,               error shrinks like h^1
#     rk4()    - classical Runge-Kutta (RK4),  error shrinks like h^4
#   plus two helpers for VERIFICATION:
#     max_error()       - largest gap between numerical and exact answers
#     observed_orders() - measures the order p from a list of errors
# =============================================================================

# Load NumPy (arrays and maths) under its standard nickname np.
import numpy as np


# -----------------------------------------------------------------------------
# A small helper used by both solvers: check the inputs are sensible.
# -----------------------------------------------------------------------------
# A name starting with an underscore, like _check_inputs, is a Python
# convention meaning "internal helper; other files should not need this".
def _check_inputs(t0: float, t_end: float, n_steps: int) -> None:
    """Stop with a clear message if the inputs make no sense."""
    # isinstance(x, int) asks "is x a whole number (an int)?" -> True/False.
    # "not" flips True to False and vice versa.
    # "or" is True if either side is True.
    # So: complain if n_steps is not a whole number, or is zero or negative.
    if not isinstance(n_steps, int) or n_steps < 1:
        # "raise" stops the program and reports an ERROR.
        # ValueError is Python's standard error type for "bad value given".
        # The f"..." is an F-STRING: text in which {n_steps} is replaced by
        # the actual value of the variable n_steps.
        raise ValueError(f"n_steps must be a positive whole number, got {n_steps}")
    # Complain if the time interval runs backwards or has zero length.
    if t_end <= t0:
        raise ValueError(f"t_end ({t_end}) must be greater than t0 ({t0})")
    # "-> None" in the def line means this function returns nothing.
    # It only exists to raise errors when something is wrong.


# -----------------------------------------------------------------------------
# Euler's method
# -----------------------------------------------------------------------------
# Parameters:
#   f       - the function f(t, y). Yes: in Python a function can be passed
#             into another function like any other value.
#   t0, y0  - starting time and starting value
#   t_end   - final time
#   n_steps - how many equal steps to take from t0 to t_end
# Returns TWO things at once (a "tuple"): the array of times and the array
# of approximate y values at those times.
def euler(f, t0: float, y0: float, t_end: float, n_steps: int):
    """Solve y' = f(t, y), y(t0) = y0 with Euler's method.

    Update rule:  y_{i+1} = y_i + h * f(t_i, y_i)
    Global error is O(h): halving h roughly halves the error.
    """
    # Run the safety checks before doing any work.
    _check_inputs(t0, t_end, n_steps)

    # Step size h: the length of the interval divided by the number of steps.
    h = (t_end - t0) / n_steps

    # np.linspace(a, b, k) makes k equally spaced numbers from a to b,
    # INCLUDING both ends. n_steps steps need n_steps + 1 points
    # (like 3 fence sections need 4 posts).
    t = np.linspace(t0, t_end, n_steps + 1)

    # np.zeros(k) makes an array of k zeros. We fill it in below.
    # Creating the full array first ("pre-allocating") is faster and
    # clearer than growing a list one item at a time.
    y = np.zeros(n_steps + 1)

    # Square brackets pick one entry of an array. Python counts from 0,
    # so y[0] is the FIRST entry. Set it to the starting value.
    y[0] = y0

    # A "for" loop repeats the indented block once for each value of i.
    # range(n_steps) produces 0, 1, 2, ..., n_steps - 1 (it stops BEFORE
    # n_steps). That is exactly right: step i computes y[i + 1] from y[i],
    # and the last step computes y[n_steps].
    for i in range(n_steps):
        # Euler's rule: new value = old value + step size * slope at old point.
        y[i + 1] = y[i] + h * f(t[i], y[i])

    # Send both arrays back. The caller writes:  t, y = euler(...)
    return t, y


# -----------------------------------------------------------------------------
# Classical fourth-order Runge-Kutta (RK4)
# -----------------------------------------------------------------------------
def rk4(f, t0: float, y0: float, t_end: float, n_steps: int):
    """Solve y' = f(t, y), y(t0) = y0 with the classical RK4 method.

    Each step samples the slope four times and takes a weighted average:
        k1 = f(t_i,       y_i)
        k2 = f(t_i + h/2, y_i + (h/2) k1)
        k3 = f(t_i + h/2, y_i + (h/2) k2)
        k4 = f(t_i + h,   y_i + h k3)
        y_{i+1} = y_i + (h/6)(k1 + 2 k2 + 2 k3 + k4)
    Global error is O(h^4): halving h divides the error by about 16.
    """
    # Same safety checks, step size, time grid and storage as Euler.
    _check_inputs(t0, t_end, n_steps)
    h = (t_end - t0) / n_steps
    t = np.linspace(t0, t_end, n_steps + 1)
    y = np.zeros(n_steps + 1)
    y[0] = y0

    for i in range(n_steps):
        # Slope at the START of the step.
        k1 = f(t[i], y[i])
        # Slope at the MIDDLE of the step, using k1 to estimate y there.
        k2 = f(t[i] + h / 2, y[i] + (h / 2) * k1)
        # Slope at the MIDDLE again, now using the better estimate k2.
        k3 = f(t[i] + h / 2, y[i] + (h / 2) * k2)
        # Slope at the END of the step, using k3.
        k4 = f(t[i] + h, y[i] + h * k3)
        # Weighted average of the four slopes (weights 1, 2, 2, 1, total 6).
        y[i + 1] = y[i] + (h / 6) * (k1 + 2 * k2 + 2 * k3 + k4)

    return t, y


# -----------------------------------------------------------------------------
# Verification helper 1: how far is the numerical answer from the exact one?
# -----------------------------------------------------------------------------
def max_error(y_numerical, y_exact) -> float:
    """Largest absolute difference over all time points (the 'max norm')."""
    # Subtracting two NumPy arrays subtracts entry by entry.
    # np.abs takes the absolute value of every entry (removes minus signs).
    # np.max returns the largest entry.
    # float(...) converts NumPy's number type into a plain Python float,
    # which prints more cleanly.
    return float(np.max(np.abs(y_numerical - y_exact)))


# -----------------------------------------------------------------------------
# Verification helper 2: measure the ORDER OF ACCURACY p.
# -----------------------------------------------------------------------------
# Theory says error E is about C * h^p. For two step sizes h1 and h2:
#     E1 / E2 = (h1 / h2)^p   =>   p = ln(E1 / E2) / ln(h1 / h2)
# Given matching lists of step sizes and errors, return one p for each
# neighbouring pair. If p settles near the theoretical value (1 for Euler,
# 4 for RK4), the code is behaving correctly.
def observed_orders(step_sizes, errors):
    """Observed order p between each pair of consecutive runs."""
    # Start with an empty list. Lists are written with square brackets.
    orders = []
    # len(errors) is how many errors we have. With k errors there are
    # k - 1 neighbouring pairs, so i goes 0, 1, ..., k - 2.
    for i in range(len(errors) - 1):
        # np.log is the NATURAL logarithm (ln).
        p = np.log(errors[i] / errors[i + 1]) / np.log(step_sizes[i] / step_sizes[i + 1])
        # .append(...) adds one item to the end of a list.
        orders.append(float(p))
    return orders
