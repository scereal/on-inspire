"""Code lab: library guides, the bug library, worked workflows and code practice.

Every `code` string here is executed at build time (see build.py: verify_code). Library examples and
workflow steps must run cleanly; their printed output is captured and shown. Each bug has a `bad` and a
`good` snippet plus a verification rule, so the symptom on the page is what the code really does.
"""
from lib import *

SCIPY, NUMPY, SKLEARN, PANDAS, PYTHON = "SciPy", "NumPy", "scikit-learn", "pandas", "Python"

# ------------------------------------------------------------------ library guides
LIBRARY = [
    {
        "id": "lib-minimize", "name": "scipy.optimize.minimize", "group": "Optimization (SciPy)",
        "summary": "One front door to most local optimizers: unconstrained, bounded and constrained.",
        "when": "Smooth objective, continuous variables, a reasonable starting point. For constrained problems use `method='SLSQP'` (SQP, dict constraints) or `method='trust-constr'` (constraint objects, reports multipliers).",
        "signature": "minimize(fun, x0, args=(), method=None, jac=None, hess=None, bounds=None, constraints=(), tol=None, options=None)",
        "args": [("fun", "your objective, called as `fun(x, *args)`; must return a scalar"),
                 ("x0", "starting point (any sequence; arrives in `fun` as a float NumPy array)"),
                 ("args", "extra arguments as a **tuple**: `(p,)`"),
                 ("method", "the algorithm; see the table below"),
                 ("jac", "gradient function, or `None` for finite differences (check it with `check_grad`)"),
                 ("bounds", "list of `(low, high)` per variable, or a `Bounds` object"),
                 ("constraints", "list of dicts `{'type': 'ineq'|'eq', 'fun': c, 'args': (...)}` with **'ineq' meaning c(x) ≥ 0**, or `NonlinearConstraint`/`LinearConstraint` objects")],
        "body": r"""
| method | family (lecture) | bounds | constraints | needs gradient |
|---|---|---|---|---|
| `Nelder-Mead`, `Powell` | derivative-free | yes | no | no |
| `CG` | conjugate gradients ([[c-conjugate-gradients]]) | no | no | yes (or finite differences) |
| `BFGS` | quasi-Newton ([[c-quasi-newton]]) | no | no | yes (or finite differences) |
| `L-BFGS-B` | limited-memory BFGS | **yes** | no | yes (or finite differences) |
| `Newton-CG`, `trust-ncg`, `trust-exact` | Newton / trust region ([[c-newton]], [[c-trust-region]]) | no | no | yes, plus Hessian |
| `SLSQP` | SQP ([[c-sqp]]) | yes | **yes** (dicts) | yes (or finite differences) |
| `trust-constr` | trust-region SQP / interior point | yes | **yes** (objects) | yes (or finite differences) |
| `COBYLA` | derivative-free linear approximations | yes (recent SciPy) | inequalities | no |

If you give `bounds` or `constraints` to a method that can't use them (like `BFGS`), SciPy **ignores them with only a warning** ([[e-method-ignores]]). With no `method`, SciPy picks `BFGS`, `L-BFGS-B` or `SLSQP` depending on whether you passed bounds or constraints.
""",
        "code": '''import numpy as np
from scipy.optimize import minimize

def f(x):                       # objective: a smooth bowl centred at (1, 2)
    return (x[0] - 1)**2 + (x[1] - 2)**2

def g(x):                       # course form: g(x) <= 0  means  x0 + 2*x1 <= 2.5
    return x[0] + 2 * x[1] - 2.5

res = minimize(f, x0=[0.5, 0.5], method="SLSQP",
               bounds=[(0, 3), (0, 3)],
               constraints=[{"type": "ineq", "fun": lambda x: -g(x)}])   # SciPy wants >= 0
print(res.success, res.message)
print("x* =", res.x.round(4), " f* =", round(res.fun, 4), " g(x*) =", round(g(res.x), 6))''',
        "concepts": ["c-sqp", "c-quasi-newton", "c-negative-null-form"], "matlab": "fmincon / fminunc",
        "errors": ["e-ineq-sign", "e-args-tuple", "e-method-ignores", "e-objective-vector", "e-bounds-format", "e-ignore-success"],
    },
    {
        "id": "lib-constraints", "name": "Constraint and bound formats", "group": "Optimization (SciPy)",
        "summary": "Three ways to write constraints for minimize; know which method takes which.",
        "when": "Every constrained problem. Dicts are simplest for SLSQP; objects work with trust-constr (and recent SLSQP).",
        "signature": "{'type': 'ineq'|'eq', 'fun': c, 'jac': dc, 'args': ()} · NonlinearConstraint(fun, lb, ub) · LinearConstraint(A, lb, ub) · Bounds(lb, ub)",
        "args": [("dict 'ineq'", "means **c(x) ≥ 0**. The course's g(x) ≤ 0 becomes `'fun': lambda x: -g(x)`"),
                 ("dict 'eq'", "means c(x) = 0"),
                 ("NonlinearConstraint(fun, lb, ub)", "lb ≤ fun(x) ≤ ub; for g(x) ≤ 0 use `NonlinearConstraint(g, -np.inf, 0)`, with no sign flip"),
                 ("LinearConstraint(A, lb, ub)", "lb ≤ A @ x ≤ ub, for linear constraints"),
                 ("Bounds(lb, ub)", "simple box constraints, or a list of `(low, high)` pairs; use `None`/`np.inf` for no bound")],
        "body": r"""
The **object** form states the inequality's direction explicitly (`-np.inf, 0`), which removes the most common sign bug. The **dict** form is shorter but has the `≥ 0` convention baked in. Pick one per project and stay with it.
""",
        "code": '''import numpy as np
from scipy.optimize import minimize, NonlinearConstraint, LinearConstraint, Bounds

f = lambda x: (x[0] - 1)**2 + (x[1] - 2)**2
g = lambda x: x[0] + 2 * x[1] - 2.5                      # want g(x) <= 0

as_dict   = [{"type": "ineq", "fun": lambda x: -g(x)}]     # dict: fun >= 0
as_object = [NonlinearConstraint(g, -np.inf, 0.0)]         # object: -inf <= g <= 0
as_linear = [LinearConstraint([[1, 2]], -np.inf, 2.5)]     # it is linear, so this works too

for cons, method in [(as_dict, "SLSQP"), (as_object, "trust-constr"), (as_linear, "trust-constr")]:
    r = minimize(f, [0.5, 0.5], method=method, constraints=cons, bounds=Bounds([0, 0], [3, 3]))
    print(f"{method:12s}", r.x.round(4))''',
        "concepts": ["c-negative-null-form", "c-feasibility"], "matlab": "fmincon's A, b, Aeq, beq, lb, ub, nonlcon",
        "errors": ["e-ineq-sign", "e-constraint-dict-typo", "e-lambda-late-binding", "e-bounds-format"],
    },
    {
        "id": "lib-result", "name": "Reading OptimizeResult", "group": "Optimization (SciPy)",
        "summary": "What minimize returns, which fields to check, and how to get multipliers.",
        "when": "After every solve. Never read `res.x` without checking `res.success`.",
        "signature": "res.x, res.fun, res.success, res.status, res.message, res.nit, res.nfev, res.jac, (trust-constr) res.v",
        "args": [("res.success", "did the solver report convergence? `False` means don't trust `x`"),
                 ("res.message", "why it stopped (read it, especially when success is False)"),
                 ("res.nit / res.nfev", "iterations and function evaluations; report them"),
                 ("res.jac", "the gradient at the solution (≈ 0 for unconstrained optima)"),
                 ("res.v (trust-constr)", "Lagrange multipliers, one array per constraint object: the μ's of the KKT conditions")],
        "body": r"""
A good report ([[c-convergence-termination]]) lists the start, the tolerances, `nit`/`nfev`, each constraint's value with 'active'/'inactive', and the multipliers. SLSQP doesn't return multipliers; `trust-constr` does, in `res.v`. Check their signs against the KKT conditions ([[c-kkt]]).
""",
        "code": '''import numpy as np
from scipy.optimize import minimize, NonlinearConstraint

f = lambda x: (x[0] - 2)**2 + (x[1] - 1)**2
g = lambda x: x[0] + x[1] - 2                       # g(x) <= 0
res = minimize(f, [0.0, 0.0], method="trust-constr",
               constraints=[NonlinearConstraint(g, -np.inf, 0.0)])
print("success:", res.success, "| nit:", res.nit, "| nfev:", res.nfev)
print("x* =", res.x.round(4), " g(x*) =", round(g(res.x), 6))
print("multiplier mu =", np.round(res.v[0], 4))    # KKT multiplier, should be >= 0 for an active g <= 0''',
        "concepts": ["c-convergence-termination", "c-kkt"], "matlab": "fmincon's exitflag, output, lambda",
        "errors": ["e-ignore-success"],
    },
    {
        "id": "lib-minimize-scalar", "name": "scipy.optimize.minimize_scalar", "group": "Optimization (SciPy)",
        "summary": "One-variable minimization, like a line search on its own.",
        "when": "A 1-D problem, or a line search along a fixed direction: minimize φ(α) = f(x + αd).",
        "signature": "minimize_scalar(fun, bracket=None, bounds=None, args=(), method='brent'|'golden'|'bounded')",
        "args": [("bounds", "an interval `(a, b)`; with bounds SciPy uses the 'bounded' method"),
                 ("method", "'brent' (default, unbounded), 'bounded' (interval), 'golden'")],
        "body": r"""
This is the one-dimensional problem at the heart of line searches ([[c-exact-line-search]], [[c-armijo]]): fix $\mathbf{x}_k$ and $\mathbf{d}_k$, then minimize over α alone.
""",
        "code": '''import numpy as np
from scipy.optimize import minimize_scalar

f = lambda x: 4*x[0]**2 + 3*x[0]*x[1] + x[1]**2
xk = np.array([1.0, 1.0])
d = -np.array([8*xk[0] + 3*xk[1], 3*xk[0] + 2*xk[1]])    # steepest-descent direction -grad f
phi = lambda a: f(xk + a * d)                              # the line-search function
res = minimize_scalar(phi, bounds=(0, 1), method="bounded")
print("alpha* =", round(res.x, 5), " (exact formula gives 146/1348 =", round(146/1348, 5), ")")''',
        "concepts": ["c-exact-line-search", "c-armijo"], "matlab": "fminbnd",
        "errors": [],
    },
    {
        "id": "lib-linprog", "name": "scipy.optimize.linprog", "group": "Optimization (SciPy)",
        "summary": "Linear programs, solved by HiGHS (simplex / interior point).",
        "when": "Objective and all constraints linear. It **minimizes**, uses `A_ub @ x <= b_ub`, and defaults to **x ≥ 0**.",
        "signature": "linprog(c, A_ub=None, b_ub=None, A_eq=None, b_eq=None, bounds=(0, None), method='highs')",
        "args": [("c", "cost vector; to maximize, pass **-c** and negate `res.fun`"),
                 ("A_ub, b_ub", "inequalities `A_ub @ x <= b_ub`; a ≥ constraint must be multiplied by −1"),
                 ("A_eq, b_eq", "equalities"),
                 ("bounds", "default `(0, None)` for every variable; use `(None, None)` for free variables"),
                 ("res.ineqlin.marginals", "shadow prices (∂f*/∂b) of the inequality constraints")],
        "body": r"""
The farmer's problem ([[c-lp-standard-form]]) in four lines. The marginals are the LP version of Lagrange multipliers: here, one more labour hour is worth 10 dollars of profit and one more acre 20 dollars. (They're negative because `linprog` minimized $-$profit.)
""",
        "code": '''from scipy.optimize import linprog

res = linprog(c=[-40, -30],                      # maximize 40x1 + 30x2  ->  minimize -(...)
              A_ub=[[2, 1], [1, 1]], b_ub=[320, 240],
              bounds=[(0, None), (0, None)], method="highs")
print("x* =", res.x, "  max profit =", -res.fun)
print("shadow prices (labour, land):", res.ineqlin.marginals)''',
        "concepts": ["c-lp-standard-form", "c-simplex", "c-lagrangian-equality"], "matlab": "linprog",
        "errors": ["e-linprog-max", "e-linprog-ge", "e-linprog-bounds"],
    },
    {
        "id": "lib-roots", "name": "brentq, fsolve, root", "group": "Optimization (SciPy)",
        "summary": "Root finding: solve r(x) = 0, e.g. FONCs, active constraints, or a check on an optimizer.",
        "when": "`brentq` for one variable with a sign change in [a, b] (guaranteed); `fsolve`/`root` for systems (Newton-like: need a good start, and check convergence).",
        "signature": "brentq(f, a, b, args=()) · fsolve(func, x0, full_output=False) · root(fun, x0, method='hybr')",
        "args": [("brentq a, b", "must bracket a root: f(a) and f(b) of opposite sign"),
                 ("fsolve full_output", "set `True` to get `ier` (1 means success). It returns *something* even on failure"),
                 ("root", "returns an object with `.success`, like minimize")],
        "body": r"""
A neat check on a constrained optimum: if you know which constraints are active, the optimum solves those equations, so `brentq` on the active constraint(s) should reproduce the optimizer's answer. Root finders are Newton–Raphson's descendants ([[p-newton-raphson]]).
""",
        "code": '''import numpy as np
from scipy.optimize import brentq, root

r = lambda x: x**2 - 2
print("brentq:", brentq(r, 0, 2))                       # sign change on [0, 2]

F = lambda v: [2*v[0] - 3*v[1] + 1, -3*v[0] + 8*v[1] - 1]   # FONC of Lecture 5's example 1
sol = root(F, x0=[0.0, 0.0])
print("root:", sol.success, sol.x.round(5), " (expected -5/7, -1/7)")''',
        "concepts": ["p-newton-raphson", "c-fonc"], "matlab": "fzero / fsolve",
        "errors": ["e-brentq-sign", "e-fsolve-silent"],
    },
    {
        "id": "lib-global", "name": "differential_evolution and multi-start", "group": "Optimization (SciPy)",
        "summary": "Global search when local optimizers get trapped.",
        "when": "Non-convex problems with multiple valleys and cheap evaluations. Needs finite bounds; uses many evaluations.",
        "signature": "differential_evolution(func, bounds, args=(), seed=None, constraints=(), maxiter=1000)",
        "args": [("bounds", "required: a finite `(low, high)` for every variable"),
                 ("seed", "fix it for reproducible results")],
        "body": r"""
A local method converges to the valley it starts in ([[c-topography]]). Below, BFGS from $x_0 = 1.5$ finds the shallower local minimum near $x\approx0.96$, while differential evolution finds the global one near $x\approx-1.04$. The cheaper alternative is a **multi-start**: run a local optimizer from several LHS starting points and keep the best ([[q-multistart]]).
""",
        "code": '''import numpy as np
from scipy.optimize import differential_evolution, minimize

f = lambda x: (x[0]**2 - 1)**2 + 0.3 * x[0]          # two valleys, the left one deeper
local = minimize(f, x0=[1.5])
glob = differential_evolution(f, bounds=[(-2, 2)], seed=0)
print("local  from 1.5:", local.x.round(3), round(local.fun, 4))
print("global (DE)    :", glob.x.round(3), round(glob.fun, 4))''',
        "concepts": ["c-topography", "q-multistart"], "matlab": "ga / globalsearch / multistart",
        "errors": ["e-ignore-success"],
    },
    {
        "id": "lib-check-grad", "name": "check_grad and approx_fprime", "group": "Optimization (SciPy)",
        "summary": "Verify an analytic gradient against finite differences before trusting it.",
        "when": "Any time you pass `jac=` to an optimizer.",
        "signature": "check_grad(func, grad, x0) · approx_fprime(x0, func, epsilon)",
        "args": [("check_grad", "returns the norm of (your gradient − finite-difference gradient); should be ~1e-6 or smaller"),
                 ("approx_fprime", "the finite-difference gradient itself")],
        "body": r"""
A wrong gradient doesn't crash anything. The optimizer just walks toward the wrong point, or stops early ([[e-wrong-jac]]). A one-line check at a random point catches it.
""",
        "code": '''import numpy as np
from scipy.optimize import check_grad, approx_fprime

f = lambda x: (x[0] - 1)**2 + 3*(x[1] - 2)**2 + x[0]*x[1]
good = lambda x: np.array([2*(x[0] - 1) + x[1], 6*(x[1] - 2) + x[0]])
x_test = np.array([0.3, -0.7])
print("check_grad:", check_grad(f, good, x_test))
print("finite differences:", approx_fprime(x_test, f, 1e-7).round(4), " analytic:", good(x_test))''',
        "concepts": ["p-gradient"], "matlab": "fmincon's CheckGradients option",
        "errors": ["e-wrong-jac"],
    },
    {
        "id": "lib-qmc-lhs", "name": "scipy.stats.qmc.LatinHypercube", "group": "Sampling and surrogates",
        "summary": "Latin hypercube samples in the unit cube, then scaled to your bounds.",
        "when": "Choosing training points for a surrogate, or starting points for a multi-start.",
        "signature": "qmc.LatinHypercube(d, seed=None).random(n) · qmc.scale(sample, l_bounds, u_bounds)",
        "args": [("d", "number of dimensions (variables)"), ("n", "number of points"),
                 ("seed", "fix it for reproducibility"), ("qmc.scale", "maps [0,1]^d to your box")],
        "body": r"""
Each column has exactly one point per interval $[i/n, (i+1)/n)$, the Latin property ([[c-doe]]).
""",
        "code": '''import numpy as np
from scipy.stats import qmc

sampler = qmc.LatinHypercube(d=2, seed=559)
unit = sampler.random(n=5)                                # points in [0, 1]^2
pts = qmc.scale(unit, l_bounds=[0.0, 10.0], u_bounds=[1.0, 20.0])
print(pts.round(3))
print("one point per fifth in column 0:", sorted(np.floor(unit[:, 0] * 5).astype(int).tolist()))''',
        "concepts": ["c-doe"], "matlab": "lhsdesign",
        "errors": [],
    },
    {
        "id": "lib-linalg", "name": "numpy.linalg: solve, lstsq, cond, eigvalsh", "group": "Linear algebra (NumPy)",
        "summary": "The linear-algebra workhorses behind least squares, Kriging and definiteness checks.",
        "when": "`solve` for square systems (never `inv(A) @ b`), `lstsq` for least squares, `cond` to check conditioning, `eigvalsh` for symmetric eigenvalues (definiteness).",
        "signature": "np.linalg.solve(A, b) · np.linalg.lstsq(Z, y, rcond=None) · np.linalg.cond(A) · np.linalg.eigvalsh(H)",
        "args": [("solve", "A must be square and non-singular; raises `LinAlgError: Singular matrix` otherwise"),
                 ("lstsq", "solves min ||Zw − y|| directly, more stably than the normal equations"),
                 ("cond", "κ(A); above ~1e12 your solution's digits are untrustworthy"),
                 ("eigvalsh", "eigenvalues of a symmetric matrix, sorted ascending")],
        "body": r"""
Classify a Hessian with `eigvalsh` ([[p-eigen-definiteness]]); check a design matrix with `cond` before and after scaling or ridge ([[c-conditioning-ridge]]).
""",
        "code": '''import numpy as np

H = np.array([[2.0, -3.0], [-3.0, 8.0]])            # Lecture 5, example 1
print("eigenvalues:", np.linalg.eigvalsh(H).round(4), "-> positive definite")

Z = np.array([[1, 0], [1, 1], [1, 2]], dtype=float); y = np.array([1, 2, 2], dtype=float)
w_normal = np.linalg.solve(Z.T @ Z, Z.T @ y)
w_lstsq = np.linalg.lstsq(Z, y, rcond=None)[0]
print("normal equations:", w_normal.round(4), " lstsq:", w_lstsq.round(4))
print("cond(Z^T Z) =", round(np.linalg.cond(Z.T @ Z), 2))''',
        "concepts": ["c-least-squares", "c-conditioning-ridge", "p-eigen-definiteness"], "matlab": "A\\b, lsqminnorm, cond, eig",
        "errors": ["e-solve-singular", "e-inv-vs-solve", "e-object-dtype", "e-star-vs-at"],
    },
    {
        "id": "lib-rbf", "name": "scipy.interpolate.RBFInterpolator", "group": "Sampling and surrogates",
        "summary": "Radial basis function interpolation in any dimension.",
        "when": "Smooth scattered-data surrogates. For the lecture's Gaussian RBF, set `kernel='gaussian'` and `epsilon=np.sqrt(lam)`.",
        "signature": "RBFInterpolator(y, d, kernel='thin_plate_spline', epsilon=None, smoothing=0.0)",
        "args": [("y, d", "**y** = input points (n, dim), **d** = data values (n,). Note SciPy's naming"),
                 ("kernel", "'gaussian' for φ = exp(−(εr)²); the default thin-plate spline ignores epsilon"),
                 ("epsilon", "shape parameter; the lecture's λ in exp(−λr²) corresponds to ε = √λ"),
                 ("smoothing", "> 0 turns interpolation into regression (for noisy data)")],
        "body": r"""
SciPy writes the Gaussian kernel as $e^{-(\varepsilon r)^2}$, so the lecture's spread $\lambda$ maps to $\varepsilon = \sqrt\lambda$ ([[c-rbf]]). The default kernel silently ignores `epsilon` ([[e-rbf-epsilon]]).
""",
        "code": '''import numpy as np
from scipy.interpolate import RBFInterpolator
from scipy.stats import qmc

X = qmc.LatinHypercube(d=2, seed=1).random(30)                 # 30 training points in [0,1]^2
y = np.sin(3 * X[:, 0]) + X[:, 1]**2
Xnew = np.array([[0.5, 0.5]])
for lam in [0.1, 10.0, 1000.0]:
    rbf = RBFInterpolator(X, y, kernel="gaussian", epsilon=np.sqrt(lam))
    print(f"lam={lam:7.1f}  prediction={rbf(Xnew)[0]: .4f}   truth={np.sin(1.5) + 0.25: .4f}")''',
        "concepts": ["c-rbf"], "matlab": "newrbe / rbfcreate (File Exchange)",
        "errors": ["e-rbf-epsilon"],
    },
    {
        "id": "lib-sklearn-linear", "name": "LinearRegression and Ridge (scikit-learn)", "group": "Sampling and surrogates",
        "summary": "Least squares and ridge regression, with an intercept handled for you.",
        "when": "Polynomial surrogates (build the polynomial features first), and checking a hand-written normal-equations fit.",
        "signature": "LinearRegression(fit_intercept=True).fit(X, y) · Ridge(alpha=1.0, fit_intercept=True).fit(X, y)",
        "args": [("X", "2-D array (n_samples, n_features), even with one feature: `x.reshape(-1, 1)`"),
                 ("fit_intercept", "True adds an **unpenalized** intercept; set False if your X already has a column of ones"),
                 ("alpha (Ridge)", "the lecture's λ"),
                 (".coef_, .intercept_", "the fitted w (excluding / the intercept)")],
        "body": r"""
The lecture's ridge formula $(\mathbf{Z}^T\mathbf{Z} + \lambda\mathbf{I})^{-1}\mathbf{Z}^T\mathbf{y}$ penalizes *every* coefficient, including the intercept. scikit-learn's `Ridge` doesn't penalize its own intercept. To reproduce the formula, include your own column of ones and pass `fit_intercept=False` ([[e-ridge-intercept]]).
""",
        "code": '''import numpy as np
from sklearn.linear_model import LinearRegression, Ridge

rng = np.random.default_rng(0)
X = rng.random((30, 2)); y = 5 + X @ np.array([1.0, 2.0]) + 0.01 * rng.standard_normal(30)
Z = np.column_stack([np.ones(len(X)), X])                       # design matrix with intercept column

w_hand = np.linalg.solve(Z.T @ Z, Z.T @ y)
lr = LinearRegression().fit(X, y)
print("normal equations:", w_hand.round(4), " sklearn:", np.r_[lr.intercept_, lr.coef_].round(4))

lam = 1.0
w_ridge = np.linalg.solve(Z.T @ Z + lam * np.eye(3), Z.T @ y)
r = Ridge(alpha=lam, fit_intercept=False).fit(Z, y)              # same formula as the lecture
print("ridge formula:", w_ridge.round(4), " sklearn Ridge (fit_intercept=False):", r.coef_.round(4))''',
        "concepts": ["c-least-squares", "c-conditioning-ridge"], "matlab": "fitlm / ridge",
        "errors": ["e-sk-1d", "e-ridge-intercept", "e-scale-leak"],
    },
    {
        "id": "lib-kfold", "name": "KFold and cross-validation (scikit-learn)", "group": "Sampling and surrogates",
        "summary": "Split the training data into k folds for honest model selection.",
        "when": "Choosing any complexity knob (degree, λ, spread, width, θ).",
        "signature": "KFold(n_splits=5, shuffle=False, random_state=None).split(X) · cross_val_score(model, X, y, cv=kf, scoring=...)",
        "args": [("shuffle", "default **False**: folds are contiguous blocks, which is bad if the data is sorted"),
                 ("random_state", "fix it (with shuffle=True) so every model sees the same folds"),
                 ("scoring", "'neg_root_mean_squared_error' gives −RMSE (higher is better)")],
        "body": r"""
Create the folds **once** and reuse them for every knob value and every model family, so the comparison is fair ([[c-model-assessment]]). And shuffle unless the data order is already random ([[e-kfold-shuffle]]).
""",
        "code": '''import numpy as np
from sklearn.model_selection import KFold
from sklearn.linear_model import Ridge

rng = np.random.default_rng(0)
X = rng.random((40, 1)); y = np.sin(6 * X[:, 0]) + 0.1 * rng.standard_normal(40)
Z = np.column_stack([X[:, 0]**k for k in range(8)])            # degree-7 polynomial features
kf = KFold(n_splits=5, shuffle=True, random_state=559)          # one set of folds, reused

for lam in [1e-6, 1e-3, 1e-1, 10]:
    errs = []
    for tr, va in kf.split(Z):
        m = Ridge(alpha=lam, fit_intercept=False).fit(Z[tr], y[tr])
        errs.append(np.sqrt(np.mean((y[va] - m.predict(Z[va]))**2)))
    print(f"lambda={lam:g}  CV RMSE={np.mean(errs):.4f}")''',
        "concepts": ["c-model-assessment", "q-knob-by-cv"], "matlab": "cvpartition / crossval",
        "errors": ["e-kfold-shuffle", "e-scale-leak"],
    },
    {
        "id": "lib-mlp", "name": "MLPRegressor (scikit-learn)", "group": "Sampling and surrogates",
        "summary": "A feedforward neural-network regressor.",
        "when": "Larger datasets or many inputs. For small smooth problems use `solver='lbfgs'` with enough `max_iter`.",
        "signature": "MLPRegressor(hidden_layer_sizes=(100,), activation='relu', solver='adam', alpha=1e-4, max_iter=200, random_state=None)",
        "args": [("hidden_layer_sizes", "a **tuple**: `(32,)` is one layer of 32 neurons"),
                 ("solver", "'lbfgs' (quasi-Newton, good for small data) or 'adam' (stochastic, for big data)"),
                 ("max_iter", "default 200 is often too few, so watch for `ConvergenceWarning`"),
                 ("alpha", "an L2 weight penalty: a second complexity knob, like ridge's λ"),
                 ("random_state", "fix it: training starts from random weights")],
        "body": r"""
Training is unconstrained optimization of the weights ([[c-ann]]), and `solver='lbfgs'` literally uses the quasi-Newton method from Lecture 6 ([[c-quasi-newton]]).
""",
        "code": '''import warnings
import numpy as np
from sklearn.neural_network import MLPRegressor

rng = np.random.default_rng(0)
X = rng.random((60, 2)); y = np.sin(3 * X[:, 0]) * X[:, 1]
net = MLPRegressor(hidden_layer_sizes=(16,), solver="lbfgs", max_iter=5000, random_state=559)
with warnings.catch_warnings():
    warnings.simplefilter("error")          # turn any ConvergenceWarning into a visible error
    net.fit(X, y)
print("converged in", net.n_iter_, "iterations; training R^2 =", round(net.score(X, y), 4))''',
        "concepts": ["c-ann"], "matlab": "fitrnet",
        "errors": ["e-mlp-convergence", "e-sk-1d"],
    },
    {
        "id": "lib-gpr", "name": "GaussianProcessRegressor (scikit-learn)", "group": "Sampling and surrogates",
        "summary": "Kriging with uncertainty: predictions and standard deviations.",
        "when": "Small, expensive datasets; when you need error bars or want to choose the next sample.",
        "signature": "GaussianProcessRegressor(kernel=None, alpha=1e-10, normalize_y=False, n_restarts_optimizer=0, random_state=None)",
        "args": [("kernel", "e.g. `ConstantKernel() * RBF(length_scale=np.ones(d))`; an **array** length scale is anisotropic (one per input)"),
                 ("alpha", "the nugget added to the diagonal (default 1e-10)"),
                 ("normalize_y", "**set True** unless your y has mean ≈ 0 and variance ≈ 1; otherwise predictions revert to 0 away from data"),
                 ("predict(X, return_std=True)", "returns the mean and the standard deviation s"),
                 ("n_restarts_optimizer", "restarts the maximum-likelihood fit of θ from random starts")],
        "body": r"""
sklearn's RBF kernel $\exp(-\|\mathbf{x}-\mathbf{x}'\|^2/(2\ell^2))$ is the lecture's correlation with $\theta = 1/(2\ell^2)$ ([[c-kriging]]), and `alpha` is the nugget. Fitting maximizes the likelihood over $\ell$ (the course: θ by maximum likelihood).
""",
        "code": '''import numpy as np
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, ConstantKernel

rng = np.random.default_rng(0)
X = rng.random((12, 1)); y = 100 + 5 * np.sin(6 * X[:, 0])        # data with a large mean
kernel = ConstantKernel(1.0) * RBF(length_scale=np.ones(1))
gp = GaussianProcessRegressor(kernel=kernel, normalize_y=True, n_restarts_optimizer=3, random_state=559).fit(X, y)
Xq = np.array([[X[0, 0]], [2.0]])                                     # a training point, and far away
mean, std = gp.predict(Xq, return_std=True)
print("at a training point: mean %.2f, std %.4f" % (mean[0], std[0]))
print("far from the data:   mean %.2f, std %.4f" % (mean[1], std[1]))''',
        "concepts": ["c-kriging", "c-gpr-uncertainty"], "matlab": "fitrgp",
        "errors": ["e-gpr-normalize", "e-sk-1d"],
    },
    {
        "id": "lib-matlab", "name": "MATLAB ↔ Python cheat sheet", "group": "Reference",
        "summary": "The course allows either language; here is the mapping.",
        "when": "Translating a MATLAB example to Python (or back).",
        "signature": "",
        "args": [],
        "body": r"""
| Task | MATLAB | Python |
|---|---|---|
| Constrained NLP | `fmincon(fun, x0, A, b, Aeq, beq, lb, ub, nonlcon)` | `minimize(..., method='SLSQP' or 'trust-constr')` |
| Constraint sign | `nonlcon` returns `c(x) <= 0` | dict `'ineq'` wants `fun(x) >= 0`, so pass `-c` |
| Unconstrained | `fminunc` / `fminsearch` | `minimize(method='BFGS')` / `method='Nelder-Mead'` |
| 1-D minimization | `fminbnd` | `minimize_scalar(method='bounded')` |
| Linear program | `linprog(f, A, b, Aeq, beq, lb, ub)` | `linprog(c, A_ub, b_ub, A_eq, b_eq, bounds)` |
| Root of 1-D function | `fzero` | `brentq` |
| System of equations | `fsolve` | `fsolve` / `root` |
| Latin hypercube | `lhsdesign(n, d)` | `qmc.LatinHypercube(d).random(n)` |
| Linear regression | `fitlm` | `LinearRegression` |
| Neural network | `fitrnet` | `MLPRegressor` |
| Gaussian process | `fitrgp` | `GaussianProcessRegressor` |
| Solve Ax = b | `A \ b` | `np.linalg.solve(A, b)` |
| Help | `help fmincon` | `help(scipy.optimize.minimize)` |

The biggest translation trap is the constraint sign: MATLAB's `nonlcon` uses the course's $c(\mathbf{x})\le0$ directly; SciPy's dict form uses $\ge0$ ([[e-ineq-sign]]). Also note MATLAB indexes from 1 and Python from 0.
""",
        "code": "",
        "concepts": ["c-negative-null-form"], "matlab": "",
        "errors": ["e-ineq-sign"],
    },
]

