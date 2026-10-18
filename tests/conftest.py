# =============================================================================
# tests/conftest.py  -  shared test setup, loaded automatically by pytest
# =============================================================================
# WHAT IS conftest.py?
#   pytest reads a file with exactly this name before running the tests in
#   its folder. It is where we put things every test file shares:
#     - extra command-line OPTIONS for pytest, and
#     - FIXTURES: functions that prepare something a test needs and hand it
#       to the test automatically.
#
# WHAT THIS FILE ADDS
#   Two options, --euler and --rk4, that choose WHICH implementation the tests
#   check. By default they check our real solvers:
#       python -m pytest
#   But we can point them at a planted bug instead:
#       python -m pytest --rk4=bugs.buggy_solvers:rk4_swapped_weights
#   If the tests are good, that second command must FAIL.
#
#   The value has the form  "module.path:function_name".
# =============================================================================

# importlib is built into Python. Its import_module function imports a module
# whose name is only known as text while the program runs.
import importlib

# Load pytest itself, so we can use its decorators such as @pytest.fixture.
import pytest

# A dictionary: method name -> where the REAL implementation lives.
DEFAULT_IMPLEMENTATIONS = {
    "euler": "simlab.ode_solvers:euler",
    "rk4": "simlab.ode_solvers:rk4",
}


# -----------------------------------------------------------------------------
# A "hook": pytest calls a function with this exact name when it starts up,
# and passes in a "parser" object that we use to register new options.
# -----------------------------------------------------------------------------
def pytest_addoption(parser):
    """Register the --euler and --rk4 command-line options."""
    # Loop over the two methods so we write the option code only once.
    for name, default in DEFAULT_IMPLEMENTATIONS.items():
        parser.addoption(
            f"--{name}",            # the option's name, e.g. "--rk4"
            action="store",         # store whatever text follows the option
            default=default,        # used when the option is not given
            help=f"implementation to test for {name}, as module:function",
        )


# -----------------------------------------------------------------------------
# Turn text like "simlab.ode_solvers:rk4" into the actual function.
# -----------------------------------------------------------------------------
def load_function(spec: str):
    """Import and return the function described by 'module.path:function'."""
    # .split(":") cuts the text at the colon and returns the two pieces as a
    # list; "unpacking" puts them into two names at once.
    module_name, function_name = spec.split(":")
    # Import the module by its name (works like "import simlab.ode_solvers").
    module = importlib.import_module(module_name)
    # getattr(module, "rk4") fetches the thing called "rk4" from the module.
    return getattr(module, function_name)


# -----------------------------------------------------------------------------
# The fixture every solver test uses.
# -----------------------------------------------------------------------------
# @pytest.fixture is a DECORATOR: a line starting with "@" placed just above a
# function, which changes how that function is used. Here it tells pytest:
# "any test that has a parameter named `method` should receive the value this
# function returns".
#
# params=["euler", "rk4"] makes the fixture run TWICE. Every test that uses
# it therefore runs twice, once per method. pytest shows these as, e.g.,
#     test_output_shape[euler]   and   test_output_shape[rk4]
@pytest.fixture(params=["euler", "rk4"])
def method(request):
    """Give the test a (name, solver function) pair for one method."""
    # request.param is the current value from params: "euler" or "rk4".
    name = request.param
    # request.config.getoption("--rk4") reads the option's value (the text).
    spec = request.config.getoption(f"--{name}")
    # A tuple: the method's name and the function to test.
    return name, load_function(spec)
