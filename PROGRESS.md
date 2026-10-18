# Progress Log

A dated record of what was built, what was verified, and what was learned at each stage.

---

## Stage 1 — Verified reference solver · October 2026

**Built**
- `simlab/ode_solvers.py`: Euler and classical RK4 solvers with input checks, plus two verification helpers (`max_error`, `observed_orders`).
- `simlab/problems.py`: test problem y′ = y − t² + 1, y(0) = 0.5 with exact solution y = (t + 1)² − 0.5eᵗ.
- `run_stage1.py`: convergence study on 6 grids, CSV table, log-log plot, and an automatic PASS/FAIL self-check.

**Verified**
- Exact solution checked by hand: it satisfies both the ODE and the initial condition (working in `STAGE1_GUIDE.md`, Part 3).
- Observed order: Euler 0.990 (theory 1), RK4 3.998 (theory 4). Self-check PASSED.
- RK4 at h = 0.2 gives y(2) ≈ 5.3053630, matching the textbook value.
- Invalid input (0 steps) raises a clear `ValueError`.

**Evaluated**
- First graded review of an AI-style answer: [`evaluations/stage1_rk4_step_size_review.md`](evaluations/stage1_rk4_step_size_review.md). Verdict: incorrect, 3 errors (wrong value, false accuracy claim from a fabricated agreement, wrong scaling factor 4 instead of 16). Every claim checked by recomputing with the verified solver.

**Learned**
- A plausible single answer is not evidence of correct code. An RK4 with swapped weights gives error ≈ 3×10⁻³ (looks fine) but converges at order 1, not 4. The convergence rate exposed it.
- Errors at the coarsest grids do not yet show the theoretical order (Euler 0.86 at first); judge the order on the finer grids.

**Next:** Stage 2 — turn these checks into automatic `pytest` tests, and write deliberately buggy solvers that the tests must catch.

---

## Stage 2 — Tests that catch flawed work · October 2026

**Built**
- `tests/test_ode_solvers.py`: 24 tests covering seven kinds of check (contract, special case, known answer, accuracy, order, SciPy reference, bad input) plus tests of the verification helpers themselves.
- `tests/conftest.py`: `--euler` / `--rk4` options so the same tests can judge any implementation, and a `method` fixture that runs each test for both methods.
- `bugs/buggy_solvers.py`: 6 realistic planted bugs and 1 correct alternative RK4 written in a different style.
- `run_stage2_bug_hunt.py`: runs the suite against every case and writes a catch matrix to `results/stage2/`.

**Verified**
- All 24 tests pass on the real solvers.
- Mutation score 6/6: every planted bug fails at least one test.
- No false positives: the correct alternative passes all 24 tests.

**Learned**
- No single kind of check catches everything. The order test misses a "slope at the wrong time" bug, because that is still a first-order method; only the known-answer and accuracy checks catch it.
- A known-answer test can be passed by a bug that copies the test's own settings (h hard-coded to 0.2).
- Exact `==` on decimals rejects correct code: 10 steps on [0, 1.7] can end at 1.6999999999999998. Compare with a tolerance.
- One bad-input case passed the buggy solver *by accident* (NumPy raised its own ValueError). Testing several bad inputs avoids relying on luck.

**Next:** Stage 3 — stiff problems and stability: write a problem where the obvious method gives a confident wrong answer, with a reference solution and a grading rubric.
