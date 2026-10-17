# Stage 1 Guide — A Verified Reference Solver

**Goal of this stage:** build two ODE solvers you can *prove* are correct, and learn the single most useful check for judging simulation code: the **convergence study**.

**Time needed:** about 2–3 hours, including reading.

---

## Part 0 — The big picture: how this kind of work is done

AI-trainer and model-evaluation jobs in quantitative fields all follow the same cycle. This project practises every step of it:

| # | Stage of the work | What it means | Where we practise it |
|---|---|---|---|
| 1 | **Pose** a problem | Write a precise technical question with a checkable answer | Every stage |
| 2 | **Build a reference solution** | Your own trusted answer, simple and readable | Stage 1 |
| 3 | **Verify** the reference | Prove it is right with checks a wrong answer cannot pass | Stages 1–2 |
| 4 | **Design hard problems** | Questions where a plausible answer is wrong | Stage 3 |
| 5 | **Evaluate** other answers | Run AI answers against your checks; grade with a rubric | Stage 4 |
| 6 | **Explain** errors in writing | Say exactly where the reasoning breaks and what is correct | Stages 4–8 |
| 7 | **Record and reproduce** | Pinned environment, saved results, a progress log | Every stage |

You can't judge anyone else's answer until you have a reference you trust. That's why Stage 1 is about building one and verifying it.

---

## Part 1 — Set up the project

### 1.1 Put the files in place

1. Find `simulation-verification-lab.zip` in your **Downloads** folder.
2. Right-click it → **Extract All…**
3. Click **Browse** and choose `Desktop\Data Analysis`. Click **Extract**.

✅ **You should see** a new folder: `Desktop\Data Analysis\simulation-verification-lab`, containing `simlab`, `run_stage1.py`, `README.md` and the other files.

### 1.2 Open it in VS Code

1. Open VS Code → **File → Open Folder…** → choose `simulation-verification-lab` → **Select Folder**.
2. Open the terminal: **Terminal → New Terminal**. It opens in PowerShell, already inside the project folder.

### 1.3 Create the virtual environment

Run these one at a time.

```powershell
py -3.13 -m venv .venv
```
✅ **You should see** no message, and a new `.venv` folder appears in the file list on the left.

```powershell
.\.venv\Scripts\Activate.ps1
```
✅ **You should see** `(.venv)` at the start of the terminal line.

```powershell
python --version
```
✅ **You should see** `Python 3.13.x`. (If you see 3.8, the environment is not active. Run the Activate line again.)

```powershell
python -m pip install -r requirements.txt
```
✅ **You should see** downloads, ending with `Successfully installed ... matplotlib-3.11.2 numpy-2.5.3 ... pytest-9.1.1 scipy-1.18.1`.

> **Why a virtual environment?** It's a private copy of Python just for this project. Libraries installed here can't clash with your other projects. Together with `requirements.txt` (exact version numbers), it makes the project **reproducible**: anyone can rebuild exactly the same setup. Job postings call this "building reproducible environments."

---

## Part 2 — Run the convergence study

```powershell
python run_stage1.py
```

✅ **You should see:**

```
Stage 1 convergence study:  y' = y - t^2 + 1,  y(0) = 0.5,  0 <= t <= 2
==========================================================================
    n         h |   Euler error  order |     RK4 error  order
--------------------------------------------------------------------------
   10   0.20000 |     4.397e-01      - |     1.089e-04      -
   20   0.10000 |     2.420e-01   0.86 |     6.990e-06   3.96
   40   0.05000 |     1.275e-01   0.92 |     4.421e-07   3.98
   80   0.02500 |     6.550e-02   0.96 |     2.779e-08   3.99
  160   0.01250 |     3.321e-02   0.98 |     1.742e-09   4.00
  320   0.00625 |     1.672e-02   0.99 |     1.090e-10   4.00
--------------------------------------------------------------------------
Self-check (observed order on the finest pair of grids):
  Euler  expected 1, observed 0.990  ->  PASS
  RK4    expected 4, observed 3.998  ->  PASS
...
RESULT: ALL CHECKS PASSED
```

