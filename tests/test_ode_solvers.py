# =============================================================================
# tests/test_ode_solvers.py  -  automatic checks for the ODE solvers
# =============================================================================
# HOW PYTEST WORKS (the 3 rules you need)
#   1. pytest finds files whose names start with "test_".
#   2. Inside them, it runs every function whose name starts with "test_".
#   3. A test PASSES if it finishes normally, and FAILS if any `assert`
#      statement inside it is False (or if an unexpected error happens).
#
#   "assert condition, message" means: "I claim this is True. If it isn't,
#   stop this test, mark it FAILED and show the message."
#
# THE KINDS OF CHECK IN THIS FILE (each catches different bugs)
#   A. Contract      - outputs have the right shape, start and end points
#   B. Special case  - a problem the method must solve EXACTLY
#   C. Known answer  - matches a published textbook value
#   D. Accuracy      - small error on a fine grid
#   E. Order         - error shrinks at the theoretical rate h^p
#   F. Independent   - agrees with a trusted library (SciPy) on a problem
#      reference       with no exact formula
#   G. Bad input     - nonsense inputs are refused with a clear error
#   H. Helpers       - the verification tools themselves are correct
#
# Every solver test takes the `method` fixture from conftest.py, so it runs
# twice: once for Euler and once for RK4.
# =============================================================================

# "math" is built into Python; we use math.isfinite to reject inf and nan.
import math

# NumPy for arrays and maths.
import numpy as np

# pytest gives us pytest.approx, pytest.raises and pytest.mark.parametrize.
import pytest

# SciPy's general-purpose ODE solver, used as an INDEPENDENT reference.
from scipy.integrate import solve_ivp

# Our verification helpers and our test problem.
from simlab.ode_solvers import max_error, observed_orders
from simlab.problems import f_example, exact_example, T0, Y0, T_END


# -----------------------------------------------------------------------------
# Expected values, kept in dictionaries keyed by method name.
# -----------------------------------------------------------------------------

# Theoretical order of accuracy p.
EXPECTED_ORDER = {"euler": 1, "rk4": 4}

# Burden & Faires, "Numerical Analysis": y(2) for our problem with h = 0.2
# (10 steps), given to 7 decimal places.
TEXTBOOK_Y2 = {"euler": 4.8657845, "rk4": 5.3053630}

# Largest error we accept on the fine grid (320 steps). Our measured errors
# are 1.67e-2 (Euler) and 1.09e-10 (RK4); each limit leaves a safety margin.
FINE_GRID_TOLERANCE = {"euler": 0.02, "rk4": 1e-9}

# Largest difference from SciPy we accept on the cross-check problem
# (400 steps). Measured: 2.3e-3 (Euler) and 8.5e-12 (RK4).
SCIPY_TOLERANCE = {"euler": 5e-3, "rk4": 1e-9}


# =============================================================================
# A. CONTRACT: the outputs have the right form
# =============================================================================
def test_output_shape(method):
    """Arrays have n_steps + 1 entries, start at (t0, y0) and end at t_end.

    Uses t_end = 1.7 and 10 steps on purpose: then t0 + 10*h comes out as
    1.6999999999999998, not exactly 1.7 (computer rounding). A CORRECT
    solver may produce either, so we compare with pytest.approx, never "==".
    """
    # Unpack the (name, function) pair that the fixture provides.
    name, solve = method
    # Run the solver on a small problem.
    t, y = solve(f_example, 0.0, 0.5, 1.7, 10)

    # len(...) is the number of entries in an array.
    assert len(t) == 11, f"{name}: expected 11 times, got {len(t)}"
    assert len(y) == 11, f"{name}: expected 11 values, got {len(y)}"
    # pytest.approx(x) means "equal to x up to tiny rounding differences".
    assert t[0] == pytest.approx(0.0), f"{name}: first time is not t0"
    assert t[-1] == pytest.approx(1.7), f"{name}: last time {t[-1]} is not t_end"
    assert y[0] == pytest.approx(0.5), f"{name}: first value is not y0"
    # np.diff(t) gives the gaps t[1]-t[0], t[2]-t[1], ...; all must be > 0.
    # np.all(...) is True only if every entry is True.
    assert np.all(np.diff(t) > 0), f"{name}: times are not increasing"
    # np.isfinite flags inf and nan (the signs of a blown-up computation).
    assert np.all(np.isfinite(y)), f"{name}: solution contains inf or nan"


