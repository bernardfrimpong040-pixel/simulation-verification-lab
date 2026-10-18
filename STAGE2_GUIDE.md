# Stage 2 Guide — Tests That Catch Flawed Work

**Goal of this stage:** turn the Stage 1 checks into an automatic **test suite** with `pytest`, then prove it works by planting realistic bugs and showing the tests catch every one, while still passing correct code written a different way.

**Time needed:** about 3 hours, including reading.

**Why this matters for the job:** the core of AI-trainer and evaluation work is checks that "reliably distinguish correct solutions from flawed ones". That has **two halves**:
1. **Catch flawed work** (no *false negatives*: a bug that slips through).
2. **Pass correct work**, even when it's written differently from yours (no *false positives*: correct code wrongly rejected).

Most people only think about the first half. This stage practises both.

---

## Part 1 — Save the new files

Stage 2 adds or changes these files. Save each into the project folder `Desktop\Data Analysis\simulation-verification-lab`, in the sub-folder shown:

| File | Save into | New or changed |
|---|---|---|
| `pytest.ini` | the main project folder | new |
| `conftest.py` | `tests\` | new |
| `test_ode_solvers.py` | `tests\` | new |
| `__init__.py` | `bugs\` | new |
| `buggy_solvers.py` | `bugs\` | new |
| `run_stage2_bug_hunt.py` | the main project folder | new |
| `test_ai_review.py` | `scratch\` | new (practice only, not uploaded) |
| `STAGE2_GUIDE.md` | the main project folder | new |
| `README.md` | the main project folder | changed |
| `PROGRESS.md` | the main project folder | changed |

> **Careful with `__init__.py`:** there are now two files with this name, one in `simlab\` (from Stage 1) and one in `bugs\` (new). Put the new one in `bugs\` only. Don't overwrite the one in `simlab\`.

✅ **You should see** this structure in VS Code's file list:

```
simulation-verification-lab/
├── bugs/
│   ├── __init__.py
│   └── buggy_solvers.py
├── evaluations/
├── results/
├── scratch/
│   └── test_ai_review.py
├── simlab/
├── tests/
│   ├── conftest.py
│   └── test_ode_solvers.py
├── pytest.ini
├── run_stage1.py
├── run_stage2_bug_hunt.py
├── PROGRESS.md
├── README.md
├── STAGE1_GUIDE.md
└── STAGE2_GUIDE.md
```

---

## Part 2 — Run the tests

```powershell
.\.venv\Scripts\Activate.ps1
python -m pytest
```

✅ **You should see:**

```
collected 24 items

tests/test_ode_solvers.py ........................                       [100%]

============================== 24 passed in 0.5s ===============================
```

Each dot is one test that passed. A failed test shows as `F`.

**Why 24 tests from one file?** Most tests run twice, once for Euler and once for RK4 (Part 4 explains how). To see every test by name:

```powershell
python -m pytest -v
```

✅ **You should see** 24 lines such as `test_order_of_accuracy[euler] PASSED` and `test_rejects_invalid_input[rk4-zero-steps] PASSED`.

> **Why `python -m pytest` and not just `pytest`?** `python -m pytest` guarantees pytest runs with the Python inside your `.venv`. Plain `pytest` can sometimes pick up a different Python (like the old Anaconda 3.8).

---

## Part 3 — Watch the tests catch a bug

Now swap in a planted bug. This command tells the tests to check `rk4_swapped_weights` instead of our real RK4:

```powershell
python -m pytest --rk4=bugs.buggy_solvers:rk4_swapped_weights
```

✅ **You should see** `5 failed, 19 passed`. A summary at the bottom names the five failed tests (the lines may be cut short to fit the window):

```
FAILED tests/test_ode_solvers.py::test_exact_for_special_case[rk4] - Assertio...
FAILED tests/test_ode_solvers.py::test_matches_textbook_value[rk4] - Assertio...
FAILED tests/test_ode_solvers.py::test_accurate_on_fine_grid[rk4] - Assertion...
FAILED tests/test_ode_solvers.py::test_order_of_accuracy[rk4] - AssertionErro...
FAILED tests/test_ode_solvers.py::test_agrees_with_scipy[rk4] - AssertionErro...
```

Scroll up to find the full message for each failure, on lines starting with `E`:

```
E       AssertionError: rk4: should be exact here, but error = 1.227e+00
E       AssertionError: rk4: y(2) = 5.3797830, textbook says 5.3053630
E       AssertionError: rk4: error 2.790e-03 exceeds 1e-09
E       AssertionError: rk4: observed order 0.991, expected 4
E       AssertionError: rk4: differs from SciPy by 3.873e-04
```

**This is the test suite doing its job.** The Euler tests (`[euler]`) still pass, because only RK4 was swapped. Read the messages: each one says *what* went wrong in plain words. Clear failure messages are part of a good test.

Now run the whole bug hunt, which does this for every planted bug automatically:

```powershell
python run_stage2_bug_hunt.py
```

✅ **You should see:**

```
Step 1: running all tests on the REAL solvers ...
  All tests pass on the real solvers.  ✓

