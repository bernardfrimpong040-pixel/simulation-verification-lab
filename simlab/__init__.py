# =============================================================================
# simlab/__init__.py
# =============================================================================
# WHAT IS THIS FILE?
#   A folder that contains a file named "__init__.py" is called a PACKAGE.
#   A package is a folder of Python files that other scripts can import from.
#
#   Because this file exists, a script in the main project folder can write:
#       from simlab.ode_solvers import euler
#   which means: "go into the folder simlab, open ode_solvers.py, and bring
#   back the function called euler."
#
#   The file can be (almost) empty. Its presence is what matters.
#   The two underscores on each side ("dunder" = double underscore) mark
#   names that Python itself gives a special meaning.
# =============================================================================

# __version__ is a common convention: a text label saying which version
# of our package this is. We raise it as the project grows (0.1 = Stage 1).
__version__ = "0.1.0"
