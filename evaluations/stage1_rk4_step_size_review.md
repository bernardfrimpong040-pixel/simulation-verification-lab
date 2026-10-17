# Evaluation 1 — RK4 step-size claim

**Stage:** 1 · **Topic:** ODE solvers, accuracy and order of convergence · **Verdict:** ❌ Incorrect (3 errors)

---

## The question

> Using RK4 with step size h = 0.5, approximate y(2) for y′ = y − t² + 1, y(0) = 0.5. Is this step size accurate enough for 4 decimal places?

## The response being evaluated

> "Using RK4 with h = 0.5 (4 steps), I get y(2) ≈ 5.30547, which matches the exact value 5.30547 to five decimal places. So h = 0.5 is easily accurate enough. Also, because RK4 is a fourth-order method, halving h to 0.25 would reduce the error by a factor of 4."

---

## Independent check

Computed with the verified reference solver from Stage 1 (`simlab/ode_solvers.py`, which passes the convergence self-check in `run_stage1.py`).

```python
from simlab.ode_solvers import rk4
from simlab.problems import f_example, exact_example
t, y = rk4(f_example, 0.0, 0.5, 2.0, 4)    # h = 0.5
y[-1]                                       # 5.301605229265987
exact_example(2.0)                          # 5.305471950534675
abs(y[-1] - exact_example(2.0))             # 0.0038667212686878116
t, y = rk4(f_example, 0.0, 0.5, 2.0, 8)    # h = 0.25
abs(y[-1] - exact_example(2.0))             # 0.0002622281000155269
```

| Quantity | Claimed | Verified |
|---|---|---|
| RK4 y(2), h = 0.5 | 5.30547 | **5.301605** |
| Exact y(2) = 9 − 0.5e² | 5.30547 | 5.305472 |
| Error, h = 0.5 | ≈ 0 | **3.87 × 10⁻³** |
| Decimal places of agreement | 5 | **2** |
| Error ratio when h is halved | 4 | **14.75** (theory: 16) |

## Claim-by-claim analysis

**Claim 1: "RK4 with h = 0.5 gives y(2) ≈ 5.30547."** ❌
The exact value rounds to 5.30547; the RK4 result rounds to 5.30161. The response reported the exact value as if it were the RK4 result.

**Claim 2: "Matches to five decimal places, so h = 0.5 is accurate enough for 4."** ❌
RK4 (5.301605) and exact (5.305472) agree only to 5.30, i.e. 2 decimal places. The error 3.9 × 10⁻³ is about 80 times larger than the 5 × 10⁻⁵ needed for 4-decimal accuracy. The "check" compared the exact value with itself, so it could never fail (a *fabricated agreement*).

**Claim 3: "Halving h reduces the error by a factor of 4."** ❌
For a fourth-order method, error ≈ C·h⁴, so halving h divides the error by 2⁴ = 16. A factor of 4 = 2² describes a second-order method. The measured ratio is 14.75, below 16 only because h = 0.5 is coarse; on finer grids it reaches 15.98 (Stage 1 table).

## Written critique

> The response contains three errors. First, the computed value is wrong: RK4 with h = 0.5 gives y(2) ≈ 5.30161, not 5.30547; the AI reported the exact value instead of the RK4 result. Second, its conclusion is therefore wrong: the true error is about 3.9 × 10⁻³, so the result agrees with the exact value to only 2 decimal places, and h = 0.5 is not accurate enough for 4. The AI's "check" compared the exact value with itself, so it could never fail. Third, the scaling claim is wrong: a fourth-order method's error scales like h⁴, so halving h should reduce the error by about 2⁴ = 16, not 4, which would indicate a second-order method. Running it confirms a reduction of about 14.75, approaching 16 as h shrinks.

## Failure modes found

- **Fabricated agreement:** a self-check that compares a value with itself.
- **Wrong scaling law:** confusing the order p with the error-reduction factor 2ᵖ.
- **Unsupported confidence:** "easily accurate enough" stated without any computed error.

## Lesson for future evaluations

Never accept a numerical answer's own claim of accuracy. Recompute it independently with a verified solver, and check how the error scales, not just one value.
