"""Layer 2: exam-style questions that need several MECH 559 ideas at once."""
import math
import sympy as sp
from lib import *

Q = "Questions that join the ideas"

CONCEPTS = [
    concept(
        "q-active-means-tradeoff", "Why is a single-objective problem with an active constraint secretly multi-objective?", 2, Q,
        r"""
An active constraint is the optimum's limiting factor: by the activity theorem, removing it would improve the objective ([[c-relaxation]]). So the objective *wants* to violate it, which means the two are in competition, the definition of a trade-off ([[c-pareto]]). The bound you picked ($\sigma_y$, $W_{max}$) chose one point on that trade-off.

So the honest answer to 'what's the optimum?' is a **curve**, traced by a parametric study on each active bound. The multiplier tells you the local slope of that curve, $\partial f^*/\partial b$ ([[c-lagrangian-equality]], [[c-kkt]]).
""",
        deeper=["c-pareto", "c-relaxation", "c-constraint-activity", "c-kkt"],
        analogy=analogy("A budget that you always spend in full: the 'best' purchase is really a statement about the budget, and a bigger budget would buy a better one.",
                        "if several constraints are active, the trade-off is a surface, not a curve, and a full parametric study becomes expensive."),
        exam="Pair every 'active' label in your results with one sentence on what relaxing that bound would buy (sign and size of its multiplier).",
        problems=[
            problem("q-amt-1", "Read a multiplier as a slope",
                    r"At the optimum, the stress constraint $\sigma_{max} - \sigma_y\le0$ is active with multiplier $\mu = 0.02$ kg/MPa.",
                    [choice("Raising $\\sigma_y$ by 10 MPa changes the optimal mass by about…", [opt("$-0.2$ kg", True), opt("$+0.2$ kg", why="Loosening an active $\\le$ constraint lowers the optimal cost: $\\Delta f^*\\approx-\\mu\\,\\Delta b$."),
                                                                                                   opt("0, because multipliers don't predict changes", why="That's exactly what they predict, to first order."),
                                                                                                   opt("$-2$ kg", why="$0.02\\times10 = 0.2$.")])]),
        ]),

    concept(
        "q-monotonicity-vs-kkt", "Monotonicity analysis predicts the active set; KKT multipliers confirm it", 2, Q,
        r"""
Two views of the same fact:
- **Monotonicity** ([[c-monotonicity]]): if the objective increases in $x_i$ and only one constraint decreases in $x_i$, that constraint must be active, decided before any solving.
- **KKT** ([[c-kkt]]): at the solution, active constraints carry $\mu_j > 0$, inactive ones $\mu_j = 0$.

So they must agree: every constraint monotonicity flags as 'must be active' should have a positive multiplier in the solver's output. If the solver reports it inactive, either your monotonicity table has a sign error or the solver stopped somewhere wrong. It's a powerful cross-check for an exam or a report.
""",
        deeper=["c-monotonicity", "c-kkt", "c-convergence-termination"],
        analogy=analogy("Predicting which beams in a structure will carry load from the drawing, then checking the strain gauges: the two must agree, or something is wrong.",
                        "monotonicity is a sufficient tool for finding *some* active constraints, not all. A constraint can be active even when the table doesn't force it."),
        exam="Put the monotonicity prediction and the solver's active set side by side in your answer.",
        problems=[
            problem("q-mk-1", "A disagreement",
                    r"Monotonicity says $g_2$ must be active, but SLSQP returns $g_2(\mathbf{x}^*) = -0.3$ with `success=True`.",
                    [choice("Most likely explanation?", [opt("A sign error in the table, or in how $g_2$ was passed to SciPy (`ineq` means ≥ 0)", True),
                                                         opt("Monotonicity analysis is unreliable", why="When it forces a constraint active, it's a theorem; check your work first."),
                                                         opt("$g_2$ is active with a negative multiplier", why="A constraint with $g_2 = -0.3$ isn't active at all."),
                                                         opt("The tolerance is too tight", why="$-0.3$ is far from zero; tolerances don't explain it.")])]),
        ]),

    concept(
        "q-knob-by-cv", "Why must every complexity knob be chosen by cross-validation, never training error?", 2, Q,
        r"""
Every surrogate family has a knob that adds flexibility: degree, ridge $\lambda$, RBF spread, network width, Kriging $\theta$ ([[c-surrogate-choice]]). Training error measures fit to the very points the model saw. More flexibility can always fit those points better, so training error keeps falling right through the overfitting regime ([[c-model-assessment]]). Cross-validation scores each candidate on points it *didn't* see, which estimates the generalization error and exposes both under- and overfitting: a U-shaped curve whose minimum is the knob value to pick.

Then judge the chosen model once on a separate **test set**. Using the test set to pick the knob would quietly turn it into training data.
""",
        deeper=["c-model-assessment", "c-surrogate-choice", "c-conditioning-ridge", "c-rbf"],
        analogy=analogy("Choosing a student's revision strategy by their score on questions they've already seen is guaranteed to favour memorization; you need fresh questions (CV), and a final exam (test set) used only once.",
                        "CV is noisy with small data. Two knob values with similar CV error are effectively tied, and the simpler one is usually wiser."),
        exam="Show the CV curve (error vs knob, log axis for λ or spread) and mark the minimum; quote test error only for the final choice.",
        problems=[
            problem("q-kcv-1", "Read the curves",
                    r"As polynomial degree rises from 1 to 10, training RMSE falls steadily; 5-fold CV RMSE falls until degree 4, then rises.",
                    [num("Which degree should you pick?", 4, ""),
                     choice("Why not degree 10?", [opt("It overfits: lowest training error but worse on unseen data", True), opt("It underfits", why="Underfitting shows high error on both curves."),
                                                   opt("It's ill-conditioned, so it can't be fitted", why="Conditioning may be poor, but the CV curve is the evidence here."),
                                                   opt("No reason: lower training error is better", why="Training error can't detect overfitting.")])]),
        ]),

    concept(
        "q-conditioning-everywhere", "Ill-conditioning keeps returning: least squares, Kriging, Newton steps and penalties", 2, Q,
        r"""
The same disease, four hosts:
- **Least squares:** nearly collinear or badly scaled columns make $\kappa(\mathbf{Z}^T\mathbf{Z})$ huge ([[c-conditioning-ridge]]).
- **Kriging:** a long correlation length (small θ) or near-duplicate points make $\mathbf{R}$ nearly singular ([[c-kriging]]).
- **Unconstrained algorithms:** a stretched Hessian makes gradient descent zigzag ([[c-scaling]]).
- **Penalty methods:** as $r\to0$ the penalized objective's Hessian blows up near the boundary ([[c-penalty-barrier]]).

And the same family of cures: **rescale** (min–max, diagonal scaling, normalized constraints), **regularize** (ridge $\lambda\mathbf{I}$, Kriging nugget $\epsilon\mathbf{I}$, the Hessian shift $\mu\mathbf{I}$), or **reformulate** (augmented Lagrangian instead of a pure penalty). Each adds something to the diagonal or evens out the axes.
""",
        deeper=["c-conditioning-ridge", "c-kriging", "c-scaling", "c-penalty-barrier", "c-variable-scaling"],
        analogy=analogy("A long, thin, wobbly ladder: every cure either shortens it (scaling) or bolts a brace across it (adding to the diagonal).",
                        "bracing (regularization) changes the problem slightly: ridge biases the coefficients, and a nugget makes Kriging stop interpolating exactly."),
        exam="When you mention a conditioning fix, name the matrix, quote κ before and after, and name the cost of the fix (bias, loss of exact interpolation).",
        problems=[
            problem("q-ce-1", "Same move, different names",
                    r"Ridge's $\lambda\mathbf{I}$, Kriging's nugget $\epsilon\mathbf{I}$ and the stabilized Newton $\mathbf{H} + \mu\mathbf{I}$ all…",
                    [choice("…do what to the matrix's eigenvalues?", [opt("raise every eigenvalue by the added amount, shrinking κ", True), opt("set the small eigenvalues to zero", why="They raise them, away from zero."),
                                                                      opt("multiply every eigenvalue by the added amount", why="Adding $c\\mathbf{I}$ shifts eigenvalues by $c$; it doesn't scale them."),
                                                                      opt("leave them unchanged but rotate the eigenvectors", why="The eigenvectors are unchanged; the eigenvalues shift.")])]),
        ]),

    concept(
        "q-newton-vs-gradient", "Why does Newton finish a quadratic in one step while gradient descent zigzags?", 2, Q,
        r"""
Gradient descent uses only the slope, so on an elongated bowl the steepest direction points across the valley more than along it. Each exact line search ends where the new gradient is perpendicular to the old step, so the path zigzags, and more severely the larger $\kappa(\mathbf{H})$ ([[c-descent]], [[c-exact-line-search]], [[c-scaling]]).

Newton's method uses the curvature too. Its model $f_k + \nabla f_k^T\mathbf{d} + \tfrac12\mathbf{d}^T\mathbf{H}\mathbf{d}$ *is* the function when $f$ is quadratic, so the model's minimizer is the true minimizer ([[c-newton]]). In effect, $\mathbf{H}^{-1}$ undoes the stretching. BFGS learns $\mathbf{H}$ gradually, and conjugate gradients finish in $n$ steps by never undoing earlier progress: both sit between the two extremes.
""",
        deeper=["c-newton", "c-descent", "c-exact-line-search", "c-quasi-newton", "c-conjugate-gradients", "c-scaling"],
        analogy=analogy("Gradient descent is a hiker who only feels the slope underfoot; Newton has a contour map of the whole bowl and walks straight to the bottom.",
                        "the map is only exact for a perfect bowl. On real terrain Newton's map is local, and without safeguards it can lead uphill."),
        exam="Back the zigzag claim with κ(H), and the one-step claim with 'the quadratic model is exact for a quadratic'.",
        widget={"type": "descent"},
        problems=[
            problem("q-nvg-1", "Count the steps",
                    r"Minimize $f = 4x_1^2 + 3x_1x_2 + x_2^2$ from $(1, 1)$.",
                    [num("Newton steps to reach the minimizer exactly?", 1, ""), num("Conjugate-gradient steps (exact arithmetic), at most?", 2, ""),
                     choice("Gradient descent with exact line search…", [opt("zigzags and converges only in the limit", True), opt("also takes exactly 1 step", why="Only if the starting gradient happens to point straight at the minimum."),
                                                                          opt("takes exactly 2 steps", why="That's CG's guarantee, not steepest descent's."), opt("diverges", why="With exact line search it converges, just slowly.")])]),
        ]),

    concept(
        "q-lp-vertex-nlp", "Why does an LP optimum sit at a vertex, while an NLP optimum can sit anywhere?", 2, Q,
        r"""
In an LP, the objective's contours are parallel straight lines and the feasible region is a convex polytope. Sliding the contour line in the improving direction, the last feasible contact is a vertex, or an edge in a tie ([[c-lp-theory]]). Interior points can't be optimal, because a linear function has no interior minimum unless it's constant.

In an NLP, curved contours can touch a constraint **tangentially in the middle of a smooth boundary** (one active constraint, $-\nabla f\parallel\nabla g$), or the minimum can be **interior** (no active constraints, $\nabla f = 0$), or at a vertex (several active, $-\nabla f$ in their cone) ([[c-topography]], [[c-kkt]]). That's why simplex can hop between vertices, while NLP methods need gradients and curvature.
""",
        deeper=["c-lp-theory", "c-simplex", "c-topography", "c-kkt"],
        analogy=analogy("A flat ramp (linear objective) always rolls a ball into a corner of the box; a curved bowl can hold it in the middle or against a wall.",
                        "with a convex quadratic objective and linear constraints (a QP), the optimum can still be mid-edge, so even mildly nonlinear problems lose the vertex property."),
        exam="A sketch of contours on the feasible region answers 'interior, edge or vertex?' faster than algebra, and it shows understanding.",
        widget={"type": "lp"},
        problems=[
            problem("q-lpv-1", "Where can the optimum be?",
                    r"Minimize $(x_1 - 1)^2 + (x_2 - 1)^2$ over the square $0\le x_1, x_2\le3$.",
                    [choice("Where is the optimum?", [opt("Interior, at $(1, 1)$: no constraint is active", True), opt("At a vertex", why="The unconstrained minimum $(1, 1)$ is inside the square."),
                                                      opt("On an edge", why="It's interior."), opt("Undefined", why="The objective is a convex bowl with its minimum inside the square.")]),
                     choice("If the objective were linear, $x_1 + x_2$, it would be at…", [opt("the vertex $(0, 0)$", True), opt("the centre", why="Linear objectives aren't minimized in the interior."),
                                                                                          opt("anywhere on an edge", why="$x_1 + x_2$ isn't parallel to an edge of the square."), opt("$(3, 3)$", why="That maximizes it.")])]),
        ]),

    concept(
        "q-multiplier-two-courses", "The multiplier in MECH 559 and the constraint force in MECH 419: the same object?", 2, Q,
        r"""
Yes, in a precise sense. In MECH 419, keeping a pendulum on its circle required a force $\mathbf{R} = \lambda\nabla h$: the multiplier times the constraint gradient, normal to the allowed motion ([[p-lagrange-419]]). In MECH 559, at a constrained optimum, $-\nabla f = \lambda\nabla h$: the objective's 'force' is balanced by the constraint's push, again along the constraint gradient, normal to the feasible directions ([[c-tangent-normal]], [[c-lagrangian-equality]]).

Both come from the same move: only motions *along* the constraint are allowed, so whatever is left over must be absorbed by something *normal* to it. The multiplier measures how hard the constraint pushes, a force in dynamics and a price (sensitivity of $f^*$) in optimization. Inequality constraints add one twist: walls can only push, so $\mu\ge0$ ([[c-kkt]]).
""",
        deeper=["p-lagrange-419", "c-lagrangian-equality", "c-tangent-normal", "c-kkt"],
        analogy=analogy("A bead on a wire: in dynamics the wire pushes so the bead stays on it while moving; in optimization the wire pushes so the bead rests at the lowest point it can reach along it.",
                        "in dynamics the balance holds at every instant along a trajectory; in optimization only at the optimum. Away from it, nothing is balanced."),
        exam="Draw $-\\nabla f$, $\\nabla h$ and the tangent line at the optimum. That one sketch states the Lagrange condition and its physical meaning.",
        problems=[
            problem("q-mtc-1", "Normal, not tangent",
                    r"At a constrained optimum on $h(\mathbf{x}) = 0$.",
                    [choice("The vector $-\\nabla f$ points…", [opt("normal to the constraint (along $\\nabla h$), with the multiplier as its scale", True), opt("tangent to the constraint", why="Any tangent component would let $f$ decrease along the constraint."),
                                                               opt("in an arbitrary direction", why="Stationarity pins it to the normal space."), opt("to zero", why="Only if the constraint is irrelevant (λ = 0).")])]),
        ]),

    concept(
        "q-multistart", "Why does your optimizer give different answers from different starting points?", 2, Q,
        r"""
Gradient-based methods (BFGS, SLSQP, trust-constr) use only local information: they converge to a **local** optimum near where they start ([[c-topography]]). If the problem isn't convex ([[c-convexity]]), different starts can land in different valleys. Different answers aren't a bug; they're evidence of non-convexity.

What to do:
1. **Multi-start:** run from several starting points, ideally spread by a DOE such as an LHS ([[c-doe]]), and keep the best feasible result.
2. Report all the distinct local optima found ([[c-convergence-termination]]).
3. For a global search, consider methods like `differential_evolution` ([[lib-global]]), which need bounds and many more evaluations.
4. Check `res.success` for each run: some 'different answers' are failed runs ([[e-ignore-success]]).
""",
        deeper=["c-topography", "c-convexity", "c-doe", "c-convergence-termination"],
        analogy=analogy("Dropping marbles on a bumpy tray: each rolls into the nearest dip. To find the deepest dip, drop many marbles spread across the tray.",
                        "even many marbles can miss a narrow, deep dip. Multi-start improves the odds; it can't prove global optimality."),
        exam="State the number of starts, how they were chosen, and how many distinct optima appeared.",
        problems=[
            problem("q-ms-1", "Order the multi-start workflow",
                    r"A non-convex constrained design problem.",
                    [order("Put the steps in order.", [
                        "Generate starting points with a DOE (e.g. an LHS) inside the bounds",
                        "Run the local optimizer from each start",
                        "Discard runs where success is False or constraints are violated",
                        "Group the distinct optima and keep the best feasible one",
                        "Report all distinct optima found",
                    ])]),
        ]),
]