# ------------------------------------------------------------------ the bug library
# kind: "crash" (raises), "warning" (warns, keeps going), "silent" (no message; wrong answer).
# verify: ("raises", "ExceptionName", "substring") | ("warns", "WarningName", "substring") | ("silent", "<expr True after bad>")
# good_check: expression that must be True after running the good snippet. show: expression printed for both.
ERRORS = [
    {
        "id": "e-ineq-sign", "title": "Passing g(x) ≤ 0 straight to SciPy's 'ineq'", "lib": SCIPY, "kind": "silent",
        "why": "SciPy's dict constraints mean `fun(x) >= 0`, the opposite of the course's negative null form `g(x) <= 0`. Passing `g` directly enforces the *reverse* of every constraint, so the solver often returns the unconstrained optimum and reports success. **Even the course's own template `constrained_optimization_template_python.py` has this bug:** its comment says \"'ineq' means constraint_fun(x) <= 0\", and run as written it returns x = (1, 2), violating both of its constraints. The correct answer is (0.5, 1).",
        "fix": "Pass `-g`: `{'type': 'ineq', 'fun': lambda x: -g(x)}`, or use `NonlinearConstraint(g, -np.inf, 0)`, which states the direction explicitly. Always print `g(res.x)` afterwards: every entry must be ≤ 0.",
        "bad": '''from scipy.optimize import minimize
f = lambda x: (x[0] - 1)**2 + (x[1] - 2)**2
g = lambda x: x[0] + 2*x[1] - 2.5                 # want g(x) <= 0
res = minimize(f, [0.5, 0.5], method="SLSQP",
               constraints=[{"type": "ineq", "fun": g}])''',
        "good": '''from scipy.optimize import minimize
f = lambda x: (x[0] - 1)**2 + (x[1] - 2)**2
g = lambda x: x[0] + 2*x[1] - 2.5                 # want g(x) <= 0
res = minimize(f, [0.5, 0.5], method="SLSQP",
               constraints=[{"type": "ineq", "fun": lambda x: -g(x)}])''',
        "verify": ("silent", "res.success and g(res.x) > 0.1"), "good_check": "abs(g(res.x)) < 1e-6 and abs(res.x[0] - 0.5) < 1e-4",
        "show": "f'x = {res.x.round(4)},  g(x) = {g(res.x):.4f},  success = {res.success}'",
        "concepts": ["c-negative-null-form", "c-feasibility"],
        "quiz": spot("Which line has the bug? (the course writes constraints as g(x) ≤ 0)", [
            ("g = lambda x: x[0] + 2*x[1] - 2.5      # g(x) <= 0", False, ""),
            ("cons = [{'type': 'ineq', 'fun': g}]", True, "SciPy's 'ineq' means fun(x) ≥ 0. Pass `lambda x: -g(x)`."),
            ("res = minimize(f, x0, method='SLSQP', constraints=cons)", False, ""),
            ("print(res.x, g(res.x))", False, ""),
        ], code=True),
    },
    {
        "id": "e-args-tuple", "title": "args=(p) instead of args=(p,) in a constraint dict", "lib": PYTHON, "kind": "crash",
        "why": "`(p)` is just `p` in parentheses; only a trailing comma makes a tuple. SciPy calls `fun(x, *args)`, and unpacking a dict with `*` passes its **keys** as extra arguments, so a 13-key parameter dict gives 'takes 2 positional arguments but 14 were given'. (In `minimize`'s own `args=`, SciPy quietly wraps a non-tuple for you, which is why the same mistake can work in one place and crash in another.)",
        "fix": "Always write `args=(p,)`. The error count is a fingerprint: 'but N+1 were given' with N = the number of keys in your dict.",
        "bad": '''from scipy.optimize import minimize
p = {"a": 1.0, "b": 2.0}
f = lambda x, p: x[0]**2
c = lambda x, p: x[0] - p["a"]
res = minimize(f, [3.0], args=(p,), method="SLSQP",
               constraints=[{"type": "ineq", "fun": c, "args": (p)}])''',
        "good": '''from scipy.optimize import minimize
p = {"a": 1.0, "b": 2.0}
f = lambda x, p: x[0]**2
c = lambda x, p: x[0] - p["a"]
res = minimize(f, [3.0], args=(p,), method="SLSQP",
               constraints=[{"type": "ineq", "fun": c, "args": (p,)}])''',
        "verify": ("raises", "TypeError", "positional argument"), "good_check": "abs(res.x[0] - 1.0) < 1e-5",
        "show": "f'x = {res.x.round(4)}'",
        "concepts": ["p-python-functions"],
        "quiz": blank("Fix the tuple: `'args': ____` (the only extra argument is `p`)", ["(p,)"], mode="code"),
    },
    {
        "id": "e-objective-vector", "title": "Objective returns an array instead of a scalar", "lib": SCIPY, "kind": "crash",
        "why": "Optimizers minimize one number. Returning several values (say, all your functions of interest at once) leaves 'minimize' undefined. (A length-1 array is tolerated, but don't rely on it.)",
        "fix": "Return a single float. If you have several objectives, combine them deliberately (weights) or turn all but one into constraints (ε-constraint method).",
        "bad": '''import numpy as np
from scipy.optimize import minimize
f = lambda x: np.array([x[0]**2, (x[0] - 1)**2])      # two objectives at once
res = minimize(f, [1.0])''',
        "good": '''import numpy as np
from scipy.optimize import minimize
f = lambda x: x[0]**2 + (x[0] - 1)**2                 # one scalar objective
res = minimize(f, [1.0])''',
        "verify": ("raises", "ValueError", "scalar"), "good_check": "abs(res.x[0] - 0.5) < 1e-5",
        "show": "f'x = {res.x.round(4)}'",
        "concepts": ["c-pareto"],
        "quiz": choice("Your `f(x)` returns `[mass, stress]`. What should you do?", [
            opt("Minimize mass and impose stress ≤ σ_y as a constraint (ε-constraint)", True),
            opt("Return `np.sum([mass, stress])`", why="Adding quantities with different units is meaningless unless you weight them deliberately."),
            opt("Return the array; SciPy handles multi-objective problems", why="`minimize` needs a scalar."),
            opt("Return `max(mass, stress)`", why="Again mixing units; and it isn't what you want.")]),
    },
    {
        "id": "e-bounds-format", "title": "Bounds written as a flat list", "lib": SCIPY, "kind": "crash",
        "why": "`bounds` needs one `(low, high)` pair **per variable**. A flat `[0, 1]` for two variables means 'variable 0 has bound 0, variable 1 has bound 1', and a single number isn't a pair.",
        "fix": "Write `bounds=[(0, 1), (0, 1)]`, or `Bounds([0, 0], [1, 1])`. Use `None` for 'no bound': `(0, None)`.",
        "bad": '''from scipy.optimize import minimize
res = minimize(lambda x: (x[0] - 2)**2 + (x[1] - 2)**2, [0.5, 0.5],
               method="L-BFGS-B", bounds=[0, 1])''',
        "good": '''from scipy.optimize import minimize
res = minimize(lambda x: (x[0] - 2)**2 + (x[1] - 2)**2, [0.5, 0.5],
               method="L-BFGS-B", bounds=[(0, 1), (0, 1)])''',
        "verify": ("raises", "TypeError", "not iterable"), "good_check": "abs(res.x[0] - 1) < 1e-6 and abs(res.x[1] - 1) < 1e-6",
        "show": "f'x = {res.x.round(4)}'",
        "concepts": ["c-negative-null-form"],
        "quiz": blank("Bounds for two variables, each in [0, 1]: `bounds=____`", ["[(0,1),(0,1)]", "[(0, 1), (0, 1)]", "((0,1),(0,1))", "[(0., 1.), (0., 1.)]", "[(0.,1.),(0.,1.)]"], mode="code"),
    },
    {
        "id": "e-method-ignores", "title": "Bounds or constraints given to a method that ignores them", "lib": SCIPY, "kind": "warning",
        "why": "Methods like `BFGS`, `CG` and `Nelder-Mead` (for constraints) don't support them. SciPy emits a `RuntimeWarning` and then **solves the unconstrained problem anyway**. In a notebook the warning is easy to miss.",
        "fix": "Use `L-BFGS-B` for bounds only, `SLSQP` or `trust-constr` for constraints. Check the result against the bounds and constraints.",
        "bad": '''from scipy.optimize import minimize
res = minimize(lambda x: (x[0] + 3)**2, [1.0], method="BFGS", bounds=[(0, 2)])''',
        "good": '''from scipy.optimize import minimize
res = minimize(lambda x: (x[0] + 3)**2, [1.0], method="L-BFGS-B", bounds=[(0, 2)])''',
        "verify": ("warns", "RuntimeWarning", "cannot handle bounds"), "good_check": "abs(res.x[0]) < 1e-6",
        "show": "f'x = {res.x.round(4)}'",
        "concepts": ["c-quasi-newton"],
        "quiz": choice("Which method respects simple bounds?", [opt("`L-BFGS-B`", True), opt("`BFGS`", why="BFGS ignores bounds (with only a warning)."),
                                                                  opt("`CG`", why="CG ignores bounds."), opt("`Newton-CG`", why="Newton-CG ignores bounds.")]),
    },
    {
        "id": "e-constraint-dict-typo", "title": "A typo in a constraint dict ('inequality', 'func')", "lib": SCIPY, "kind": "crash",
        "why": "The dict keys and values are fixed strings: `'type'` must be exactly `'ineq'` or `'eq'`, and the function key is `'fun'` (not `'func'` or `'function'`).",
        "fix": "Copy a working template, or use `NonlinearConstraint`, where a typo is a Python error at the point you make it.",
        "bad": '''from scipy.optimize import minimize
res = minimize(lambda x: x[0]**2, [3.0], method="SLSQP",
               constraints=[{"type": "inequality", "fun": lambda x: x[0] - 1}])''',
        "good": '''from scipy.optimize import minimize
res = minimize(lambda x: x[0]**2, [3.0], method="SLSQP",
               constraints=[{"type": "ineq", "fun": lambda x: x[0] - 1}])''',
        "verify": ("raises", "ValueError", "Unknown constraint type"), "good_check": "abs(res.x[0] - 1) < 1e-6",
        "show": "f'x = {res.x.round(4)}'",
        "concepts": ["c-negative-null-form"],
        "quiz": spot("Which dict is wrong?", [
            ("{'type': 'ineq', 'fun': c1}", False, ""),
            ("{'type': 'eq', 'fun': h1}", False, ""),
            ("{'type': 'ineq', 'func': c2}", True, "The key is `'fun'`. SciPy raises 'Constraint 0 has no function defined'."),
            ("{'type': 'ineq', 'fun': c3, 'args': (p,)}", False, ""),
        ], code=True),
    },
    {
        "id": "e-lambda-late-binding", "title": "Lambdas built in a loop all use the last loop value", "lib": PYTHON, "kind": "silent",
        "why": "A lambda looks up `i` when it is **called**, not when it's created. After the loop finishes, `i` is the last value, so every constraint enforces the same thing. Here, three intended constraints x_i ≥ limit_i collapse into three copies of x₂ ≥ 3.",
        "fix": "Freeze the value with a default argument, `lambda x, i=i: ...`, as the course's own ε-constraint notebooks do with `e=eps_k`.",
        "bad": '''from scipy.optimize import minimize
import numpy as np
limits = [1.0, 2.0, 3.0]
cons = [{"type": "ineq", "fun": lambda x: x[i] - limits[i]} for i in range(3)]
res = minimize(lambda x: (x**2).sum(), [5.0, 5.0, 5.0], method="SLSQP", constraints=cons)''',
        "good": '''from scipy.optimize import minimize
import numpy as np
limits = [1.0, 2.0, 3.0]
cons = [{"type": "ineq", "fun": lambda x, i=i: x[i] - limits[i]} for i in range(3)]
res = minimize(lambda x: (x**2).sum(), [5.0, 5.0, 5.0], method="SLSQP", constraints=cons)''',
        "verify": ("silent", "abs(res.x[0]) < 1e-4 and abs(res.x[2] - 3) < 1e-4"), "good_check": "np.allclose(res.x, [1, 2, 3], atol=1e-5)",
        "show": "f'x = {res.x.round(4)}'",
        "concepts": ["p-python-functions", "c-pareto"],
        "quiz": blank("Fix it: `lambda x, ____: x[i] - limits[i]` (freeze the loop value)", ["i=i"], mode="code"),
    },
    {
        "id": "e-int-array", "title": "An integer array swallows a small finite-difference step", "lib": NUMPY, "kind": "silent",
        "why": "`np.array([1, 2])` has an **integer** dtype. Adding `1e-4` to one entry truncates it straight back to the integer, so your hand-made finite difference (or monotonicity nudge) changes nothing and reports 'independent'.",
        "fix": "Create float arrays: `np.array(x, dtype=float)`, or write the starting values as floats (`[1.0, 2.0]`). The course's HW1 guide does exactly this.",
        "bad": '''import numpy as np
x = np.array([1, 2])        # integer dtype
x[0] += 1e-4''',
        "good": '''import numpy as np
x = np.array([1, 2], dtype=float)
x[0] += 1e-4''',
        "verify": ("silent", "x[0] == 1"), "good_check": "abs(x[0] - 1.0001) < 1e-12",
        "show": "f'x = {x}  dtype = {x.dtype}'",
        "concepts": ["p-numpy-shapes", "c-monotonicity"],
        "quiz": choice("`x = np.array([1, 2]); x[0] += 0.5; print(x)` prints…", [opt("`[1 2]`", True), opt("`[1.5 2. ]`", why="The array is integer-typed; 1.5 is truncated to 1 on assignment."),
                                                                                  opt("an error", why="NumPy silently casts."), opt("`[2 2]`", why="It truncates, it doesn't round.")]),
    },
    {
        "id": "e-view-copy", "title": "Modifying a 'copy' that is really the same array", "lib": NUMPY, "kind": "silent",
        "why": "`step = base` doesn't copy anything; both names point to the same array. Nudging `step` also moves `base`, so every later comparison is against a corrupted base point.",
        "fix": "Use `step = base.copy()` (or `np.array(base, dtype=float)`, which also copies) whenever you'll modify it.",
        "bad": '''import numpy as np
base = np.array([0.1, 0.2])
step = base
step[0] += 1e-4''',
        "good": '''import numpy as np
base = np.array([0.1, 0.2])
step = base.copy()
step[0] += 1e-4''',
        "verify": ("silent", "base[0] != 0.1"), "good_check": "base[0] == 0.1 and step[0] != 0.1",
        "show": "f'base = {base}'",
        "concepts": ["p-numpy-shapes"],
        "quiz": blank("Make an independent copy: `step = base____`", [".copy()"], mode="code"),
    },
    {
        "id": "e-ignore-success", "title": "Reading res.x without checking res.success", "lib": SCIPY, "kind": "silent",
        "why": "Optimizers always return *some* `x`, even when they failed (infeasible constraints, iteration limits, line-search failure). Here the constraints `x ≥ 1` and `x ≤ 0` are inconsistent; SLSQP returns `success=False` and an `x` that looks perfectly ordinary.",
        "fix": "Always print `res.success` and `res.message`, and verify feasibility yourself: `np.all(g(res.x) <= 1e-6)`. In a parametric study, store NaN for failed runs, as HW1's guide does.",
        "bad": '''from scipy.optimize import minimize
res = minimize(lambda x: x[0], [0.0], method="SLSQP",
               constraints=[{"type": "ineq", "fun": lambda x: x[0] - 1},     # x >= 1
                            {"type": "ineq", "fun": lambda x: -x[0]}])       # x <= 0
x_opt = res.x''',
        "good": '''from scipy.optimize import minimize
res = minimize(lambda x: x[0], [0.0], method="SLSQP",
               constraints=[{"type": "ineq", "fun": lambda x: x[0] - 1},
                            {"type": "ineq", "fun": lambda x: -x[0]}])
x_opt = res.x if res.success else None          # refuse to use a failed result''',
        "verify": ("silent", "not res.success"), "good_check": "x_opt is None",
        "show": "f'success = {res.success}, message = {res.message!r}, x = {res.x}'",
        "concepts": ["c-convergence-termination", "c-feasibility"],
        "quiz": order("A safe post-solve routine: put the steps in order.", [
            "Check res.success and read res.message",
            "Evaluate every constraint at res.x and confirm g ≤ tolerance",
            "Label each constraint active or inactive",
            "Only then report res.x and res.fun",
        ]),
    },
    {
        "id": "e-nan-domain", "title": "The optimizer steps outside your function's domain (NaN)", "lib": SCIPY, "kind": "silent",
        "why": "Unbounded methods take trial steps anywhere. If your model uses `np.sqrt`, `log` or fractional powers, a step to a negative value returns NaN, and the run ends in nonsense (here x ≈ −1000, f = nan, 'precision loss').",
        "fix": "Give bounds that keep the variables in the model's valid domain (e.g. `(1e-9, None)`) and use a bounded method (`L-BFGS-B`, `SLSQP`). Physical variables like radii and thicknesses should always be bounded away from 0.",
        "bad": '''import numpy as np, warnings
from scipy.optimize import minimize
warnings.simplefilter("ignore")
f = lambda x: (x[0] - 0.3)**2 + np.sqrt(x[0])
res = minimize(f, [0.9], method="BFGS")''',
        "good": '''import numpy as np, warnings
from scipy.optimize import minimize
warnings.simplefilter("ignore")
f = lambda x: (x[0] - 0.3)**2 + np.sqrt(x[0])
res = minimize(f, [0.9], method="L-BFGS-B", bounds=[(1e-9, None)])''',
        "verify": ("silent", "np.isnan(res.fun) or res.x[0] < 0"), "good_check": "res.success and res.x[0] >= 0 and np.isfinite(res.fun)",
        "show": "f'x = {res.x.round(4)}, f = {res.fun}, success = {res.success}'",
        "concepts": ["c-boundedness", "c-analysis-to-synthesis"],
        "quiz": choice("Your model computes `R**(2/3)` and the optimizer returns NaN. Best fix?", [
            opt("Add a bound keeping R > 0 and use a bounded method", True), opt("Wrap the model in try/except", why="NaN isn't an exception; it silently propagates."),
            opt("Use `abs(R)**(2/3)`", why="That hides the problem: negative radii would look valid to the optimizer."), opt("Tighten the tolerance", why="Tolerance doesn't keep R positive.")]),
    },
    {
        "id": "e-bad-scaling", "title": "Badly scaled variables stall the optimizer", "lib": SCIPY, "kind": "silent",
        "why": "With one variable around 10⁻³ (metres) and another around 10⁸ (pascals), the gradient's components differ by ~10¹¹. Finite-difference steps and stopping tests use absolute sizes, so the optimizer barely moves the large variable and stops early ([[c-scaling]]).",
        "fix": "Optimize in scaled units, e.g. `z = x / x_ref` so every variable is order 1, and normalize constraints as `g/g_max − 1`. Convert back at the end.",
        "bad": '''from scipy.optimize import minimize
f = lambda x: (x[0] / 1e-3 - 2)**2 + (x[1] / 1e8 - 3)**2     # true optimum (2e-3, 3e8)
res = minimize(f, [1e-3, 1e8], method="BFGS")''',
        "good": '''import numpy as np
from scipy.optimize import minimize
x_ref = np.array([1e-3, 1e8])
f = lambda x: (x[0] / 1e-3 - 2)**2 + (x[1] / 1e8 - 3)**2
res = minimize(lambda z: f(z * x_ref), [1.0, 1.0], method="BFGS")   # optimize z = x / x_ref
res.x = res.x * x_ref''',
        "verify": ("silent", "abs(res.x[1] / 1e8 - 3) > 0.5"), "good_check": "abs(res.x[1] / 1e8 - 3) < 1e-4 and abs(res.x[0] / 1e-3 - 2) < 1e-4",
        "show": "f'x = {res.x}'",
        "concepts": ["c-scaling", "c-negative-null-form"],
        "quiz": choice("Which formulation is best scaled?", [opt("Variables in mm and MPa so all are order 1, constraints as σ/σ_y − 1 ≤ 0", True),
                                                              opt("SI units throughout, constraints as σ − σ_y ≤ 0", why="Pascals (~10⁸) next to metres (~10⁻³) is the classic bad scaling."),
                                                              opt("Whatever units the data came in", why="Scaling is a deliberate choice."), opt("All variables multiplied by 10⁶", why="Uniform scaling doesn't fix *relative* scale differences.")]),
    },
    {
        "id": "e-wrong-jac", "title": "A wrong analytic gradient (jac=) misleads the optimizer", "lib": SCIPY, "kind": "silent",
        "why": "When you pass `jac=`, the optimizer trusts it for directions **and** for stopping. Here the gradient forgets the `x0*x1` cross-term in ∂f/∂x0, so the optimizer heads for the wrong point and stops away from the true optimum (0, 2).",
        "fix": "Check every hand-written gradient with `scipy.optimize.check_grad(f, grad, x_test)` at a random point. The result should be ~1e-6 or smaller. Or omit `jac` and let SciPy use finite differences.",
        "bad": '''import numpy as np, warnings
from scipy.optimize import minimize
warnings.simplefilter("ignore")
f = lambda x: (x[0] - 1)**2 + 3*(x[1] - 2)**2 + x[0]*x[1]
grad = lambda x: np.array([2*(x[0] - 1), 6*(x[1] - 2) + x[0]])      # missing  + x[1]
res = minimize(f, [1.0, 1.0], jac=grad, method="BFGS")''',
        "good": '''import numpy as np, warnings
from scipy.optimize import minimize
warnings.simplefilter("ignore")
f = lambda x: (x[0] - 1)**2 + 3*(x[1] - 2)**2 + x[0]*x[1]
grad = lambda x: np.array([2*(x[0] - 1) + x[1], 6*(x[1] - 2) + x[0]])
res = minimize(f, [1.0, 1.0], jac=grad, method="BFGS")''',
        "verify": ("silent", "np.linalg.norm(res.x - np.array([0.0, 2.0])) > 0.1"), "good_check": "np.allclose(res.x, [0.0, 2.0], atol=1e-5)",
        "show": "f'x = {res.x.round(4)}, success = {res.success}'",
        "concepts": ["p-gradient", "c-quasi-newton"],
        "quiz": choice("`check_grad(f, grad, x)` returns 2.0. What does that mean?", [opt("Your gradient disagrees with finite differences: it's wrong", True),
                                                                                       opt("The gradient is correct to two digits", why="It's the norm of the *difference*; it should be ~1e-6."),
                                                                                       opt("The optimizer will take 2 iterations", why="It says nothing about iterations."), opt("x is a stationary point", why="It compares two gradient computations.")]),
    },
    {
        "id": "e-linprog-max", "title": "Forgetting that linprog minimizes", "lib": SCIPY, "kind": "silent",
        "why": "`linprog` always minimizes. Passing the profit coefficients `[40, 30]` minimizes profit, so it happily returns x = (0, 0), with zero profit and 'success'.",
        "fix": "To maximize, pass `-c`, then report `-res.fun`.",
        "bad": '''from scipy.optimize import linprog
res = linprog([40, 30], A_ub=[[2, 1], [1, 1]], b_ub=[320, 240])''',
        "good": '''from scipy.optimize import linprog
res = linprog([-40, -30], A_ub=[[2, 1], [1, 1]], b_ub=[320, 240])
profit = -res.fun''',
        "verify": ("silent", "res.success and abs(res.fun) < 1e-9"), "good_check": "abs(profit - 8000) < 1e-6",
        "show": "f'x = {res.x}, fun = {res.fun}'",
        "concepts": ["c-lp-standard-form"],
        "quiz": blank("Maximize 40x₁ + 30x₂ with linprog: `c = ____`", ["[-40,-30]", "[-40, -30]", "np.array([-40,-30])", "-np.array([40,30])", "(-40,-30)"], mode="code"),
    },
    {
        "id": "e-linprog-ge", "title": "Passing a ≥ constraint as A_ub without flipping its sign", "lib": SCIPY, "kind": "silent",
        "why": "`A_ub @ x <= b_ub` only. Writing the requirement x₁ + x₂ ≥ 2 as `A_ub=[[1, 1]], b_ub=[2]` encodes x₁ + x₂ ≤ 2, the opposite. Here it returns (0, 0), which violates the real requirement.",
        "fix": "Multiply both sides by −1: `A_ub=[[-1, -1]], b_ub=[-2]`.",
        "bad": '''from scipy.optimize import linprog
res = linprog([1, 1], A_ub=[[1, 1]], b_ub=[2])         # meant: x1 + x2 >= 2''',
        "good": '''from scipy.optimize import linprog
res = linprog([1, 1], A_ub=[[-1, -1]], b_ub=[-2])      # -(x1 + x2) <= -2''',
        "verify": ("silent", "res.x.sum() < 2 - 1e-9"), "good_check": "abs(res.x.sum() - 2) < 1e-9",
        "show": "f'x = {res.x}, x1+x2 = {res.x.sum()}'",
        "concepts": ["c-lp-standard-form", "c-negative-null-form"],
        "quiz": blank("Encode 3x₁ − x₂ ≥ 5 as a row of A_ub: `A_ub=[____], b_ub=[-5]`", ["[-3,1]", "[-3, 1]"], mode="code"),
    },
    {
        "id": "e-linprog-bounds", "title": "linprog's default bounds make every variable non-negative", "lib": SCIPY, "kind": "silent",
        "why": "The default is `bounds=(0, None)` for every variable, the LP standard form's x ≥ 0. A variable that should be free can't go negative, so you get the wrong optimum with no warning. Here min x with x ≥ −5 returns 0 instead of −5.",
        "fix": "Give bounds explicitly: `bounds=[(None, None)]` for a free variable.",
        "bad": '''from scipy.optimize import linprog
res = linprog([1], A_ub=[[-1]], b_ub=[5])                 # minimize x  s.t.  x >= -5''',
        "good": '''from scipy.optimize import linprog
res = linprog([1], A_ub=[[-1]], b_ub=[5], bounds=[(None, None)])''',
        "verify": ("silent", "abs(res.x[0]) < 1e-9"), "good_check": "abs(res.x[0] + 5) < 1e-9",
        "show": "f'x = {res.x}'",
        "concepts": ["c-lp-standard-form"],
        "quiz": choice("A variable represents a temperature change that may be negative. In linprog you should…", [opt("set its bounds to `(None, None)`", True),
                                                                                                                  opt("leave the default bounds", why="The default forces it ≥ 0."), opt("substitute z = u − v by hand", why="That works, but `bounds=(None, None)` does it for you."),
                                                                                                                  opt("add a slack variable", why="Slacks are for inequalities, not free variables.")]),
    },
    {
        "id": "e-brentq-sign", "title": "brentq without a sign change on the bracket", "lib": SCIPY, "kind": "crash",
        "why": "Brent's method needs f(a) and f(b) of opposite signs, so that a root is guaranteed in between. If both have the same sign there may be no root, or an even number of them.",
        "fix": "Plot or tabulate f first, and pick [a, b] where it changes sign. For a constraint residual, evaluate it at both ends before calling.",
        "bad": '''from scipy.optimize import brentq
r = brentq(lambda t: (t - 3)**2 - 1, 0, 1)''',
        "good": '''from scipy.optimize import brentq
r = brentq(lambda t: (t - 3)**2 - 1, 0, 3)               # f(0) = 8 > 0, f(3) = -1 < 0''',
        "verify": ("raises", "ValueError", "different signs"), "good_check": "abs(r - 2) < 1e-9",
        "show": "f'root = {r}'",
        "concepts": ["p-newton-raphson"],
        "quiz": choice("f(1) = 4 and f(5) = 2. Can you call `brentq(f, 1, 5)`?", [opt("No: same sign, no guaranteed root", True), opt("Yes, it will find the minimum", why="brentq finds roots, not minima."),
                                                                                  opt("Yes, but slowly", why="It raises immediately."), opt("Only with a tighter tolerance", why="Tolerance doesn't create a sign change.")]),
    },
    {
        "id": "e-fsolve-silent", "title": "fsolve returns a non-solution with only a warning", "lib": SCIPY, "kind": "warning",
        "why": "`fsolve` always returns an array. When it fails (here t² + 1 = 0 has no real root) it warns 'not making good progress' and returns its last iterate, which looks like a perfectly normal number.",
        "fix": "Use `root(...)` and check `.success`, or `fsolve(..., full_output=True)` and check `ier == 1`. Always plug the answer back in and confirm the residual is ~0.",
        "bad": '''from scipy.optimize import fsolve
x = fsolve(lambda t: t**2 + 1, 1.0)''',
        "good": '''from scipy.optimize import root
sol = root(lambda t: t**2 + 1, 1.0)
x = sol.x if sol.success else None''',
        "verify": ("warns", "RuntimeWarning", "not making good progress"), "good_check": "x is None",
        "show": "f'x = {x}'",
        "concepts": ["p-newton-raphson"],
        "quiz": choice("After `x = fsolve(F, x0)`, the most reliable check is…", [opt("compute F(x) and confirm it's ≈ 0", True), opt("check that x is finite", why="Failed runs return finite numbers too."),
                                                                                   opt("check x is different from x0", why="It moved; that doesn't mean it solved anything."), opt("none: fsolve raises on failure", why="It only warns.")]),
    },
    {
        "id": "e-solve-singular", "title": "np.linalg.solve on a singular matrix", "lib": NUMPY, "kind": "crash",
        "why": "A matrix with dependent columns has no inverse. In least squares this happens when a feature is a copy or multiple of another, or when you have fewer data points than coefficients.",
        "fix": "Check `np.linalg.matrix_rank` and `np.linalg.cond`. Remove duplicate features, collect more data, use `lstsq`, or regularize (ridge).",
        "bad": '''import numpy as np
A = np.array([[1.0, 2.0], [2.0, 4.0]])
x = np.linalg.solve(A, np.array([1.0, 2.0]))''',
        "good": '''import numpy as np
A = np.array([[1.0, 2.0], [2.0, 4.0]])
x = np.linalg.lstsq(A, np.array([1.0, 2.0]), rcond=None)[0]    # minimum-norm least-squares solution''',
        "verify": ("raises", "LinAlgError", "Singular matrix"), "good_check": "np.allclose(A @ x, [1, 2])",
        "show": "f'x = {x.round(4)}'",
        "concepts": ["p-linear-systems", "c-least-squares"],
        "quiz": choice("You add a feature x₃ = 2·x₁ to your regression. `solve(Z.T @ Z, ...)` now…", [opt("fails or is wildly unstable: the columns are dependent", True),
                                                                                                      opt("gets more accurate", why="A redundant feature adds no information and breaks invertibility."),
                                                                                                      opt("is unchanged", why="ZᵀZ becomes singular."), opt("runs faster", why="Not relevant.")]),
    },
    {
        "id": "e-inv-vs-solve", "title": "Computing inv(A) @ b instead of solve(A, b)", "lib": NUMPY, "kind": "silent",
        "why": "Forming the inverse explicitly is slower and loses more accuracy. On an ill-conditioned matrix (here a 12×12 Hilbert matrix, κ ≈ 10¹⁶) the error with `inv` is far larger than with `solve`, with no warning either way.",
        "fix": "Use `np.linalg.solve(A, b)`, or `lstsq` for least squares. And check `np.linalg.cond(A)`: above ~1e12, expect few correct digits whatever you do.",
        "bad": '''import numpy as np
from scipy.linalg import hilbert
A = hilbert(12); x_true = np.ones(12); b = A @ x_true
x = np.linalg.inv(A) @ b''',
        "good": '''import numpy as np
from scipy.linalg import hilbert
A = hilbert(12); x_true = np.ones(12); b = A @ x_true
x = np.linalg.solve(A, b)''',
        "verify": ("silent", "np.abs(x - x_true).max() > 1.0"), "good_check": "np.abs(x - x_true).max() < 1.0",
        "show": "f'max error = {np.abs(x - x_true).max():.3g}'",
        "concepts": ["c-conditioning-ridge", "p-linear-systems"],
        "quiz": blank("Solve A x = b the stable way: `x = np.linalg.____(A, b)`", ["solve"], mode="code"),
    },
    {
        "id": "e-object-dtype", "title": "A pandas table with a text column becomes an 'object' array", "lib": PANDAS, "kind": "crash",
        "why": "`df.values` on a DataFrame with any non-numeric column produces an array of Python objects (dtype `O`). NumPy's linear algebra refuses it, with a cryptic 'Cannot cast ufunc ... from dtype('O')'.",
        "fix": "Select the numeric columns explicitly and convert: `df[cols].to_numpy(dtype=float)`, as the HW2 template's `make_raw` does.",
        "bad": '''import numpy as np, pandas as pd
df = pd.DataFrame({"a": [1.0, 2.0, 3.0], "b": [1.0, 0.0, 1.0], "split": ["train", "train", "test"]})
A = df.values[:, :2]
x = np.linalg.solve(A[:2].T @ A[:2], np.ones(2))''',
        "good": '''import numpy as np, pandas as pd
df = pd.DataFrame({"a": [1.0, 2.0, 3.0], "b": [1.0, 0.0, 1.0], "split": ["train", "train", "test"]})
A = df[["a", "b"]].to_numpy(dtype=float)
x = np.linalg.solve(A[:2].T @ A[:2], np.ones(2))''',
        "verify": ("raises", "UFuncTypeError", "dtype('O')"), "good_check": "A.dtype == float and np.all(np.isfinite(x))",
        "show": "f'A.dtype = {A.dtype}'",
        "concepts": ["p-numpy-shapes"],
        "quiz": blank("Convert columns `cols` of `df` to a float array: `X = df[cols].____`", ["to_numpy(dtype=float)", "to_numpy(float)", "to_numpy().astype(float)", "values.astype(float)", "astype(float).to_numpy()"], mode="code"),
    },
    {
        "id": "e-broadcast-residual", "title": "Shapes (n,) and (n, 1) broadcast into an n×n residual", "lib": NUMPY, "kind": "silent",
        "why": "`y - yhat` with `y.shape == (n, 1)` and `yhat.shape == (n,)` doesn't fail. NumPy broadcasts it to an `(n, n)` array of every pairwise difference, so your RMSE is the average over all pairs: plausible-looking and completely wrong.",
        "fix": "Flatten both: `y.ravel() - yhat.ravel()`, and `assert y.shape == yhat.shape` before computing errors.",
        "bad": '''import numpy as np
y = np.array([1.0, 2.0, 3.0, 4.0, 5.0]).reshape(-1, 1)     # column vector (5, 1)
yhat = np.array([1.0, 2.0, 3.0, 4.0, 5.0])                  # perfect predictions, shape (5,)
rmse = np.sqrt(np.mean((y - yhat)**2))''',
        "good": '''import numpy as np
y = np.array([1.0, 2.0, 3.0, 4.0, 5.0]).reshape(-1, 1)
yhat = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
rmse = np.sqrt(np.mean((y.ravel() - yhat.ravel())**2))''',
        "verify": ("silent", "rmse > 1.0"), "good_check": "rmse == 0.0",
        "show": "f'rmse = {rmse}'",
        "concepts": ["p-numpy-shapes", "c-error-metrics"],
        "quiz": blank("Shape of `np.zeros((4,)) - np.zeros((4, 1))`?", ["(4,4)", "(4, 4)"], mode="code"),
    },
    {
        "id": "e-star-vs-at", "title": "Using * when you meant matrix multiplication @", "lib": NUMPY, "kind": "silent",
        "why": "`*` multiplies element by element (with broadcasting). For a matrix and a vector of compatible length it silently returns a matrix of scaled columns, not the matrix–vector product.",
        "fix": "Use `@` for matrix products: `Z @ w`, `Z.T @ Z`. Check result shapes.",
        "bad": '''import numpy as np
Z = np.array([[1.0, 0.0], [1.0, 1.0], [1.0, 2.0]]); w = np.array([1.0, 0.5])
yhat = Z * w''',
        "good": '''import numpy as np
Z = np.array([[1.0, 0.0], [1.0, 1.0], [1.0, 2.0]]); w = np.array([1.0, 0.5])
yhat = Z @ w''',
        "verify": ("silent", "yhat.shape == (3, 2)"), "good_check": "np.allclose(yhat, [1.0, 1.5, 2.0])",
        "show": "f'yhat = {yhat.tolist()}'",
        "concepts": ["p-numpy-shapes", "c-least-squares"],
        "quiz": blank("Predictions from design matrix `Z` and coefficients `w`: `yhat = Z ____ w`", ["@"], mode="code"),
    },
    {
        "id": "e-pandas-align", "title": "Subtracting pandas Series aligns on the index, giving NaN", "lib": PANDAS, "kind": "silent",
        "why": "Arithmetic between two Series matches rows by **index label**, not position. A test set sliced from a larger table keeps its original index (say 400–499); predictions built fresh have index 0–99. Nothing overlaps, so every difference is NaN, and `np.mean` of NaNs is NaN.",
        "fix": "Convert to NumPy before doing maths, `y = test['CL'].to_numpy(dtype=float)`, or `reset_index(drop=True)` after splitting (the HW2 template does both).",
        "bad": '''import numpy as np, pandas as pd
y = pd.Series([1.0, 2.0, 3.0], index=[400, 401, 402])    # test rows keep their original index
yhat = pd.Series([1.0, 2.0, 3.0])                           # predictions: index 0, 1, 2
err = y - yhat''',
        "good": '''import numpy as np, pandas as pd
y = pd.Series([1.0, 2.0, 3.0], index=[400, 401, 402])
yhat = pd.Series([1.0, 2.0, 3.0])
err = y.to_numpy() - yhat.to_numpy()''',
        "verify": ("silent", "np.isnan(np.asarray(err, dtype=float)).all()"), "good_check": "np.allclose(err, 0)",
        "show": "f'err = {np.asarray(err, dtype=float).tolist()}'",
        "concepts": ["p-numpy-shapes"],
        "quiz": choice("`(y - yhat).mean()` returns NaN, though both Series are full of numbers. Likely cause?", [opt("Their indexes don't match, so pandas aligned them into NaNs", True),
                                                                                                                opt("A division by zero", why="Subtraction alone produced NaN through index alignment."),
                                                                                                                opt("The Series are too long", why="Length isn't the issue."), opt("pandas can't subtract floats", why="It can; it aligns first.")]),
    },
    {
        "id": "e-sk-1d", "title": "Passing a 1-D array as X to scikit-learn", "lib": SKLEARN, "kind": "crash",
        "why": "scikit-learn expects X as a 2-D array (n_samples, n_features), even with one feature, so it can tell one feature × n samples from n features × one sample.",
        "fix": "`X.reshape(-1, 1)` for a single feature (one column), or `X[:, None]`.",
        "bad": '''import numpy as np
from sklearn.linear_model import LinearRegression
x = np.array([1.0, 2.0, 3.0]); y = np.array([2.0, 4.0, 6.0])
model = LinearRegression().fit(x, y)''',
        "good": '''import numpy as np
from sklearn.linear_model import LinearRegression
x = np.array([1.0, 2.0, 3.0]); y = np.array([2.0, 4.0, 6.0])
model = LinearRegression().fit(x.reshape(-1, 1), y)''',
        "verify": ("raises", "ValueError", "Expected 2D array"), "good_check": "abs(model.coef_[0] - 2) < 1e-9",
        "show": "f'slope = {model.coef_[0]:.3f}'",
        "concepts": ["p-numpy-shapes"],
        "quiz": blank("Turn the 1-D array `x` into a single-column 2-D array: `X = x.reshape(____)`", ["-1,1", "-1, 1", "(-1,1)", "(-1, 1)", "len(x),1", "len(x), 1"], mode="code"),
    },
    {
        "id": "e-scale-leak", "title": "Scaling with bounds computed from all the data (leakage)", "lib": SKLEARN, "kind": "silent",
        "why": "Computing min–max bounds (or a `StandardScaler`) on train **and** test data lets test information shape the training inputs. The model is evaluated on points it has already, in effect, seen. Errors look better than they really are, and future data is scaled inconsistently.",
        "fix": "Compute `lo, hi` from the training rows only and apply the same `lo, hi` to test rows and new predictions. Test values outside [0, 1] are fine. In scikit-learn, put the scaler inside a `Pipeline` so cross-validation refits it on each training fold.",
        "bad": '''import numpy as np
Xtr = np.array([[0.0], [10.0]]); Xte = np.array([[20.0]])
allX = np.vstack([Xtr, Xte]); lo, hi = allX.min(0), allX.max(0)
Xtr_s = (Xtr - lo) / (hi - lo)''',
        "good": '''import numpy as np
Xtr = np.array([[0.0], [10.0]]); Xte = np.array([[20.0]])
lo, hi = Xtr.min(0), Xtr.max(0)                    # training bounds only
Xtr_s = (Xtr - lo) / (hi - lo)''',
        "verify": ("silent", "Xtr_s.max() < 1.0"), "good_check": "Xtr_s.max() == 1.0 and Xtr_s.min() == 0.0",
        "show": "f'scaled training data = {Xtr_s.ravel()}'",
        "concepts": ["c-variable-scaling", "c-model-assessment"],
        "quiz": choice("With training bounds [2, 12], a test point x = 14 scales to 1.2. You should…", [opt("keep 1.2: test values may fall outside [0, 1]", True),
                                                                                                         opt("clip it to 1", why="That distorts the input; the model should see 1.2."),
                                                                                                         opt("recompute the bounds including the test set", why="That's data leakage."), opt("drop the test point", why="Nothing is wrong with it.")]),
    },
    {
        "id": "e-ridge-intercept", "title": "Ridge with your own ones column and fit_intercept=True", "lib": SKLEARN, "kind": "silent",
        "why": "The lecture's ridge formula penalizes every coefficient including the intercept. If your design matrix already has a column of ones and you leave `fit_intercept=True`, scikit-learn adds a *second*, unpenalized intercept. Your ones column gets a zero coefficient, and the fit no longer matches the formula.",
        "fix": "With your own ones column: `Ridge(alpha=lam, fit_intercept=False)`. Without it: let `fit_intercept=True` handle the intercept, but know it isn't penalized.",
        "bad": '''import numpy as np
from sklearn.linear_model import Ridge
rng = np.random.default_rng(0); X = rng.random((30, 2)); y = 5 + X @ np.array([1.0, 2.0])
Z = np.column_stack([np.ones(30), X]); lam = 1.0
w_formula = np.linalg.solve(Z.T @ Z + lam * np.eye(3), Z.T @ y)
w = Ridge(alpha=lam).fit(Z, y).coef_''',
        "good": '''import numpy as np
from sklearn.linear_model import Ridge
rng = np.random.default_rng(0); X = rng.random((30, 2)); y = 5 + X @ np.array([1.0, 2.0])
Z = np.column_stack([np.ones(30), X]); lam = 1.0
w_formula = np.linalg.solve(Z.T @ Z + lam * np.eye(3), Z.T @ y)
w = Ridge(alpha=lam, fit_intercept=False).fit(Z, y).coef_''',
        "verify": ("silent", "not np.allclose(w, w_formula, atol=1e-6)"), "good_check": "np.allclose(w, w_formula)",
        "show": "f'sklearn w = {np.round(w, 4)},  formula = {np.round(w_formula, 4)}'",
        "concepts": ["c-conditioning-ridge"],
        "quiz": blank("Reproduce (ZᵀZ + λI)⁻¹Zᵀy with Z already holding a ones column: `Ridge(alpha=lam, fit_intercept=____)`", ["False"], mode="code"),
    },
    {
        "id": "e-mlp-convergence", "title": "MLPRegressor stops at max_iter=200 before converging", "lib": SKLEARN, "kind": "warning",
        "why": "The default solver `adam` with `max_iter=200` often hasn't converged on small smooth datasets. scikit-learn warns (`ConvergenceWarning`) and returns an undertrained network, and you might blame the network width instead.",
        "fix": "For small data use `solver='lbfgs', max_iter=5000`, fix `random_state`, and check `n_iter_` against `max_iter`.",
        "bad": '''import numpy as np
from sklearn.neural_network import MLPRegressor
rng = np.random.default_rng(0); X = rng.random((50, 2)); y = X @ np.array([1.0, 2.0])
net = MLPRegressor(hidden_layer_sizes=(8,), random_state=0).fit(X, y)''',
        "good": '''import numpy as np
from sklearn.neural_network import MLPRegressor
rng = np.random.default_rng(0); X = rng.random((50, 2)); y = X @ np.array([1.0, 2.0])
net = MLPRegressor(hidden_layer_sizes=(8,), solver="lbfgs", max_iter=5000, random_state=0).fit(X, y)''',
        "verify": ("warns", "ConvergenceWarning", "Maximum iterations"), "good_check": "net.n_iter_ < 5000 and net.score(X, y) > 0.99",
        "show": "f'iterations = {net.n_iter_}, R^2 = {net.score(X, y):.4f}'",
        "concepts": ["c-ann"],
        "quiz": choice("You see `ConvergenceWarning: Maximum iterations (200) reached`. First thing to try?", [opt("`solver='lbfgs'` with a larger `max_iter`", True),
                                                                                                                opt("A wider network", why="The network didn't finish training; make it train properly first."),
                                                                                                                opt("Ignore it", why="An undertrained network makes the knob comparison meaningless."), opt("Fewer data points", why="That doesn't fix convergence.")]),
    },
    {
        "id": "e-gpr-normalize", "title": "GaussianProcessRegressor without normalize_y on data with a large mean", "lib": SKLEARN, "kind": "silent",
        "why": "By default the GP assumes the data has mean 0. Away from the training points, predictions fall back toward that prior mean, here from ≈100 down to ≈20, giving absurd extrapolations and miscalibrated uncertainty.",
        "fix": "Set `normalize_y=True` (it subtracts the mean and scales by the standard deviation internally), as the HW2 template suggests.",
        "bad": '''import numpy as np
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF
rng = np.random.default_rng(0); X = rng.random((15, 1)); y = 100 + 5 * np.sin(6 * X[:, 0])
gp = GaussianProcessRegressor(RBF(0.2), optimizer=None).fit(X, y)
far = gp.predict(np.array([[1.5]]))[0]''',
        "good": '''import numpy as np
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF
rng = np.random.default_rng(0); X = rng.random((15, 1)); y = 100 + 5 * np.sin(6 * X[:, 0])
gp = GaussianProcessRegressor(RBF(0.2), optimizer=None, normalize_y=True).fit(X, y)
far = gp.predict(np.array([[1.5]]))[0]''',
        "verify": ("silent", "far < 50"), "good_check": "abs(far - 100) < 10",
        "show": "f'prediction far from the data = {far:.1f}  (data mean = {y.mean():.1f})'",
        "concepts": ["c-kriging", "c-gpr-uncertainty"],
        "quiz": choice("Far from all training data, a GP with `normalize_y=False` predicts…", [opt("values near 0, the prior mean", True), opt("the mean of the training data", why="That's what `normalize_y=True` gives."),
                                                                                                opt("the nearest training value", why="It reverts to the prior mean."), opt("an error", why="It predicts happily, just badly.")]),
    },
    {
        "id": "e-kfold-shuffle", "title": "KFold without shuffling on ordered data", "lib": SKLEARN, "kind": "silent",
        "why": "`KFold(n_splits=5)` defaults to `shuffle=False`: each fold is a contiguous block. If the rows are sorted (by an input, or by when they were generated), each validation fold covers a region the training folds never saw, so CV measures extrapolation, not interpolation.",
        "fix": "`KFold(n_splits=5, shuffle=True, random_state=...)`, created once and reused for every model and knob value.",
        "bad": '''import numpy as np
from sklearn.model_selection import KFold
x = np.arange(10.0)                                  # sorted inputs
tr, va = next(KFold(n_splits=5).split(x))''',
        "good": '''import numpy as np
from sklearn.model_selection import KFold
x = np.arange(10.0)
tr, va = next(KFold(n_splits=5, shuffle=True, random_state=559).split(x))''',
        "verify": ("silent", "list(va) == [0, 1]"), "good_check": "list(va) != [0, 1]",
        "show": "f'first validation fold = {x[va].tolist()}'",
        "concepts": ["c-model-assessment"],
        "quiz": blank("Shuffled, reproducible 5-fold CV: `KFold(n_splits=5, shuffle=True, ____=559)`", ["random_state"], mode="code"),
    },
    {
        "id": "e-rbf-epsilon", "title": "RBFInterpolator's default kernel ignores epsilon", "lib": SCIPY, "kind": "silent",
        "why": "The default kernel is the thin-plate spline, which has no shape parameter, so changing `epsilon` changes nothing. A 'spread sweep' gives identical predictions at every value. (With `kernel='gaussian'` you *must* pass `epsilon`, or it raises.)",
        "fix": "`RBFInterpolator(X, y, kernel='gaussian', epsilon=np.sqrt(lam))` for the lecture's φ(r) = exp(−λr²).",
        "bad": '''import numpy as np
from scipy.interpolate import RBFInterpolator
rng = np.random.default_rng(0); X = rng.random((20, 2)); y = np.sin(3 * X[:, 0])
a = RBFInterpolator(X, y, epsilon=0.1)(X[:3] + 0.05)
b = RBFInterpolator(X, y, epsilon=10.0)(X[:3] + 0.05)''',
        "good": '''import numpy as np
from scipy.interpolate import RBFInterpolator
rng = np.random.default_rng(0); X = rng.random((20, 2)); y = np.sin(3 * X[:, 0])
a = RBFInterpolator(X, y, kernel="gaussian", epsilon=0.1)(X[:3] + 0.05)
b = RBFInterpolator(X, y, kernel="gaussian", epsilon=10.0)(X[:3] + 0.05)''',
        "verify": ("silent", "np.allclose(a, b)"), "good_check": "not np.allclose(a, b)",
        "show": "f'same predictions for both epsilons: {np.allclose(a, b)}'",
        "concepts": ["c-rbf"],
        "quiz": blank("Lecture spread λ = 4 → SciPy Gaussian epsilon = ____", ["2", "2.0", "np.sqrt(4)", "sqrt(4)"], mode="code"),
    },
    {
        "id": "e-meshgrid-index", "title": "Mixing up meshgrid's row and column order", "lib": NUMPY, "kind": "silent",
        "why": "`np.meshgrid(xs, ys)` returns arrays of shape `(len(ys), len(xs))`: rows follow **y**, columns follow **x** ('xy' indexing). After `np.unravel_index(np.argmin(F), F.shape)` gives `(i, j)`, `i` indexes **ys** and `j` indexes **xs**. Reading `xs[i]` reports the wrong optimum.",
        "fix": "Read the coordinates from the grids themselves, `X[i, j]` and `Y[i, j]` (as HW1's guide does with `RR[idx]`), or use `indexing='ij'` consistently.",
        "bad": '''import numpy as np
xs = np.linspace(0, 2, 3); ys = np.linspace(0, 1, 5)
X, Y = np.meshgrid(xs, ys); F = (X - 2)**2 + (Y - 0.25)**2     # minimum at x = 2, y = 0.25
i, j = np.unravel_index(np.argmin(F), F.shape)
x_best, y_best = xs[i], ys[j]''',
        "good": '''import numpy as np
xs = np.linspace(0, 2, 3); ys = np.linspace(0, 1, 5)
X, Y = np.meshgrid(xs, ys); F = (X - 2)**2 + (Y - 0.25)**2
i, j = np.unravel_index(np.argmin(F), F.shape)
x_best, y_best = X[i, j], Y[i, j]''',
        "verify": ("silent", "(x_best, y_best) != (2.0, 0.25)"), "good_check": "(x_best, y_best) == (2.0, 0.25)",
        "show": "f'reported optimum = ({x_best}, {y_best})'",
        "concepts": ["p-numpy-shapes"],
        "quiz": blank("`X, Y = np.meshgrid(xs, ys)` with 3 xs and 5 ys: shape of X?", ["(5,3)", "(5, 3)"], mode="code"),
    },
    {
        "id": "e-np-all-axis", "title": "np.all without axis= collapses a whole grid to one True/False", "lib": NUMPY, "kind": "silent",
        "why": "For constraint values `G` with shape `(m, ...)` (one row per constraint), `np.all(G <= 0)` asks 'is every constraint satisfied at **every** point?' and returns one boolean, usually False, instead of a feasibility map.",
        "fix": "`np.all(G <= 0, axis=0)` reduces over constraints only, giving a True/False per design point.",
        "bad": '''import numpy as np
G = np.array([[-1.0, 0.5, -0.2],        # g1 at three design points
              [-2.0, -1.0, -0.1]])      # g2 at the same points
feasible = np.all(G <= 0)''',
        "good": '''import numpy as np
G = np.array([[-1.0, 0.5, -0.2],
              [-2.0, -1.0, -0.1]])
feasible = np.all(G <= 0, axis=0)''',
        "verify": ("silent", "np.ndim(feasible) == 0"), "good_check": "feasible.tolist() == [True, False, True]",
        "show": "f'feasible = {feasible}'",
        "concepts": ["c-feasibility", "p-numpy-shapes"],
        "quiz": blank("Feasibility per point, constraints along axis 0: `np.all(G <= 0, ____)`", ["axis=0"], mode="code"),
    },
]

