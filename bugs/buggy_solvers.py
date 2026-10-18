# =============================================================================
# bugs/buggy_solvers.py  -  deliberately flawed solvers ("planted bugs")
# =============================================================================
# PURPOSE
#   A test suite is only useful if it FAILS on wrong code. The way to prove
#   that is to plant realistic bugs and check the tests catch every one.
#   This idea is called MUTATION TESTING; each planted bug is a "mutant".
#   A mutant the tests catch is "killed"; one they miss "survives".
#
#   Every bug below is the kind of mistake a person or an AI coding agent
#   really makes: each one runs without crashing and returns believable
#   numbers. That is what makes them dangerous.
#
#   The file ALSO contains one CORRECT solver written in a different style.
#   Good tests must PASS it. Tests that reject correct-but-different code
#   are as bad as tests that accept wrong code: both fail to "reliably
#   distinguish correct solutions from flawed ones".
#
# Each function has the same inputs and outputs as the real solvers in
# simlab/ode_solvers.py, so the tests can swap them in.
#
# HOW TO READ THIS FILE
#   Bug 1 is commented line by line. Bugs 2-6 copy the same lines, so their
#   comments focus on the ONE line that is different, marked "PLANTED BUG".
#   Comparing a mutant with the real solver to find that one line is itself
#   good practice for reviewing code.
# =============================================================================

# Load NumPy under its standard nickname np.
import numpy as np

# Reuse the real input checks, so each mutant differs from the real solver
# in ONE way only: the planted bug. (Bug 5 deliberately leaves them out.)
# The leading underscore says _check_inputs is an internal helper; importing
# it here is fine because this file is part of our own project.
from simlab.ode_solvers import _check_inputs


# -----------------------------------------------------------------------------
# BUG 1: RK4 with two weights swapped
# -----------------------------------------------------------------------------
def rk4_swapped_weights(f, t0, y0, t_end, n_steps):
    """BUG: uses weights (1, 2, 1, 2) instead of (1, 2, 2, 1).

    Why it looks right: the weights still add up to 6, so the formula
    "looks balanced", and the answers are close to the truth.
    What actually happens: the order of accuracy drops from 4 to 1.
    """
    # Stop with a clear error if the inputs make no sense.
    _check_inputs(t0, t_end, n_steps)
    # Step size: interval length divided by the number of steps.
    h = (t_end - t0) / n_steps
    # n_steps + 1 equally spaced times from t0 to t_end (both ends included).
    t = np.linspace(t0, t_end, n_steps + 1)
    # An array of zeros to fill with the solution values.
    y = np.zeros(n_steps + 1)
    # The first value is the starting value.
    y[0] = y0
    # Take n_steps steps: i = 0, 1, ..., n_steps - 1.
    for i in range(n_steps):
        # Slope at the start of the step.
        k1 = f(t[i], y[i])
        # Slope at the midpoint, using k1.
        k2 = f(t[i] + h / 2, y[i] + (h / 2) * k1)
        # Slope at the midpoint, using k2.
        k3 = f(t[i] + h / 2, y[i] + (h / 2) * k2)
        # Slope at the end of the step, using k3.
        k4 = f(t[i] + h, y[i] + h * k3)
        # PLANTED BUG: k3 gets weight 1 and k4 gets weight 2.
        # Correct line:  y[i + 1] = y[i] + (h / 6) * (k1 + 2 * k2 + 2 * k3 + k4)
        y[i + 1] = y[i] + (h / 6) * (k1 + 2 * k2 + k3 + 2 * k4)
    # Return the times and the (wrong) solution values.
    return t, y


# -----------------------------------------------------------------------------
# BUG 2: RK4 evaluates the second slope at the wrong time
# -----------------------------------------------------------------------------
def rk4_wrong_stage_time(f, t0, y0, t_end, n_steps):
    """BUG: k2 is evaluated at time t + h instead of the midpoint t + h/2.

    Why it looks right: a one-character slip ("h" instead of "h / 2") in a
    long formula. For problems where f does not depend on t, it gives the
    correct answer, so a careless check might pass it.
    """
    _check_inputs(t0, t_end, n_steps)
    h = (t_end - t0) / n_steps
    t = np.linspace(t0, t_end, n_steps + 1)
    y = np.zeros(n_steps + 1)
    y[0] = y0
    for i in range(n_steps):
        k1 = f(t[i], y[i])
        # PLANTED BUG: the time should be t[i] + h / 2.
        k2 = f(t[i] + h, y[i] + (h / 2) * k1)
        k3 = f(t[i] + h / 2, y[i] + (h / 2) * k2)
        k4 = f(t[i] + h, y[i] + h * k3)
        y[i + 1] = y[i] + (h / 6) * (k1 + 2 * k2 + 2 * k3 + k4)
    return t, y


