# =============================================================================
# run_stage1.py  -  Stage 1: a verified reference solver (convergence study)
# =============================================================================
# WHAT THIS SCRIPT DOES
#   1. Solves y' = y - t^2 + 1, y(0) = 0.5 on [0, 2] with Euler and RK4,
#      using 10, 20, 40, 80, 160 and 320 steps.
#   2. Measures the error against the exact solution each time.
#   3. Measures the observed order of accuracy p (should be 1 and 4).
#   4. Saves a table (CSV) and a log-log plot into results/stage1/.
#   5. Runs a SELF-CHECK and reports PASS or FAIL.
#
# HOW TO RUN (from the project folder, with the .venv activated):
#       python run_stage1.py
#
# WHY A CONVERGENCE STUDY?
#   One correct-looking number proves very little: a buggy solver can still
#   land close to the answer. But a bug almost always ruins the ORDER of
#   accuracy. Checking that the error shrinks at the predicted rate is the
#   standard way simulation engineers verify code, and it is the main tool
#   you will use to judge AI-written simulation code.
# =============================================================================

# --- Imports -----------------------------------------------------------------
# "sys" is built into Python. We use sys.exit() to end the program with a
# PASS (0) or FAIL (1) code that other tools can read.
import sys

# "pathlib" is built into Python. Its Path object handles folder and file
# paths, and works the same on Windows ("\") and Mac/Linux ("/").
from pathlib import Path

# "import matplotlib" loads the plotting library.
import matplotlib

# Choose the "Agg" back-end: it draws pictures straight into image files
# without opening a window. This must come BEFORE importing pyplot.
# It keeps the script working on any computer, even one with no screen.
matplotlib.use("Agg")

# pyplot is matplotlib's main plotting module; "plt" is its standard nickname.
import matplotlib.pyplot as plt

# NumPy for arrays and maths.
import numpy as np

# "from X import a, b" brings specific names out of our own package simlab.
# The brackets let one import statement continue over several lines.
from simlab.ode_solvers import euler, rk4, max_error, observed_orders
from simlab.problems import f_example, exact_example, T0, Y0, T_END


# --- Settings ------------------------------------------------------------------
# A LIST of step counts. Each one doubles the previous, so h halves each time.
STEP_COUNTS = [10, 20, 40, 80, 160, 320]

# A DICTIONARY maps a key to a value: here, method name -> theoretical order.
# Curly braces {} make a dictionary; each entry is  key: value.
EXPECTED_ORDER = {"Euler": 1, "RK4": 4}

# How close the observed order must be to the theory to PASS.
# 0.1 is a common, honest tolerance for a smooth problem like this one.
TOLERANCE = 0.1

# Path(__file__) is the location of THIS script. ".parent" is its folder.
# The "/" operator joins path pieces: project_folder/results/stage1.
OUTPUT_DIR = Path(__file__).parent / "results" / "stage1"


