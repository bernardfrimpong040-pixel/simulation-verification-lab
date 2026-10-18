# Simulation Verification Lab

**Verifying numerical simulation and quantitative reasoning — the core skill behind evaluating AI-generated technical work.**

AI models can now write simulation code and quantitative analysis that *looks* right. Judging whether it actually *is* right takes a practitioner: someone who builds a trusted reference solution, designs checks that separate correct work from plausible-but-wrong work, and explains exactly where a flawed answer breaks.

This repository builds that skill set step by step, in my own field of applied mathematics (numerical methods, ODEs/PDEs, and Stokes flow simulation from my M.S. thesis).

**Author:** Bernard Frimpong — M.S. Applied Mathematics, University of Akron (2026) · B.S. Mathematics, KNUST
**GitHub:** [bernardfrimpong040-pixel](https://github.com/bernardfrimpong040-pixel)

---

## The workflow this project practises

Every stage follows the same professional cycle:

1. **Pose** a technical problem precisely, with a known or independently checkable answer.
2. **Build a reference solution** that is simple, readable and verified.
3. **Verify** it with checks that a wrong answer cannot pass (exact solutions, convergence rates, conservation laws, statistical coverage).
4. **Evaluate** other solutions — deliberately flawed ones and real AI-generated ones — against those checks.
5. **Explain** what is wrong, why, and what the correct reasoning is, in clear writing.
6. **Record** results so anyone can reproduce them.

## Roadmap and progress

| Stage | What is built | Skill demonstrated | Status |
|---|---|---|---|
| 1 | Reference ODE solvers (Euler, RK4) with a convergence study against an exact solution | Building and verifying a reference solution | ✅ Done |
| 2 | Automatic tests with `pytest` (7 kinds of check, 24 tests), plus deliberately buggy solvers the tests must catch and a correct alternative they must pass | Writing checks that separate correct from flawed work | ✅ Done |
| 3 | Stiff problems and stability: a problem where the "obvious" method gives a confident wrong answer; written as a problem statement, reference answer and grading rubric | Designing problems that expose shallow reasoning | ⏳ Next |
| 4 | Grading AI responses: real chatbot answers to Stages 1–3 problems, run against the tests, scored with the rubric, with written critiques | Evaluating AI-generated technical work | |
| 5 | Monte Carlo simulation and statistical inference: confidence intervals with coverage checks, A/B-test power by simulation | Statistical inference and experiment design | |
| 6 | Regression and time-series forecasting: honest validation, leakage traps, error metrics | Predictive modelling and forecasting | |
| 7 | Capstone in my research area: regularized Stokeslets for Stokes flow past a sphere, verified against the exact drag 6πμaU | Domain expertise in simulation | |
| 8 | Final report: evaluation log summary, lessons on common AI failure modes | Clear technical writing | |

Detailed notes for each stage are in `STAGEn_GUIDE.md`, and a dated log is in [`PROGRESS.md`](PROGRESS.md).

---

## Stage 1 result: a verified reference solver

**Problem.** y′ = y − t² + 1, y(0) = 0.5, on 0 ≤ t ≤ 2. Exact solution: y(t) = (t + 1)² − 0.5eᵗ.

**Method.** Solve with Euler's method and classical RK4 on 10, 20, 40, 80, 160 and 320 steps. Measure the maximum error against the exact solution, then the observed order of accuracy p from p = ln(E₁/E₂) / ln(h₁/h₂).

| n | h | Euler error | order | RK4 error | order |
|---:|---:|---:|---:|---:|---:|
| 10 | 0.20000 | 4.397e-01 | – | 1.089e-04 | – |
| 20 | 0.10000 | 2.420e-01 | 0.86 | 6.990e-06 | 3.96 |
| 40 | 0.05000 | 1.275e-01 | 0.92 | 4.421e-07 | 3.98 |
| 80 | 0.02500 | 6.550e-02 | 0.96 | 2.779e-08 | 3.99 |
| 160 | 0.01250 | 3.321e-02 | 0.98 | 1.742e-09 | 4.00 |
| 320 | 0.00625 | 1.672e-02 | 0.99 | 1.090e-10 | 4.00 |

![Convergence plot](results/stage1/convergence_plot.png)

**Findings.**
- Both methods converge at their theoretical rates: Euler → 1, RK4 → 4. The self-check passes (tolerance ±0.1 on the finest pair of grids).
- RK4 with h = 0.2 gives y(2) ≈ 5.3053630, matching the published textbook value, an independent cross-check.
- **A single number is weak evidence; the order of accuracy is strong evidence.** An RK4 with two weights swapped still produces a plausible answer (error ≈ 3×10⁻³), but its observed order collapses from 4 to 1. The convergence study catches this immediately. That is exactly the kind of error to look for when grading AI-written simulation code.

### First evaluation: grading an AI answer

Using the verified solver, I checked an AI-style response claiming that RK4 with h = 0.5 gives y(2) accurate to five decimals and that halving h cuts the error by 4.

| Claim | Verified |
|---|---|
| y(2) ≈ 5.30547 | RK4 gives **5.30161** (5.30547 is the *exact* value) |
| Accurate to 5 decimals | Error 3.9 × 10⁻³, only **2** decimals |
| Halving h divides error by 4 | Measured **14.75**; theory 2⁴ = **16** |

**Verdict: incorrect, three errors**, including a *fabricated agreement* (the response compared the exact value with itself). Full analysis and written critique: [`evaluations/stage1_rk4_step_size_review.md`](evaluations/stage1_rk4_step_size_review.md).

---

## Stage 2 result: tests that catch flawed work and pass correct work

A test suite is only trustworthy if it **fails on wrong code** *and* **passes correct code written differently**. Stage 2 checks both.

**The suite** (`tests/test_ode_solvers.py`, 24 tests) uses seven kinds of check:

| | Kind of check | Example |
|---|---|---|
| A | Contract | n_steps + 1 points, starts at (t₀, y₀), ends at t_end, no inf/nan |
| B | Special case | Euler exact for y′ = 3; RK4 exact for y′ = 4t³ (it reduces to Simpson's rule) |
| C | Known answer | y(2) with h = 0.2 matches Burden & Faires to 7 decimals |
| D | Accuracy | error below tolerance on a 320-step grid |
| E | Order | observed order within 0.1 of theory (1 and 4) |
| F | Independent reference | agrees with SciPy's 8th-order DOP853 on y′ = cos(ty), which has no closed form |
| G | Bad input | zero, negative or fractional steps and empty or backwards intervals raise `ValueError` |

**The bug hunt** (`run_stage2_bug_hunt.py`) swaps six realistic planted bugs into the same tests, plus one correct RK4 written in a different style:

| Case | What is wrong | A | B | C | D | E | F | G | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| `rk4_swapped_weights` | weights (1,2,1,2) instead of (1,2,2,1) | · | ✗ | ✗ | ✗ | ✗ | ✗ | · | caught |
| `rk4_wrong_stage_time` | k2 evaluated at t+h instead of t+h/2 | · | ✗ | ✗ | ✗ | ✗ | ✗ | · | caught |
| `rk4_no_input_checks` | input validation removed | · | · | · | · | · | · | ✗ | caught |
| `euler_off_by_one` | loop stops one step early | · | ✗ | ✗ | ✗ | ✗ | ✗ | · | caught |
| `euler_fixed_step` | step size hard-coded to 0.2 | · | ✗ | · | ✗ | ✗ | ✗ | · | caught |
| `euler_wrong_slope_time` | slope taken at t_{i+1} instead of t_i | · | · | ✗ | ✗ | · | · | · | caught |
| `rk4_alternative_correct` | *correct* RK4, different style | · | · | · | · | · | · | · | **passed** |

✗ = that kind of check failed the solver (caught it) · = passed. Full report: [`results/stage2/bug_hunt_report.md`](results/stage2/bug_hunt_report.md).

**Findings.**
- **Mutation score 6/6**, and **no false positives**: the correct alternative passes all 24 tests.
- **No single kind of check catches every bug.** The order test misses `euler_wrong_slope_time`: taking the slope at the next time is still a first-order method (its one-step error is (h²/2)(f_y·f − f_t), which is O(h²)), just not Euler's method. Only the known-answer and accuracy checks catch it.
- **A known-answer test can be passed by a copied setting.** `euler_fixed_step` hard-codes h = 0.2, the textbook's own step, so it passes the textbook check and fails everything that uses other step counts.
- **Exact `==` comparisons reject correct code.** With 10 steps on [0, 1.7], the alternative solver ends at 1.6999999999999998 instead of 1.7. The tests compare with `pytest.approx`, so both pass.

---

## How to reproduce

Requires Python 3.13. On Windows (PowerShell), from the project folder:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python run_stage1.py
python -m pytest
python run_stage2_bug_hunt.py
```

- `run_stage1.py` prints the convergence table, saves `results/stage1/convergence_table.csv` and `convergence_plot.png`, and ends with `RESULT: ALL CHECKS PASSED`.
- `python -m pytest` runs the 24 tests and should report `24 passed`.
- `run_stage2_bug_hunt.py` runs the tests against every planted bug, saves `results/stage2/bug_hunt_report.md` and `bug_hunt.csv`, and ends with `RESULT: TESTS CATCH EVERY BUG AND PASS CORRECT CODE`.

To test any single implementation, name it with the `--euler` or `--rk4` option:

```powershell
python -m pytest --rk4=bugs.buggy_solvers:rk4_swapped_weights
```

## Project structure

```
simulation-verification-lab/
├── simlab/                  # the reusable code (a Python package)
│   ├── __init__.py          # marks the folder as a package
│   ├── ode_solvers.py       # Euler, RK4 and verification helpers
│   └── problems.py          # test problems with exact solutions
├── tests/                   # the automatic test suite
│   ├── conftest.py          # shared setup: --euler / --rk4 options, `method` fixture
│   └── test_ode_solvers.py  # 24 tests, seven kinds of check
├── bugs/                    # deliberately flawed solvers (never used for results)
│   ├── __init__.py
│   └── buggy_solvers.py     # 6 planted bugs + 1 correct alternative
├── results/
│   ├── stage1/              # table and plot produced by run_stage1.py
│   └── stage2/              # bug-hunt report produced by run_stage2_bug_hunt.py
├── evaluations/             # graded reviews of AI-style answers
│   └── stage1_rk4_step_size_review.md
├── run_stage1.py            # Stage 1 convergence study with self-check
├── run_stage2_bug_hunt.py   # Stage 2 mutation test of the test suite
├── pytest.ini               # pytest settings
├── STAGE1_GUIDE.md          # step-by-step guides: maths and Python explained
├── STAGE2_GUIDE.md
├── PROGRESS.md              # dated progress log
├── requirements.txt         # pinned library versions
└── .gitignore
```

## Tools

Python 3.13 · NumPy · Matplotlib · SciPy · pytest