# -----------------------------------------------------------------------------
# BUG 3: Euler stops one step early (an "off-by-one" error)
# -----------------------------------------------------------------------------
def euler_off_by_one(f, t0, y0, t_end, n_steps):
    """BUG: the loop runs n_steps - 1 times, so the last value is never computed.

    Why it looks right: the arrays still have the correct length, and every
    value except the last one is correct. The final entry stays at 0.0,
    which is easy to miss if you only plot or print the start of the array.
    """
    _check_inputs(t0, t_end, n_steps)
    h = (t_end - t0) / n_steps
    t = np.linspace(t0, t_end, n_steps + 1)
    y = np.zeros(n_steps + 1)
    y[0] = y0
    # PLANTED BUG: should be range(n_steps).
    for i in range(n_steps - 1):
        y[i + 1] = y[i] + h * f(t[i], y[i])
    return t, y


# -----------------------------------------------------------------------------
# BUG 4: Euler with a hard-coded step size
# -----------------------------------------------------------------------------
def euler_fixed_step(f, t0, y0, t_end, n_steps):
    """BUG: h is fixed at 0.2 instead of being computed from n_steps.

    Why it looks right: 0.2 was copied from a textbook example (n_steps = 10
    on [0, 2]). With exactly those settings the answer is perfect, so a
    single known-answer check passes. Any other n_steps gives wrong results.
    """
    _check_inputs(t0, t_end, n_steps)
    # PLANTED BUG: should be h = (t_end - t0) / n_steps.
    h = 0.2
    t = np.linspace(t0, t_end, n_steps + 1)
    y = np.zeros(n_steps + 1)
    y[0] = y0
    for i in range(n_steps):
        y[i + 1] = y[i] + h * f(t[i], y[i])
    return t, y


# -----------------------------------------------------------------------------
# BUG 5: RK4 with no input checks
# -----------------------------------------------------------------------------
def rk4_no_input_checks(f, t0, y0, t_end, n_steps):
    """BUG: the input checks were removed.

    Why it looks right: every normal call gives exactly the right answer.
    What goes wrong: with t_end < t0 it silently integrates BACKWARDS and
    returns numbers with no warning; with n_steps = 0 it crashes with a
    confusing ZeroDivisionError instead of a clear message.
    """
    # PLANTED BUG: no call to _check_inputs here.
    h = (t_end - t0) / n_steps
    t = np.linspace(t0, t_end, n_steps + 1)
    y = np.zeros(n_steps + 1)
    y[0] = y0
    for i in range(n_steps):
        k1 = f(t[i], y[i])
        k2 = f(t[i] + h / 2, y[i] + (h / 2) * k1)
        k3 = f(t[i] + h / 2, y[i] + (h / 2) * k2)
        k4 = f(t[i] + h, y[i] + h * k3)
        y[i + 1] = y[i] + (h / 6) * (k1 + 2 * k2 + 2 * k3 + k4)
    return t, y


# -----------------------------------------------------------------------------
# BUG 6: Euler uses the slope at the wrong time
# -----------------------------------------------------------------------------
def euler_wrong_slope_time(f, t0, y0, t_end, n_steps):
    """BUG: uses f(t_{i+1}, y_i) instead of f(t_i, y_i).

    Why it looks right: it still converges, and still at order 1, so a
    convergence study alone does NOT catch it. It is simply not Euler's
    method, so it gives different numbers from the method that was asked for.
    """
    _check_inputs(t0, t_end, n_steps)
    h = (t_end - t0) / n_steps
    t = np.linspace(t0, t_end, n_steps + 1)
    y = np.zeros(n_steps + 1)
    y[0] = y0
    for i in range(n_steps):
        # PLANTED BUG: the time should be t[i], not t[i + 1].
        y[i + 1] = y[i] + h * f(t[i + 1], y[i])
    return t, y


# -----------------------------------------------------------------------------
# NOT A BUG: a correct RK4 written in a different style
# -----------------------------------------------------------------------------
def rk4_alternative_correct(f, t0, y0, t_end, n_steps):
    """CORRECT RK4, written differently from ours. The tests must PASS it.

    Differences from simlab.ode_solvers.rk4:
      - builds Python lists with .append() instead of filling NumPy arrays;
      - computes each time as t0 + i * h instead of using np.linspace.
    The second point matters: t0 + n_steps * h can differ from t_end in the
    last few digits (rounding). For example, with t0 = 0, t_end = 1.7 and
    10 steps, it ends at 1.6999999999999998, not 1.7. A test that demands
    t[-1] == t_end EXACTLY would wrongly fail this correct solver, so our
    tests compare with a tolerance (pytest.approx).
    """
    _check_inputs(t0, t_end, n_steps)
    h = (t_end - t0) / n_steps
    # Two Python lists that start with the starting time and value.
    times = [t0]
    values = [y0]
    for i in range(n_steps):
        # The time at the start of step i, computed directly.
        t_i = t0 + i * h
        # values[-1] is the most recent value: where this step starts.
        y_i = values[-1]
        k1 = f(t_i, y_i)
        k2 = f(t_i + h / 2, y_i + (h / 2) * k1)
        k3 = f(t_i + h / 2, y_i + (h / 2) * k2)
        k4 = f(t_i + h, y_i + h * k3)
        # Add the new value and the new time to the ends of the lists.
        values.append(y_i + (h / 6) * (k1 + 2 * k2 + 2 * k3 + k4))
        times.append(t0 + (i + 1) * h)
    # np.array converts the lists into NumPy arrays, the same output type
    # as our solvers.
    return np.array(times), np.array(values)