# --- Main program ----------------------------------------------------------------
def main() -> int:
    """Run the convergence study. Return 0 if every check passes, else 1."""

    # Create the output folder. parents=True also creates "results" if it is
    # missing; exist_ok=True means "no error if it already exists".
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Another dictionary: method name -> the solver function itself.
    methods = {"Euler": euler, "RK4": rk4}

    # A LIST COMPREHENSION: a one-line way to build a list.
    # Read it as: "for each n in STEP_COUNTS, compute (T_END - T0) / n".
    # Result: the step size h for every run.
    step_sizes = [(T_END - T0) / n for n in STEP_COUNTS]

    # Empty dictionary to collect results: method name -> list of errors.
    errors = {}

    # Loop over the dictionary's (key, value) pairs.
    # .items() gives both: name = "Euler", solver = the euler function, etc.
    for name, solver in methods.items():
        # Empty list for this method's errors.
        errors[name] = []
        for n in STEP_COUNTS:
            # Solve the ODE. The function returns two arrays; Python
            # "unpacks" them into the two names t and y.
            t, y = solver(f_example, T0, Y0, T_END, n)
            # Compare with the exact solution at the same time points.
            errors[name].append(max_error(y, exact_example(t)))

    # --- Print the convergence table ---------------------------------------------
    print()
    print("Stage 1 convergence study:  y' = y - t^2 + 1,  y(0) = 0.5,  0 <= t <= 2")
    print("=" * 74)  # "=" * 74 repeats the character 74 times: a divider line.
    # In an f-string, {"n":>5} means: right-align the text in 5 characters.
    print(f'{"n":>5} {"h":>9} | {"Euler error":>13} {"order":>6} | {"RK4 error":>13} {"order":>6}')
    print("-" * 74)

    # Work out the observed orders for each method.
    orders = {name: observed_orders(step_sizes, errors[name]) for name in methods}
    # (That line was a DICTIONARY comprehension: same idea as the list one.)

    # enumerate() gives a counter i alongside each item: (0, 10), (1, 20), ...
    for i, n in enumerate(STEP_COUNTS):
        # The first row has no previous run, so it has no order yet.
        # This is a one-line "if/else" (a conditional expression).
        # Format codes:  .4f = 4 decimals,  .3e = scientific notation (1.234e-05),
        # .2f = 2 decimals.  orders[name][i - 1] is the order between run i-1 and i.
        e_order = f"{orders['Euler'][i - 1]:.2f}" if i > 0 else "-"
        r_order = f"{orders['RK4'][i - 1]:.2f}" if i > 0 else "-"
        print(f"{n:>5} {step_sizes[i]:>9.5f} | {errors['Euler'][i]:>13.3e} {e_order:>6} "
              f"| {errors['RK4'][i]:>13.3e} {r_order:>6}")
    print("-" * 74)

    # --- Save the table as a CSV file ----------------------------------------------
    # np.column_stack glues lists side by side as columns of one 2-D array.
    table = np.column_stack([STEP_COUNTS, step_sizes, errors["Euler"], errors["RK4"]])
    # np.savetxt writes the array to a text file.
    #   delimiter=","  -> separate columns with commas (CSV format)
    #   header=...     -> first line with the column names
    #   comments=""    -> stop NumPy putting "#" before the header
    #   fmt=[...]      -> number format for each column
    np.savetxt(
        OUTPUT_DIR / "convergence_table.csv",
        table,
        delimiter=",",
        header="n_steps,h,euler_max_error,rk4_max_error",
        comments="",
        fmt=["%d", "%.6f", "%.6e", "%.6e"],
    )

    # --- Draw the log-log convergence plot -------------------------------------------
    make_plot(step_sizes, errors)

    # --- Self-check: does each observed order match the theory? ----------------------
    print("Self-check (observed order on the finest pair of grids):")
    # Start by assuming everything passes; switch to False on any failure.
    all_passed = True
    for name, expected in EXPECTED_ORDER.items():
        # [-1] picks the LAST item of a list: the finest pair of grids,
        # where the error is closest to the theoretical C * h^p behaviour.
        observed = orders[name][-1]
        # abs(...) is the absolute value. Pass if within TOLERANCE of theory.
        passed = abs(observed - expected) <= TOLERANCE
        # A one-line if/else picks the label to print.
        label = "PASS" if passed else "FAIL"
        print(f"  {name:<6} expected {expected}, observed {observed:.3f}  ->  {label}")
        # "and" is True only if both sides are True: one failure makes it False.
        all_passed = all_passed and passed

    print()
    print(f"Saved: {OUTPUT_DIR / 'convergence_table.csv'}")
    print(f"Saved: {OUTPUT_DIR / 'convergence_plot.png'}")
    print()
    print("RESULT:", "ALL CHECKS PASSED" if all_passed else "SOME CHECKS FAILED")

    # Return 0 for success and 1 for failure (the standard exit codes).
    return 0 if all_passed else 1


def make_plot(step_sizes, errors) -> None:
    """Save a log-log plot of error against step size h."""
    # Colours from a colour-blind-safe palette, plus different marker shapes,
    # so the two lines can be told apart without relying on colour alone.
    styles = {"Euler": ("#2a78d6", "o"), "RK4": ("#eb6834", "s")}

    # plt.subplots() creates a FIGURE (the whole picture) and AXES (the plot
    # area). figsize is width and height in inches.
    fig, ax = plt.subplots(figsize=(7, 5))

    # np.array turns the list into a NumPy array so we can do maths on it.
    h = np.array(step_sizes)

    for name, (colour, marker) in styles.items():
        e = np.array(errors[name])
        # loglog draws a line with BOTH axes on a logarithmic scale.
        # On log-log axes, E = C * h^p becomes a STRAIGHT line of slope p.
        ax.loglog(h, e, color=colour, marker=marker, linewidth=2, markersize=8, label=name)

        # A dashed reference line with the theoretical slope, drawn through
        # the coarsest point:  ref = e[0] * (h / h[0])^p.
        p = EXPECTED_ORDER[name]
        ax.loglog(h, e[0] * (h / h[0]) ** p, color=colour, linestyle="--",
                  linewidth=1, alpha=0.6)
        # Label each line directly at its right-hand end (the largest h).
        ax.annotate(f"{name} (slope {p})", xy=(h[0], e[0]), xytext=(8, 0),
                    textcoords="offset points", va="center", fontsize=10, color="#333333")

    # Axis titles (r"..." is a RAW string so the backslash is kept for maths text).
    ax.set_xlabel(r"step size $h$")
    ax.set_ylabel(r"maximum error $\max_i |y_i - y(t_i)|$")
    ax.set_title("Convergence study: error shrinks like $h^p$ (dashed = theory)")
    # Faint grid lines on major and minor ticks to help read values.
    ax.grid(True, which="both", color="#dddddd", linewidth=0.6)
    # Leave room on the right for the direct labels.
    ax.set_xlim(h.min() * 0.7, h.max() * 3)
    ax.legend(loc="lower right")
    # tight_layout stops labels from being cut off at the edges.
    fig.tight_layout()
    # Save the image. dpi = dots per inch (sharpness).
    fig.savefig(OUTPUT_DIR / "convergence_plot.png", dpi=150)
    # Close the figure to free memory.
    plt.close(fig)


# This line means: "only run main() when this file is run directly
# (python run_stage1.py), not when another file imports it".
# __name__ is set to "__main__" only for the file you actually ran.
if __name__ == "__main__":
    # sys.exit(code) ends the program and hands the code (0 or 1) back
    # to PowerShell, so automated tools can tell whether it passed.
    sys.exit(main())