Then open `results\stage1\convergence_plot.png` (click it in VS Code's file list). ✅ **You should see** two straight lines on log-log axes: a shallow blue one (Euler) and a steep orange one (RK4), each lying along its dashed "theory" line.

**How to read the numbers:** `4.397e-01` is scientific notation for 4.397 × 10⁻¹ = 0.4397. `1.090e-10` means 1.090 × 10⁻¹⁰, about one ten-billionth.

---

## Part 3 — The mathematics, with full working

### 3.1 The problem

$$y'(t) = y - t^2 + 1, \qquad y(0) = 0.5, \qquad 0 \le t \le 2$$

Claimed exact solution: $y(t) = (t+1)^2 - 0.5\,e^{t}$.

### 3.2 Check the exact solution (never trust a formula you haven't checked)

**Step 1: differentiate the claimed solution.**
$$y'(t) = \frac{d}{dt}\big[(t+1)^2\big] - 0.5\,\frac{d}{dt}\big[e^t\big] = 2(t+1) - 0.5\,e^t$$

**Step 2: compute the right-hand side using the claimed solution.**
$$y - t^2 + 1 = \big[(t+1)^2 - 0.5e^t\big] - t^2 + 1$$
Expand $(t+1)^2 = t^2 + 2t + 1$:
$$= t^2 + 2t + 1 - 0.5e^t - t^2 + 1 = 2t + 2 - 0.5e^t = 2(t+1) - 0.5e^t$$

**Step 3: compare.** Step 1 and Step 2 give the same expression, so the ODE is satisfied. ✓

**Step 4: check the starting value.**
$$y(0) = (0+1)^2 - 0.5e^0 = 1 - 0.5 = 0.5 \;\checkmark$$

Both conditions hold, so this *is* the exact solution, and it is safe to measure errors against.

> **Trainer habit:** this four-step check is exactly what you do when an AI says "the exact solution is …". Differentiate it, substitute it, and check the initial condition. AI models often give a formula that satisfies the ODE but has the wrong constant, so it fails Step 4.

### 3.3 Euler's method

**Idea.** Over a short step h, follow the tangent line. From Taylor's theorem:
$$y(t+h) = y(t) + h\,y'(t) + \tfrac{h^2}{2}y''(\xi) \approx y(t) + h\,f(t, y(t))$$

Dropping the $h^2$ term gives the update rule:
$$y_{i+1} = y_i + h\,f(t_i, y_i)$$

**Worked by hand, h = 0.2** (compare with the code: `euler(f_example, 0, 0.5, 2, 10)` gives `y[1] = 0.8`, `y[2] = 1.152`):

*Step 1*, from $t_0 = 0$, $y_0 = 0.5$:
$$f(t_0, y_0) = 0.5 - 0^2 + 1 = 1.5$$
$$y_1 = 0.5 + 0.2 \times 1.5 = 0.5 + 0.3 = 0.8$$

*Step 2*, from $t_1 = 0.2$, $y_1 = 0.8$:
$$f(t_1, y_1) = 0.8 - 0.2^2 + 1 = 0.8 - 0.04 + 1 = 1.76$$
$$y_2 = 0.8 + 0.2 \times 1.76 = 0.8 + 0.352 = 1.152$$

*Error at* $t_2 = 0.4$:
$$y(0.4) = (1.4)^2 - 0.5e^{0.4} = 1.96 - 0.5 \times 1.4918247 = 1.96 - 0.7459123 = 1.2140877$$
$$|y_2 - y(0.4)| = |1.152 - 1.2140877| = 0.0620877$$

**Why the error is order 1.** Each step drops an $h^2$ term (the *local* error). Reaching $t = 2$ takes $N = 2/h$ steps, so the errors add up to roughly
$$N \times C h^2 = \frac{2}{h} \times C h^2 = 2C\,h$$
The total (*global*) error is proportional to $h^1$: **halve h, halve the error.**

### 3.4 RK4 (classical Runge–Kutta)

**Idea.** Instead of one slope, sample four and average them so the errors cancel up to the $h^4$ term:

$$
\begin{aligned}
k_1 &= f(t_i,\; y_i) && \text{slope at the start} \\
k_2 &= f(t_i + \tfrac{h}{2},\; y_i + \tfrac{h}{2}k_1) && \text{slope at the middle, using } k_1 \\
k_3 &= f(t_i + \tfrac{h}{2},\; y_i + \tfrac{h}{2}k_2) && \text{slope at the middle, using } k_2 \\
k_4 &= f(t_i + h,\; y_i + h\,k_3) && \text{slope at the end} \\
y_{i+1} &= y_i + \tfrac{h}{6}\,(k_1 + 2k_2 + 2k_3 + k_4)
\end{aligned}
$$

The weights 1, 2, 2, 1 (total 6) are exactly Simpson's rule: if $f$ depends only on $t$, RK4 *becomes* Simpson's rule. Its local error is $O(h^5)$, so the global error is $O(h^4)$: **halve h and the error drops by about $2^4 = 16$.**

### 3.5 Measuring the order of accuracy p

If the error behaves like $E \approx C h^p$, then for two runs with step sizes $h_1$ and $h_2$:

$$\frac{E_1}{E_2} = \frac{C h_1^p}{C h_2^p} = \left(\frac{h_1}{h_2}\right)^p$$

Take the natural log of both sides:

$$\ln\frac{E_1}{E_2} = p \,\ln\frac{h_1}{h_2} \quad\Longrightarrow\quad p = \frac{\ln(E_1/E_2)}{\ln(h_1/h_2)}$$

When $h_2 = h_1/2$, $\ln(h_1/h_2) = \ln 2$, so $p = \log_2(E_1/E_2)$.

**Worked from our table (finest pair, n = 160 → 320):**

*Euler:*
$$\frac{E_1}{E_2} = \frac{3.320765\times10^{-2}}{1.672143\times10^{-2}} = 1.98593, \qquad p = \log_2(1.98593) = 0.990$$

*RK4:*
$$\frac{E_1}{E_2} = \frac{1.741646\times10^{-9}}{1.089964\times10^{-10}} = 15.979, \qquad p = \log_2(15.979) = 3.998$$

Both match theory (1 and 4). This is what the script's self-check tests.

**Why does Euler show 0.86 at first?** $E \approx Ch^p$ is only the *leading* term; higher terms like $C_2 h^2$ still matter when h is large. As h shrinks they fade, and p settles at 1. **Always judge the order on the finest grids**, and be suspicious of an AI answer that claims a precise order from just two coarse runs.

### 3.6 Why a straight line on the log-log plot

Take logs of $E = Ch^p$: $\log E = \log C + p\,\log h$. That is a straight line in $(\log h, \log E)$ with **slope p**. So on the plot, Euler's line rises 1 decade per decade of h, and RK4's rises 4 decades per decade.

---

## Part 4 — The Python, explained

Every line in the code has a comment. This table collects the syntax you'll see again and again, so you can look it up quickly.

| Syntax | Meaning | Example from our code |
|---|---|---|
| `import numpy as np` | Load a library and give it a nickname | `np.exp(t)` |
| `from a.b import c` | Bring one name out of a file in a package | `from simlab.ode_solvers import euler` |
| `def name(x, y):` | Define a function; its body is indented 4 spaces | `def euler(f, t0, ...):` |
| `x: float`, `-> float` | Type hints: documentation of input and output types | `def f_example(t: float, y: float) -> float:` |
| `"""text"""` | Docstring: the function's built-in manual | under every `def` |
| `return a, b` | Send values back (two values form a *tuple*) | `return t, y` → caller writes `t, y = euler(...)` |
| `**` | Power (`^` does **not** mean power in Python) | `t**2` |
| `for i in range(n):` | Repeat for i = 0, 1, …, n−1 | the solver loops |
| `y[i]` | Entry i of an array; counting starts at **0** | `y[0] = y0` |
| `x[-1]` | The **last** item | `orders[name][-1]` |
| `[ ... ]` | A list | `STEP_COUNTS = [10, 20, ...]` |
| `{key: value}` | A dictionary (look up a value by its key) | `EXPECTED_ORDER = {"Euler": 1, "RK4": 4}` |
| `[expr for x in items]` | List comprehension: build a list in one line | `[(T_END - T0) / n for n in STEP_COUNTS]` |
| `f"...{x:.3f}..."` | f-string: insert a value, formatted (3 decimals here) | the printed table |
| `a if cond else b` | One-line choice | `"PASS" if passed else "FAIL"` |
| `raise ValueError(...)` | Stop with an error message | bad `n_steps` |
| `if __name__ == "__main__":` | Run only when this file is run directly | bottom of `run_stage1.py` |

**How the files connect**

```
run_stage1.py  ──imports──▶  simlab/ode_solvers.py   (euler, rk4, max_error, observed_orders)
               ──imports──▶  simlab/problems.py      (f_example, exact_example, T0, Y0, T_END)
               ──writes───▶  results/stage1/convergence_table.csv, convergence_plot.png
```

Keeping the **reusable code** (`simlab/`) separate from the **scripts that run experiments** (`run_stage1.py`) is standard professional practice. In Stage 2 the tests will import the same `simlab` functions, so the checks always test the real code.

---

## Part 5 — Trainer's corner: using this to judge other people's work

### 5.1 Why the order of accuracy catches bugs that a single answer hides

Imagine an AI writes RK4 but swaps two weights, using `(k1 + 2*k2 + k3 + 2*k4)` instead of `(k1 + 2*k2 + 2*k3 + k4)`. The weights still add to 6, so it looks fine. We tested this broken version:

| n | 10 | 20 | 40 | 80 | 160 | 320 |
|---|---|---|---|---|---|---|
| error | 7.4e-2 | 4.1e-2 | 2.1e-2 | 1.1e-2 | 5.6e-3 | 2.8e-3 |
| order | – | 0.86 | 0.93 | 0.97 | 0.98 | 0.99 |

At n = 320 its error is 0.003, an answer many people would accept. But the order is **1, not 4**: the method is no better than Euler. The convergence study exposes the bug in seconds. In Stage 2 you'll write this broken solver yourself and a test that fails it automatically.

### 5.2 Exercise: grade an AI answer

Here is a response an AI chatbot might give. **Find every error**, using your own code to check.

> **Question:** Using RK4 with step size h = 0.5, approximate y(2) for y′ = y − t² + 1, y(0) = 0.5. Is this step size accurate enough for 4 decimal places?
>
> **AI response:** "Using RK4 with h = 0.5 (4 steps), I get y(2) ≈ 5.30547, which matches the exact value 5.30547 to five decimal places. So h = 0.5 is easily accurate enough. Also, because RK4 is a fourth-order method, halving h to 0.25 would reduce the error by a factor of 4."

**How to check it yourself, in the Python prompt.** With `(.venv)` active, type `python` and press Enter. You'll see `>>>`. Type each line and press Enter:

```python
from simlab.ode_solvers import rk4
from simlab.problems import f_example, exact_example
t, y = rk4(f_example, 0.0, 0.5, 2.0, 4)
y[-1]
exact_example(2.0)
abs(y[-1] - exact_example(2.0))
```

Then repeat with `8` steps instead of `4` (h = 0.25), and divide the first error by the second. Type `exit()` to leave the Python prompt.

**Write your critique in 3–5 sentences** before opening the answer key. A good critique names each error, gives the correct value, and explains *why* the reasoning is wrong.

<details>
<summary><b>Answer key (open after you've written yours)</b></summary>

Your numbers should be:
- RK4, h = 0.5: y(2) ≈ **5.3016052**; exact y(2) = 9 − 0.5e² ≈ **5.3054720**; error ≈ **3.87 × 10⁻³**
- RK4, h = 0.25: error ≈ **2.62 × 10⁻⁴**; ratio ≈ 3.87e-3 / 2.62e-4 ≈ **14.7**

**Model critique:**
"The response contains three errors. (1) The computed value is wrong: RK4 with h = 0.5 gives y(2) ≈ 5.30161, not 5.30547. The response appears to have reported the exact value rather than the RK4 result. (2) The conclusion is therefore wrong: the true error is about 3.9 × 10⁻³, so the result is accurate to only two decimal places, not four. (3) The scaling claim is wrong: a fourth-order method's error scales like h⁴, so halving h should reduce the error by about 2⁴ = 16, not 4 (a factor of 4 would mean second order). Running the computation confirms a reduction of about 14.7, approaching 16 as h shrinks."

Notice the pattern. Error (1) is a **fabricated agreement**: the AI's "check" compares the exact value with itself. This is one of the most common failure modes in AI quantitative answers, and only an independent computation catches it.
</details>

---

## Part 6 — Publish to GitHub

### 6.1 Create the empty repository on GitHub

1. Go to github.com → **+** (top right) → **New repository**.
2. Repository name: `simulation-verification-lab`
3. Description: `Verifying numerical simulation and quantitative reasoning: reference solvers, convergence tests, and evaluation of AI-generated technical work.`
4. Choose **Public**.
5. **Do NOT tick** "Add a README file", ".gitignore" or "license". (Ticking these caused rejected pushes before.)
6. Click **Create repository**.

### 6.2 Push from VS Code's terminal

Run these one at a time, in the project folder.

```powershell
git init
```
✅ `Initialized empty Git repository in ...`

```powershell
git add .
```
✅ No message.

```powershell
git status
```
✅ A green list of new files, including `README.md`, `run_stage1.py`, `simlab/...` and `results/stage1/...`. **Check that `.venv` is NOT listed.**

```powershell
git commit -m "Stage 1: verified Euler and RK4 reference solvers with convergence study"
```
✅ `... files changed ...`

```powershell
git branch -M main
```
✅ No message.

```powershell
git remote add origin https://github.com/bernardfrimpong040-pixel/simulation-verification-lab.git
```
✅ No message.

```powershell
git push -u origin main
```
✅ Upload messages ending with `branch 'main' set up to track 'origin/main'`.

Refresh the GitHub page. ✅ **You should see** the README with the results table and the convergence plot showing.

---

## Glossary

| Term | Plain-language meaning |
|---|---|
| **ODE** | Ordinary differential equation: an equation relating a function to its derivative |
| **IVP** | Initial value problem: an ODE plus a starting value |
| **Step size h** | The time gap between computed points |
| **Local error** | The error made in a single step |
| **Global error** | The total error accumulated by the final time |
| **Order of accuracy p** | How fast the error shrinks: error ≈ C·hᵖ |
| **Convergence study** | Solving with smaller and smaller h to measure p |
| **Verification** | Checking the code solves the equations correctly ("solving the equations right") |
| **Validation** | Checking the equations describe reality ("solving the right equations") |
| **Reference solution** | Your own trusted, verified answer, used to judge others |
| **Max norm** | The largest absolute error over all points |
| **Reproducible environment** | A setup anyone can rebuild identically (pinned versions, virtual environment) |
| **Package** | A folder of Python files with an `__init__.py`, importable by other code |
| **Exit code** | A number a program returns when it ends: 0 = success, non-zero = failure |
| **Fabricated agreement** | When an answer "confirms" itself by comparing a value with itself |
