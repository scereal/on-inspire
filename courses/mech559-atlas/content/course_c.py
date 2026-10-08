"""Layer 1, Lectures 5-6: unconstrained optimality conditions and algorithms."""
import math
import sympy as sp
from lib import *

L5, L6 = "Lecture 5 · Unconstrained optimality", "Lecture 6 · Unconstrained algorithms"

r_ = sp.Symbol("r", positive=True)
F1 = x1**2 - 3 * x1 * x2 + 4 * x2**2 + x1 - x2           # Lecture 5 example 1
_st = sp.solve([sp.diff(F1, x1), sp.diff(F1, x2)], [x1, x2])
assert _st == {x1: sp.Rational(-5, 7), x2: sp.Rational(-1, 7)}

FQ = 4 * x1**2 + 3 * x1 * x2 + x2**2                      # Lecture 6's running example
_g = sp.Matrix([sp.diff(FQ, v) for v in (x1, x2)]).subs({x1: 1, x2: 1})
_H = sp.hessian(FQ, (x1, x2))
_alpha_exact = (_g.T * _g)[0] / (_g.T * _H * _g)[0]
assert _alpha_exact == sp.Rational(146, 1348)
_newton = -_H.inv() * _g
assert list(_newton) == [-1, -1]

# Armijo interval for f = x1^2 + x2^2 from (1, 1), epsilon = 0.1 (slides: 0.45 <= alpha <= 0.9).
_a = sp.Symbol("a", positive=True)
_phi = 2 * (1 - 2 * _a)**2
_hi = max(sp.solve(sp.Eq(_phi, 2 - 0.8 * _a), _a))
_lo = max(sp.solve(sp.Eq(_phi.subs(_a, 2 * _a), 2 - 1.6 * _a), _a))
assert abs(float(_hi) - 0.9) < 1e-9 and abs(float(_lo) - 0.45) < 1e-9

# BFGS one step from the slides: x0 = (1,1), alpha0 = 0.1, H0 = I.
_s0 = -sp.Rational(1, 10) * _g
_x1p = sp.Matrix([1, 1]) + _s0
_g1 = sp.Matrix([sp.diff(FQ, v) for v in (x1, x2)]).subs({x1: _x1p[0], x2: _x1p[1]})
_y0 = _g1 - _g
_H0 = sp.eye(2)
_Hb = _H0 - (_H0 * _s0 * _s0.T * _H0) / (_s0.T * _H0 * _s0)[0] + (_y0 * _y0.T) / (_y0.T * _s0)[0]

# Scaling example: H = [[2000, 40], [40, 2]].
_Hs_off = 40 / math.sqrt(2000 * 2)
_kHs = (1 + _Hs_off) / (1 - _Hs_off)

