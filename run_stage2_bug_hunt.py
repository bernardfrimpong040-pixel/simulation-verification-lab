# =============================================================================
# run_stage2_bug_hunt.py  -  Stage 2: do our tests catch every planted bug?
# =============================================================================
# WHAT THIS SCRIPT DOES
#   1. Runs the full test suite on our REAL solvers. Everything must pass;
#      otherwise a failure later would mean nothing.
#   2. Runs the suite again for each PLANTED BUG in bugs/buggy_solvers.py,
#      swapping the bug in with the --euler or --rk4 option.
#   3. Runs it for a CORRECT alternative solver, which must pass everything.
#   4. Prints which tests caught which bug, and saves a report to
#      results/stage2/ (Markdown table + CSV).
#
# HOW TO RUN (project folder, .venv active):
#       python run_stage2_bug_hunt.py
#
# HOW IT RUNS PYTEST
#   It starts pytest as a separate program (a "subprocess") for each case and
#   asks pytest to write its results as an XML file (--junitxml). XML is a
#   structured text format, so the script can read exactly which tests
#   failed instead of guessing from printed text.
# =============================================================================

# --- Imports (all built into Python) -------------------------------------------
# csv: write comma-separated files.
import csv
# subprocess: run another program (here, pytest) from inside Python.
import subprocess
# sys: sys.executable is the path of the Python running this script (the one
# inside .venv), and sys.exit ends the program with a PASS/FAIL code.
import sys
# tempfile: create a temporary folder that is deleted automatically.
import tempfile
# ElementTree: read XML files. "as ET" is its standard nickname.
import xml.etree.ElementTree as ET
# Path: handle file and folder paths on any operating system.
from pathlib import Path


# --- Settings ------------------------------------------------------------------
# The folder this script lives in, i.e. the project folder.
PROJECT_DIR = Path(__file__).parent
# Where the report goes.
OUTPUT_DIR = PROJECT_DIR / "results" / "stage2"

# Every case to run. Each entry is a DICTIONARY with:
#   name     - the function's name in bugs/buggy_solvers.py
#   method   - which solver it replaces: "euler" or "rk4"
#   correct  - True if it is correct code (must PASS), False if it is a bug
#   summary  - one line describing the bug
CASES = [
    {"name": "rk4_swapped_weights", "method": "rk4", "correct": False,
     "summary": "weights (1,2,1,2) instead of (1,2,2,1)"},
    {"name": "rk4_wrong_stage_time", "method": "rk4", "correct": False,
     "summary": "k2 evaluated at t+h instead of t+h/2"},
    {"name": "rk4_no_input_checks", "method": "rk4", "correct": False,
     "summary": "input validation removed"},
    {"name": "euler_off_by_one", "method": "euler", "correct": False,
     "summary": "loop stops one step early"},
    {"name": "euler_fixed_step", "method": "euler", "correct": False,
     "summary": "step size hard-coded to 0.2"},
    {"name": "euler_wrong_slope_time", "method": "euler", "correct": False,
     "summary": "slope taken at t_{i+1} instead of t_i"},
    {"name": "rk4_alternative_correct", "method": "rk4", "correct": True,
     "summary": "correct RK4 written in a different style"},
]

# Map each test FUNCTION name to the kind of check it performs (the letters
# match the sections in tests/test_ode_solvers.py).
CHECK_KINDS = {
    "test_output_shape": "A. Contract",
    "test_exact_for_special_case": "B. Special case",
    "test_matches_textbook_value": "C. Known answer",
    "test_accurate_on_fine_grid": "D. Accuracy",
    "test_order_of_accuracy": "E. Order",
    "test_agrees_with_scipy": "F. SciPy reference",
    "test_rejects_invalid_input": "G. Bad input",
}


# --- Run pytest once and collect the failing tests -----------------------------
def run_pytest(extra_options: list[str], xml_path: Path) -> list[str]:
    """Run the test suite and return the names of the tests that failed.

    `list[str]` is a type hint meaning "a list of text strings".
    """
    # The command, as a list of pieces. It is the same as typing:
    #   python -m pytest -q -p no:cacheprovider --junitxml=<file> <options>
    #   -q                  quiet output (we read the XML instead)
    #   -p no:cacheprovider don't write pytest's cache folder
    command = [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider",
               f"--junitxml={xml_path}"] + extra_options

    # subprocess.run starts the command and waits for it to finish.
    #   cwd=PROJECT_DIR      run it from the project folder
    #   capture_output=True  keep pytest's printed text out of our screen
    #   text=True            treat that captured output as text
    subprocess.run(command, cwd=PROJECT_DIR, capture_output=True, text=True)

    # Read the XML file pytest wrote. .getroot() gives the top element.
    root = ET.parse(xml_path).getroot()
    failed = []
    # .iter("testcase") visits every <testcase> element: one per test run.
    for case in root.iter("testcase"):
        # A test failed if its element contains a <failure> or <error> element.
        # case.find("failure") returns that element, or None if there isn't one.
        # "is not None" checks that something was found.
        if case.find("failure") is not None or case.find("error") is not None:
            # .get("name") reads an attribute, e.g. "test_order_of_accuracy[rk4]".
            failed.append(case.get("name"))
    return failed


def kind_of(test_name: str) -> str:
    """Turn 'test_order_of_accuracy[rk4]' into its check kind, 'E. Order'."""
    # .split("[")[0] keeps the text before the first "[": the function name.
    return CHECK_KINDS[test_name.split("[")[0]]


