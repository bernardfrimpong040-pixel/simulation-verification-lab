# =============================================================================
# bugs/__init__.py
# =============================================================================
# This empty-looking file turns the "bugs" folder into a PACKAGE, so the tests
# can load a solver from it by name, for example:
#     bugs.buggy_solvers:rk4_swapped_weights
#
# The "bugs" package holds DELIBERATELY FLAWED code. It is never used for real
# results. Its only job is to prove that our tests catch realistic mistakes.
# =============================================================================
