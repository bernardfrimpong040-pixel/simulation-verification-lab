# =============================================================================
# simlab/problems.py
# =============================================================================
# PURPOSE
#   Store TEST PROBLEMS whose EXACT answer we already know.
#
# WHY THIS MATTERS FOR AI-TRAINER WORK
#   When an AI (or a person) gives you a numerical answer, you cannot judge it
#   unless you have something trustworthy to compare it against. The most
#   trustworthy comparison is an exact formula. This is called a
#   "manufactured" or "analytic" test problem, and checking code against it
#   is called VERIFICATION.
#
# THE PROBLEM IN THIS FILE (Initial Value Problem, "IVP")
#   Differential equation:   y'(t) = y - t^2 + 1
#   Starting value:          y(0)  = 0.5
#   Time interval:           0 <= t <= 2
#   Exact solution:          y(t)  = (t + 1)^2 - 0.5 * e^t
#
#   (This is a classic textbook problem from Burden & Faires,
#    "Numerical Analysis". STAGE1_GUIDE.md proves the exact solution is right.)
# =============================================================================

# "import numpy as np"
#   import  -> load a library (a toolbox of ready-made code) into this file.
#   numpy   -> the standard Python library for numbers, arrays and maths.
#   as np   -> give it the short nickname "np", so we type np.exp instead
#              of numpy.exp. Every professional uses this same nickname.
import numpy as np


# -----------------------------------------------------------------------------
# Constants: values that never change while the program runs.
# Writing names in CAPITAL_LETTERS is the Python convention for "constant".
# -----------------------------------------------------------------------------

# The starting time t0.  "0.0" (not "0") makes it a decimal number (a "float").
T0 = 0.0

# The starting value y(t0) = y(0).
Y0 = 0.5

# The final time we solve up to.
T_END = 2.0


# -----------------------------------------------------------------------------
# The right-hand side of the differential equation, f(t, y).
# -----------------------------------------------------------------------------
# "def" starts the definition of a FUNCTION (a reusable, named block of code).
#   f_example        -> the function's name.
#   (t: float, y: float) -> its two INPUTS (called "parameters").
#       ": float" is a TYPE HINT. It tells the reader "t should be a decimal
#       number". Python does NOT enforce it; it is documentation that
#       professional code always includes, and editors like VS Code use it
#       to warn you about mistakes.
#   -> float         -> type hint for the OUTPUT: this function returns a float.
#   The colon ":" at the end means "the body of the function starts on the
#   next lines". The body MUST be indented (4 spaces). Indentation is how
#   Python knows which lines belong to the function.
def f_example(t: float, y: float) -> float:
    # A text in triple quotes right under "def" is a DOCSTRING: the function's
    # built-in manual. Typing help(f_example) in Python prints it.
    """Right-hand side of y' = y - t^2 + 1."""
    # "return" sends a value back to whoever called the function.
    # "**" is Python's POWER operator:  t**2 means t squared.
    # (Careful: "^" does NOT mean power in Python. That is a common AI and
    #  beginner mistake, worth remembering when you grade code.)
    return y - t**2 + 1


# -----------------------------------------------------------------------------
# The exact solution y(t), so we can measure the error of a numerical method.
# -----------------------------------------------------------------------------
# The input t can be a single number OR a whole NumPy array of times.
# np.exp works on both: given an array, it computes e^t for every entry
# at once. This "whole-array at once" style is called VECTORISATION.
def exact_example(t):
    """Exact solution y(t) = (t + 1)^2 - 0.5 e^t."""
    # np.exp(t) is e raised to the power t (e = 2.71828...).
    return (t + 1) ** 2 - 0.5 * np.exp(t)