# =============================================================================
# B. SPECIAL CASE: problems each method must solve exactly
# =============================================================================
# Euler follows straight lines, so it is EXACT when the slope is constant:
#     y' = 3,  y(0) = 1   ->   y = 1 + 3t
# RK4 reduces to Simpson's rule when f depends only on t, and Simpson's rule
# is exact for polynomials up to degree 3, so RK4 is EXACT for:
#     y' = 4t^3,  y(0) = 1   ->   y = t^4 + 1
# "lambda t, y: 3.0" is a LAMBDA: a tiny one-line function with no name.
# It is the same as:  def f(t, y): return 3.0
EXACT_CASES = {
    "euler": (lambda t, y: 3.0, lambda t: 1 + 3 * t),
    "rk4": (lambda t, y: 4 * t**3, lambda t: t**4 + 1),
}


def test_exact_for_special_case(method):
    """Each method reproduces its special-case solution to rounding error."""
    name, solve = method
    # Unpack the right-hand side and exact solution for this method.
    f, exact = EXACT_CASES[name]
    # Only 5 large steps: an exact method needs no small steps.
    t, y = solve(f, 0.0, 1.0, 2.0, 5)
    error = max_error(y, exact(t))
    # 1e-12 is "zero up to rounding" for numbers of this size.
    assert error < 1e-12, f"{name}: should be exact here, but error = {error:.3e}"


# =============================================================================
# C. KNOWN ANSWER: agreement with a published value
# =============================================================================
def test_matches_textbook_value(method):
    """y(2) with h = 0.2 matches the textbook table to 7 decimal places."""
    name, solve = method
    t, y = solve(f_example, T0, Y0, T_END, 10)
    # abs=1e-7 means "within 0.0000001", i.e. the 7 printed decimals.
    assert y[-1] == pytest.approx(TEXTBOOK_Y2[name], abs=1e-7), (
        f"{name}: y(2) = {y[-1]:.7f}, textbook says {TEXTBOOK_Y2[name]:.7f}"
    )


# =============================================================================
# D. ACCURACY: small error on a fine grid
# =============================================================================
def test_accurate_on_fine_grid(method):
    """With 320 steps the maximum error is below the method's tolerance."""
    name, solve = method
    t, y = solve(f_example, T0, Y0, T_END, 320)
    error = max_error(y, exact_example(t))
    assert error < FINE_GRID_TOLERANCE[name], (
        f"{name}: error {error:.3e} exceeds {FINE_GRID_TOLERANCE[name]:.0e}"
    )


# =============================================================================
# E. ORDER: the error shrinks at the theoretical rate
# =============================================================================
def test_order_of_accuracy(method):
    """Observed order on the finest pair of grids is within 0.1 of theory."""
    name, solve = method
    step_counts = [40, 80, 160, 320]
    # List comprehensions: one step size and one error per grid.
    step_sizes = [(T_END - T0) / n for n in step_counts]
    errors = []
    for n in step_counts:
        t, y = solve(f_example, T0, Y0, T_END, n)
        errors.append(max_error(y, exact_example(t)))

    # The last entry is the order between the two finest grids.
    observed = observed_orders(step_sizes, errors)[-1]
    expected = EXPECTED_ORDER[name]
    # A broken solver can produce inf or nan; that must count as a failure.
    assert math.isfinite(observed), f"{name}: observed order is {observed}"
    assert abs(observed - expected) <= 0.1, (
        f"{name}: observed order {observed:.3f}, expected {expected}"
    )