Step 2: swapping in each planted bug ...

Case                       Type     Failed tests  Result
--------------------------------------------------------------------------
rk4_swapped_weights        bug                 5  CAUGHT ✓
rk4_wrong_stage_time       bug                 5  CAUGHT ✓
rk4_no_input_checks        bug                 4  CAUGHT ✓
euler_off_by_one           bug                 5  CAUGHT ✓
euler_fixed_step           bug                 4  CAUGHT ✓
euler_wrong_slope_time     bug                 2  CAUGHT ✓
rk4_alternative_correct    correct             0  passed all tests ✓
--------------------------------------------------------------------------

Bugs caught: 6 of 6
...
RESULT: TESTS CATCH EVERY BUG AND PASS CORRECT CODE
```

It takes about 10 seconds. Then open `results\stage2\bug_hunt_report.md` in VS Code and press **Ctrl+Shift+V** to see it as a formatted table.

---

## Part 4 — How pytest works (the Python, explained)

### 4.1 The three rules

1. pytest looks for **files** named `test_*.py` (here, in the `tests` folder, as set in `pytest.ini`).
2. Inside them, it runs every **function** named `test_*`.
3. A test **passes** if it finishes normally. It **fails** if an `assert` is False or an unexpected error happens.

```python
assert len(t) == 11, f"{name}: expected 11 times, got {len(t)}"
#      └── the claim ──┘  └──── message shown if the claim is False ────┘
```

### 4.2 Fixtures: how each test runs for both methods

In `tests/conftest.py`:

```python
@pytest.fixture(params=["euler", "rk4"])
def method(request):
    name = request.param
    ...
    return name, load_function(spec)
```

- `@pytest.fixture` is a **decorator** (a line starting with `@` above a function). It tells pytest: "any test with a parameter called `method` gets what this function returns."
- `params=["euler", "rk4"]` makes the fixture run **twice**, so every test that uses `method` also runs twice. That's how the count reaches 24: 6 solver tests × 2 methods = 12, the bad-input test × 5 inputs × 2 methods = 10, plus 2 tests of the helper functions.

In the test file, a test just names the fixture as a parameter:

```python
def test_order_of_accuracy(method):
    name, solve = method        # e.g. ("rk4", <the rk4 function>)
