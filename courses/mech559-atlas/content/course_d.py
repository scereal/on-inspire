"""Layer 1, Lectures 7-9: linear programming, nonlinear programming, constrained algorithms."""
import math
import sympy as sp
from lib import *

L7, L8, L9 = "Lecture 7 · Linear programming", "Lecture 8 · Nonlinear programming", "Lecture 9 · Constrained algorithms"

# Farmer LP basic solution for B = {x1, x2}.
_xb = sp.Matrix([[2, 1], [1, 1]]).solve(sp.Matrix([320, 240]))
assert list(_xb) == [80, 160]

# Reduced-gradient / Lagrangian example: min x1^2 + x2^2 s.t. x1 + x2 - 2 = 0.
_fr = x1**2 + x2**2
_hr = x1 + x2 - 2
_redgrad = sp.diff(_fr, x2) - sp.diff(_fr, x1) * (1 / sp.diff(_hr, x1)) * sp.diff(_hr, x2)
_lag_sol = sp.solve([sp.diff(_fr + lam1 * _hr, v) for v in (x1, x2)] + [_hr], [x1, x2, lam1])
assert _lag_sol == {x1: 1, x2: 1, lam1: -2}

# KKT example: min (x1-2)^2 + (x2-1)^2 s.t. x1 + x2 - 2 <= 0.
_fk = (x1 - 2)**2 + (x2 - 1)**2
_gk = x1 + x2 - 2
_kkt = sp.solve([sp.diff(_fk + mu * _gk, v) for v in (x1, x2)] + [_gk], [x1, x2, mu])
assert _kkt == {x1: sp.Rational(3, 2), x2: sp.Rational(1, 2), mu: 1}

# Penalty / barrier on min x^2 s.t. x >= 1 (g = 1 - x <= 0), r = 0.1.
_r = 0.1
_x_pen = 1 / (1 + _r)
_xs = sp.Symbol("xs", real=True)
_x_bar = float(sp.nsolve(2 * _xs * (_xs - 1)**2 - _r, _xs, 1.3))
assert _x_bar > 1

