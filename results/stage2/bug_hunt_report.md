# Stage 2 bug hunt

**Bugs caught: 6 of 6.** ✗ = this kind of check FAILED the solver (caught it); · = passed.

| Case | What is wrong | A. Contract | B. Special case | C. Known answer | D. Accuracy | E. Order | F. SciPy reference | G. Bad input | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| `rk4_swapped_weights` | weights (1,2,1,2) instead of (1,2,2,1) | · | ✗ | ✗ | ✗ | ✗ | ✗ | · | caught ✓ |
| `rk4_wrong_stage_time` | k2 evaluated at t+h instead of t+h/2 | · | ✗ | ✗ | ✗ | ✗ | ✗ | · | caught ✓ |
| `rk4_no_input_checks` | input validation removed | · | · | · | · | · | · | ✗ | caught ✓ |
| `euler_off_by_one` | loop stops one step early | · | ✗ | ✗ | ✗ | ✗ | ✗ | · | caught ✓ |
| `euler_fixed_step` | step size hard-coded to 0.2 | · | ✗ | · | ✗ | ✗ | ✗ | · | caught ✓ |
| `euler_wrong_slope_time` | slope taken at t_{i+1} instead of t_i | · | · | ✗ | ✗ | · | · | · | caught ✓ |
| `rk4_alternative_correct` | correct RK4 written in a different style | · | · | · | · | · | · | · | passed (correct code) ✓ |