# --- Main program ----------------------------------------------------------------
def main() -> int:
    """Run the bug hunt. Return 0 if the tests behave perfectly, else 1."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # "with ... as tmp:" opens a temporary folder and deletes it automatically
    # when the indented block ends. Code that cleans up after itself like this
    # is called a CONTEXT MANAGER.
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)

        # --- Step 1: baseline, the real solvers ---------------------------------
        print("\nStep 1: running all tests on the REAL solvers ...")
        baseline_failures = run_pytest([], tmp_dir / "baseline.xml")
        if baseline_failures:  # a non-empty list counts as True
            print("  The real solvers FAIL these tests, so the bug hunt is meaningless:")
            for name in baseline_failures:
                print(f"   - {name}")
            return 1
        print("  All tests pass on the real solvers.  ✓")

        # --- Step 2: every planted bug and the correct alternative ---------------
        print("\nStep 2: swapping in each planted bug ...\n")
        rows = []  # one dictionary of results per case
        for case in CASES:
            # Build the option, e.g. --rk4=bugs.buggy_solvers:rk4_swapped_weights
            option = f"--{case['method']}=bugs.buggy_solvers:{case['name']}"
            failures = run_pytest([option], tmp_dir / f"{case['name']}.xml")
            # A SET keeps each item once, so repeated kinds (e.g. 4 bad-input
            # cases) are counted once. sorted() turns it into an ordered list.
            kinds = sorted({kind_of(name) for name in failures})
            caught = len(failures) > 0
            # The tests behaved correctly if they caught a bug, or passed a
            # correct solver. "!=" means "is not equal to".
            behaved_well = caught != case["correct"]
            rows.append({**case, "failures": failures, "kinds": kinds,
                         "caught": caught, "ok": behaved_well})
            # ({**case, ...} copies every entry of `case` into a new
            #  dictionary and adds the new entries after it.)

    # --- Print the results --------------------------------------------------------
    print(f"{'Case':<26} {'Type':<8} {'Failed tests':>12}  Result")
    print("-" * 74)
    for row in rows:
        kind_label = "correct" if row["correct"] else "bug"
        if row["correct"]:
            result = "passed all tests ✓" if row["ok"] else "WRONGLY REJECTED ✗"
        else:
            result = "CAUGHT ✓" if row["ok"] else "MISSED ✗"
        print(f"{row['name']:<26} {kind_label:<8} {len(row['failures']):>12}  {result}")
    print("-" * 74)

    # all(...) is True only if every item is True.
    all_ok = all(row["ok"] for row in rows)
    n_bugs = sum(1 for row in rows if not row["correct"])
    n_caught = sum(1 for row in rows if not row["correct"] and row["caught"])
    print(f"\nBugs caught: {n_caught} of {n_bugs}")

    # --- Save the report ----------------------------------------------------------
    save_csv(rows)
    save_markdown(rows, n_caught, n_bugs)
    print(f"Saved: {OUTPUT_DIR / 'bug_hunt.csv'}")
    print(f"Saved: {OUTPUT_DIR / 'bug_hunt_report.md'}")
    print("\nRESULT:", "TESTS CATCH EVERY BUG AND PASS CORRECT CODE" if all_ok
          else "TESTS NEED IMPROVING")
    return 0 if all_ok else 1


def save_csv(rows) -> None:
    """Write one line per case to bug_hunt.csv."""
    # open(..., "w") opens a file for WRITING (it replaces any old file).
    #   newline=""  stops Windows adding blank lines between CSV rows
    #   encoding="utf-8"  allows any characters to be saved safely
    with open(OUTPUT_DIR / "bug_hunt.csv", "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        # writerow writes one line; a list becomes the comma-separated columns.
        writer.writerow(["case", "method", "is_correct_code", "tests_failed",
                         "check_kinds_that_failed", "tests_behaved_correctly"])
        for row in rows:
            writer.writerow([row["name"], row["method"], row["correct"],
                             len(row["failures"]), "; ".join(row["kinds"]), row["ok"]])
            # "; ".join(list) glues the list items into one text, separated by "; ".


def save_markdown(rows, n_caught: int, n_bugs: int) -> None:
    """Write a 'catch matrix' showing which kind of check caught which bug."""
    kinds = list(CHECK_KINDS.values())
    # Build the report as a list of text lines, then join them at the end.
    lines = [
        "# Stage 2 bug hunt",
        "",
        f"**Bugs caught: {n_caught} of {n_bugs}.** "
        "✗ = this kind of check FAILED the solver (caught it); · = passed.",
        "",
        # The header row: "| Case | A. Contract | B. Special case | ... |"
        "| Case | What is wrong | " + " | ".join(kinds) + " | Verdict |",
        # The separator row Markdown needs under a header.
        "|" + "---|" * (len(kinds) + 3),
    ]
    for row in rows:
        marks = ["✗" if kind in row["kinds"] else "·" for kind in kinds]
        if row["correct"]:
            verdict = "passed (correct code) ✓" if row["ok"] else "wrongly rejected ✗"
        else:
            verdict = "caught ✓" if row["ok"] else "missed ✗"
        lines.append(f"| `{row['name']}` | {row['summary']} | "
                     + " | ".join(marks) + f" | {verdict} |")
    # write_text saves the whole text at once; "\n" is a line break.
    (OUTPUT_DIR / "bug_hunt_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