```

### 4.3 Swapping in a bug: the `--euler` and `--rk4` options

`conftest.py` also adds two options to pytest. Their values say *which function to test*, written as `module:function`:

| Command | What gets tested |
|---|---|
| `python -m pytest` | the real `simlab.ode_solvers:euler` and `:rk4` (the defaults) |
| `python -m pytest --rk4=bugs.buggy_solvers:rk4_swapped_weights` | the buggy RK4, real Euler |
| `python -m pytest --euler=bugs.buggy_solvers:euler_off_by_one` | the buggy Euler, real RK4 |

This is exactly how evaluation platforms work: **the same tests run against different submissions**. The tests never change; only the code being judged does.

### 4.4 New Python syntax in this stage

| Syntax | Meaning | Example |
|---|---|---|
| `assert x, "msg"` | Claim x is True; fail with "msg" if not | every test |
| `@decorator` | A line above a function that changes how it's used | `@pytest.fixture`, `@pytest.mark.parametrize` |
| `pytest.approx(x)` | "Equal to x apart from tiny rounding" | `t[-1] == pytest.approx(1.7)` |
| `pytest.approx(x, abs=1e-7)` | "Within 0.0000001 of x" | the textbook test |
| `with pytest.raises(ValueError):` | The indented code **must** raise ValueError | the bad-input test |
| `@pytest.mark.parametrize(...)` | Run the test once per listed case | 5 bad inputs |
| `lambda t, y: 3.0` | A tiny unnamed one-line function | `EXACT_CASES` |
| `with ... as tmp:` | Context manager: sets up and cleans up automatically | temporary folder in the bug hunt |
| `{x for x in items}` | Set comprehension: like a list, but each item once | check kinds in the bug hunt |
| `{**d, "k": v}` | Copy dictionary d and add or replace entries | building result rows |
| `subprocess.run([...])` | Run another program from Python | running pytest per bug |
| `importlib.import_module(name)` | Import a module whose name is held as text | `load_function` |
| `getattr(obj, "name")` | Fetch the thing called "name" from obj | `load_function` |

---

## Part 5 — The seven kinds of check, and the maths behind them

Each kind of check catches *different* bugs. That's the main lesson of this stage.

### A. Contract: right shape, start and end

Arrays have `n_steps + 1` entries, start at (t₀, y₀), end at t_end, with increasing times and no `inf` or `nan`. This catches crashes and gross mistakes. None of our planted bugs failed it, because all of them return arrays of the right shape. That's why a contract check is never enough on its own.

### B. Special case: problems the method must solve *exactly*

**Euler is exact when the slope is constant.** For y′ = 3, y(0) = 1, the solution is y = 1 + 3t, a straight line. Euler follows straight lines, so every step lands exactly on it:

$$y_{i+1} = y_i + h \cdot 3 \quad\Longrightarrow\quad y_i = 1 + 3ih = 1 + 3t_i \;\checkmark$$

**RK4 is exact for y′ = 4t³** (f depends only on t). Full working:

*Step 1: when f depends only on t, the stages simplify.* The y-arguments no longer matter:
$$k_1 = f(t_i), \quad k_2 = k_3 = f(t_i + \tfrac{h}{2}), \quad k_4 = f(t_i + h)$$

*Step 2: substitute into the RK4 update.*
$$y_{i+1} = y_i + \frac{h}{6}\Big[f(t_i) + 4f(t_i + \tfrac{h}{2}) + f(t_i + h)\Big]$$
That's **Simpson's rule** for $\int_{t_i}^{t_i+h} f(t)\,dt$.

*Step 3: Simpson's rule is exact for cubics.* Check on the hardest term, $\int_0^h t^3\,dt$ (shifting $t_i$ to 0):
- Exact: $\int_0^h t^3\,dt = \frac{h^4}{4}$
- Simpson: $\frac{h}{6}\Big[0^3 + 4\left(\tfrac{h}{2}\right)^3 + h^3\Big] = \frac{h}{6}\Big[\frac{4h^3}{8} + h^3\Big] = \frac{h}{6}\cdot\frac{3h^3}{2} = \frac{3h^4}{12} = \frac{h^4}{4} \;\checkmark$

So each RK4 step integrates 4t³ exactly, and RK4 reproduces y = t⁴ + 1 to rounding error, even with only 5 large steps.

**Why this check is powerful:** a correct method gives error ≈ 10⁻¹⁵, so *any* bug in the formula shows up instantly. It caught 4 of the 6 bugs.

### C. Known answer: match a published value

y(2) with h = 0.2 must match Burden & Faires' table: Euler 4.8657845, RK4 5.3053630. This is an **independent** check: the numbers come from someone else's computation.

**Its weakness:** it checks only *one* setting. `euler_fixed_step` (h hard-coded to 0.2) passes it, because with 10 steps on [0, 2] the true h *is* 0.2. A bug copied from the textbook example passes the textbook test. Only the other checks, which use different step counts, catch it.

### D. Accuracy: small error on a fine grid

With 320 steps: Euler error < 0.02, RK4 error < 10⁻⁹. Simple and effective; it caught 5 of 6 bugs.

### E. Order: the error shrinks at the right rate

The Stage 1 convergence study, automated. It caught 4 of 6 bugs, but it **missed** `euler_wrong_slope_time`. Here's why, with full working.

The buggy method is $y_{i+1} = y_i + h\,f(t_i + h,\; y_i)$ (slope taken at the *next* time).

*Step 1: expand the buggy slope with Taylor's theorem in t:*
$$f(t_i + h, y_i) = f + h\,f_t + O(h^2) \qquad (f, f_t \text{ evaluated at } (t_i, y_i))$$

*Step 2: so one buggy step gives:*
$$y_{i+1} = y_i + h f + h^2 f_t + O(h^3)$$

*Step 3: the exact solution over one step* (using $y'' = f_t + f_y f$):
$$y(t_i + h) = y_i + h f + \tfrac{h^2}{2}(f_t + f_y f) + O(h^3)$$

*Step 4: subtract to get the error made in one step:*
$$\tfrac{h^2}{2}(f_t + f_y f) - h^2 f_t + O(h^3) = \tfrac{h^2}{2}(f_y f - f_t) + O(h^3)$$

The one-step error is $O(h^2)$, exactly like real Euler's, so after $2/h$ steps the total error is $O(h)$: **still first order**. The method is wrong, but it converges at the "right" rate with a bigger constant. The order test can't see that. The known-answer and accuracy tests can.

> **Lesson:** "converges at the right order" does *not* mean "is the method that was asked for". This is a classic way an AI answer can look verified when it isn't.

**Why the swapped weights drop RK4 all the way to order 1.** A Runge–Kutta method with weights $b_i$ and stage times $c_i$ is second-order only if $\sum b_i c_i = \tfrac12$. With $c = (0, \tfrac12, \tfrac12, 1)$:
- Correct weights $(\tfrac16, \tfrac26, \tfrac26, \tfrac16)$: $\;0 + \tfrac26\cdot\tfrac12 + \tfrac26\cdot\tfrac12 + \tfrac16\cdot 1 = \tfrac16 + \tfrac16 + \tfrac16 = \tfrac12 \;\checkmark$
- Swapped weights $(\tfrac16, \tfrac26, \tfrac16, \tfrac26)$: $\;0 + \tfrac26\cdot\tfrac12 + \tfrac16\cdot\tfrac12 + \tfrac26\cdot 1 = \tfrac{2}{12} + \tfrac{1}{12} + \tfrac{4}{12} = \tfrac{7}{12} \neq \tfrac12 \;\times$

The weights still sum to 1 (so it converges at all), but the second-order condition fails, so the method is only first order.

### F. Independent reference: agree with SciPy

For y′ = cos(ty), y(0) = 1, there's **no formula** for the solution. When there's no exact answer, the professional approach is to compare against a trusted, independently written solver run at very high accuracy. Here that's SciPy's 8th-order `DOP853` with tolerances of 10⁻¹². Its error is far smaller than ours, so it can stand in for the truth. This kind of check is what you'll use most in real evaluation work, because real problems rarely have exact solutions.

### G. Bad input: refuse nonsense clearly

Zero, negative or fractional step counts, and empty or backwards intervals, must raise `ValueError`. This caught `rk4_no_input_checks`, which silently integrates *backwards* when t_end < t₀ and returns numbers with no warning.

**Notice something subtle:** for negative steps, the buggy solver *did* raise a ValueError, but only by accident (NumPy's `linspace` refuses a negative count). So that single case passed for the wrong reason. The other four cases caught the bug. This is why we test several bad inputs, not one.

### Which check caught which bug

From `results/stage2/bug_hunt_report.md` (✗ = caught, · = passed):

| Bug | A | B | C | D | E | F | G |
|---|---|---|---|---|---|---|---|
| `rk4_swapped_weights` | · | ✗ | ✗ | ✗ | ✗ | ✗ | · |
| `rk4_wrong_stage_time` | · | ✗ | ✗ | ✗ | ✗ | ✗ | · |
| `rk4_no_input_checks` | · | · | · | · | · | · | ✗ |
| `euler_off_by_one` | · | ✗ | ✗ | ✗ | ✗ | ✗ | · |
| `euler_fixed_step` | · | ✗ | **·** | ✗ | ✗ | ✗ | · |
| `euler_wrong_slope_time` | · | **·** | ✗ | ✗ | **·** | **·** | · |

**No single column catches every bug.** That's the whole argument for a varied test suite.

---

## Part 6 — The other half: never reject correct code

`rk4_alternative_correct` is a **correct** RK4 written differently: Python lists instead of NumPy arrays, and times computed as t₀ + i·h. It passes all 24 tests, as it should.

**The trap it avoids.** With t₀ = 0, t_end = 1.7 and 10 steps:
- our solver (using `np.linspace`) ends at exactly **1.7**
- the alternative ends at **1.6999999999999998** (computer rounding of 10 × 0.17)

Both are correct. A test written as `assert t[-1] == 1.7` would **wrongly fail** the alternative. That's why `test_output_shape` uses exactly these numbers and compares with `pytest.approx(1.7)`.

> **Rule:** never compare decimal numbers with `==` in a test. Use `pytest.approx`, with a tolerance that matches what the method can actually achieve.

---

## Part 7 — What "mutation testing" means

What you just did has a name.
- Each planted bug is a **mutant**: the correct code with one small change.
- A mutant the tests catch is **killed**. One they miss **survives**.
- **Mutation score** = killed ÷ total. Ours is 6/6 = 100%.

A surviving mutant tells you exactly which test to add. If `euler_wrong_slope_time` had survived, the fix would be a known-answer test, which is the check that catches it.

When you evaluate an AI-written test suite, this is the question to ask: *"What realistic bug would these tests let through?"*

---

## Part 8 — Trainer's corner: review an AI-written test

An AI coding assistant was asked to write a test for our RK4 solver. It produced the file `scratch\test_ai_review.py`:

```python
def test_rk4():
    t, y = rk4(f_example, 0.0, 0.5, 2.0, 10)
    assert y[-1] == 5.305363
    assert len(y) == 10