# ------------------------------------------------------------------ workflows (taught on fresh examples, not the homework)
WORKFLOWS = [
    {
        "id": "w-constrained-design", "title": "Solve a constrained design problem with SciPy, start to finish",
        "summary": "Lecture 1's cantilever beam with width b and height h: minimize mass subject to stress, deflection and an aspect-ratio limit. The same skills as a design-optimization assignment, on a different problem.",
        "concepts": ["c-negative-null-form", "c-monotonicity", "c-boundedness", "c-sqp", "c-constraint-activity", "c-pareto"],
        "steps": [
            ("Put every fixed parameter in one dictionary (SI units), so a parametric study can change one entry at a time.",
             """import numpy as np
from scipy.optimize import minimize, brentq

p = {"P": 2000.0, "L": 1.0, "E": 70e9, "rho": 2700.0,      # tip load, length, aluminium modulus and density
     "sigma_y": 150e6, "delta_max": 5e-3, "ratio": 5.0}     # allowable stress, allowable deflection, max h/b
print(len(p), "parameters")"""),
            ("Write the analysis models as small functions of the design x = [b, h].",
             """def mass(x, p):
    b, h = x
    return p["rho"] * b * h * p["L"]

def stress(x, p):
    b, h = x
    return 6 * p["P"] * p["L"] / (b * h**2)

def deflection(x, p):
    b, h = x
    return 4 * p["P"] * p["L"]**3 / (p["E"] * b * h**3)

print(f"mass at b=2 cm, h=10 cm: {mass([0.02, 0.10], p):.2f} kg")"""),
            ("Formulate in normalized negative null form: every g ≤ 0, each of order 1.",
             """def f(x, p):
    return mass(x, p)

def g(x, p):
    b, h = x
    return np.array([stress(x, p) / p["sigma_y"] - 1,         # g1: stress     <= allowable
                     deflection(x, p) / p["delta_max"] - 1,   # g2: deflection <= allowable
                     h / (p["ratio"] * b) - 1])               # g3: h/b        <= ratio (keeps beam theory valid)

print("g at b=2 cm, h=10 cm:", np.round(g([0.02, 0.10], p), 3))"""),
            ("Monotonicity before solving. Mass increases in b and in h. g1 and g2 decrease in both, so they bound b and h from below. But nothing stops b → 0 while h grows: mass ∝ bh can shrink forever along that direction. Only g3, which increases in h and decreases in b, closes that escape. So g3 must be active, plus at least one of g1, g2.",
             """# Quick evidence: without g3 the optimizer runs b to its lower bound (the escape direction).
x_ref = np.array([0.02, 0.1])                               # typical sizes, for scaling
bounds = [(0.005, 0.2), (0.005, 0.5)]
zb = [(lo / s, hi / s) for (lo, hi), s in zip(bounds, x_ref)]
r = minimize(lambda z, p: mass(z * x_ref, p), [1.0, 1.0], args=(p,), method="SLSQP", bounds=zb,
             constraints=[{"type": "ineq", "fun": lambda z, p: -g(z * x_ref, p)[:2], "args": (p,)}])
print("without g3: b =", (r.x * x_ref)[0], "(its lower bound)")"""),
            ("Solve with SLSQP in scaled variables z = x / x_ref. Remember SciPy's 'ineq' means ≥ 0, so pass −g.",
             """def solve(p):
    return minimize(lambda z, p: mass(z * x_ref, p), x0=[1.0, 1.0], args=(p,), method="SLSQP",
                    bounds=zb, constraints=[{"type": "ineq", "fun": lambda z, p: -g(z * x_ref, p), "args": (p,)}])

res = solve(p)
x_opt = res.x * x_ref
print(res.success, res.message)
print(f"b* = {x_opt[0]*100:.2f} cm, h* = {x_opt[1]*100:.2f} cm, mass* = {mass(x_opt, p):.3f} kg")"""),
            ("Check feasibility and label each constraint active or inactive, with a tolerance.",
             """for name, v in zip(["stress", "deflection", "aspect"], g(x_opt, p)):
    print(f"{name:10s} {v:+.5f}  {'active' if abs(v) < 1e-4 else 'inactive'}")"""),
            ("Cross-check with a root finder: with deflection and aspect active, h = ratio·b and the deflection residual must vanish. That is one equation in b, which brentq can solve.",
             """resid = lambda b, p: g([b, p["ratio"] * b], p)[1]          # deflection residual on the line h = ratio*b
b_chk = brentq(resid, 1e-3, 0.2, args=(p,))
print(f"brentq: b = {b_chk*100:.2f} cm, h = {p['ratio']*b_chk*100:.2f} cm  (matches SLSQP)")"""),
            ("Parametric study on an active bound (δ_max), using a modified copy of p each time. Watch which constraint governs.",
             """for dmax in [2e-3, 5e-3, 20e-3, 50e-3]:
    q = {**p, "delta_max": dmax}                      # a modified COPY; p is untouched
    r = solve(q); x = r.x * x_ref
    ok = r.success and np.all(g(x, q) <= 1e-6)
    active = [n for n, v in zip(["stress", "deflection", "aspect"], g(x, q)) if abs(v) < 1e-4]
    print(f"delta_max = {dmax*1000:4.0f} mm  mass* = {mass(x, q):.3f} kg  active: {active}" if ok else f"{dmax}: failed")"""),
        ],
    },
    {
        "id": "w-surrogate-cv", "title": "Fit, scale and tune surrogates with k-fold cross-validation",
        "summary": "On a synthetic, slightly noisy 2-D test function: build a design matrix, fix its conditioning, and choose each family's complexity knob by CV. The same skills as a surrogate-modelling assignment, on different data.",
        "concepts": ["c-doe", "c-least-squares", "c-conditioning-ridge", "c-variable-scaling", "c-model-assessment", "c-rbf", "c-kriging", "c-gpr-uncertainty"],
        "steps": [
            ("Sample 40 training points (with a little measurement noise) and 200 test points by Latin hypercube, in deliberately badly scaled physical units: x₁ ∈ [0, 1], x₂ ∈ [100, 300].",
             """import numpy as np
from scipy.stats import qmc

def truth(X):                                     # a smooth test function standing in for a simulation
    u, v = X[:, 0], (X[:, 1] - 100) / 200
    return np.sin(4 * u) * np.cos(3 * v) + 0.5 * u * v

lo_b, hi_b = np.array([0.0, 100.0]), np.array([1.0, 300.0])
rng = np.random.default_rng(559)
Xtr = qmc.scale(qmc.LatinHypercube(d=2, seed=1).random(40), lo_b, hi_b)
Xte = qmc.scale(qmc.LatinHypercube(d=2, seed=2).random(200), lo_b, hi_b)
ytr = truth(Xtr) + 0.05 * rng.standard_normal(len(Xtr))   # noisy training data
yte = truth(Xte)
print(Xtr.shape, Xte.shape)"""),
            ("Build a degree-6 polynomial design matrix (28 terms) and look at its condition number with the raw inputs.",
             """def poly(X, deg=6):
    return np.column_stack([X[:, 0]**i * X[:, 1]**j for i in range(deg + 1) for j in range(deg + 1 - i)])

Z_raw = poly(Xtr)
print(Z_raw.shape, f" cond(Z^T Z), raw inputs: {np.linalg.cond(Z_raw.T @ Z_raw):.1e}")"""),
            ("Min–max scale with the **training** bounds only, apply the same bounds to the test set, and rebuild. The condition number drops by about 20 orders of magnitude (still large: 28 terms from 40 points).",
             """lo, hi = Xtr.min(axis=0), Xtr.max(axis=0)
scale = lambda X: (X - lo) / (hi - lo)
Xtr_s, Xte_s = scale(Xtr), scale(Xte)
Z, Zte = poly(Xtr_s), poly(Xte_s)
print(f"cond(Z^T Z), scaled inputs: {np.linalg.cond(Z.T @ Z):.1e}")"""),
            ("Create **one** set of 5 shuffled folds and reuse it for every candidate. Sweep ridge λ and pick it by CV RMSE: λ = 0 overfits the noise, large λ underfits.",
             """from sklearn.model_selection import KFold
kf = KFold(n_splits=5, shuffle=True, random_state=559)
rmse = lambda a, b: float(np.sqrt(np.mean((a - b)**2)))

def ridge(Z, y, lam):
    return np.linalg.solve(Z.T @ Z + lam * np.eye(Z.shape[1]), Z.T @ y)

def cv_ridge(lam):
    return np.mean([rmse(ytr[va], Z[va] @ ridge(Z[tr], ytr[tr], lam)) for tr, va in kf.split(Z)])

lams = [0, 1e-8, 1e-6, 1e-4, 1e-2, 1]
scores = {lam: round(float(cv_ridge(lam)), 4) for lam in lams}
best_lam = min(scores, key=scores.get)
print(scores, "-> best lambda", best_lam)"""),
            ("Sweep the Gaussian RBF spread over orders of magnitude, on the same folds (note `kernel='gaussian'`, `epsilon=√λ`). Very wide bumps (small λ) make the system ill-conditioned; very narrow ones (large λ) spike at the data.",
             """from scipy.interpolate import RBFInterpolator

def cv_rbf(lam):
    return np.mean([rmse(ytr[va], RBFInterpolator(Xtr_s[tr], ytr[tr], kernel="gaussian", epsilon=np.sqrt(lam))(Xtr_s[va]))
                    for tr, va in kf.split(Xtr_s)])

spreads = [1e-2, 1e-1, 1, 10, 100, 1000]
rbf_scores = {s: round(float(cv_rbf(s)), 4) for s in spreads}
best_spread = min(rbf_scores, key=rbf_scores.get)
print(rbf_scores, "-> best spread", best_spread)"""),
            ("Fit a Gaussian process: an anisotropic kernel (one length scale per input), normalize_y=True, and a WhiteKernel to model the noise (a learned nugget). Compare its uncertainty near and far from the training data.",
             """from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, ConstantKernel, WhiteKernel
from scipy.spatial.distance import cdist

kernel = ConstantKernel(1.0, (1e-3, 1e3)) * RBF(length_scale=np.ones(2), length_scale_bounds=(1e-2, 1e3)) \\
         + WhiteKernel(1e-3, (1e-6, 1.0))
gp = GaussianProcessRegressor(kernel=kernel, normalize_y=True, n_restarts_optimizer=3, random_state=559).fit(Xtr_s, ytr)
mean, std = gp.predict(Xte_s, return_std=True)
d_min = cdist(Xte_s, Xtr_s).min(axis=1)
i_near, i_far = np.argmin(d_min), np.argmax(d_min)
print("fitted kernel:", gp.kernel_)
print(f"std at the test point nearest the data {std[i_near]:.3f}, farthest {std[i_far]:.3f}")"""),
            ("Score each family's CV-chosen model **once** on the test set and tabulate the knob, test error and whether it gives uncertainty.",
             """rbf = RBFInterpolator(Xtr_s, ytr, kernel="gaussian", epsilon=np.sqrt(best_spread))
rows = [("degree-6 poly + ridge", f"lambda={best_lam:g}", rmse(yte, Zte @ ridge(Z, ytr, best_lam)), "no"),
        ("Gaussian RBF", f"spread={best_spread:g}", rmse(yte, rbf(Xte_s)), "no"),
        ("Kriging / GP", "theta by max. likelihood", rmse(yte, mean), "yes (std)")]
for name, knob, err, uq in rows:
    print(f"{name:22s} {knob:26s} test RMSE {err:.4f}   native UQ: {uq}")"""),
        ],
    },
    {
        "id": "w-linprog", "title": "Solve and interpret a linear program with linprog",
        "summary": "The farmer's LP, plus what the shadow prices say.",
        "concepts": ["c-lp-standard-form", "c-simplex", "c-lagrangian-equality"],
        "steps": [
            ("Write the data: maximize profit, so negate the cost vector.",
             '''import numpy as np
from scipy.optimize import linprog
c = -np.array([40.0, 30.0])                       # maximize 40 x1 + 30 x2
A_ub = np.array([[2.0, 1.0], [1.0, 1.0]]); b_ub = np.array([320.0, 240.0])   # labour, land
print(c, A_ub.shape)'''),
            ("Solve with HiGHS, check success, and report the profit with the sign flipped back.",
             '''res = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=[(0, None)] * 2, method="highs")
print(res.status, res.message)
print("acres:", res.x, " profit:", -res.fun)'''),
            ("Read the slacks and the shadow prices: which resources bind, and what one more unit of each is worth.",
             '''print("slack (unused):", res.ineqlin.residual)
print("shadow prices :", -res.ineqlin.marginals, "(profit per extra labour hour, per extra acre)")'''),
            ("Confirm the shadow price by re-solving with one more acre of land.",
             '''res2 = linprog(c, A_ub=A_ub, b_ub=b_ub + np.array([0.0, 1.0]), method="highs")
print("profit gain from one more acre:", round(-res2.fun - (-res.fun), 6))'''),
        ],
    },
    {
        "id": "w-unconstrained", "title": "Compare unconstrained methods and check your gradient",
        "summary": "Beale's function, a flat-bottomed curved valley: Nelder–Mead vs BFGS with and without an analytic gradient, plus a gradient check.",
        "concepts": ["c-quasi-newton", "c-newton", "c-convergence-termination"],
        "steps": [
            ("Define a test function with a flat, curved valley (Beale's function, minimum at (3, 0.5)) and its analytic gradient, built term by term so it's easy to check.",
             '''import numpy as np
from scipy.optimize import minimize, check_grad

c = np.array([1.5, 2.25, 2.625])

def f(x):
    r = c - x[0] + x[0] * x[1] ** np.arange(1, 4)     # three residuals
    return float(r @ r)

def grad(x):
    k = np.arange(1, 4)
    r = c - x[0] + x[0] * x[1] ** k
    dr_dx0 = -1 + x[1] ** k
    dr_dx1 = x[0] * k * x[1] ** (k - 1)
    return np.array([2 * r @ dr_dx0, 2 * r @ dr_dx1])

print("f(3, 0.5) =", f([3.0, 0.5]))'''),
            ("Check the gradient against finite differences before trusting it. A small number (relative to the gradient's size) means it's right.",
             '''x_test = np.array([1.0, 1.0])
print("check_grad:", check_grad(f, grad, x_test), " |grad| =", np.linalg.norm(grad(x_test)).round(3))'''),
            ("Run three methods from the same start and compare iterations and function evaluations. The analytic gradient saves the finite-difference evaluations, not iterations.",
             '''x0 = [1.0, 1.0]
for label, kw in [("Nelder-Mead", dict(method="Nelder-Mead")),
                  ("BFGS (finite diff.)", dict(method="BFGS")),
                  ("BFGS (analytic jac)", dict(method="BFGS", jac=grad))]:
    r = minimize(f, x0, **kw)
    print(f"{label:20s} success={r.success!s:5s} nit={r.nit:4d} nfev={r.nfev:4d} x={r.x.round(5)}")'''),
        ],
    },
]

