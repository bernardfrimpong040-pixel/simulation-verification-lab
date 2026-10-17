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