# =============================================================================
# F. INDEPENDENT REFERENCE: agreement with SciPy
# =============================================================================
# y' = cos(t * y), y(0) = 1 has NO formula for its solution. When there is no
# exact answer, the professional approach is to compare with a trusted,
# independently written solver run at very high accuracy. SciPy's DOP853 is
# an 8th-order method; rtol and atol of 1e-12 make it far more accurate than
# the methods being tested, so its answer can serve as "the truth".
def f_cross_check(t, y):
    """Right-hand side y' = cos(t * y) for the SciPy cross-check."""
    return np.cos(t * y)


def test_agrees_with_scipy(method):
    """Our solver matches SciPy's high-accuracy solution on a nonlinear ODE."""
    name, solve = method
    t, y = solve(f_cross_check, 0.0, 1.0, 2.0, 400)

    # solve_ivp(f, (start, end), [start values], ...) solves the ODE.
    #   dense_output=True lets us evaluate SciPy's solution at ANY time,
    #   so we can compare at exactly our time points.
    reference = solve_ivp(
        f_cross_check, (0.0, 2.0), [1.0],
        method="DOP853", rtol=1e-12, atol=1e-12, dense_output=True,
    )
    # reference.sol(t) returns a 2-D array (one row per equation); [0] takes
    # the row for our single equation.
    y_reference = reference.sol(t)[0]

    difference = max_error(y, y_reference)
    assert difference < SCIPY_TOLERANCE[name], (
        f"{name}: differs from SciPy by {difference:.3e}"
    )


# =============================================================================
# G. BAD INPUT: nonsense is refused with a clear ValueError
# =============================================================================
# @pytest.mark.parametrize runs the test once for EACH entry in the list.
#   "t0, t_end, n_steps" names the three values each entry supplies.
#   ids=[...] gives each case a readable label in the test report.
# Combined with the `method` fixture, this test runs 2 x 5 = 10 times.
@pytest.mark.parametrize(
    "t0, t_end, n_steps",
    [
        (0.0, 2.0, 0),      # zero steps
        (0.0, 2.0, -5),     # negative steps
        (0.0, 2.0, 2.5),    # not a whole number
        (2.0, 2.0, 10),     # interval of zero length
        (2.0, 0.0, 10),     # interval runs backwards
    ],
    ids=["zero-steps", "negative-steps", "fractional-steps",
         "empty-interval", "backwards-interval"],
)
def test_rejects_invalid_input(method, t0, t_end, n_steps):
    """Invalid inputs raise ValueError, not a confusing crash or silent nonsense."""
    name, solve = method
    # "with pytest.raises(ValueError):" means: the indented code MUST raise a
    # ValueError. If it raises nothing, or a different error, the test fails.
    with pytest.raises(ValueError):
        solve(f_example, t0, 0.5, t_end, n_steps)


# =============================================================================
# H. HELPERS: test the verification tools themselves
# =============================================================================
# If max_error or observed_orders were wrong, every test above would be
# measuring with a broken ruler. So we check them on inputs whose answers we
# can work out by hand.
def test_max_error_known_values():
    """Largest absolute difference of [1, 2, 3] and [1, 2.5, 2.9] is 0.5."""
    # Differences: |1-1| = 0, |2-2.5| = 0.5, |3-2.9| = 0.1  ->  max 0.5
    assert max_error(np.array([1.0, 2.0, 3.0]), np.array([1.0, 2.5, 2.9])) == pytest.approx(0.5)


def test_observed_orders_recovers_known_power():
    """For errors made to be exactly E = 3h^2, every observed order is 2."""
    step_sizes = [0.4, 0.2, 0.1, 0.05]
    errors = [3 * h**2 for h in step_sizes]
    # pytest.approx also works on whole lists.
    assert observed_orders(step_sizes, errors) == pytest.approx([2.0, 2.0, 2.0])