# ------------------------------------------------------------------ extra code-practice problems (beyond each bug's quiz)
CODE_PROBLEMS = [
    problem("cp-method-1", "Pick the method", "You have bounds on every variable and two nonlinear inequality constraints, but no gradients.",
            [choice("Which `minimize` method fits best?", [opt("`SLSQP` (finite-difference gradients are fine)", True), opt("`BFGS`", why="BFGS ignores bounds and constraints."),
                                                          opt("`L-BFGS-B`", why="Handles bounds but not general constraints."), opt("`Newton-CG`", why="Needs gradients and ignores constraints.")])]),
    problem("cp-reading-1", "Read a result", "`res.success == True`, `res.message == 'Optimization terminated successfully'`, but `g(res.x)` returns `[0.12, -0.4]`.",
            [choice("What do you conclude?", [opt("The first constraint is violated: suspect the sign convention for SciPy's 'ineq'", True), opt("The solution is fine because success is True", why="Success reports convergence of the algorithm on the problem you *gave* it, possibly the wrong one."),
                                              opt("Tighten the tolerance", why="A violation of 0.12 is a formulation problem, not a tolerance one."), opt("The second constraint is violated", why="Negative means satisfied.")])]),
    problem("cp-workflow-1", "Order the surrogate workflow", "Building and tuning a surrogate for an expensive model.",
            [order("Put the steps in order.", ["Sample training points with an LHS", "Compute scaling bounds from the training data only",
                                               "Create one KFold object (shuffle, fixed seed)", "Sweep the complexity knob and record mean CV error",
                                               "Refit at the best knob on all training data", "Report test error once"])]),
    problem("cp-spot-1", "Find the bug in a parametric study", "A loop meant to re-solve the problem for several loads:",
            [spot("Which line is the bug?", [
                ("for P in [25e3, 50e3, 100e3]:", False, ""),
                ("    q = p", True, "`q = p` doesn't copy the dict, so `q['P'] = P` also overwrites `p`. Use `q = {**p, 'P': P}` or `p.copy()`."),
                ("    q['P'] = P", False, ""),
                ("    res = solve(q)", False, ""),
            ], code=True)]),
    problem("cp-linprog-1", "Shadow prices", "`linprog` (minimizing −profit) returns `res.ineqlin.marginals = [-10, -20]` for (labour, land).",
            [num("How much extra profit would one more acre of land bring?", 20, "$"),
             choice("Why are the marginals negative?", [opt("linprog minimized −profit, so improving the objective means decreasing it", True), opt("Land loses money", why="It earns $20 per extra acre."),
                                                        opt("A sign bug in SciPy", why="It's the minimization convention."), opt("The constraints are inactive", why="Inactive constraints have zero marginals.")])]),
]