CONCEPTS = [
    concept(
        "c-lp-standard-form", "Linear programming in standard form: minimize cᵀx subject to Ax = b, x ≥ 0", 1, L7,
        r"""
When the objective and every constraint are linear, write the problem in **standard form**:
$$\min_{\mathbf{x}}\ \mathbf{c}^T\mathbf{x}\quad\text{s.t.}\quad\mathbf{A}\mathbf{x} = \mathbf{b},\ \ \mathbf{x}\ge\mathbf{0}.$$
Converting:
- **maximize → minimize** by negating $\mathbf{c}$ (the farmer's profit $40x_1 + 30x_2$ becomes $\min -40x_1 - 30x_2$);
- each $\le$ constraint gets a **slack** variable: $2x_1 + x_2\le320\ \to\ 2x_1 + x_2 + s_1 = 320$, $s_1\ge0$;
- each $\ge$ constraint gets a **surplus** variable: $\mathbf{A}_3\mathbf{z} - \mathbf{s}_2 = \mathbf{b}_3$;
- a free variable becomes $z = u - v$ with $u, v\ge0$ (more variables, same problem).

SciPy's `linprog` accepts the friendlier `A_ub`, `b_ub`, `A_eq`, `b_eq`, `bounds` form and does the conversion for you. But it **minimizes**, and its default bounds are $x\ge0$ ([[lib-linprog]], [[e-linprog-max]]).
""",
        deeper=["c-negative-null-form", "p-linear-systems"],
        math=[r"\min_{\mathbf{x}}\ \mathbf{c}^T\mathbf{x}\ \ \text{s.t.}\ \ \mathbf{A}\mathbf{x} = \mathbf{b},\ \mathbf{x}\ge\mathbf{0}"],
        analogy=analogy("Slack is literally the unused resource: if the farmer has 320 labour hours and plans 300, the slack variable holds the 20 spare hours.",
                        "slack variables only exist for inequalities; equality constraints have no 'spare' to measure."),
        exam="Write the A matrix with columns labelled ($x_1, x_2, s_1, s_2$). It makes basic-solution and tableau questions mechanical.",
        widget={"type": "lp"},
        source="Lecture 7 (combined slides 173–182)",
        problems=[
            problem("c-lpsf-1", "Convert the farmer's problem",
                    r"$\max 40x_1 + 30x_2$ s.t. $2x_1 + x_2\le320$ (labour), $x_1 + x_2\le240$ (land), $x\ge0$.",
                    [blank("In standard form the objective is $\\min$ ____ (type it with x1, x2).", ["-40*x1-30*x2", "-40x1-30x2", "-40*x1 - 30*x2", "-(40*x1+30*x2)"], mode="code",
                           explain="Maximizing $40x_1 + 30x_2$ is minimizing $-40x_1 - 30x_2$."),
                     choice("The labour constraint becomes…", [opt("$2x_1 + x_2 + s_1 = 320$, $s_1\\ge0$", True), opt("$2x_1 + x_2 - s_1 = 320$", why="A $\\le$ constraint gets a slack added; subtracting is for $\\ge$ (surplus)."),
                                                              opt("$2x_1 + x_2 = 320$", why="That forces all the labour to be used."), opt("$-2x_1 - x_2\\le-320$", why="That flips the inequality and still isn't standard form.")])]),
            problem("c-lpsf-2", "A free variable",
                    r"A variable $z$ may be negative, but standard form needs $\mathbf{x}\ge\mathbf{0}$.",
                    [blank("Substitute $z = $ ____ with two new non-negative variables $u, v$.", ["u-v", "u - v"], mode="code")]),
        ]),

    concept(
        "c-basic-solutions", "Basic solutions: choose m columns, solve for them, set the rest to zero", 1, L7,
        r"""
With $\mathbf{A}\in\mathbb{R}^{m\times n}$, $n > m$ and full rank, choose $m$ linearly independent columns as the **basis** $\mathbf{B}$. Solve $\mathbf{B}\mathbf{x}_B = \mathbf{b}$ and set the other $n - m$ (**non-basic**) variables to zero. The result is a **basic solution**:
- **feasible** if $\mathbf{x}_B\ge\mathbf{0}$ (a basic feasible solution, BFS);
- **degenerate** if some basic variable is zero.

There are at most $M = \dfrac{n!}{m!(n-m)!}$ bases. The farmer's problem ($m = 2$, $n = 4$) has 6. The basis $\{x_1, x_2\}$ gives $(80, 160, 0, 0)$ with $f = -8000$, the optimum; two other bases give negative variables, which are infeasible.
""",
        deeper=["c-lp-standard-form", "p-linear-systems"],
        math=[r"\mathbf{x} = \begin{bmatrix}\mathbf{B}^{-1}\mathbf{b}\\ \mathbf{0}\end{bmatrix},\qquad M = \binom{n}{m}"],
        analogy=analogy("Choosing which m 'workers' do the job and benching the rest: each choice of team gives one way to meet the quota exactly, possibly with someone working negative hours (infeasible).",
                        "the count $\\binom nm$ explodes quickly (n = 100, m = 50 gives about $10^{29}$), so enumerating every team is hopeless. Hence simplex."),
        exam="For each basis, show $\\mathbf{B}$, $\\mathbf{B}^{-1}\\mathbf{b}$, feasibility, and $\\mathbf{c}^T\\mathbf{x}$ in a table, as in the lecture.",
        source="Lecture 7 (combined slides 183–189)",
        problems=[
            problem("c-bs-1", "The farmer's bases",
                    r"Standard form: $\mathbf{A} = \begin{bmatrix}2&1&1&0\\1&1&0&1\end{bmatrix}$, $\mathbf{b} = (320, 240)$, $\mathbf{c} = (-40, -30, 0, 0)$.",
                    [num("How many possible bases?", math.comb(4, 2), ""),
                     num(r"With basis $\{x_1, x_2\}$, what is $x_2$?", int(_xb[1]), "", explain="Solve $2x_1 + x_2 = 320$, $x_1 + x_2 = 240$: $x_1 = 80$, $x_2 = 160$."),
                     num("Objective value there?", -40 * 80 - 30 * 160, "")]),
            problem("c-bs-2", "Example 1 from the slides",
                    r"$\min x_1 + x_2 + x_3$ s.t. $x_1 + 2x_2 + 3x_3 = 4$, $\mathbf{x}\ge0$ ($m = 1$, $n = 3$).",
                    [num("Optimal objective value (check the three basic solutions)?", sp.Rational(4, 3), "",
                         explain="The bases give $(4,0,0)$, $(0,2,0)$, $(0,0,4/3)$ with objectives $4$, $2$, $4/3$. The third is optimal.")]),
        ]),

    concept(
        "c-lp-theory", "The fundamental theorem of LP: if there's an optimum, there's one at a vertex", 1, L7,
        r"""
For a standard-form LP with $\mathbf{A}$ of full rank:
1. if there is a feasible solution, there is a **basic** feasible solution;
2. if there is an optimal feasible solution, there is an optimal **basic** feasible solution.

And geometrically: **basic feasible solutions are exactly the extreme points (vertices)** of the convex polytope $\{\mathbf{x}: \mathbf{A}\mathbf{x} = \mathbf{b},\ \mathbf{x}\ge0\}$. So an LP's optimum, if it exists, sits at a vertex, and we only ever need to examine vertices. (An extreme point of a convex set can't be written as a mix of two other points of the set.)
""",
        deeper=["c-basic-solutions", "c-convexity"],
        math=[r"\text{BFS}\iff\text{vertex of } \{\mathbf{x}:\mathbf{A}\mathbf{x} = \mathbf{b},\ \mathbf{x}\ge0\}"],
        analogy=analogy("Sliding a ruler (a level line of the linear objective) across a polygon: the last point it touches is always a corner, or a whole edge if the ruler is parallel to it.",
                        "an edge tie gives infinitely many optima, but a corner is still among them, which is all the theorem promises."),
        exam="In a graphical LP, list the vertices with their objective values. That's a complete solution method, justified by this theorem.",
        source="Lecture 7 (combined slides 190–192)",
        problems=[
            problem("c-lpt-1", "Why vertices?",
                    r"An LP has a feasible region shaped like a pentagon.",
                    [choice("Where must you look for its optimum?", [opt("At its five vertices (a tie can also include an edge)", True), opt("At its centroid", why="A linear objective is never best at an interior point unless it's constant."),
                                                                    opt("Anywhere on the boundary", why="The theorem narrows it to vertices."), opt("Only where all constraints are active", why="In 2-D, two active constraints define a vertex; not all of them.")])]),
        ]),

    concept(
        "c-simplex", "The simplex method walks from vertex to better vertex", 1, L7,
        r"""
Enumerating every basis is hopeless at scale, so Dantzig's **simplex method** (1947) moves from one BFS to an adjacent, better one:

1. Start from a BFS in canonical (tableau) form.
2. Compute the **reduced costs** $r_j = c_j - f_j$ for non-basic variables. If all $r_j\ge0$, stop: optimal.
3. **Entering variable:** the most negative $r_q$.
4. **Ratio test:** among rows with $y_{iq} > 0$, pick the smallest $y_{0i}/y_{iq}$. That basic variable **leaves**. If no $y_{iq} > 0$, the problem is unbounded.
5. **Pivot** on $y_{pq}$ (divide its row by $y_{pq}$, eliminate the column elsewhere) and repeat.

Farmer: $x_1$ enters first ($r = -40$); ratios $320/2 = 160$ and $240/1 = 240$, so $s_1$ leaves. After one more pivot ($x_2$ enters, $s_2$ leaves), all $r_j\ge0$ at $(80, 160)$, $f = -8000$. Modern solvers like HiGHS (`linprog(method="highs")`) use refined simplex and interior-point methods.
""",
        deeper=["c-lp-theory"],
        math=[r"r_j = c_j - f_j,\quad f_j = \sum_i y_{ij}c_i", r"\text{leave: }\ \min_i\Big\{\frac{y_{0i}}{y_{iq}}: y_{iq} > 0\Big\}"],
        analogy=analogy("Climbing a crystal along its edges: at each corner, take the edge that improves fastest, and stop at the corner where every edge leads down.",
                        "'improves fastest' per unit of the entering variable doesn't mean the best total improvement. Simplex can take many steps, but in practice it's remarkably efficient."),
        exam="Show every tableau with its reduced-cost row and ratio column; name the entering and leaving variables at each pivot.",
        widget={"type": "lp"},
        source="Lecture 7 (combined slides 193–206)",
        problems=[
            problem("c-spx-1", "First pivot of the farmer's problem",
                    r"Initial tableau: basis $\{s_1, s_2\}$, reduced costs $r = (-40, -30, 0, 0)$ for $(x_1, x_2, s_1, s_2)$; rows $s_1$: $[2, 1, 1, 0 \mid 320]$, $s_2$: $[1, 1, 0, 1 \mid 240]$.",
                    [choice("Which variable enters?", [opt("$x_1$: the most negative reduced cost", True), opt("$x_2$", why="$-30$ isn't the most negative; $-40$ is."),
                                                       opt("$s_1$", why="Basic variables don't enter."), opt("None: it's optimal", why="Negative reduced costs mean it can still improve.")]),
                     choice("Which variable leaves?", [opt("$s_1$: ratio $320/2 = 160$ is smallest", True), opt("$s_2$", why="Its ratio $240/1 = 240$ is larger."),
                                                       opt("$x_2$", why="$x_2$ isn't basic."), opt("Both", why="One variable leaves per pivot.")])]),
            problem("c-spx-2", "Order one iteration",
                    r"One iteration of the simplex algorithm.",
                    [order("Put the steps in order.", [
                        "Check reduced costs; stop if all are ≥ 0",
                        "Pick the entering variable (most negative reduced cost)",
                        "Ratio test over rows with positive pivot-column entries",
                        "Pick the leaving variable (smallest ratio)",
                        "Pivot to update the tableau",
                    ])]),
        ]),

    concept(
        "c-dof-regularity", "Constrained degrees of freedom: n − m free directions, if the constraints are regular", 1, L8,
        r"""
With $n$ variables and $m$ equality constraints (including the active inequalities):
- $m > n$: dependent, redundant or inconsistent constraints;
- $m = n$: the constraints alone pin down the feasible point(s);
- $n > m$: the interesting case, with $p = n - m$ **degrees of freedom**.

That count holds only if the constraints are functionally independent, meaning their gradients $\nabla h_j(\mathbf{x})$ are **linearly independent**. That is the **constraint qualification**, and a point where it holds is **regular**. KKT theory is only guaranteed at regular points: Lecture 8's exercise with $g_1 = x_2 - (1 - x_1)^3\le0$, $g_2 = -x_2\le0$ has its optimum at $(1, 0)$, where $\nabla g_1$ and $\nabla g_2$ are parallel, so KKT fails there ([[c-kkt]]).
""",
        deeper=["c-feasibility", "p-linear-systems", "p-gradient"],
        math=[r"p = n - m,\qquad \{\nabla h_j(\mathbf{x})\}\ \text{linearly independent}\ \Rightarrow\ \mathbf{x}\ \text{regular}"],
        analogy=analogy("Each constraint is a rail you must stay on: with 3 coordinates and 1 rail-surface you can still move in 2 directions. But two rails that touch tangentially don't pin you down the way two crossing rails would.",
                        "'regular' is about the constraints' gradients at one point. A problem can be regular almost everywhere and fail exactly at the optimum."),
        exam="To check regularity, write the active constraints' gradients at the point and show they're linearly independent (e.g. a nonzero 2×2 determinant).",
        source="Lecture 8 (combined slides 208–211, 229)",
        problems=[
            problem("c-dof-1", "Count the freedom",
                    r"3 variables, 1 equality constraint, at a regular point.",
                    [num("Degrees of freedom?", 2, ""),
                     choice(r"At $\mathbf{x}^* = (1, 0)$, $\nabla g_1 = (0, 1)$ and $\nabla g_2 = (0, -1)$, both active. Is $\mathbf{x}^*$ regular?",
                            [opt("No: the active gradients are linearly dependent (parallel)", True), opt("Yes: both gradients are nonzero", why="Nonzero isn't enough; they must be linearly independent."),
                             opt("Yes: there are only two constraints", why="Regularity depends on independence, not count."), opt("It can't be determined", why="Check independence: $(0,1)$ and $(0,-1)$ are parallel.")])]),
        ]),

    concept(
        "c-tangent-normal", "Feasible directions lie in the tangent space; constraint gradients span the normal space", 1, L8,
        r"""
Stack the constraint gradients as rows of the **Jacobian** $\mathbf{J} = \nabla\mathbf{h}(\mathbf{x})\in\mathbb{R}^{m\times n}$. To first order, a small move $\partial\mathbf{x}$ keeps $\mathbf{h} = \mathbf{0}$ only if $\nabla\mathbf{h}\,\partial\mathbf{x} = \mathbf{0}$. Those moves form the **tangent hyperplane**, the feasible directions. Its orthogonal complement, the **normal hyperplane**, is spanned by the constraint gradients: $\mathbf{z} = \sum_j\lambda_j\nabla h_j$.

So a constrained minimum is a point where $f$ can't decrease along any tangent direction: $\nabla f^T\partial\mathbf{x}\ge0$ for all feasible $\partial\mathbf{x}$. That forces $\nabla f$ into the normal space, which is the Lagrange condition ([[c-lagrangian-equality]]).
""",
        deeper=["c-dof-regularity"],
        math=[r"\nabla\mathbf{h}(\mathbf{x})\,\mathbf{y} = \mathbf{0}\ \text{(tangent)},\qquad \mathbf{z} = \textstyle\sum_j\lambda_j\nabla h_j\ \text{(normal)}"],
        analogy=analogy("Standing on a curved roof: you can walk along it (tangent directions) but not straight up or down through it (normal directions).",
                        "the tangent plane is only a first-order picture. Walk far along it and you leave the curved surface, which is why GRG needs a correction step."),
        exam="Find a tangent direction by solving $\\nabla h^T\\mathbf{y} = 0$ for a nonzero $\\mathbf{y}$, and check it with the dot product.",
        source="Lecture 8 (combined slides 212–216)",
        problems=[
            problem("c-tn-1", "Walk along a circle",
                    r"$h(\mathbf{x}) = x_1^2 + x_2^2 - 1 = 0$ at $\mathbf{x} = (1, 0)$.",
                    [choice(r"$\nabla h$ there is…", [opt("$(2, 0)$", True), opt("$(1, 0)$", why="$\\partial h/\\partial x_1 = 2x_1 = 2$."), opt("$(0, 2)$", why="$\\partial h/\\partial x_2 = 2x_2 = 0$ at $x_2 = 0$."), opt("$(2, 2)$", why="Evaluate at $(1, 0)$.")]),
                     choice("A feasible (tangent) direction is…", [opt("$(0, 1)$", True), opt("$(1, 0)$", why="That's along $\\nabla h$: it leaves the circle."),
                                                                   opt("$(1, 1)$", why="$\\nabla h^T(1,1) = 2\\ne0$."), opt("$(-1, 0)$", why="Also normal, just pointing inward.")])]),
        ]),

    concept(
        "c-reduced-gradient", "The reduced gradient eliminates the constraints by splitting x into state and decision variables", 1, L8,
        r"""
Split $\mathbf{x}$ into $m$ **state** variables $\mathbf{x}_s$ (determined by the constraints) and $p = n - m$ **decision** variables $\mathbf{x}_d$ (free). Linearizing $\mathbf{h} = \mathbf{0}$: $\nabla_{x_s}\mathbf{h}\,\partial\mathbf{x}_s = -\nabla_{x_d}\mathbf{h}\,\partial\mathbf{x}_d$, so $\partial\mathbf{x}_s = -(\nabla_{x_s}\mathbf{h})^{-1}\nabla_{x_d}\mathbf{h}\,\partial\mathbf{x}_d$. Substituting into $\partial f$:
$$\nabla w^T = \nabla_{x_d}f^T - \nabla_{x_s}f^T(\nabla_{x_s}\mathbf{h})^{-1}\nabla_{x_d}\mathbf{h}.$$
This **reduced (constrained) gradient** is the gradient of $f$ in the decision variables alone, with the constraints already accounted for. The constrained FONC is $\nabla w = \mathbf{0}$, plus $\mathbf{h} = \mathbf{0}$. It requires $\nabla_{x_s}\mathbf{h}$ to be non-singular, so choose state variables that make it so.
""",
        deeper=["c-tangent-normal", "c-fonc"],
        math=[r"\nabla w^T = \nabla_{x_d}f^T - \nabla_{x_s}f^T(\nabla_{x_s}\mathbf{h})^{-1}\nabla_{x_d}\mathbf{h}"],
        analogy=analogy("Steering a car whose trailer follows automatically: you only control the car (decision variables); the trailer's position (state) is determined by the hitch (constraints). The reduced gradient is how the cost changes as you steer, trailer included.",
                        "the 'hitch' relation is linearized, so it's exact only for small moves. That's why GRG adds a Newton correction."),
        exam="State which variables you chose as state vs decision, and check that $\\nabla_{x_s}\\mathbf{h}$ is invertible there.",
        source="Lecture 8 (combined slides 217–219)",
        problems=[
            problem("c-rg-1", "A reduced gradient",
                    r"$\min f = x_1^2 + x_2^2$ s.t. $h = x_1 + x_2 - 2 = 0$. Take $x_1$ as the state variable and $x_2$ as the decision variable.",
                    [expr(r"Type the reduced gradient $\nabla w$ (a scalar here).", _redgrad, ["x1", "x2"],
                          explain="$\\nabla w = 2x_2 - 2x_1\\cdot(1)^{-1}\\cdot1 = 2x_2 - 2x_1$."),
                     choice(r"Setting $\nabla w = 0$ with $h = 0$ gives…", [opt("$x_1 = x_2 = 1$", True), opt("$x_1 = 2, x_2 = 0$", why="Then $\\nabla w = -4\\ne0$."),
                                                                           opt("$x_1 = x_2 = 0$", why="That violates $h = 0$."), opt("No solution", why="$x_1 = x_2$ and $x_1 + x_2 = 2$ give $(1, 1)$.")])]),
        ]),

    concept(
        "c-lagrangian-equality", "The Lagrangian turns an equality-constrained problem into an unconstrained stationarity condition", 1, L8,
        r"""
Define $\boldsymbol\lambda^T = -\nabla_{x_s}f^T(\nabla_{x_s}\mathbf{h})^{-1}$. Then both pieces of the reduced-gradient condition combine into
$$\nabla f + \nabla\mathbf{h}^T\boldsymbol\lambda = \mathbf{0},\qquad \mathbf{h} = \mathbf{0}.$$
These are exactly the stationarity conditions of the **Lagrangian** $L(\mathbf{x}, \boldsymbol\lambda) = f(\mathbf{x}) + \boldsymbol\lambda^T\mathbf{h}(\mathbf{x})$ in both $\mathbf{x}$ and $\boldsymbol\lambda$. The **Lagrange multipliers** $\boldsymbol\lambda$ measure sensitivity: for $h = \text{(constraint)} - b$, $\partial f^*/\partial b = -\lambda$. They are the 'price' of each constraint, the same objects you met as constraint forces in MECH 419 ([[p-lagrange-419]]).
""",
        deeper=["c-reduced-gradient", "p-lagrange-419"],
        math=[r"L = f + \boldsymbol\lambda^T\mathbf{h}", r"\nabla_x L = \nabla f + \nabla\mathbf{h}^T\boldsymbol\lambda = \mathbf{0},\quad \nabla_\lambda L = \mathbf{h} = \mathbf{0}"],
        analogy=analogy("At the optimum on a constraint, the objective's pull and the constraint's push are in balance, like a ball resting against a curved wall. λ is how hard the wall pushes.",
                        "a stationary point of L can be a constrained maximum or saddle. The constrained SOSC decides ([[c-constrained-sosc]])."),
        exam="Write all $n + m$ equations ($\\nabla_x L = 0$ and $\\mathbf{h} = 0$) before solving, and report λ with its interpretation.",
        source="Lecture 8 (combined slides 220–221)",
        problems=[
            problem("c-lag-1", "Solve with a multiplier",
                    r"$\min f = x_1^2 + x_2^2$ s.t. $h = x_1 + x_2 - 2 = 0$, with $L = f + \lambda h$.",
                    [expr(r"Type $\partial L/\partial x_1$ (use `lambda1` for λ).", sp.diff(_fr + lam1 * _hr, x1), ["x1", "x2", "lambda1"]),
                     num(r"$\lambda$ at the optimum?", int(_lag_sol[lam1]), "", explain="$2x_1 + \\lambda = 0$ with $x_1 = 1$ gives $\\lambda = -2$."),
                     choice(r"If the constraint were $x_1 + x_2 = b$, then $f^* = b^2/2$. What is $df^*/db$ at $b = 2$, and how does it relate to λ?",
                            [opt("$2 = -\\lambda$: the multiplier is (minus) the sensitivity", True), opt("$-2 = \\lambda$, with no relation", why="$df^*/db = b = 2$, and that's exactly $-\\lambda$."),
                             opt("$4$", why="$\\frac{d}{db}(b^2/2) = b = 2$."), opt("$0$", why="Moving the constraint changes the optimum.")])]),
        ]),

    concept(
        "c-constrained-sosc", "Constrained second-order test: the Lagrangian's Hessian must curve upward along the constraints", 1, L8,
        r"""
A KKT or Lagrange point is only stationary. To confirm a minimum, check the **Hessian of the Lagrangian** $\nabla^2_x L = \nabla^2 f + \sum_j\lambda_j\nabla^2h_j$, but only **on the tangent subspace** of the active constraints:
$$\partial\mathbf{x}^T\nabla^2_x L\,\partial\mathbf{x} > 0\quad\text{for all nonzero }\partial\mathbf{x}\text{ with }\nabla\mathbf{h}\,\partial\mathbf{x} = \mathbf{0}.$$
(It equals the reduced Hessian $\nabla^2w$ in the decision variables.) Directions that leave the constraints don't matter, since you can't move that way. Lecture 8's Class Exercise 3 has a KKT point that is a local **maximizer**: its Lagrangian Hessian is negative along the feasible directions.
""",
        deeper=["c-lagrangian-equality", "c-sosc", "c-tangent-normal"],
        math=[r"\partial\mathbf{x}^T\,\nabla^2_xL\,\partial\mathbf{x} > 0\ \ \forall\,\partial\mathbf{x}\ne0:\ \nabla\mathbf{h}\,\partial\mathbf{x} = \mathbf{0}"],
        analogy=analogy("On a mountain road, what matters is whether the road dips or rises along its length, not how steep the hillside is above and below it.",
                        "the test needs the multipliers inside $\\nabla^2_xL$. Using $\\nabla^2f$ alone ignores the constraints' curvature and can give the wrong verdict."),
        exam="Find a basis for the tangent space, then compute the 1×1 or 2×2 reduced matrix $\\mathbf{Y}^T\\nabla^2L\\,\\mathbf{Y}$. Its definiteness is the answer.",
        source="Lecture 8 (combined slides 222, 230–231)",
        problems=[
            problem("c-csosc-1", "Which Hessian, which directions?",
                    r"You've found a KKT point $(\mathbf{x}^*, \boldsymbol\lambda, \boldsymbol\mu)$.",
                    [choice("To confirm a local minimum you check…", [opt("$\\nabla^2_xL$ is positive definite on the tangent space of the active constraints", True),
                                                                      opt("$\\nabla^2f$ is positive definite everywhere", why="That ignores the constraints' curvature and the multipliers."),
                                                                      opt("$\\nabla^2_xL$ is positive definite in all directions", why="Only feasible (tangent) directions matter."),
                                                                      opt("the multipliers are positive", why="That's a first-order KKT condition, not the second-order test.")])]),
        ]),

    concept(
        "c-kkt", "KKT conditions: stationarity, feasibility, non-negative multipliers, complementary slackness", 1, L8,
        r"""
For $\min f$ s.t. $\mathbf{g}(\mathbf{x})\le\mathbf{0}$, $\mathbf{h}(\mathbf{x}) = \mathbf{0}$, at a **regular** local minimizer there exist multipliers with:
1. **Stationarity:** $\nabla f + \nabla\mathbf{g}^T\boldsymbol\mu + \nabla\mathbf{h}^T\boldsymbol\lambda = \mathbf{0}$
2. **Feasibility:** $\mathbf{h} = \mathbf{0}$, $\mathbf{g}\le\mathbf{0}$
3. **Sign:** $\boldsymbol\mu\ge\mathbf{0}$, and $\boldsymbol\lambda$ unrestricted in sign *(the slides write "λ ≠ 0"; the standard statement is that λ may take any sign, including zero)*
4. **Complementary slackness:** $\boldsymbol\mu^T\mathbf{g} = 0$: each $\mu_j$ is zero unless its $g_j$ is active.

Why $\mu\ge0$: moving into the feasible region makes active $g$'s more negative, which mustn't decrease $f$. Geometrically, $-\nabla f$ lies in the cone of the active constraints' gradients ([[c-topography]]). KKT points are only stationary: check the constrained SOSC ([[c-constrained-sosc]]). For convex problems a KKT point is the global minimizer.
""",
        deeper=["c-lagrangian-equality", "c-topography", "c-dof-regularity"],
        math=[r"\nabla f + \nabla\mathbf{g}^T\boldsymbol\mu + \nabla\mathbf{h}^T\boldsymbol\lambda = \mathbf{0}", r"\boldsymbol\mu\ge\mathbf{0},\qquad \boldsymbol\mu^T\mathbf{g} = 0"],
        analogy=analogy("Walls can only push, never pull: an active wall pushes back with some force μ ≥ 0, and a wall you're not touching pushes with zero force. That's complementary slackness.",
                        "the push/pull picture assumes regular points. At a cusp (like Lecture 8's exercise) the walls' directions line up and no balance of pushes exists, even at the true optimum."),
        exam="Guess the active set, solve the equations, then *verify* μ ≥ 0 for active constraints and g ≤ 0 for inactive ones. If either fails, change the guess.",
        widget={"type": "kkt"},
        source="Lecture 8 (combined slides 223–231)",
        problems=[
            problem("c-kkt-1", "Solve a KKT system",
                    r"$\min (x_1 - 2)^2 + (x_2 - 1)^2$ s.t. $g = x_1 + x_2 - 2\le0$. The unconstrained minimum $(2, 1)$ violates $g$, so guess $g$ active.",
                    [num(r"$x_1^*$?", float(_kkt[x1]), ""), num(r"$\mu$?", float(_kkt[mu]), "",
                         explain="$2(x_1 - 2) + \\mu = 0$ and $2(x_2 - 1) + \\mu = 0$ give $x_1 - 2 = x_2 - 1$; with $x_1 + x_2 = 2$: $(1.5, 0.5)$, $\\mu = 1\\ge0$. Valid."),
                     choice("What would a negative μ have told you?", [opt("The constraint shouldn't be active: drop it from the active set and re-solve", True),
                                                                       opt("The problem is infeasible", why="A negative multiplier means the guessed active set is wrong."),
                                                                       opt("The point is a maximum", why="It signals a wrong active set, not a maximum."),
                                                                       opt("Nothing, since μ can have any sign", why="μ for inequalities must be ≥ 0.")])]),
            problem("c-kkt-2", "Spot the wrong condition",
                    r"A student lists the KKT conditions for $\min f$ s.t. $\mathbf{g}\le0$, $\mathbf{h} = 0$.",
                    [spot("Which line is wrong?", [
                        (r"$\nabla f + \nabla\mathbf{g}^T\boldsymbol\mu + \nabla\mathbf{h}^T\boldsymbol\lambda = \mathbf{0}$", False, ""),
                        (r"$\mathbf{h} = \mathbf{0}$, $\mathbf{g}\le\mathbf{0}$", False, ""),
                        (r"$\boldsymbol\mu\ge\mathbf{0}$ and $\boldsymbol\lambda\ge\mathbf{0}$", True, "Equality multipliers have no sign restriction: an equality can push either way."),
                        (r"$\boldsymbol\mu^T\mathbf{g} = 0$", False, ""),
                    ])]),
        ]),

    concept(
        "c-grg", "Generalized reduced gradient: step in the decision variables, update the states, pull back onto the constraints", 1, L9,
        r"""
GRG turns the reduced gradient into an algorithm:
1. **Move in decision space:** $\mathbf{x}_{d,k+1} = \mathbf{x}_{d,k} + \partial\mathbf{x}_{d,k}$, e.g. $-\alpha_k\nabla w_k$ (or Newton, quasi-Newton, with a line search or trust region).
2. **Move the states linearly:** $\hat{\mathbf{x}}_{s,k+1} = \mathbf{x}_{s,k} - (\nabla_{x_s}\mathbf{h})_k^{-1}(\nabla_{x_d}\mathbf{h})_k\partial\mathbf{x}_{d,k}$.
3. **Correct with Newton–Raphson:** the linear update generally leaves $\mathbf{h}\ne\mathbf{0}$, so iterate $\mathbf{x}_s\leftarrow\mathbf{x}_s - (\nabla_{x_s}\mathbf{h})^{-1}\mathbf{h}$ until the constraints hold ([[p-newton-raphson]]).

Every iterate is feasible, which is valuable when the analysis model can't run at infeasible designs. (Excel's Solver uses a GRG method.)
""",
        deeper=["c-reduced-gradient", "p-newton-raphson"],
        math=[r"[\mathbf{x}_s]_{i+1} = [\mathbf{x}_s]_i - \big[(\nabla_{x_s}\mathbf{h})^{-1}\mathbf{h}\big]_i"],
        analogy=analogy("Steering the car (decision variables), letting the trailer swing along (linear state update), then nudging the trailer back into its lane (Newton correction).",
                        "the correction can fail to converge for big steps on highly curved constraints, and the algorithm must then shorten the step."),
        exam="Name the three stages explicitly in any GRG answer: decision step, linear state update, Newton–Raphson restoration.",
        source="Lecture 9 (combined slides 233–235)",
        problems=[
            problem("c-grg-1", "Order a GRG iteration",
                    r"One iteration of generalized reduced gradient.",
                    [order("Put the steps in order.", [
                        "Compute the reduced gradient ∇w at the current point",
                        "Step the decision variables, e.g. along −∇w",
                        "Update the state variables with the linearized constraints",
                        "Apply Newton–Raphson to restore h(x) = 0",
                    ])]),
        ]),

    concept(
        "c-active-set", "Active-set strategy: guess which inequalities bind, solve, then add or drop one at a time", 1, L9,
        r"""
Treat a **working set** of inequalities as equalities and solve that easier problem (usually just for a KKT point). Then:
- if the solution satisfies every constraint outside the working set **and** every multiplier is non-negative: done;
- if it **violates** an outside constraint, add the most violated one to the working set;
- if nothing is violated but some multiplier is **negative**, remove the constraint with the most negative multiplier.

Change one constraint at a time and repeat. This is how many SQP codes decide which inequalities to linearize as equalities ([[c-sqp]]).
""",
        deeper=["c-kkt", "c-relaxation"],
        math=[],
        analogy=analogy("Guessing which walls of a room you'll end up leaning on: if you pass through a wall you ignored, start respecting it; if a wall you're leaning on is 'pulling' you (negative push), stop leaning on it.",
                        "with many constraints the add/drop sequence can be long, and cycling is possible without safeguards."),
        exam="Trace the working set in a table (iterate, working set, KKT?, constraint values, multiplier signs), as in the lecture's example.",
        source="Lecture 9 (combined slides 236–238)",
        problems=[
            problem("c-as-1", "Next move",
                    r"Solving with working set $\{g_1, g_2\}$ gives a point satisfying all other constraints, with $\mu_1 = 0.7$ and $\mu_2 = -0.4$.",
                    [choice("What does the active-set strategy do next?", [opt("Remove $g_2$ from the working set and re-solve", True), opt("Stop: the point is optimal", why="A negative multiplier means the point isn't a valid KKT point."),
                                                                           opt("Remove $g_1$", why="$\\mu_1 > 0$ is fine; drop the one with the negative multiplier."),
                                                                           opt("Add another constraint", why="Nothing is violated; the issue is the negative multiplier.")])]),
        ]),

    concept(
        "c-penalty-barrier", "Penalty and barrier methods: replace constraints by a cost, and tighten it over a sequence", 1, L9,
        r"""
Turn $\min f$ s.t. $\mathbf{g}\le\mathbf{0}$ into a **sequence of unconstrained problems** $\min T(\mathbf{x}, r_k)$ with $r_k\to0$:

- **Barrier (interior-point):** $T = f + rB(\mathbf{x})$ with $B = -\sum_j 1/g_j(\mathbf{x})$, which is positive inside and $\to\infty$ at the boundary. Iterates stay **feasible** and approach the boundary from inside.
- **Penalty (exterior):** $T = f + \tfrac1r P(\mathbf{x})$ with $P = \sum_j\max\{0, g_j\}^2$, zero when feasible. Iterates are typically slightly **infeasible** and approach from outside.

As $r_k\to0$ the minimizers $\mathbf{x}_k^*\to\mathbf{x}^*$, but $T$ becomes ever more steep near the boundary, making the subproblems **ill-conditioned** ([[c-scaling]]). Augmented Lagrangian methods fix that ([[c-augmented-lagrangian]]).
""",
        deeper=["c-unconstrained-why", "c-feasibility"],
        math=[r"T_{barrier} = f - r\sum_j\frac{1}{g_j},\qquad T_{penalty} = f + \frac1r\sum_j\max\{0, g_j\}^2"],
        analogy=analogy("A barrier is an electric fence inside the boundary: you're repelled before you ever reach the line. A penalty is a fine you pay for crossing it, growing steeper each time.",
                        "the fence and fine distort the landscape near the boundary, making the subproblems hard to solve precisely as they matter most."),
        exam="State which side the iterates approach from (barrier: inside, feasible; penalty: outside, infeasible). It's the classic comparison question.",
        widget={"type": "penalty"},
        source="Lecture 9 (combined slides 239–244)",
        problems=[
            problem("c-pb-1", "Exterior penalty in 1-D",
                    r"$\min x^2$ s.t. $g = 1 - x\le0$ ($x\ge1$). Penalty: $T = x^2 + \tfrac1r\max\{0, 1-x\}^2$. For $x < 1$, $dT/dx = 0$ gives $x = 1/(1 + r)$.",
                    [num(r"$x_k^*$ for $r = 0.1$?", _x_pen, ""),
                     choice("This iterate is…", [opt("slightly infeasible (below 1), approaching from outside", True), opt("feasible", why="$0.909 < 1$ violates $x\\ge1$."),
                                                 opt("exactly optimal", why="It only reaches $x^* = 1$ as $r\\to0$."), opt("approaching from inside", why="That's barrier behaviour.")])]),
            problem("c-pb-2", "Interior barrier in 1-D",
                    r"Same problem with a barrier: $T = x^2 + r\cdot\dfrac{1}{x - 1}$ for $x > 1$, $r = 0.1$. Then $dT/dx = 2x - \dfrac{r}{(x-1)^2} = 0$.",
                    [num(r"$x_k^*$ (to 3 decimals)?", _x_bar, "", tol=0.002, explain=f"Solving $2x(x-1)^2 = 0.1$ numerically gives $x\\approx{_x_bar:.3f}$: feasible, approaching 1 from inside.")]),
        ]),

    concept(
        "c-augmented-lagrangian", "Augmented Lagrangian: add multiplier estimates so the penalty needn't blow up", 1, L9,
        r"""
Combine the Lagrangian with a penalty:
$$T(\mathbf{x}, r, \boldsymbol\mu) = f(\mathbf{x}) + \boldsymbol\mu^T\mathbf{g}(\mathbf{x}) + \frac1r P(\mathbf{x}),$$
and after each subproblem update the multiplier estimates, $[\mu_j]_{k+1} = [\mu_j]_k + \dfrac2{r_k}g_j(\mathbf{x}_k)$. The multiplier term does the work that a vanishing $r$ would otherwise have to do, so $r$ needn't go to zero, and the subproblems stay **well-conditioned** close to the constraint boundary. Also called **multiplier methods**.
""",
        deeper=["c-penalty-barrier", "c-kkt"],
        math=[r"T = f + \boldsymbol\mu^T\mathbf{g} + \tfrac1r P,\qquad \mu_{k+1} = \mu_k + \frac{2}{r_k}g(\mathbf{x}_k)"],
        analogy=analogy("Instead of making the fine for crossing the line ever more brutal, you learn the 'fair price' of the constraint (μ) and charge that, so a modest fine suffices.",
                        "if the multiplier estimates are poor at first, it behaves like a plain penalty method for a few rounds before settling."),
        exam="Show one multiplier update with numbers; it's the step that distinguishes this method from a plain penalty.",
        source="Lecture 9 (combined slides 245–246)",
        problems=[
            problem("c-al-1", "One multiplier update",
                    r"$\mu_0 = 0$, $r_0 = 0.5$, and the subproblem's minimizer has $g(\mathbf{x}_0) = 0.2$ (slightly violated).",
                    [num(r"$\mu_1$?", 0 + (2 / 0.5) * 0.2, "", explain="$0 + (2/0.5)(0.2) = 0.8$: the violation raises the price of the constraint.")]),
        ]),

    concept(
        "c-sqp", "SQP is Newton's method on the KKT conditions, posed as a sequence of quadratic programs", 1, L9,
        r"""
For $\min f$ s.t. $\mathbf{h} = \mathbf{0}$ (active inequalities included via an active-set strategy), the FONC is $\nabla_y L = \mathbf{0}$ with $\mathbf{y} = (\mathbf{x}, \boldsymbol\lambda)$. Newton–Raphson on it gives the **Lagrange–Newton equations**, with $\mathbf{W} = \nabla^2_x L$ and $\mathbf{A} = \nabla\mathbf{h}$:
$$\begin{bmatrix}\mathbf{W}_k & \mathbf{A}_k^T\\ \mathbf{A}_k & \mathbf{0}\end{bmatrix}\begin{bmatrix}\partial\mathbf{x}_k\\ \boldsymbol\lambda_{k+1}\end{bmatrix} = \begin{bmatrix}-\nabla f_k\\ -\mathbf{h}_k\end{bmatrix}.$$
These are exactly the KKT conditions of a **quadratic program**: minimize $\tfrac12\partial\mathbf{x}^T\mathbf{W}_k\partial\mathbf{x} + \nabla L_k^T\partial\mathbf{x}$ subject to the linearized constraints $\mathbf{A}_k\partial\mathbf{x} + \mathbf{h}_k = \mathbf{0}$. So solving a **sequence of QPs** is Newton's method for the constrained problem. It needs regularity (full-rank $\mathbf{A}$) and a positive definite $\mathbf{W}$; practical codes use a BFGS-type approximation of $\mathbf{W}$. SciPy's `SLSQP` is a sequential least-squares quadratic programming method ([[lib-minimize]]).
""",
        deeper=["c-newton", "c-kkt", "c-active-set", "p-newton-raphson"],
        math=[r"\begin{bmatrix}\mathbf{W} & \mathbf{A}^T\\ \mathbf{A} & \mathbf{0}\end{bmatrix}\begin{bmatrix}\partial\mathbf{x}\\ \boldsymbol\lambda_{k+1}\end{bmatrix} = -\begin{bmatrix}\nabla f\\ \mathbf{h}\end{bmatrix}"],
        analogy=analogy("At each step, replace the curvy, walled landscape with the best quadratic bowl and straight walls that match it locally, solve that easy problem exactly, move, and redraw.",
                        "the local model can be poor far from the solution, so practical SQP adds a line search or trust region (and a merit function) to stay robust."),
        exam="If asked why SQP converges fast, answer: it's Newton's method on the KKT system, so it converges quadratically near a regular solution, or superlinearly with quasi-Newton W.",
        source="Lecture 9 (combined slides 247–253)",
        problems=[
            problem("c-sqp-1", "Order the SQP loop",
                    r"The SQP algorithm principle.",
                    [order("Put the steps in order.", [
                        "Choose an initial design x₀ (and multiplier estimates)",
                        "Build the QP: quadratic model of L, linearized constraints",
                        "Solve the QP for the step and new multipliers",
                        "Check termination",
                        "Update xₖ₊₁ and repeat",
                    ])]),
            problem("c-sqp-2", "What SLSQP is",
                    r"You call `minimize(..., method='SLSQP')`.",
                    [choice("What algorithm family is that?", [opt("Sequential quadratic programming (a quasi-Newton SQP)", True), opt("Simplex for linear programs", why="That's `linprog`."),
                                                               opt("A penalty method", why="SLSQP solves QP subproblems with linearized constraints."), opt("Pure steepest descent", why="It uses a quasi-Newton model of the Lagrangian's curvature.")])]),
        ]),

    concept(
        "c-convergence-termination", "Convergence, termination and honest reporting", 1, L9,
        r"""
- **Initial guesses matter:** gradient methods converge to *a* local optimum depending on $\mathbf{x}_0$. Use several starts, perhaps from a DOE (**multi-start**).
- **Global convergence** means converging to *some* local minimizer from *any* start; **local convergence rate** is how fast near it: *linear* $\|\mathbf{x}_{k+1} - \mathbf{x}^*\|\le c\|\mathbf{x}_k - \mathbf{x}^*\|$ ($0<c<1$), *superlinear* (with $c_k\to0$), *quadratic* $\le c\|\mathbf{x}_k - \mathbf{x}^*\|^2$.
- **Termination** is not convergence. The true criterion is $\|\nabla L\|\le\epsilon$; codes also stop on small $|f_{k+1} - f_k|$, small $\|\mathbf{x}_{k+1} - \mathbf{x}_k\|$, or iteration limits, so $\epsilon$ affects results. Feasibility is also only to a tolerance.

**A good report includes:** initial guess(es), tolerances and any finite-difference settings, iterations and function evaluations, active constraints with their multipliers, parametric studies on active bounds, and any multiple local optima found.
""",
        deeper=["c-topography", "c-kkt"],
        math=[r"\text{linear: } e_{k+1}\le c\,e_k,\qquad \text{quadratic: } e_{k+1}\le c\,e_k^2"],
        analogy=analogy("Linear convergence gains a fixed number of correct digits per step; quadratic convergence *doubles* the number of correct digits per step.",
                        "rates describe behaviour near the solution. Far away, a 'quadratic' method can be slower than a robust linear one."),
        exam="Check `res.success` and `res.message`, and report `nit`/`nfev` and the constraint values at the solution. Never report `res.x` alone ([[e-ignore-success]]).",
        source="Lecture 9 (combined slides 254–257)",
        problems=[
            problem("c-conv-1", "Identify the rate",
                    r"Errors $\|\mathbf{x}_k - \mathbf{x}^*\|$: $10^{-1}, 10^{-2}, 10^{-4}, 10^{-8}$.",
                    [choice("The rate is…", [opt("quadratic: each error is about the square of the previous", True), opt("linear", why="Linear would shrink by a constant factor each step (like $10^{-1}, 10^{-2}, 10^{-3}$)."),
                                             opt("sublinear", why="It's accelerating, not slowing."), opt("superlinear but not quadratic", why="$e_{k+1} = e_k^2$ exactly matches the quadratic definition.")])]),
            problem("c-conv-2", "Reporting checklist",
                    r"You've solved a constrained design problem.",
                    [spot("Which item does NOT belong in a good results report?", [
                        ("Initial guess(es) and tolerance settings", False, ""),
                        ("Number of iterations / function evaluations", False, ""),
                        ("Active constraints and their Lagrange multipliers", False, ""),
                        ("Only the final x*, since the rest is implementation detail", True, "Without starts, tolerances, active set and multipliers, nobody can judge or reproduce the result."),
                    ])]),
        ]),
]
