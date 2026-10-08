"""Layer 0: what MECH 559 assumes you already own (calculus, linear algebra, Python)."""
import math
import sympy as sp
from lib import *

C_ = "Multivariable calculus"
L_ = "Linear algebra"
A_ = "Analysis and numerics"
P_ = "Python and NumPy"
X_ = "From MECH 419"

F_BFGS = 4 * x1**2 + 3 * x1 * x2 + x2**2       # the course's favourite quadratic (Lectures 6)
MECH419 = "https://scereal.github.io/on-inspire/dynamics/mech-419/"  # the public MECH 419 atlas

CONCEPTS = [
    concept(
        "p-gradient", "The gradient points straight uphill, and its length is the steepness", 0, C_,
        r"""
For $f:\mathbb{R}^n\to\mathbb{R}$, the gradient stacks the partial derivatives into a vector:
$$\nabla f = \Big[\frac{\partial f}{\partial x_1}\ \cdots\ \frac{\partial f}{\partial x_n}\Big]^T.$$
Three facts carry the whole course:

- **Direction of steepest increase.** Moving a small step $\mathbf{d}$ changes $f$ by about $\nabla f^T\mathbf{d}$ (the *directional derivative*). That is largest when $\mathbf{d}$ points along $\nabla f$, and most negative along $-\nabla f$, which is why steepest descent uses $\mathbf{d} = -\nabla f$ ([[c-descent]]).
- **Perpendicular to contours.** Along a contour $f$ doesn't change, so $\nabla f^T\mathbf{d} = 0$ for every direction along it.
- **Zero at a smooth interior optimum** ([[c-fonc]]).

For a constraint $g(\mathbf{x})\le 0$, $\nabla g$ points out of the feasible region, into where $g$ grows. That picture is the heart of the KKT conditions ([[c-kkt]]).
""",
        math=[r"\nabla f = \Big[\tfrac{\partial f}{\partial x_1}\ \cdots\ \tfrac{\partial f}{\partial x_n}\Big]^T", r"\Delta f \approx \nabla f^T\mathbf{d}"],
        analogy=analogy("Standing on a hillside in fog: the gradient is the arrow your feet feel pointing straight uphill, and its length is how steep the slope is there.",
                        "the arrow is local. Follow it too far and the hill may curve away, which is why algorithms need step sizes ([[c-gradient-method]])."),
        exam="On an open-book exam, write the gradient as a column with each entry labelled $\\partial f/\\partial x_i$ before plugging in numbers. Most algorithm marks start from a correct $\\nabla f_k$.",
        problems=[
            problem("p-grad-1", "Gradient of the course's favourite quadratic",
                    r"$f(\mathbf{x}) = 4x_1^2 + 3x_1x_2 + x_2^2$ appears again and again in Lecture 6.",
                    [expr(r"Type $\partial f/\partial x_1$.", sp.diff(F_BFGS, x1), ["x1", "x2"],
                          explain="$8x_1 + 3x_2$: the $3x_1x_2$ term contributes $3x_2$."),
                     expr(r"Type $\partial f/\partial x_2$.", sp.diff(F_BFGS, x2), ["x1", "x2"]),
                     num(r"At $\mathbf{x} = (1, 1)$, what is the directional derivative along $\mathbf{d} = -\nabla f$?",
                         -(11**2 + 5**2), "", explain="$\\nabla f = (11, 5)$, so $\\nabla f^T(-\\nabla f) = -\\|\\nabla f\\|^2 = -146$: strongly downhill.")]),
            problem("p-grad-2", "Which way is uphill?",
                    r"A contour line of $f$ passes through a point.",
                    [choice(r"How is $\nabla f$ oriented relative to the contour there?",
                            [opt("Perpendicular to it, pointing toward higher $f$", True),
                             opt("Tangent to it", why="Along the contour $f$ is constant, so $\\nabla f^T\\mathbf{d} = 0$ there: the gradient is perpendicular."),
                             opt("Perpendicular, pointing toward lower $f$", why="That's $-\\nabla f$, the descent direction."),
                             opt("It depends on the step size", why="The gradient is a property of $f$ at the point; step sizes belong to algorithms.")])]),
        ]),

    concept(
        "p-hessian", "The Hessian collects every second derivative: the curvature of f", 0, C_,
        r"""
$H_{ij} = \dfrac{\partial^2 f}{\partial x_i\partial x_j}$. For a twice continuously differentiable $f$ it's square and **symmetric** ($H_{12} = H_{21}$). It describes curvature: how the slope changes as you move.

The Hessian decides what kind of stationary point you've found ([[c-sosc]]), it appears in Newton's step $\mathbf{d} = -\mathbf{H}^{-1}\nabla f$ ([[c-newton]]), and in exact line search ([[c-exact-line-search]]). For a quadratic $f = \tfrac12\mathbf{x}^T\mathbf{A}\mathbf{x} + \mathbf{b}^T\mathbf{x} + c$ it is simply the constant matrix $\mathbf{A}$ ([[c-quadratic-functions]]).
""",
        deeper=["p-gradient"],
        math=[r"H_{ij} = \frac{\partial^2 f}{\partial x_i\,\partial x_j} = H_{ji}"],
        analogy=analogy("If the gradient is the slope under your feet, the Hessian is the shape of the ground: a bowl, a dome, or a saddle.",
                        "it's local too. A non-quadratic function's Hessian changes from point to point, so a bowl here can be a saddle there."),
        exam="Check symmetry as you go: if your $H_{12}\\ne H_{21}$, you've made a differentiation error.",
        problems=[
            problem("p-hess-1", "Hessian of the quadratic",
                    r"$f = 4x_1^2 + 3x_1x_2 + x_2^2$.",
                    [num(r"$H_{11}$?", 8, ""), num(r"$H_{12}$?", 3, "", explain="$\\partial^2 f/\\partial x_1\\partial x_2 = 3$, and $H_{21}$ is the same."),
                     num(r"$H_{22}$?", 2, "")]),
            problem("p-hess-2", "Find the slip",
                    r"A student computes the Hessian of $f = x_1^2x_2 + x_2^3$.",
                    [spot("Which line is wrong?", [
                        (r"$\partial f/\partial x_1 = 2x_1x_2$", False, ""),
                        (r"$\partial f/\partial x_2 = x_1^2 + 3x_2^2$", False, ""),
                        (r"$H_{11} = 2x_2$, $H_{22} = 6x_2$", False, ""),
                        (r"$H_{12} = 2x_1x_2$", True, "Differentiate $\\partial f/\\partial x_1 = 2x_1x_2$ with respect to $x_2$: you get $2x_1$, not $2x_1x_2$. Cross-check: $\\partial/\\partial x_1(x_1^2 + 3x_2^2) = 2x_1$ too."),
                    ], explain="$H = \\begin{bmatrix}2x_2 & 2x_1\\\\ 2x_1 & 6x_2\\end{bmatrix}$; the symmetry check catches the slip.")]),
        ]),

    concept(
        "p-taylor-vector", "Near any point, f looks like a tilted plane plus a bowl", 0, C_,
        r"""
The multivariable Taylor expansion about $\mathbf{x}_o$:
$$f(\mathbf{x}_o + \Delta\mathbf{x}) \approx f(\mathbf{x}_o) + \nabla f_o^T\Delta\mathbf{x} + \tfrac12\Delta\mathbf{x}^T\mathbf{H}_o\Delta\mathbf{x}.$$
Keep only the first two terms and you have the local *plane* that gradient methods use; keep the third and you have the local *bowl* that Newton's method and trust regions use. For a quadratic function the second-order expansion is **exact**, which is why Newton's method solves a quadratic in one step.

The optimality conditions come straight from this: at a minimum, the linear term must vanish ([[c-fonc]]) and the quadratic term must be non-negative ([[c-sosc]]).
""",
        deeper=["p-gradient", "p-hessian"],
        math=[r"\Delta f \approx \nabla f^T\Delta\mathbf{x} + \tfrac12\,\Delta\mathbf{x}^T\mathbf{H}\,\Delta\mathbf{x}"],
        analogy=analogy("Zoom far enough into a smooth hillside and it looks flat and tilted; zoom out a little and the curvature appears as a bowl or dome.",
                        "zoom out too far and neither picture holds. That's why line searches and trust regions limit how far you trust the model."),
        exam="When asked to 'approximate' a value, state which order you used and why it's (or isn't) exact for that function.",
        problems=[
            problem("p-tay-1", "Second-order prediction",
                    r"$f = 4x_1^2 + 3x_1x_2 + x_2^2$ at $\mathbf{x}_o = (1,1)$: $f_o = 8$, $\nabla f_o = (11, 5)$, $\mathbf{H} = \begin{bmatrix}8&3\\3&2\end{bmatrix}$. Step $\Delta\mathbf{x} = (0.1, -0.1)$.",
                    [num(r"First-order term $\nabla f_o^T\Delta\mathbf{x}$?", 11 * 0.1 + 5 * (-0.1), ""),
                     num(r"Second-order term $\tfrac12\Delta\mathbf{x}^T\mathbf{H}\Delta\mathbf{x}$?", 0.5 * (8 * 0.01 + 2 * 3 * 0.1 * (-0.1) + 2 * 0.01), "",
                         explain="$\\tfrac12(0.08 - 0.06 + 0.02) = 0.02$."),
                     num(r"Predicted $f(1.1, 0.9)$?", 8.62, "", explain="$8 + 0.6 + 0.02 = 8.62$, exactly $f(1.1, 0.9)$, because $f$ is quadratic.")]),
        ]),

    concept(
        "p-matrix-calculus", "Two rules differentiate almost every vector expression in the course", 0, L_,
        r"""
$$\frac{\partial(\mathbf{a}^T\mathbf{x})}{\partial\mathbf{x}} = \mathbf{a},\qquad \frac{\partial(\mathbf{x}^T\mathbf{A}\mathbf{x})}{\partial\mathbf{x}} = (\mathbf{A} + \mathbf{A}^T)\mathbf{x} = 2\mathbf{A}\mathbf{x}\ \ \text{if }\mathbf{A}\text{ is symmetric}.$$
The first holds because $\mathbf{a}^T\mathbf{x}$ is a scalar, equal to its own transpose $\mathbf{x}^T\mathbf{a}$. The second is why the ½ in $\tfrac12\mathbf{x}^T\mathbf{A}\mathbf{x}$ is so convenient: its gradient is just $\mathbf{A}\mathbf{x}$.

These two rules derive the normal equations of least squares ([[c-least-squares]]), ridge regression ([[c-conditioning-ridge]]), and the gradient of every quadratic ([[c-quadratic-functions]]).
""",
        deeper=["p-gradient"],
        math=[r"\nabla_{\mathbf{x}}(\mathbf{a}^T\mathbf{x}) = \mathbf{a}", r"\nabla_{\mathbf{x}}(\mathbf{x}^T\mathbf{A}\mathbf{x}) = (\mathbf{A}+\mathbf{A}^T)\mathbf{x}"],
        analogy=analogy("They're the vector versions of $\\frac{d}{dx}(ax) = a$ and $\\frac{d}{dx}(ax^2) = 2ax$.",
                        "the scalar intuition hides the transpose: for a non-symmetric $\\mathbf{A}$ you get $(\\mathbf{A}+\\mathbf{A}^T)\\mathbf{x}$, not $2\\mathbf{A}\\mathbf{x}$."),
        exam="Write the expression out as a scalar first (expand $\\varepsilon = \\mathbf{w}^T\\mathbf{Z}^T\\mathbf{Z}\\mathbf{w} - 2\\mathbf{w}^T\\mathbf{Z}^T\\mathbf{y} + \\mathbf{y}^T\\mathbf{y}$), then apply the two rules term by term.",
        problems=[
            problem("p-mc-1", "Derive the normal equations",
                    r"$\varepsilon(\mathbf{w}) = (\mathbf{Z}\mathbf{w} - \mathbf{y})^T(\mathbf{Z}\mathbf{w} - \mathbf{y})$.",
                    [spot("Which line of this derivation is wrong?", [
                        (r"$\varepsilon = \mathbf{w}^T\mathbf{Z}^T\mathbf{Z}\mathbf{w} - \mathbf{w}^T\mathbf{Z}^T\mathbf{y} - \mathbf{y}^T\mathbf{Z}\mathbf{w} + \mathbf{y}^T\mathbf{y}$", False, ""),
                        (r"$\varepsilon = \mathbf{w}^T\mathbf{Z}^T\mathbf{Z}\mathbf{w} - 2\mathbf{w}^T\mathbf{Z}^T\mathbf{y} + \mathbf{y}^T\mathbf{y}$", False, ""),
                        (r"$\partial\varepsilon/\partial\mathbf{w} = \mathbf{Z}^T\mathbf{Z}\mathbf{w} - 2\mathbf{Z}^T\mathbf{y}$", True, "$\\mathbf{Z}^T\\mathbf{Z}$ is symmetric, so $\\partial(\\mathbf{w}^T\\mathbf{Z}^T\\mathbf{Z}\\mathbf{w})/\\partial\\mathbf{w} = 2\\mathbf{Z}^T\\mathbf{Z}\\mathbf{w}$. The 2 is missing."),
                        (r"$\mathbf{Z}^T\mathbf{Z}\mathbf{w} = \mathbf{Z}^T\mathbf{y}$", False, ""),
                    ], explain="With the 2 restored, $2\\mathbf{Z}^T\\mathbf{Z}\\mathbf{w} - 2\\mathbf{Z}^T\\mathbf{y} = 0$ gives the normal equations.")]),
            problem("p-mc-2", "A non-symmetric matrix",
                    r"$\mathbf{A} = \begin{bmatrix}1 & 4\\ 0 & 1\end{bmatrix}$ (not symmetric).",
                    [choice(r"What is $\nabla(\mathbf{x}^T\mathbf{A}\mathbf{x})$?",
                            [opt(r"$\begin{bmatrix}2 & 4\\4 & 2\end{bmatrix}\mathbf{x}$", True),
                             opt(r"$\begin{bmatrix}2 & 8\\0 & 2\end{bmatrix}\mathbf{x}$", why="That's $2\\mathbf{A}\\mathbf{x}$, valid only for symmetric $\\mathbf{A}$. Use $(\\mathbf{A} + \\mathbf{A}^T)\\mathbf{x}$."),
                             opt(r"$\mathbf{A}\mathbf{x}$", why="That would be the gradient of $\\tfrac12\\mathbf{x}^T\\mathbf{A}\\mathbf{x}$ for symmetric $\\mathbf{A}$ only."),
                             opt(r"$\mathbf{A}^T\mathbf{x}$", why="Both $\\mathbf{A}$ and $\\mathbf{A}^T$ contribute.")],
                            explain="Only the symmetric part of $\\mathbf{A}$ matters in a quadratic form, which is why the course always assumes symmetric $\\mathbf{A}$ 'without loss of generality'.")]),
        ]),

    concept(
        "p-eigen-definiteness", "Eigenvalues of a symmetric matrix tell you if it's a bowl, a dome or a saddle", 0, L_,
        r"""
A symmetric matrix $\mathbf{A}$ has real eigenvalues. Its quadratic form $\mathbf{y}^T\mathbf{A}\mathbf{y}$ is:

| Eigenvalues | Quadratic form | Name | Shape |
|---|---|---|---|
| all $> 0$ | $> 0$ for all $\mathbf{y}\ne 0$ | positive definite | bowl |
| all $\ge 0$ | $\ge 0$ | positive semi-definite | trough |
| all $< 0$ | $< 0$ | negative definite | dome |
| mixed signs | either sign | indefinite | saddle |

For a $2\times2$ matrix, the leading principal minors are a quick test: positive definite iff $a_{11} > 0$ and $\det\mathbf{A} > 0$. The condition number $\kappa = |\lambda_{max}|/|\lambda_{min}|$ measures how stretched the bowl is ([[c-conditioning-ridge]]).
""",
        deeper=["p-hessian"],
        math=[r"\mathbf{A}\mathbf{v} = \lambda\mathbf{v},\qquad \kappa(\mathbf{A}) = \frac{|\lambda_{max}|}{|\lambda_{min}|}"],
        analogy=analogy("Eigenvectors are the bowl's principal axes, and each eigenvalue is how steeply the bowl curves along that axis.",
                        "for a non-symmetric matrix, eigenvalues can be complex and don't describe a quadratic form's shape. Always symmetrize first."),
        exam="For 2×2 matrices use minors ($a_{11}$ and the determinant); for 3×3, compute all leading minors. State which test you used.",
        widget={"type": "definiteness"},
        problems=[
            problem("p-eig-1", "Classify by eigenvalues",
                    r"$\mathbf{A} = \begin{bmatrix}2 & 1\\ 1 & 2\end{bmatrix}$.",
                    [num("Smaller eigenvalue?", 1, ""), num("Larger eigenvalue?", 3, ""),
                     choice("So $\\mathbf{A}$ is…", [opt("positive definite", True), opt("indefinite", why="Both eigenvalues are positive."),
                                                    opt("positive semi-definite but not definite", why="Neither eigenvalue is zero."),
                                                    opt("negative definite", why="The eigenvalues are 1 and 3.")])]),
            problem("p-eig-2", "Minors test",
                    r"$\mathbf{B} = \begin{bmatrix}1 & 2\\ 2 & 1\end{bmatrix}$.",
                    [num(r"$\det\mathbf{B}$?", -3, ""),
                     choice("So $\\mathbf{B}$ is…", [opt("indefinite (a saddle)", True), opt("positive definite", why="$a_{11} > 0$ but $\\det < 0$: the eigenvalues have opposite signs ($-1$ and $3$)."),
                                                    opt("negative definite", why="That needs $a_{11} < 0$ and $\\det > 0$."), opt("singular", why="$\\det = -3 \\ne 0$.")])]),
        ]),

    concept(
        "p-linear-systems", "Ax = b: square and full rank means one answer; tall means least squares; wide means many", 0, L_,
        r"""
For $\mathbf{A}\in\mathbb{R}^{m\times n}$:

- **Square, full rank** ($m = n$, $\det\ne0$): exactly one solution, $\mathbf{x} = \mathbf{A}^{-1}\mathbf{b}$. Compute it with `np.linalg.solve`, not by forming the inverse.
- **Tall** ($m > n$, more equations than unknowns): generally no exact solution. Least squares picks the best fit ([[c-least-squares]]).
- **Wide** ($m < n$): infinitely many solutions if consistent. Linear programming lives here: choose $m$ basic variables, set the rest to zero ([[c-basic-solutions]]).

A matrix with linearly dependent columns (rank-deficient) is singular, and a *nearly* dependent one is ill-conditioned: tiny changes in $\mathbf{b}$ swing $\mathbf{x}$ wildly.
""",
        math=[r"\operatorname{rank}(\mathbf{A}) = \text{number of independent columns}"],
        analogy=analogy("Unknowns are things you want to pin down, equations are pins: too few pins and the board can still slide; too many and they fight each other.",
                        "nearly-parallel pins technically pin the board, but it wobbles enormously. That's ill-conditioning, not singularity."),
        exam="Before solving, state the shape ($m\\times n$) and which case you're in; it tells you whether to expect one, none, or many solutions.",
        problems=[
            problem("p-lin-1", "Which case?",
                    r"Fitting a 3-coefficient model to $p = 40$ data points gives $\mathbf{Z}\mathbf{w} = \mathbf{y}$ with $\mathbf{Z}\in\mathbb{R}^{40\times3}$.",
                    [choice("What kind of system is it?", [opt("Overdetermined: solve in the least-squares sense", True),
                                                          opt("Square: invert $\\mathbf{Z}$", why="$\\mathbf{Z}$ is $40\\times3$, not square."),
                                                          opt("Underdetermined: infinitely many fits", why="There are more equations (40) than unknowns (3)."),
                                                          opt("Singular, so no fit exists", why="A least-squares fit always exists.")])]),
            problem("p-lin-2", "Spot the dependence",
                    r"$\mathbf{A} = \begin{bmatrix}1 & 2\\ 2 & 4\end{bmatrix}$.",
                    [num(r"$\operatorname{rank}(\mathbf{A})$?", 1, "", explain="The second column is twice the first."),
                     choice("What does `np.linalg.solve(A, b)` do?", [opt("Raises `LinAlgError: Singular matrix`", True),
                                                                      opt("Returns the least-squares solution", why="That's `np.linalg.lstsq`; `solve` needs a non-singular square matrix."),
                                                                      opt("Returns zeros", why="It can't return a solution of a singular system; it raises an error."),
                                                                      opt("Silently returns garbage", why="For an *exactly* singular matrix it raises; *nearly* singular ones are where silent garbage appears.")])]),
        ]),

    concept(
        "p-sets-compactness", "On a closed, bounded set, a continuous function always reaches its best and worst", 0, A_,
        r"""
- A set is **closed** if it contains its boundary ($[0,1]$), **open** if it contains none of it ($(0,1)$).
- It's **bounded** if it fits inside a ball of finite radius.
- **Compact** = closed and bounded (in $\mathbb{R}^n$).

**Weierstrass's extreme value theorem:** a continuous function on a compact set attains its maximum and minimum there. It guarantees a solution *exists* before you look for one. When a problem has no solution it's usually because one of these fails: the feasible set is open (the best point is excluded) or unbounded (the objective improves forever), as in Russell's example ([[c-boundedness]]).
""",
        math=[r"\text{compact} = \text{closed} + \text{bounded}"],
        analogy=analogy("A fenced field, gate shut: walk anywhere inside and there's guaranteed to be a highest and a lowest spot, fence included.",
                        "remove the fence (open set) and the highest spot can be on the line you're not allowed to stand on; remove the field's edges (unbounded) and you can climb forever."),
        exam="To argue a solution exists, check three things in one line: $f$ continuous, feasible set closed, feasible set bounded.",
        problems=[
            problem("p-set-1", "Which set guarantees an optimum?",
                    r"Minimize a continuous $f$ over one of these sets.",
                    [choice("Which set guarantees a minimizer exists?",
                            [opt(r"$[0, 1]\times[0, 2]$", True), opt(r"$(0, 1]$", why="Not closed: an infimum at 0 would never be attained."),
                             opt(r"$[0, \infty)$", why="Unbounded: $f$ may keep decreasing as $x\\to\\infty$."),
                             opt(r"$\{x : x > 0\}$", why="Neither closed nor bounded.")])]),
        ]),

    concept(
        "p-newton-raphson", "Newton–Raphson: replace the curve by its tangent, jump to where the tangent hits zero", 0, A_,
        r"""
To solve $r(x) = 0$, linearize at $x_k$ and solve the linear model: $x_{k+1} = x_k - r(x_k)/r'(x_k)$. For a system $\mathbf{r}(\mathbf{x}) = \mathbf{0}$: $\mathbf{x}_{k+1} = \mathbf{x}_k - \mathbf{J}^{-1}\mathbf{r}(\mathbf{x}_k)$.

Near a root it converges quadratically (the number of correct digits roughly doubles each step). Optimization reuses it everywhere: Newton's method is Newton–Raphson applied to $\nabla f = 0$ ([[c-newton]]); SQP applies it to the KKT conditions ([[c-sqp]]); GRG uses it to pull the state variables back onto the constraints ([[c-grg]]).
""",
        deeper=["p-taylor-vector"],
        math=[r"x_{k+1} = x_k - \frac{r(x_k)}{r'(x_k)}", r"\mathbf{x}_{k+1} = \mathbf{x}_k - \mathbf{J}(\mathbf{x}_k)^{-1}\mathbf{r}(\mathbf{x}_k)"],
        analogy=analogy("Sliding down the tangent line to the axis, then repeating from the new point.",
                        "far from the root, or near a flat spot ($r'\\approx 0$), the tangent can throw you somewhere absurd. Newton is fast only when you're already close."),
        exam="Show one or two iterations in a table ($k$, $x_k$, $r(x_k)$, $r'(x_k)$); that is usually what's marked.",
        problems=[
            problem("p-nr-1", "Two steps toward √2",
                    r"Solve $r(x) = x^2 - 2 = 0$ starting from $x_0 = 1$.",
                    [num(r"$x_1$?", 1.5, ""), num(r"$x_2$?", 1.5 - (1.5**2 - 2) / 3, "", explain="$1.5 - 0.25/3 = 1.41667$, already three correct digits of $\\sqrt2 = 1.41421$.")]),
        ]),

    concept(
        "p-statistics", "Mean, variance and the bell curve: the vocabulary of noisy data", 0, A_,
        r"""
- **Mean** $\bar y = \frac1q\sum y_i$; **variance** $\frac1q\sum(y_i - \bar y)^2$; **standard deviation** its square root.
- **Sum of squares** $\sum(y_i - \bar y)^2$ measures the total variability; the coefficient of determination $R^2$ compares a model's leftover error with it ([[c-error-metrics]]).
- **Gaussian (normal) distribution:** about 68% of values fall within $\pm1\sigma$ of the mean, about 95% within $\pm2\sigma$. Kriging treats the unknown function as a Gaussian process, and its predicted $s$ gives that kind of error bar ([[c-gpr-uncertainty]]).
""",
        math=[r"\bar y = \frac1q\sum_{i=1}^q y_i,\qquad \sigma^2 = \frac1q\sum_{i=1}^q(y_i - \bar y)^2"],
        analogy=analogy("The mean is where the data balances on a seesaw; the standard deviation is how far, typically, a point sits from that balance point.",
                        "for skewed or multi-peaked data, mean ± σ misleads; the Gaussian rules of thumb only hold for bell-shaped data."),
        exam="Keep units: $\\sigma$ and RMSE carry the units of $y$; variance carries units squared; $R^2$ has none.",
        problems=[
            problem("p-stat-1", "Spread of three numbers",
                    r"$y = [1, 2, 3]$.",
                    [num("Sum of squares about the mean, $\\sum(y_i - \\bar y)^2$?", 2, ""),
                     choice(r"A Kriging model predicts $\hat y = 5$ with $s = 0.5$. Which interval holds the true value with about 95% confidence?",
                            [opt("$[4, 6]$", True), opt("$[4.5, 5.5]$", why="That's $\\pm1s$, about 68%."),
                             opt("$[3.5, 6.5]$", why="That's $\\pm3s$, about 99.7%."), opt("$[4.75, 5.25]$", why="That's $\\pm\\tfrac12 s$.")])]),
        ]),

    concept(
        "p-chain-rule", "The chain rule multiplies rates through a pipeline of functions", 0, C_,
        r"""
If $z = f(u)$ and $u = g(w)$, then $\frac{dz}{dw} = \frac{dz}{du}\frac{du}{dw}$. With vectors, the factors become Jacobian matrices multiplied in order.

A neural network is a long pipeline: weights → weighted sums → activations → … → prediction → loss. **Backpropagation** is the chain rule applied from the loss backwards, reusing each intermediate derivative, so the gradient of the loss with respect to every weight costs about as much as one forward pass ([[c-ann]]).
""",
        deeper=["p-gradient"],
        math=[r"\frac{dz}{dw} = \frac{dz}{du}\,\frac{du}{dw}"],
        analogy=analogy("Gears in a gearbox: the output's speed per input turn is the product of the ratios of every gear pair in between.",
                        "gears have fixed ratios; in a network each 'ratio' (derivative) depends on the current inputs, so it must be recomputed for each data point."),
        exam="Write the pipeline as a chain of named intermediate variables before differentiating; it prevents lost factors.",
        problems=[
            problem("p-chain-1", "One neuron, one data point",
                    r"Loss $\varepsilon = \tfrac12(wx - y)^2$ for a single linear neuron, with $x = 2$, $y = 1$, $w = 1$.",
                    [expr(r"Type $\partial\varepsilon/\partial w$ in terms of $w$, $x$, $y$.", (sp.Symbol("w", real=True) * sp.Symbol("x", real=True) - sp.Symbol("y", real=True)) * sp.Symbol("x", real=True),
                          ["w", "x", "y"], explain="Chain rule: $\\frac{\\partial\\varepsilon}{\\partial(wx-y)}\\cdot\\frac{\\partial(wx-y)}{\\partial w} = (wx - y)\\,x$."),
                     num("Its value at the given numbers?", (1 * 2 - 1) * 2, "")]),
        ]),

    concept(
        "p-numpy-shapes", "NumPy shapes: (n,) is not (n, 1), and * is not @", 0, P_,
        r"""
NumPy arrays carry a **shape**. A 1-D array of length $n$ has shape `(n,)`; a column vector has shape `(n, 1)`; a matrix `(m, n)`.

- `A @ B` is matrix multiplication; `A * B` is element-by-element.
- **Broadcasting** stretches size-1 dimensions to match: `(5,) - (5, 1)` silently becomes a `(5, 5)` array. This is the source of many silent bugs in residuals and RMSEs ([[e-broadcast-residual]]).
- `axis=0` works down the rows (one result per column); `axis=1` across columns. `np.all(G <= 0, axis=0)` asks 'is every constraint satisfied?' separately at each design point.
- Slicing returns a **view** that shares memory; use `.copy()` when you'll modify it ([[e-view-copy]]).
""",
        math=[r"(m\times n)\,@\,(n\times k) \to (m\times k)"],
        analogy=analogy("Shapes are like units in physics: every operation must make dimensional sense, and broadcasting is a unit conversion NumPy does for you without asking.",
                        "physics would flag 'metres minus seconds' as an error; NumPy happily broadcasts `(5,) - (5,1)` into nonsense. You have to be the unit checker."),
        exam="Print `.shape` of every array the first time you build it. Most code bugs in this course are shape bugs.",
        problems=[
            problem("p-np-1", "Predict the shape",
                    r"`A` has shape `(3, 2)` and `x` has shape `(2,)`.",
                    [blank("What shape does `A @ x` have? (type it as Python prints it)", ["(3,)"], mode="code", placeholder="(…)",
                           explain="A (3×2) matrix times a length-2 vector gives a length-3 vector: `(3,)`."),
                     choice("And `y - yhat` where `y.shape == (5,)` and `yhat.shape == (5, 1)`?",
                            [opt("`(5, 5)`: broadcasting compares every pair", True), opt("`(5,)`", why="Broadcasting stretches both arrays: `(5,)` acts as `(1, 5)` and pairs with `(5, 1)` to make `(5, 5)`."),
                             opt("`(5, 1)`", why="The `(5,)` array is stretched along a new axis, giving `(5, 5)`."),
                             opt("A `ValueError`", why="NumPy doesn't refuse; it broadcasts. That's what makes the bug silent.")])]),
        ]),

    concept(
        "p-python-functions", "Python functions: arguments, tuples and lambdas, as optimizers call them", 0, P_,
        r"""
Optimizers call *your* function as `fun(x, *args)`. So:

- `args` must be a **tuple**: one extra argument is `(p,)`, with the comma. `(p)` is just `p` in parentheses ([[e-args-tuple]]).
- `x` arrives as a **NumPy array** of floats, even if your initial guess was a list.
- A `lambda` is a one-line anonymous function: `lambda x: -g(x, p)`.
- A lambda created in a loop looks up loop variables **when called, not when created**, so every lambda sees the last value unless you freeze it with a default argument: `lambda x, e=eps: e - W(x)` (the course's own notebooks use this trick) ([[e-lambda-late-binding]]).
- A dict like `{"type": "ineq", "fun": g_scipy, "args": (p,)}` describes one constraint for SciPy's SLSQP.
""",
        math=[],
        analogy=analogy("Handing an optimizer your function is like handing a lab technician a procedure: they'll run it many times with different inputs, and any extra materials (`args`) must be packed in the box they expect (a tuple).",
                        "a technician might notice a mislabelled box; Python often won't, and you get a confusing `TypeError` many calls later."),
        exam="On an open-book coding question, write the call signature `fun(x, *args)` at the top of your answer and check every function against it.",
        problems=[
            problem("p-py-1", "The one-element tuple",
                    r"You want SciPy to call `f(x, p)`, passing the parameter dictionary `p` as the only extra argument.",
                    [blank("Complete: `minimize(f, x0, args=____)`", ["(p,)"], mode="code", explain="`(p,)` is a one-element tuple. Without the comma, `(p)` is just `p`."),
                     choice("What does this print?\n```python\nfs = [lambda: i for i in range(3)]\nprint([f() for f in fs])\n```",
                            [opt("`[2, 2, 2]`", True), opt("`[0, 1, 2]`", why="Each lambda looks up `i` when it's *called*, after the loop has finished with `i = 2`."),
                             opt("`[0, 0, 0]`", why="The lambdas see the final value of `i`, not the first."), opt("An error", why="It runs; it just doesn't do what you might expect.")],
                            explain="Freeze the value with a default argument: `lambda i=i: i` gives `[0, 1, 2]`.")]),
        ]),

    concept(
        "p-lagrange-419", "You've met Lagrange multipliers before: in MECH 419 they were constraint forces", 0, X_,
        rf"""
In analytical dynamics, a multiplier $\lambda$ entered Lagrange's equations as $\sum_i\lambda_ia_{{ij}}$ and turned out to be the **constraint force**: the push needed to keep the system on its constraint (see the [MECH 419 atlas]({MECH419})).

In optimization the multiplier plays the same role for a constrained *minimum*: at the optimum, the objective's downhill pull $-\nabla f$ is balanced by $\sum\lambda_j\nabla h_j$, the constraints pushing back ([[c-lagrangian-equality]]). Its size is a **price**: how much the optimal objective would improve if the constraint were relaxed by one unit. A zero multiplier means the constraint isn't 'pushing' at all, which, for an inequality, means it's inactive ([[c-kkt]]).
""",
        math=[r"\nabla f + \sum_j\lambda_j\nabla h_j = \mathbf{0}"],
        analogy=analogy("A ball held still in a bowl by a wall: the wall's push (the multiplier) exactly cancels the ball's urge to roll downhill, and how hard it pushes tells you how much the ball 'wants' the wall moved.",
                        "in dynamics, λ balances inertia and forces at every instant; in optimization it only has to balance gradients at the optimum."),
        exam="Use the 'price' reading to sanity-check signs: if loosening a constraint should lower the cost, the multiplier for a $\\le$ constraint in negative null form must be $\\ge 0$.",
        problems=[
            problem("p-l419-1", "Same idea, new setting",
                    r"In MECH 419, a pendulum in $(x, y)$ had $\mathbf{R} = \lambda(x\mathbf{i} + y\mathbf{j})$, the rod tension.",
                    [choice("In an optimization problem, what does a large multiplier on an active constraint tell you?",
                            [opt("Relaxing that constraint slightly would improve the optimum a lot", True),
                             opt("The constraint is inactive", why="Inactive inequality constraints have zero multipliers."),
                             opt("The problem has no solution", why="Multipliers exist at regular optima; a large one just means the constraint matters a lot."),
                             opt("The objective is convex", why="Multipliers say nothing about convexity.")])]),
        ]),
]