CONCEPTS = [
    concept(
        "c-unconstrained-why", "Unconstrained optimization matters because constrained methods are built on it", 1, L5,
        r"""
Engineering problems are almost always constrained, yet unconstrained optimization is foundational:
- its theory (FONC, SOSC) is the basis of the constrained theory;
- some problems are naturally unconstrained (least squares, solving nonlinear equations);
- one-dimensional minimization (**line search**) sits inside nearly every algorithm;
- constrained problems can be turned into unconstrained ones, by **substituting** an active equality constraint or by penalty methods ([[c-penalty-barrier]]).

Substitution: to minimize $f(r, h) = -2\pi r^2 - 2\pi rh$ with the volume constraint $\pi r^2h = 1$ active, solve $h = 1/(\pi r^2)$ and substitute, leaving a one-variable unconstrained problem in $r$.
""",
        deeper=["c-constraint-activity"],
        math=[r"\min_r\ f\big(r, h(r)\big)\ \text{ with }\ h(r) = \frac{1}{\pi r^2}"],
        analogy=analogy("If a recipe insists the cake always weighs exactly 1 kg, you only really choose the shape; the height follows from it. Substitution removes the forced choice.",
                        "substitution only works for constraints you're sure are active, and that you can solve for one variable."),
        exam="Before substituting, state why the constraint is active (monotonicity or relaxation); otherwise the substitution is unjustified.",
        source="Lecture 5, slides 7–10",
        problems=[
            problem("c-uw-1", "Substitute the active constraint",
                    r"$\min f(r, h) = -2\pi r^2 - 2\pi rh$ with $\pi r^2h = 1$ active.",
                    [expr(r"Type $f$ as a function of $r$ alone.", -2 * sp.pi * r_**2 - 2 / r_, ["r"], ranges={"r": [0.3, 2]},
                          explain="$h = 1/(\\pi r^2)$, so $-2\\pi rh = -2/r$, giving $f(r) = -2\\pi r^2 - 2/r$.")]),
        ]),

    concept(
        "c-fonc", "First-order necessary condition: at a smooth interior minimum, the gradient is zero", 1, L5,
        r"""
If $\mathbf{x}^*$ is a local minimum and $f$ is continuously differentiable there, the first-order Taylor term $\nabla f^{*T}(\mathbf{x} - \mathbf{x}^*)$ must be $\ge0$ for every nearby $\mathbf{x}$. Since $\mathbf{x} - \mathbf{x}^*$ can point in any direction, positive or negative, that forces
$$\nabla f(\mathbf{x}^*) = \mathbf{0}.$$
A point satisfying this is a **stationary point**, and it isn't necessarily a minimizer. $f(x) = 1/(1+x^2)$ is stationary at $x = 0$, which is a *maximum*; $x_1^2 - x_2^2$ has a saddle at the origin. Second-order information decides ([[c-sosc]]).
""",
        deeper=["p-taylor-vector", "p-gradient"],
        math=[r"\nabla f(\mathbf{x}^*) = \mathbf{0}"],
        analogy=analogy("At the very bottom of a valley, the ground is level in every direction: no slope to roll down.",
                        "the top of a hill and the middle of a saddle are level too. 'Flat' finds candidates; it doesn't tell valleys from peaks."),
        exam="Solve $\\nabla f = 0$ as a system, list every stationary point, then classify each one. Don't stop at the first solution.",
        source="Lecture 5, slides 12–50",
        problems=[
            problem("c-fonc-1", "Find the stationary point",
                    r"$f = x_1^2 - 3x_1x_2 + 4x_2^2 + x_1 - x_2$ (Lecture 5, example 1).",
                    [expr(r"Type $\partial f/\partial x_1$.", sp.diff(F1, x1), ["x1", "x2"]),
                     expr(r"Type $\partial f/\partial x_2$.", sp.diff(F1, x2), ["x1", "x2"]),
                     num(r"$x_1^*$?", float(_st[x1]), ""), num(r"$x_2^*$?", float(_st[x2]), "", explain="Solve $2x_1 - 3x_2 = -1$ and $-3x_1 + 8x_2 = 1$: $\\mathbf{x}^* = (-5/7, -1/7)$.")]),
            problem("c-fonc-2", "Stationary isn't optimal",
                    r"$f(x) = \dfrac{1}{1 + x^2}$.",
                    [choice("At $x = 0$…", [opt("$f'(0) = 0$, but it's a maximum", True), opt("$f'(0) = 0$, so it's a minimum", why="A zero derivative only marks a stationary point; here $f$ is largest at 0."),
                                           opt("$f'(0)\\ne0$", why="$f'(x) = -2x/(1+x^2)^2$ vanishes at 0."), opt("$f$ isn't differentiable there", why="It's smooth everywhere.")])]),
        ]),

    concept(
        "c-sosc", "Second-order sufficient condition: zero gradient plus a positive definite Hessian means a strict local minimum", 1, L5,
        r"""
At a stationary point the first-order term vanishes, so $\Delta f\approx\tfrac12\Delta\mathbf{x}^T\mathbf{H}^*\Delta\mathbf{x}$. For $f$ to rise in every direction we need that quadratic form positive:

> If $\nabla f(\mathbf{x}^*) = \mathbf{0}$ and $\mathbf{H}(\mathbf{x}^*)$ is **positive definite**, then $\mathbf{x}^*$ is a strict (unique) local minimizer.

If $\mathbf{H}$ is positive definite *everywhere* (not just at $\mathbf{x}^*$), the minimizer is global. A merely semi-definite Hessian is inconclusive by this test.
""",
        deeper=["c-fonc", "p-eigen-definiteness"],
        math=[r"\nabla f^* = \mathbf{0},\ \ \mathbf{H}^*\succ0\ \Rightarrow\ \text{strict local minimum}"],
        analogy=analogy("Level ground (zero gradient) that curves upward in every direction (positive definite) is the bottom of a bowl: drop a marble and it stays.",
                        "a trough (semi-definite) is level along its length, so the marble can roll along it. That's why semi-definite isn't sufficient for a *strict* minimum."),
        exam="Classify with eigenvalues or minors and write the conclusion in words: 'H is positive definite, so x* is a strict local minimizer'.",
        source="Lecture 5, slides 55–57, 74–81",
        problems=[
            problem("c-sosc-1", "Classify three quadratics",
                    r"Lecture 5's three examples.",
                    [choice(r"$f_1 = x_1^2 - 3x_1x_2 + 4x_2^2 + x_1 - x_2$, $\mathbf{H} = \begin{bmatrix}2 & -3\\-3 & 8\end{bmatrix}$:",
                            [opt("positive definite ($2 > 0$, $\\det = 7 > 0$): a unique minimizer", True), opt("indefinite", why="Both leading minors are positive."),
                             opt("positive semi-definite", why="$\\det = 7\\ne0$."), opt("negative definite", why="$H_{11} = 2 > 0$.")]),
                     choice(r"$f_2 = 4x_1^2 - 4x_1x_2 + x_2^2 - 4x_1 + 2x_2$, $\mathbf{H} = \begin{bmatrix}8 & -4\\-4 & 2\end{bmatrix}$:",
                            [opt("positive semi-definite ($\\det = 0$): minimizers along a line, all with the same value", True), opt("positive definite", why="$\\det = 16 - 16 = 0$."),
                             opt("indefinite", why="The eigenvalues are 0 and 10, neither negative."), opt("negative definite", why="$H_{11} > 0$.")]),
                     choice(r"$f_3 = -x_1^2 + x_2^2$:", [opt("indefinite: the origin is a saddle (inflection point)", True), opt("positive definite", why="$H_{11} = -2 < 0$."),
                                                       opt("negative definite", why="$H_{22} = 2 > 0$."), opt("semi-definite", why="The eigenvalues $-2$ and $2$ have opposite signs.")])]),
        ]),

    concept(
        "c-quadratic-functions", "Quadratic functions are the special case everything else is compared with", 1, L5,
        r"""
For $f(\mathbf{x}) = \tfrac12\mathbf{x}^T\mathbf{A}\mathbf{x} + \mathbf{b}^T\mathbf{x} + c$ with symmetric $\mathbf{A}$:
1. $\nabla f = \mathbf{A}\mathbf{x} + \mathbf{b}$ (linear in $\mathbf{x}$);
2. $\mathbf{H} = \mathbf{A}$ (constant everywhere);
3. $\nabla f_2 - \nabla f_1 = \mathbf{H}(\mathbf{x}_2 - \mathbf{x}_1)$.

So the stationary point solves the linear system $\mathbf{A}\mathbf{x} = -\mathbf{b}$, the Hessian's nature is the same everywhere, and property 3 (the *secant condition*) is exactly what quasi-Newton methods impose on their Hessian approximations ([[c-quasi-newton]]). Algorithms are tested on quadratics because every smooth function looks quadratic near a minimum.
""",
        deeper=["p-matrix-calculus", "p-hessian"],
        math=[r"\nabla f = \mathbf{A}\mathbf{x} + \mathbf{b},\quad \mathbf{H} = \mathbf{A},\quad \nabla f_2 - \nabla f_1 = \mathbf{H}(\mathbf{x}_2 - \mathbf{x}_1)"],
        analogy=analogy("Quadratics are the lab bench of optimization: a controlled setting where you can predict exactly what an algorithm should do.",
                        "real functions are only quadratic locally, so behaviour that's guaranteed on the bench (like CG finishing in n steps) becomes approximate in the field."),
        exam="To find the Hessian of a quadratic quickly, read it off: the diagonal gets twice the coefficient of $x_i^2$, and the off-diagonal gets the coefficient of $x_ix_j$.",
        source="Lecture 5, slides 47–49",
        problems=[
            problem("c-quad-1", "Read off the pieces",
                    r"$f = 4x_1^2 + 3x_1x_2 + x_2^2$, written as $\tfrac12\mathbf{x}^T\mathbf{A}\mathbf{x}$.",
                    [num(r"$A_{11}$?", 8, "", explain="$\\tfrac12A_{11}x_1^2 = 4x_1^2$, so $A_{11} = 8$."), num(r"$A_{12}$?", 3, ""),
                     num(r"Using property 3, $\nabla f(2,0) - \nabla f(1,0)$ has first component…", 8, "", explain="$\\mathbf{H}(1, 0)^T = (8, 3)$: first component 8.")]),
        ]),

    concept(
        "c-convexity", "Convexity turns a local minimum into the global one", 1, L5,
        r"""
- A **set** is convex if the segment between any two of its points stays inside it: $\alpha\mathbf{x} + (1-\alpha)\mathbf{y}\in\mathcal S$ for $0\le\alpha\le1$.
- A **function** is convex if its graph lies on or below every chord: $f(\alpha\mathbf{x} + (1-\alpha)\mathbf{y})\le\alpha f(\mathbf{x}) + (1-\alpha)f(\mathbf{y})$. Strictly convex if $<$.

Useful facts: intersections of convex sets are convex, unions usually aren't; sums of convex functions are convex; $f$ is concave if $-f$ is convex (there is no such thing as a concave set).

The payoff: a convex function lies above all its tangent planes, $f(\mathbf{x})\ge f(\mathbf{x}_o) + \nabla f_o^T(\mathbf{x} - \mathbf{x}_o)$. So at a stationary point, $f(\mathbf{x})\ge f(\mathbf{x}^*)$ everywhere: **a stationary point of a (strictly) convex function on a convex set is the (unique) global minimizer.**
""",
        deeper=["c-sosc"],
        math=[r"f(\alpha\mathbf{x} + (1-\alpha)\mathbf{y})\le\alpha f(\mathbf{x}) + (1-\alpha)f(\mathbf{y})", r"f(\mathbf{x})\ge f(\mathbf{x}_o) + \nabla f_o^T(\mathbf{x}-\mathbf{x}_o)"],
        analogy=analogy("A single smooth bowl: wherever you stand, walking downhill leads to the same bottom. Non-convex terrain can have several hollows.",
                        "convexity of the *objective* isn't enough with constraints; the feasible *set* must be convex too, or the landscape can still trap you."),
        exam="To claim a global optimum, cite convexity of both the objective and the feasible set, with a reason for each (e.g. a positive definite Hessian everywhere; linear constraints).",
        source="Lecture 5, slides 58–68",
        problems=[
            problem("c-cvx-1", "Which statements hold?",
                    r"About convex sets and functions:",
                    [spot("Which statement is false?", [
                        ("The intersection of two convex sets is convex.", False, ""),
                        ("The sum of two convex functions is convex.", False, ""),
                        ("The union of two convex sets is convex.", True, "Two separate discs are each convex, but the segment between them leaves their union."),
                        ("A stationary point of a strictly convex function on a convex set is the unique global minimizer.", False, ""),
                    ])]),
            problem("c-cvx-2", "Concave sets?",
                    r"Someone describes a feasible region as 'a concave set'.",
                    [choice("What's wrong with that?", [opt("There's no definition of a concave set; sets are convex or non-convex", True), opt("Nothing: concave sets are the opposite of convex ones", why="Concavity is defined for functions only."),
                                                        opt("Concave sets are always empty", why="The term isn't defined."), opt("It should say 'quasi-concave'", why="That's also a property of functions.")])]),
        ]),

    concept(
        "c-descent", "A descent direction makes a negative angle with the gradient; steepest descent uses −∇f itself", 1, L6,
        r"""
Iterative algorithms update $\mathbf{x}_{k+1} = \mathbf{x}_k + \alpha_k\mathbf{d}_k$. To first order, $f_{k+1} - f_k\approx\alpha_k\nabla f_k^T\mathbf{d}_k$, so $\mathbf{d}_k$ is a **descent direction** whenever
$$\nabla f_k^T\mathbf{d}_k < 0.$$
The obvious choice, $\mathbf{d}_k = -\nabla f_k$, gives $\nabla f_k^T\mathbf{d}_k = -\|\nabla f_k\|^2 < 0$ and is called **steepest descent**. With a fixed step of 1 it can overshoot. On $f = x^2$ from $x_0 = 1$: $x_1 = 1 - 2 = -1$, then $x_2 = 1$, oscillating forever. The direction is right; the distance is wrong. That's why step-size control exists ([[c-gradient-method]]).
""",
        deeper=["p-gradient", "c-fonc"],
        math=[r"\nabla f_k^T\mathbf{d}_k < 0", r"\mathbf{x}_{k+1} = \mathbf{x}_k - \nabla f_k"],
        analogy=analogy("Blindfolded on a slope, you can feel which way is downhill (the direction), but not how far the valley floor is. Stride too far and you climb the opposite side.",
                        "steepest descent is only steepest locally; on a long narrow valley, the steepest direction points mostly across it, not along it, which causes zigzagging."),
        exam="To show a direction is a descent direction, compute $\\nabla f^T\\mathbf{d}$ and show it's negative. One line.",
        widget={"type": "descent"},
        source="Lecture 6, slides 16–29",
        problems=[
            problem("c-desc-1", "The oscillation",
                    r"Steepest descent with unit step on $f(x) = x^2$, from $x_0 = 1$.",
                    [num(r"$x_1$?", -1, ""), num(r"$x_2$?", 1, "", explain="It bounces between $\\pm1$ forever: the step is too long.")]),
            problem("c-desc-2", "Is it downhill?",
                    r"At a point, $\nabla f = (2, -1)$.",
                    [choice("Which direction is a descent direction?", [opt("$\\mathbf{d} = (-1, 0)$", True), opt("$\\mathbf{d} = (1, 1)$", why="$\\nabla f^T\\mathbf{d} = 2 - 1 = 1 > 0$: uphill."),
                                                                        opt("$\\mathbf{d} = (1, 2)$", why="$\\nabla f^T\\mathbf{d} = 2 - 2 = 0$: along the contour, not descent."),
                                                                        opt("$\\mathbf{d} = (2, -1)$", why="That's $+\\nabla f$, steepest *ascent*.")],
                            explain="$\\nabla f^T(-1, 0) = -2 < 0$.")]),
        ]),

    concept(
        "c-gradient-method", "The gradient method adds a step size α to steepest descent", 1, L6,
        r"""
$$\mathbf{x}_{k+1} = \mathbf{x}_k - \alpha_k\nabla f_k,\qquad \alpha_k > 0.$$
With $\alpha = 1$ it *is* steepest descent; with a small α (say 0.01) it creeps but doesn't overshoot; and $\alpha_k$ may change each iteration. The general loop: pick $\mathbf{x}_0$, choose a direction, choose a step, update, and stop when $\|\nabla f_k\| < \varepsilon_{tol}$ or $k\ge k_{max}$.

For $f = x^2$, $x_{k+1} = (1 - 2\alpha)x_k$, which converges iff $|1 - 2\alpha| < 1$, i.e. $0 < \alpha < 1$. Choosing $\alpha_k$ well, without guessing, is the job of line searches ([[c-exact-line-search]], [[c-armijo]]).
""",
        deeper=["c-descent"],
        math=[r"\mathbf{x}_{k+1} = \mathbf{x}_k - \alpha_k\nabla f_k"],
        analogy=analogy("Walking downhill in fog with a chosen stride: too long and you overshoot the valley, too short and you're there by nightfall.",
                        "one fixed stride can't suit both steep slopes and gentle ones, which is why adaptive step sizes (line searches) win."),
        exam="State your stopping criterion explicitly ($\\|\\nabla f\\| < \\varepsilon$, a maximum $k$); results depend on it.",
        widget={"type": "descent"},
        source="Lecture 6, slides 7–11, 31, 86",
        problems=[
            problem("c-gm-1", "A safe step",
                    r"Gradient method on $f(x) = x^2$ from $x_0 = 1$ with $\alpha = 0.25$.",
                    [num(r"$x_1$?", 1 - 0.25 * 2, ""), num(r"Largest fixed α for which it still converges?", 1, "",
                         explain="$x_{k+1} = (1 - 2\\alpha)x_k$ needs $|1 - 2\\alpha| < 1$, i.e. $\\alpha < 1$. At $\\alpha = 1$ it oscillates.")]),
        ]),

    concept(
        "c-exact-line-search", "Exact line search: pick the step that minimizes f along the direction", 1, L6,
        r"""
Given a direction $\mathbf{d}_k$, the best step solves a one-dimensional problem: $\min_{\alpha>0}f(\mathbf{x}_k + \alpha\mathbf{d}_k)$. Using the second-order Taylor model with $\mathbf{d}_k = -\nabla f_k$:
$$f(\mathbf{x}_k - \alpha\nabla f_k)\approx f_k - \alpha\nabla f_k^T\nabla f_k + \tfrac12\alpha^2\nabla f_k^T\mathbf{H}_k\nabla f_k,$$
and its minimizer is
$$\alpha_k^* = \frac{\nabla f_k^T\nabla f_k}{\nabla f_k^T\mathbf{H}_k\nabla f_k}.$$
The SOSC needs $\nabla f_k^T\mathbf{H}_k\nabla f_k > 0$; in practice we require $\mathbf{H}_k$ positive definite. Exact steps need the Hessian at every iteration, which is costly; that's the motivation for inexact searches ([[c-armijo]]).
""",
        deeper=["c-gradient-method", "p-taylor-vector"],
        math=[r"\alpha_k^* = \frac{\nabla f_k^T\nabla f_k}{\nabla f_k^T\mathbf{H}_k\nabla f_k}"],
        analogy=analogy("Having picked a compass bearing, walk along it exactly to the lowest point on that line, then take a new bearing.",
                        "on a quadratic this is exact; on other functions it's exact only for the local quadratic model, so the true minimum along the line may differ."),
        exam="Show $\\nabla f_k$, $\\mathbf{H}_k$, the numerator and the denominator separately; marks are often per piece.",
        source="Lecture 6, slides 35–45",
        problems=[
            problem("c-els-1", "Compute the exact step",
                    r"$f = 4x_1^2 + 3x_1x_2 + x_2^2$ at $\mathbf{x}_k = (1, 1)$: $\nabla f_k = (11, 5)$, $\mathbf{H} = \begin{bmatrix}8&3\\3&2\end{bmatrix}$.",
                    [num(r"$\nabla f_k^T\nabla f_k$?", 146, ""), num(r"$\nabla f_k^T\mathbf{H}\nabla f_k$?", 1348, ""),
                     num(r"$\alpha_k^*$?", float(_alpha_exact), "", explain="$146/1348\\approx0.108$.")]),
        ]),

    concept(
        "c-armijo", "Armijo line search: any step with sufficient decrease will do; backtrack until you find one", 1, L6,
        r"""
Let $\phi(\alpha) = f(\mathbf{x}_k + \alpha\mathbf{d}_k)$, with $\phi(0) = f_k$ and slope $\phi'(0) = \nabla f_k^T\mathbf{d}_k < 0$. **Armijo's test** with $\epsilon\in[0.1, 0.2]$:
1. $\phi(\alpha)\le\phi(0) + \epsilon\,\phi'(0)\,\alpha$ — **sufficient decrease** (not too long);
2. $\phi(2\alpha)\ge\phi(0) + 2\epsilon\,\phi'(0)\,\alpha$ — doubling would fail it (not too short).

**Backtracking:** start at $\alpha = 1$; while condition 1 fails, set $\alpha\leftarrow\beta\alpha$ with $\beta\in[0.8, 0.9]$. No Hessian needed, just function values. (Armijo–Goldstein is the version with two parallel lines, $\epsilon_2 = 1 - \epsilon_1$.)
""",
        deeper=["c-exact-line-search"],
        math=[r"\phi(\alpha)\le\phi(0) + \epsilon\,\phi'(0)\,\alpha", r"\phi(2\alpha)\ge\phi(0) + 2\epsilon\,\phi'(0)\,\alpha"],
        analogy=analogy("House-hunting with a rule: accept any house that's 'enough better than now' (condition 1), but don't settle for one so close by you could easily have done twice as well (condition 2).",
                        "'good enough' steps can still slow convergence. Some theory (for certain algorithms) needs exact steps."),
        exam="Show $\\phi(0)$ and $\\phi'(0)$ first, then plug them into both inequalities and solve for the α interval.",
        widget={"type": "armijo"},
        source="Lecture 6, slides 47–70",
        problems=[
            problem("c-arm-1", "The acceptable interval",
                    r"$f = x_1^2 + x_2^2$ at $\mathbf{x}_k = (1,1)$ with $\mathbf{d}_k = -\nabla f_k$, so $\phi(\alpha) = 2(1 - 2\alpha)^2$, $\phi(0) = 2$, $\phi'(0) = -8$. Take $\epsilon = 0.1$.",
                    [num("Largest α satisfying condition 1?", float(_hi), ""), num("Smallest α satisfying condition 2?", float(_lo), "",
                         explain="Condition 1 gives $\\alpha\\le0.9$, condition 2 gives $\\alpha\\ge0.45$, so $0.45\\le\\alpha\\le0.9$. (α = 0.5 lands exactly on the minimizer.)")]),
            problem("c-arm-2", "Order the backtracking loop",
                    r"Backtracking line search based on Armijo's first condition.",
                    [order("Put the steps in order.", [
                        "Pick α₀ (e.g. 1), ε ∈ [0.1, 0.2] and β ∈ [0.8, 0.9]",
                        "Test f(xₖ + α dₖ) ≤ f(xₖ) + ε α ∇f(xₖ)ᵀdₖ",
                        "If it fails, shrink α ← βα and test again",
                        "When it passes, accept α and take the step",
                    ])]),
        ]),

    concept(
        "c-newton", "Newton's method jumps to the minimum of the local quadratic model", 1, L6,
        r"""
Minimize the second-order model $F(\mathbf{d}) = f_k + \nabla f_k^T\mathbf{d} + \tfrac12\mathbf{d}^T\mathbf{H}_k\mathbf{d}$: setting $\nabla_{\mathbf{d}}F = \mathbf{H}_k\mathbf{d} + \nabla f_k = \mathbf{0}$ gives
$$\mathbf{d}_k = -\mathbf{H}_k^{-1}\nabla f_k\qquad(\alpha = 1).$$
On a quadratic the model is exact, so Newton lands on the minimizer **in one step**. Near a minimum it converges quadratically ([[c-convergence-termination]]). The costs: computing *and* inverting (in practice, solving with) $\mathbf{H}_k$ every iteration. The danger: if $\mathbf{H}_k$ isn't positive definite, the 'minimum' of the model may be a saddle or maximum, and the step may go uphill ([[c-stabilization]]).
""",
        deeper=["c-gradient-method", "p-taylor-vector", "p-newton-raphson"],
        math=[r"\mathbf{d}_k = -\mathbf{H}_k^{-1}\nabla f_k"],
        analogy=analogy("Instead of feeling your way downhill, you fit a bowl to the ground under your feet and jump straight to the bowl's bottom.",
                        "if the ground is saddle-shaped, the 'bowl' you fit is upside down in some direction, and jumping to its 'bottom' can take you uphill."),
        exam="Compute $\\mathbf{d}$ by solving $\\mathbf{H}\\mathbf{d} = -\\nabla f$ (show the 2×2 inverse if done by hand), and verify it's a descent direction.",
        widget={"type": "descent"},
        source="Lecture 6, slide 75",
        problems=[
            problem("c-newt-1", "One step to the bottom",
                    r"$f = 4x_1^2 + 3x_1x_2 + x_2^2$ from $\mathbf{x}_0 = (1, 1)$: $\nabla f_0 = (11, 5)$, $\mathbf{H}^{-1} = \tfrac17\begin{bmatrix}2&-3\\-3&8\end{bmatrix}$.",
                    [num(r"$d_1$?", int(_newton[0]), ""), num(r"$d_2$?", int(_newton[1]), "",
                         explain="$\\mathbf{d} = -\\tfrac17(22 - 15,\\ -33 + 40) = (-1, -1)$, so $\\mathbf{x}_1 = (0, 0)$: the exact minimizer, in one step.")]),
            problem("c-newt-2", "When Newton fails",
                    r"Newton's method is started near a saddle point.",
                    [choice("What can go wrong?", [opt("$\\mathbf{H}$ isn't positive definite, so the step can head uphill or toward the saddle", True),
                                                   opt("Nothing: Newton always descends", why="Only with a positive definite Hessian."),
                                                   opt("It converges linearly", why="The issue is direction, not rate."), opt("It needs a line search to start", why="The core problem is the Hessian's indefiniteness.")])]),
        ]),

    concept(
        "c-quasi-newton", "Quasi-Newton (BFGS): learn the Hessian from gradient changes, no second derivatives needed", 1, L6,
        r"""
Instead of computing $\mathbf{H}_k$, build an approximation $\hat{\mathbf{H}}_k$, usually starting from $\hat{\mathbf{H}}_0 = \mathbf{I}$, that (1) stays symmetric positive definite, (2) uses only gradients, and (3) improves as $k$ grows. The famous **BFGS** update (Broyden–Fletcher–Goldfarb–Shanno), with $\mathbf{s}_k = \mathbf{x}_{k+1} - \mathbf{x}_k$ and $\mathbf{y}_k = \nabla f_{k+1} - \nabla f_k$:
$$\hat{\mathbf{H}}_{k+1} = \hat{\mathbf{H}}_k - \frac{\hat{\mathbf{H}}_k\mathbf{s}_k\mathbf{s}_k^T\hat{\mathbf{H}}_k}{\mathbf{s}_k^T\hat{\mathbf{H}}_k\mathbf{s}_k} + \frac{\mathbf{y}_k\mathbf{y}_k^T}{\mathbf{y}_k^T\mathbf{s}_k}.$$
It satisfies the secant condition $\hat{\mathbf{H}}_{k+1}\mathbf{s}_k = \mathbf{y}_k$ (the quadratic property $\nabla f_2 - \nabla f_1 = \mathbf{H}(\mathbf{x}_2 - \mathbf{x}_1)$). Many implementations update the *inverse* directly, so no solve is needed. SciPy's `method="BFGS"` and `"L-BFGS-B"` are this family ([[lib-minimize]]).
""",
        deeper=["c-newton", "c-quadratic-functions"],
        math=[r"\hat{\mathbf{H}}_{k+1} = \hat{\mathbf{H}}_k - \frac{\hat{\mathbf{H}}_k\mathbf{s}_k\mathbf{s}_k^T\hat{\mathbf{H}}_k}{\mathbf{s}_k^T\hat{\mathbf{H}}_k\mathbf{s}_k} + \frac{\mathbf{y}_k\mathbf{y}_k^T}{\mathbf{y}_k^T\mathbf{s}_k}"],
        analogy=analogy("Learning the shape of a dark room by noting how the floor's slope changes with each step you take: no blueprint (second derivatives), just accumulated experience.",
                        "early on the 'map' is crude (it starts as the identity), so the first few steps behave like gradient descent."),
        exam="In a hand calculation, compute $\\mathbf{s}$, $\\mathbf{y}$, $\\mathbf{s}^T\\mathbf{s}$ and $\\mathbf{y}^T\\mathbf{s}$ as labelled intermediate results before assembling the update.",
        source="Lecture 6, slides 78–86",
        problems=[
            problem("c-bfgs-1", "One BFGS update (Lecture 6's example)",
                    r"$f = 4x_1^2 + 3x_1x_2 + x_2^2$, $\mathbf{x}_0 = (1,1)$, $\hat{\mathbf{H}}_0 = \mathbf{I}$, line search gave $\alpha_0 = 0.1$, so $\mathbf{s}_0 = (-1.1, -0.5)$ and $\mathbf{x}_1 = (-0.1, 0.5)$.",
                    [num(r"$\nabla f_1$, first component?", float(_g1[0]), ""),
                     num(r"$\mathbf{y}_0 = \nabla f_1 - \nabla f_0$, first component?", float(_y0[0]), ""),
                     num(r"$\hat H_{1,11}$ after the update?", float(_Hb[0, 0]), "", tol=0.005,
                         explain="$\\approx8.04$, against the true $H_{11} = 8$. The off-diagonal comes out $\\approx2.91$ (true 3): an excellent approximation after one step.")]),
        ]),

    concept(
        "c-conjugate-gradients", "Conjugate gradients: n cleverly chosen directions finish an n-variable quadratic", 1, L6,
        r"""
Directions $\mathbf{d}_i$, $\mathbf{d}_j$ are **Q-orthogonal** (conjugate) if $\mathbf{d}_i^T\mathbf{Q}\mathbf{d}_j = 0$. For a convex quadratic $f = \tfrac12\mathbf{x}^T\mathbf{Q}\mathbf{x} - \mathbf{b}^T\mathbf{x}$ (minimizer solves $\mathbf{Q}\mathbf{x}^* = \mathbf{b}$), $n$ conjugate directions form a basis, and minimizing along each in turn reaches $\mathbf{x}^*$ in **at most $n$ steps** (exact arithmetic).

The CG algorithm builds them on the fly: $\mathbf{d}_0 = -\mathbf{g}_0$, $\alpha_k = -\dfrac{\mathbf{g}_k^T\mathbf{d}_k}{\mathbf{d}_k^T\mathbf{Q}\mathbf{d}_k}$, then $\mathbf{d}_{k+1} = -\mathbf{g}_{k+1} + \beta_k\mathbf{d}_k$ with $\beta_k = \dfrac{\mathbf{g}_{k+1}^T\mathbf{Q}\mathbf{d}_k}{\mathbf{d}_k^T\mathbf{Q}\mathbf{d}_k}$. For general functions, practical nonlinear CG is Hessian-free, using a line search and Fletcher–Reeves $\beta_k = \|\mathbf{g}_{k+1}\|^2/\|\mathbf{g}_k\|^2$, which makes it attractive at large scale.
""",
        deeper=["c-exact-line-search", "c-quadratic-functions"],
        math=[r"\mathbf{d}_i^T\mathbf{Q}\,\mathbf{d}_j = 0\ (i\ne j)", r"\beta_k^{FR} = \frac{\|\mathbf{g}_{k+1}\|^2}{\|\mathbf{g}_k\|^2}"],
        analogy=analogy("Tuning two coupled dials: adjust one, then the other in a 'compensating' direction that doesn't undo the first adjustment. With the right pairings you never revisit a dial.",
                        "on non-quadratic functions the 'compensation' is only approximate, so CG takes more than n steps and may need restarts."),
        exam="To check conjugacy, compute $\\mathbf{d}_1^T\\mathbf{Q}\\mathbf{d}_2$ explicitly; it must be 0 (up to rounding).",
        widget={"type": "descent"},
        source="Lecture 6, slides 89–106",
        problems=[
            problem("c-cg-1", "Build a conjugate direction",
                    r"$\mathbf{Q} = \begin{bmatrix}8 & 3\\3 & 2\end{bmatrix}$, $\mathbf{d}_1 = (1, 0)$. Find $\mathbf{d}_2 = (3, b)$ with $\mathbf{d}_1^T\mathbf{Q}\mathbf{d}_2 = 0$.",
                    [num("$b$?", -8, "", explain="$\\mathbf{d}_1^T\\mathbf{Q}\\mathbf{d}_2 = 8(3) + 3b = 0$, so $b = -8$."),
                     num("At most how many CG iterations does a 2-variable convex quadratic need?", 2, "")]),
        ]),

    concept(
        "c-stabilization", "Stabilization: force the Newton matrix to be positive definite so every step descends", 1, L6,
        r"""
All the methods are $\mathbf{x}_{k+1} = \mathbf{x}_k - \alpha_k\mathbf{M}_k\nabla f_k$, with $\mathbf{M}_k = \mathbf{I}$ (gradient) or $\mathbf{H}_k^{-1}$ (Newton). To first order $f_{k+1} - f_k\approx-\alpha_k\nabla f_k^T\mathbf{M}_k\nabla f_k$, so descent is guaranteed only if $\mathbf{M}_k$ is **positive (semi-)definite**.

When $\mathbf{H}_k$ isn't positive definite (near saddles or inflection points), replace it by $\hat{\mathbf{H}}_k = \mathbf{H}_k + \mu_k\mathbf{I}$ (or more generally $\mathbf{H}_k + \mathbf{E}_k$), found by **modified Cholesky factorization** $\hat{\mathbf{H}}_k = \hat{\mathbf{L}}_k\hat{\mathbf{D}}_k\hat{\mathbf{L}}_k^T$. Lecture 6's example shows the effect: without it, Newton converges to a saddle; with it, to a local minimum. The factors also give a direction of negative curvature to escape saddles.
""",
        deeper=["c-newton", "p-eigen-definiteness"],
        math=[r"\hat{\mathbf{H}}_k = \mathbf{H}_k + \mu_k\mathbf{I}\succ0"],
        analogy=analogy("Adding a stiff spring under a wobbly floor: the floor now curves upward everywhere, so any step 'downhill' on it really is downhill.",
                        "too stiff a spring (huge μ) turns Newton back into a slow gradient method; the correction should be just enough."),
        exam="If asked why plain Newton found a saddle, answer: $\\mathbf{H}$ was indefinite there, so $-\\mathbf{H}^{-1}\\nabla f$ wasn't guaranteed to descend.",
        source="Lecture 6, slides 111–118",
        problems=[
            problem("c-stab-1", "How much shift?",
                    r"At an iterate, $\mathbf{H}_k$ has eigenvalues $-2$ and $5$.",
                    [choice(r"Which shift makes $\mathbf{H}_k + \mu\mathbf{I}$ positive definite?", [opt("$\\mu = 3$", True), opt("$\\mu = 1$", why="Eigenvalues become $-1$ and $6$: still indefinite."),
                                                                                                    opt("$\\mu = 2$", why="Eigenvalues become $0$ and $7$: only semi-definite."), opt("$\\mu = -3$", why="That makes it worse.")],
                            explain="Adding μI shifts every eigenvalue by μ; you need $-2 + \\mu > 0$.")]),
        ]),

    concept(
        "c-scaling", "Scaling: a badly scaled problem has a stretched Hessian; rescaling makes the bowl round", 1, L6,
        r"""
If one variable matters 1000 times more than another, the contours become long thin ellipses, the Hessian is ill-conditioned, and gradient methods zigzag. For $f = 1000x_1^2 + 40x_1x_2 + x_2^2$, $\mathbf{H} = \begin{bmatrix}2000 & 40\\40 & 2\end{bmatrix}$ has $\kappa\approx1.7\times10^3$.

**Diagonal scaling:** with $D_{ii} = 1/|H_{ii}|$, $\mathbf{H}_s = \mathbf{D}^{1/2}\mathbf{H}\mathbf{D}^{1/2}$ has unit diagonal. Here $\mathbf{H}_s = \begin{bmatrix}1 & 0.632\\0.632 & 1\end{bmatrix}$ with $\kappa = 4.44$. Equivalently transform variables $\mathbf{x}_s = \mathbf{D}\mathbf{x}$, which rescales the gradient and Hessian: $\nabla_x f = \mathbf{D}\nabla_{x_s}f$, $\nabla^2_x f = \mathbf{D}\nabla^2_{x_s}f\,\mathbf{D}$. In code, the cheap version is to work in normalized units (e.g. metres vs micrometres) and normalized constraints ([[e-bad-scaling]]).
""",
        deeper=["c-gradient-method", "c-conditioning-ridge"],
        math=[r"\mathbf{H}_s = \mathbf{D}^{1/2}\mathbf{H}\mathbf{D}^{1/2},\quad D_{ii} = \frac{1}{|H_{ii}|}"],
        analogy=analogy("Reading a map whose north–south scale is 1000 times its east–west scale: 'downhill' looks almost purely east–west, and you zigzag. Redraw it at equal scales and the right direction is obvious.",
                        "diagonal scaling fixes axis-aligned stretching only. A tilted ellipse (strong coupling) needs more than per-variable rescaling."),
        exam="Report κ before and after scaling; that ratio is the quantitative point.",
        widget={"type": "descent", "preset": "scaling"},
        source="Lecture 6, slides 121–122",
        problems=[
            problem("c-scal-1", "Scale the Hessian",
                    r"$\mathbf{H} = \begin{bmatrix}2000 & 40\\40 & 2\end{bmatrix}$, scaled with $D_{ii} = 1/|H_{ii}|$.",
                    [num(r"Off-diagonal entry of $\mathbf{H}_s$?", _Hs_off, "", explain="$40/\\sqrt{2000\\cdot2} = 40/63.25\\approx0.632$."),
                     num(r"$\kappa(\mathbf{H}_s)$?", _kHs, "", explain="Eigenvalues $1\\pm0.632$, so $\\kappa = 1.632/0.368\\approx4.44$, down from about 1700.")]),
        ]),

    concept(
        "c-trust-region", "Trust regions: decide how far to trust the model first, then find the best step inside", 1, L6,
        r"""
Line searches pick a direction, then a distance. Trust regions reverse that: trust the quadratic model only within radius $\Delta_k$ and solve
$$\min_{\mathbf{d}}\ f_k + \nabla f_k^T\mathbf{d} + \tfrac12\mathbf{d}^T\mathbf{H}_k\mathbf{d}\quad\text{s.t.}\ \|\mathbf{d}\|\le\Delta_k.$$
If the model's minimizer is inside the region, the constraint is inactive and $\mathbf{d}_k = -\mathbf{H}_k^{-1}\nabla f_k$ (a Newton step). Otherwise it's active and $\mathbf{d}_k(\mu) = -(\mathbf{H}_k + \mu_k\mathbf{I})^{-1}\nabla f_k$ with $\mu_k > 0$ (the same shift as in stabilization).

The ratio $\rho_k = \dfrac{\text{actual reduction}}{\text{predicted reduction}}$ decides: a small $\rho$ means the model lied, so reject the step and shrink $\Delta$; a $\rho$ near or above 1 means accept, and expand $\Delta$ if the step hit the boundary.
""",
        deeper=["c-newton", "c-stabilization"],
        math=[r"\rho_k = \frac{f(\mathbf{x}_k) - f(\mathbf{x}_k + \mathbf{d}_k)}{m_k(\mathbf{0}) - m_k(\mathbf{d}_k)}"],
        analogy=analogy("Trusting a weather forecast only a few days out: plan boldly within that horizon, and if yesterday's forecast was badly wrong, shorten the horizon you rely on.",
                        "the radius policy (thresholds, growth factors) is a design choice, not physics; different solvers tune it differently."),
        exam="Compute ρ explicitly and say 'accept/reject, expand/shrink'. That decision is what the question tests.",
        widget={"type": "trust"},
        source="Lecture 6, slides 128–136",
        problems=[
            problem("c-tr-1", "Accept or reject?",
                    r"A trust-region step predicted a decrease of 0.5; the actual decrease was 0.03.",
                    [num(r"$\rho$?", 0.03 / 0.5, ""), choice("What should the algorithm do?", [opt("Reject the step and shrink the radius", True), opt("Accept and expand", why="ρ = 0.06: the model badly over-promised."),
                                                                                              opt("Accept and keep the radius", why="Such a low ratio means the model isn't trustworthy at this size."),
                                                                                              opt("Switch to steepest descent", why="The trust-region fix is to shrink Δ.")])]),
            problem("c-tr-2", "Inside or on the boundary?",
                    r"The model's unconstrained minimizer lies inside the trust region.",
                    [choice("Then the step is…", [opt("the Newton step $-\\mathbf{H}^{-1}\\nabla f$, with the region constraint inactive ($\\mu = 0$)", True),
                                                  opt("on the boundary, with $\\mu > 0$", why="That's when the minimizer is outside the region."),
                                                  opt("zero", why="The model's minimizer is a nonzero step."), opt("$-\\nabla f$", why="With the Hessian available, the step is Newton's.")])]),
        ]),
]