```

**Step 1: run it.**

```powershell
python -m pytest scratch/test_ai_review.py
```

✅ **You should see** `1 failed`, with:

```
E       assert np.float64(5.305363000692653) == 5.305363
```

**Step 2: think.** Our RK4 is correct (it passed 24 tests and the bug hunt). So when this test fails, *the test* is wrong, not the solver.

**Step 3: write your review.** Find **every** problem. There are four. For each, say what's wrong, why it matters, and how to fix it. Hints:
1. Look at the comparison operator in the first `assert`.
2. Count the points: how many values does 10 steps produce?
3. Think about `euler_fixed_step`. Which kind of bug would this test let through, even after fixing problems 1 and 2?
4. Which of the seven kinds of check from Part 5 are missing entirely?

Send me your review before opening the answer key.

<details>
<summary><b>Answer key (open after you've written yours)</b></summary>

**Verdict: the test is unreliable in both directions. It rejects correct code and would accept flawed code.**

1. **Exact equality on a decimal number (false positive).** RK4 gives 5.305363000692653; the test demands exactly 5.305363. The textbook value is rounded to 7 decimals, so a correct solver can never match it with `==`. Fix: `assert y[-1] == pytest.approx(5.3053630, abs=1e-7)`.
2. **Wrong expected length (false positive).** 10 steps produce 11 points (t₀ plus one per step), so `len(y) == 10` fails on correct code. It never got to run, because the first assert failed first. Fix: `assert len(y) == 11`.
3. **Only one step size (false negatives).** Even with 1 and 2 fixed, the test checks a single setting. A solver with h hard-coded to 0.2 passes it (the RK4 version of `euler_fixed_step`), and it can't detect a wrong order of accuracy. Fix: add an order-of-accuracy test and a fine-grid accuracy test.
4. **Missing kinds of check.** No special case (B), no order (E), no independent reference on a harder problem (F), and no bad-input checks (G). So bugs like removed input validation would pass.

**Failure modes found:** brittle exact comparison; off-by-one in the expected size; a single-point check mistaken for verification.
</details>

---

## Part 9 — Publish to GitHub

```powershell
git add .
git status
```

✅ `git status` lists the new files in green: `bugs/`, `tests/`, `pytest.ini`, `run_stage2_bug_hunt.py`, `results/stage2/...`, and the changed `README.md` and `PROGRESS.md`. **Check that `scratch/` is NOT listed** (it's ignored on purpose).

```powershell
git commit -m "Stage 2: pytest suite, planted bugs and bug hunt (6/6 caught, correct alternative passes)"
git push
```

✅ Refresh GitHub: the README shows the Stage 2 results and the roadmap marks Stage 2 done.

---

## Glossary

| Term | Plain-language meaning |
|---|---|
| **Test suite** | The full set of automatic tests for a piece of code |
| **pytest** | Python's most widely used testing tool |
| **assert** | A claim in code; the test fails if it's False |
| **Fixture** | A function that prepares something a test needs and hands it over automatically |
| **Parametrize** | Run one test several times with different inputs |
| **Decorator** | A line starting with `@` that changes how the function below it behaves |
| **False negative** | A flawed solution that the tests wrongly pass |
| **False positive** | A correct solution that the tests wrongly fail |
| **Mutant** | Correct code with one small deliberate bug |
| **Killed / survived** | A mutant the tests catch / miss |
| **Mutation score** | Fraction of mutants killed |
| **Contract** | What a function promises about its outputs (shape, start, end) |
| **Independent reference** | A trusted answer computed by different code (e.g. SciPy) |
| **Tolerance** | How close is "close enough" in a numerical comparison |
| **Order conditions** | Equations a Runge–Kutta method's coefficients must satisfy to reach a given order |
| **Subprocess** | A separate program started from inside Python |
| **JUnit XML** | A standard file format test tools use to report which tests passed or failed |
