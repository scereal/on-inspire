"""Layer 1, Lectures 1-3: introduction, problem formulation, basic concepts."""
import math
import sympy as sp
from lib import *

L1, L2, L3 = "Lecture 1 · Introduction", "Lecture 2 · Problem formulation", "Lecture 3 · Basic concepts"

# Beam numbers for the epsilon-constraint problem (not the homework's drone).
P_, Lb, b_, rho_, sy = 1000.0, 1.0, 0.05, 2700.0, 100e6
h_star = math.sqrt(6 * P_ * Lb / (b_ * sy))
W_star = rho_ * b_ * h_star * Lb

CONCEPTS = [
    concept(
        "c-functions-of-interest", "Functions of interest come from analysis models; we optimize them over independent variables", 1, L1,
        r"""
Designing a cantilever beam of width $b$ and height $h$ under a tip load $P$, three quantities matter: mass, peak stress and tip deflection. **Analysis models** compute them:
$$W = \rho bhL,\qquad \sigma_{max} = \frac{Mh/2}{I} = \frac{6PL}{bh^2},\qquad \delta_{tip} = \frac{4PL^3}{Ebh^3}.$$
Stress is a **dependent variable**: a function of others. $M = PL$ and $I = bh^3/12$ are **intermediate variables**, still dependent but expressible in the independent ones ($P, L, b, h$).

We optimize functions of interest *with respect to independent variables*. Never pick a dependent variable (like $\sigma_{max}$) as a design variable, or you'll be optimizing a quantity that is secretly tied to the others.
""",
        deeper=["p-gradient"],
        math=[r"W = \rho bhL,\quad \sigma_{max} = \frac{6PL}{bh^2},\quad \delta_{tip} = \frac{4PL^3}{Ebh^3}"],
        analogy=analogy("A recipe: the oven temperature and baking time are what you choose (independent); how brown the crust gets is a result (dependent).",
                        "in a recipe you can taste and adjust; in optimization, a dependent quantity can only change through the variables that drive it."),
        exam="Draw the dependency chain ($P, L, b, h \\to M, I \\to \\sigma$) before formulating; it shows which quantities may be design variables.",
        source="Lecture 1, slides 2–5",
        problems=[
            problem("c-foi-1", "Stress in the beam",
                    r"$P = 1000$ N, $L = 1$ m, $b = 0.05$ m, $h = 0.1$ m.",
                    [num(r"$\sigma_{max}$ in MPa?", 6 * P_ * Lb / (b_ * 0.1**2) / 1e6, "MPa"),
                     num("If $h$ is halved, by what factor does the stress grow?", 4, "", explain="$\\sigma\\propto 1/h^2$: halving $h$ quadruples it.")]),
            problem("c-foi-2", "Which kind of variable?",
                    r"In the beam model, consider $M = PL$ and $I = bh^3/12$.",
                    [choice("What are $M$ and $I$?", [opt("Intermediate (dependent) variables", True),
                                                       opt("Design variables", why="They're computed from $P, L, b, h$; choosing them independently would break those relations."),
                                                       opt("Parameters", why="Parameters are held fixed for a run; $M$ and $I$ change whenever $h$ does."),
                                                       opt("Constants", why="Constants are universal, like $\\pi$.")])]),
        ]),

    concept(
        "c-variables-parameters", "Variables are what the optimizer changes; parameters are fixed for one run, so x* depends on p", 1, L1,
        r"""
- **Design variables** $\mathbf{x}$: varied by the optimization algorithm.
- **Parameters** $\mathbf{p}$: could vary in general, but are held fixed for a particular run (load, material, allowable stress).
- **Constants**: universally fixed ($\pi$).

So the functions are written $f(\mathbf{x};\mathbf{p})$, and an optimal design is always tied to the parameter values it was found for: $\mathbf{x}^*(\mathbf{p})$. Change a parameter and the optimum moves. That's why good studies report how $\mathbf{x}^*$ changes as key parameters change: a **parametric study** ([[c-pareto]]).
""",
        deeper=["c-functions-of-interest"],
        math=[r"f(\mathbf{x};\mathbf{p}),\qquad \mathbf{x}^* = \mathbf{x}^*(\mathbf{p})"],
        analogy=analogy("Tuning a race car for one track: the setup (variables) is optimal for that track's corners (parameters). On a new track, the best setup changes.",
                        "a real team can re-tune between races; an optimization result says nothing about other tracks unless you rerun it."),
        exam="State which quantities are variables and which are parameters at the top of every formulation. Graders look for it.",
        source="Lecture 1, slides 3–5",
        problems=[
            problem("c-vp-1", "The semicolon",
                    r"The course writes functions as $f(\mathbf{x};\mathbf{p})$.",
                    [choice("What does the semicolon separate?", [opt("What the optimizer varies (before) from what is held fixed in this run (after)", True),
                                                                   opt("Inputs from outputs", why="Both $\\mathbf{x}$ and $\\mathbf{p}$ are inputs."),
                                                                   opt("Objective from constraints", why="That's not what the notation means."),
                                                                   opt("Continuous from integer variables", why="It's about what varies in a run, not variable type.")]),
                     choice("You re-run with a higher load $P$. What happens to $\\mathbf{x}^*$?",
                            [opt("It generally changes: $\\mathbf{x}^*$ is a function of $\\mathbf{p}$", True), opt("Nothing: the optimum is a property of the design", why="The optimum is tied to the parameters it was found for."),
                             opt("It scales by the same factor as $P$", why="It changes, but generally not proportionally."), opt("It becomes infeasible", why="Not necessarily; it simply moves.")])]),
        ]),

    concept(
        "c-pareto", "Competing objectives give a trade-off curve, traced one constrained optimization at a time", 1, L1,
        r"""
Mass and stress compete: a lighter beam is more highly stressed. To quantify the trade-off, turn one objective into a constraint with a bound and sweep the bound (the **ε-constraint method**):
$$\min_h W(h)\quad\text{s.t.}\quad \sigma_{max}(h)\le\sigma_y,\qquad \sigma_y = \text{many values}.$$
Each run gives one point $(W^*, \sigma_y)$; together they trace the **Pareto front**, the set of designs where you can't improve one objective without worsening the other.

Here the stress constraint is **always active**, because mass and stress pull in opposite directions in $h$. The lecture's bottom line: *every single-objective problem with an active inequality constraint is really a multi-objective problem*, and its solution is just one Pareto point. Always run a parametric study on active constraint bounds.
""",
        deeper=["c-variables-parameters"],
        math=[r"h^* = \sqrt{\frac{6PL}{b\,\sigma_y}},\qquad W^* = \rho\,b\,h^*L"],
        analogy=analogy("Buying a laptop: every machine on the Pareto front is either lighter or faster than every other one, never worse in both. Which you pick depends on what you value.",
                        "the front shows the options; it doesn't choose for you. That needs a preference (a weight or a bound), which is a decision, not math."),
        exam="When a constraint is active, say so explicitly and comment on what happens if its bound changes: that sentence earns the 'interpretation' marks.",
        widget={"type": "pareto"},
        source="Lecture 1, slides 6–11",
        problems=[
            problem("c-par-1", "One point on the front",
                    rf"Minimize $W = \rho bhL$ subject to $\sigma_{{max}} = 6PL/(bh^2)\le\sigma_y$, with $P = 1000$ N, $L = 1$ m, $b = 0.05$ m, $\rho = 2700$ kg/m³, $\sigma_y = 100$ MPa.",
                    [choice("Which constraint direction bounds $h$?", [opt("$h$ is bounded below: stress rises as $h$ shrinks", True),
                                                                        opt("$h$ is bounded above", why="Stress falls as $h$ grows; the constraint only stops $h$ getting too small."),
                                                                        opt("$h$ is unbounded", why="The stress constraint stops $h\\to0$."),
                                                                        opt("Both", why="Nothing stops $h$ growing, except that mass grows too.")]),
                     num(r"$h^*$ in mm?", h_star * 1000, "mm", explain="The stress constraint is active: $h^* = \\sqrt{6PL/(b\\sigma_y)}\\approx 34.6$ mm."),
                     num(r"$W^*$ in kg?", W_star, "kg"),
                     choice(r"If $\sigma_y$ is halved, $W^*$…", [opt("grows by a factor of $\\sqrt2$", True), opt("doubles", why="$h^*\\propto1/\\sqrt{\\sigma_y}$, and $W^*\\propto h^*$."),
                                                               opt("halves", why="A tighter stress limit forces a thicker, heavier beam."), opt("doesn't change", why="The constraint is active, so its bound moves the optimum.")])]),
            problem("c-par-2", "Find the false statement",
                    r"About the ε-constraint study above:",
                    [spot("Which statement is wrong?", [
                        ("Each value of $\\sigma_y$ gives one Pareto-optimal design.", False, ""),
                        ("The stress constraint is active at every one of those optima.", False, ""),
                        ("Because the problem has a single objective, its solution is the whole answer.", True, "With an active constraint, the solution is one point on a trade-off curve; the bound $\\sigma_y$ is itself a choice, so a parametric study is needed."),
                        ("Plotting $(W^*, \\sigma_y)$ for many bounds traces the Pareto front.", False, ""),
                    ])]),
        ]),

    concept(
        "c-models-and-classes", "Systems, models and the zoo of optimization problems", 1, L1,
        r"""
A **system** is a set of interacting components with a boundary that defines its inputs and outputs. **Models** represent it: physical prototypes, drawings, words, mathematics, and especially **computational models** that evaluate $\mathbf{y} = \mathbf{f}(\mathbf{x};\mathbf{p})$, from analytical formulas and spreadsheets to finite-element and CFD codes. They come physics-based or data-driven ([[c-surrogates-why]]), at varying fidelity. ("All models are wrong, but some are useful.")

**Mathematical programming** (numerical optimization) is classified by the functions and variables involved:

| Class | Objective / constraints | Variables |
|---|---|---|
| Linear programming (LP) | all linear | continuous |
| Quadratic programming (QP) | quadratic objective, linear constraints | continuous |
| Nonlinear programming (NLP) | any smooth nonlinear | continuous |
| Convex programming | convex objective, convex feasible set | continuous |
| Integer / combinatorial / mixed | any | some discrete |

The class decides the tool: `linprog` for LP ([[c-simplex]]), SQP-type methods for smooth NLP ([[c-sqp]]).
""",
        deeper=["c-functions-of-interest"],
        math=[],
        analogy=analogy("Problem classes are like soil types for a builder: identify the ground first, and the right foundation (algorithm) follows.",
                        "real problems blur categories; a mostly-linear problem with one nonlinear constraint is an NLP, and LP tools won't touch it."),
        exam="Name the problem class before choosing a solver, and justify it from the formulation's functions and variables.",
        source="Lecture 1, slides 13–17",
        problems=[
            problem("c-cls-1", "Name the class",
                    r"$\min_{\mathbf{x}}\ \tfrac12\mathbf{x}^T\mathbf{Q}\mathbf{x} + \mathbf{c}^T\mathbf{x}$ subject to $\mathbf{A}\mathbf{x}\le\mathbf{b}$, with $\mathbf{x}$ continuous.",
                    [choice("What class is it?", [opt("Quadratic programming", True), opt("Linear programming", why="The objective has a quadratic term."),
                                                  opt("Integer programming", why="The variables are continuous."), opt("Unconstrained", why="There are linear inequality constraints.")]),
                     choice("If two of the variables must be whole numbers, it becomes…", [opt("mixed-integer (mixed-variable) programming", True), opt("still QP", why="Integer restrictions change the class and the algorithms."),
                                                                                           opt("LP", why="Integer variables make it combinatorial, not linear."), opt("convex programming", why="Integer feasible sets aren't convex.")])]),
        ]),

    concept(
        "c-analysis-to-synthesis", "From analysis to synthesis: turn the physics into an objective, constraints and bounds", 1, L2,
        r"""
The drive-screw example (Papalambros & Wilde) shows the workflow:

1. **Attributes** to care about: performance, durability, manufacturing, cost.
2. **Analysis models** that quantify them: bending stress $\sigma_{max} = 16F(L_1+L_2+L_3)/(\pi d_2^3)$, shear stress, cycle rate, a no-slip condition, volume.
3. **Synthesis**: choose design variables ($d_1, d_2, d_3, L_1, L_2, L_3, N_t, N_s$), choose a criterion (minimize volume × cost $c$), and turn every requirement into a constraint: allowable stresses, speed, no-slip.
4. **Bounds and extra restrictions** from manufacturing, packaging and model validity (e.g. $d_2 - d_1\ge d_{12,min}$, length ratios).

Model-validity constraints are easy to forget. An analysis formula is only trustworthy inside the range where its assumptions hold, and the optimizer will happily exploit the formula outside it.
""",
        deeper=["c-functions-of-interest", "c-variables-parameters"],
        math=[r"f = c\,\frac{\pi}{4}\big(d_1^2L_1 + d_2^2L_2 + d_3^2L_3\big)"],
        analogy=analogy("Writing a job ad from interviews: what people *need* (attributes) becomes measurable requirements (constraints), and the thing you'll rank candidates by becomes the objective.",
                        "a job ad can stay vague; an optimizer takes every word literally and exploits any loophole, like a missing validity bound."),
        exam="For each constraint, write one phrase saying which requirement it encodes. Unexplained constraints lose marks even when they're right.",
        source="Lecture 2, slides 3–10",
        problems=[
            problem("c-ats-1", "Order the workflow",
                    r"You're formulating a design optimization problem from scratch.",
                    [order("Put the steps in order.", [
                        "List the attributes that matter (performance, cost, …)",
                        "Write analysis models that quantify them",
                        "Choose design variables and the objective",
                        "Turn requirements into constraints",
                        "Add bounds and model-validity restrictions",
                    ])]),
            problem("c-ats-2", "The forgotten constraint",
                    r"An analysis formula for a part is only valid for slender geometry, $L/d\ge10$.",
                    [choice("What happens if you leave $L/d\\ge10$ out of the formulation?",
                            [opt("The optimizer may find a 'better' design where the model is no longer valid", True),
                             opt("Nothing: the physics enforces it automatically", why="The formula doesn't know its own limits; only a constraint does."),
                             opt("The problem becomes infeasible", why="Removing a constraint enlarges the feasible set."),
                             opt("The solver raises an error", why="Solvers have no idea which formulas are valid where.")])]),
        ]),

    concept(
        "c-negative-null-form", "Negative null form: every inequality as g(x) ≤ 0, every equality as h(x) = 0", 1, L2,
        r"""
The standard way to write a design problem:
$$\min_{\mathbf{x}}\ f(\mathbf{x};\mathbf{p})\quad\text{s.t.}\quad \mathbf{g}(\mathbf{x};\mathbf{p})\le\mathbf{0},\ \ \mathbf{h}(\mathbf{x};\mathbf{p}) = \mathbf{0},\ \ \mathbf{l}\le\mathbf{x}\le\mathbf{u}.$$
To convert: move everything to one side. $\sigma\le\sigma_{allow}$ becomes $g = \sigma - \sigma_{allow}\le0$; a requirement $T\ge W$ becomes $g = W - T\le0$ (careful with the direction).

**Normalize** whenever you can: $g = \sigma/\sigma_{allow} - 1\le0$ makes every constraint dimensionless and of order 1, which helps solvers and makes 'active' easy to read ($g\approx0$).

**SciPy uses the opposite sign.** `scipy.optimize.minimize` treats `{"type": "ineq", "fun": c}` as $c(\mathbf{x})\ge0$. So you pass `-g`. Getting this backwards is the most common bug in the course ([[e-ineq-sign]]).
""",
        deeper=["c-analysis-to-synthesis", "p-python-functions"],
        math=[r"\min_{\mathbf{x}} f(\mathbf{x})\ \text{ s.t. }\ \mathbf{g}(\mathbf{x})\le\mathbf{0},\ \mathbf{h}(\mathbf{x}) = \mathbf{0},\ \mathbf{l}\le\mathbf{x}\le\mathbf{u}", r"g = \frac{\sigma}{\sigma_{allow}} - 1\le0"],
        analogy=analogy("Like writing every bank transaction as a signed number: one convention for everything means no one has to remember which column is which.",
                        "two conventions are in play here: the course's $g\\le0$ and SciPy's $c\\ge0$. Translating between them is where the bugs live."),
        exam="Write the problem in negative null form even when the question doesn't ask; then translate to the solver's convention as a separate, labelled step.",
        source="Lecture 2, slides 11–12",
        problems=[
            problem("c-nnf-1", "Rewrite a requirement",
                    r"A requirement says $x_1x_2\ge4$.",
                    [expr(r"Write it in normalized negative null form, $g(\mathbf{x}) = 1 - (\ldots)\le0$. Type $g$.", 1 - x1 * x2 / 4, ["x1", "x2"],
                          ranges={"x1": [0.5, 3], "x2": [0.5, 3]}, explain="$x_1x_2\\ge4 \\iff 1 - x_1x_2/4\\le0$."),
                     blank(r"For `scipy.optimize.minimize`, complete the constraint: `{'type': 'ineq', 'fun': lambda x: ____}` (use `g(x)`).",
                           ["-g(x)", "-1*g(x)", "-(g(x))", "0-g(x)"], mode="code",
                           explain="SciPy's 'ineq' means `fun(x) >= 0`, so pass `-g(x)`.")]),
            problem("c-nnf-2", "Spot the sign error",
                    r"Requirement: a wing's lift $L(\mathbf{x})$ must be at least $n$ times the aircraft weight $W$ (load factor $n$).",
                    [spot("Which conversion is wrong?", [
                        (r"$L(\mathbf{x})\ge nW$", False, ""),
                        (r"$nW - L(\mathbf{x})\le0$", False, ""),
                        (r"$g = 1 - \dfrac{L(\mathbf{x})}{nW}\le0$", False, ""),
                        (r"$g = \dfrac{L(\mathbf{x})}{nW} - 1\le0$", True, "This says lift must be *at most* $nW$, the opposite requirement. Dividing $nW - L\le0$ by $nW>0$ gives $1 - L/(nW)\le0$."),
                    ])]),
        ]),

    concept(
        "c-boundedness", "A problem needs a well-bounded objective to have a solution at all", 1, L3,
        r"""
A problem is **well bounded** (well constrained) when the objective can't improve without limit over the feasible set. Two things can break it:

- the feasible set is **unbounded** in a direction along which $f$ keeps decreasing; or
- the best value is approached but **never attained**, because the set is open.

Russell's example: maximize $f(r) = 2\pi + 2/r$ over $0 < r < \infty$. As $r\to0^+$, $f\to\infty$, and $r = 0$ is excluded anyway: no maximizer exists. Boundedness can come from explicit bounds or implicitly from the other constraints. Monotonicity analysis checks it before you solve ([[c-monotonicity]]).
""",
        deeper=["p-sets-compactness"],
        math=[r"\inf_{\mathbf{x}\in\mathcal F} f(\mathbf{x})\ \text{ must be finite and attained}"],
        analogy=analogy("Asking for 'the largest number less than 1': you can always get closer, so there isn't one.",
                        "engineering problems rarely fail this obviously. The usual culprit is a variable you forgot to bound that the objective quietly drives to 0 or ∞."),
        exam="If a solver returns a variable at a huge or tiny value, suspect a missing bound before suspecting the solver.",
        source="Lecture 3, slides 4–7",
        problems=[
            problem("c-bnd-1", "Russell's problem",
                    r"Maximize $f(r) = 2\pi + 2/r$ for $0 < r < \infty$.",
                    [choice("Why is there no solution?", [opt("$f$ grows without limit as $r\\to0^+$, and $r = 0$ isn't allowed", True),
                                                           opt("$f$ isn't continuous anywhere", why="It's continuous on $(0, \\infty)$."),
                                                           opt("The maximum is at $r\\to\\infty$", why="As $r\\to\\infty$, $f\\to2\\pi$, its lowest values."),
                                                           opt("It has two maximizers", why="It has none.")])]),
            problem("c-bnd-2", "Diagnose a solver result",
                    r"Minimizing beam mass, a solver returns $h = 3\times10^{-9}$ m and $W\approx0$.",
                    [choice("Most likely cause?", [opt("The stress (or a bound on $h$) constraint is missing or wrongly signed, so nothing stops $h\\to0$", True),
                                                   opt("The solver's tolerance is too loose", why="Tolerances affect digits, not whether $h$ runs off to zero."),
                                                   opt("The objective is non-convex", why="Non-convexity gives local optima, not a run-away to the boundary."),
                                                   opt("Nothing is wrong: thin beams are lighter", why="An unbounded objective means a broken formulation.")])]),
        ]),

    concept(
        "c-feasibility", "The feasible set is the intersection of every constraint set", 1, L3,
        r"""
Each constraint defines a set, $\mathcal C_i = \{\mathbf{x}: g_i(\mathbf{x})\le0\}$. The **feasible set** is where all of them overlap: $\mathcal F = \bigcap_i\mathcal C_i$. The constraints are **consistent** iff $\mathcal F\ne\emptyset$.

A design is:
- **interior** if every constraint holds strictly ($g_i < 0$ for all $i$);
- **on the boundary** if at least one holds with equality ($g_i = 0$: active);
- **exterior** (infeasible) if at least one is violated ($g_i > 0$).
""",
        deeper=["c-negative-null-form"],
        math=[r"\mathcal F = \bigcap_i\{\mathbf{x}: g_i(\mathbf{x})\le0\}"],
        analogy=analogy("Each constraint is a stencil with a hole in it; stack all the stencils and the feasible set is wherever light still gets through.",
                        "stencils are flat; real feasible sets can be curved, disconnected, or empty (inconsistent constraints), and you may not see that until a solver fails."),
        exam="Classify a candidate point by evaluating every $g_i$ and listing their signs. It takes a line, and it's the first check of any reported optimum.",
        widget={"type": "feasible"},
        source="Lecture 3, slides 8–10",
        problems=[
            problem("c-feas-1", "Classify three designs",
                    r"$g_1(\mathbf{x}) = -x_1^2 + x_2\le0$ and $g_2(\mathbf{x}) = -x_1 - x_2 + 2\le0$ (Lecture 3's example).",
                    [choice(r"$\mathbf{x} = (2, 1)$ is…", [opt("interior", True), opt("on the boundary", why="$g_1 = -3 < 0$ and $g_2 = -1 < 0$: both strict."),
                                                         opt("exterior", why="Both constraints hold."), opt("undefined", why="Just evaluate both $g$'s.")]),
                     choice(r"$\mathbf{x} = (1, 1)$ is…", [opt("on the boundary, with both constraints active", True), opt("interior", why="$g_1 = 0$ and $g_2 = 0$: both active."),
                                                         opt("exterior", why="Neither constraint is violated."), opt("on the boundary, $g_1$ active only", why="$g_2 = -1 - 1 + 2 = 0$ too.")]),
                     choice(r"$\mathbf{x} = (0, 0)$ is…", [opt("exterior: $g_2 = 2 > 0$", True), opt("on the boundary: $g_1 = 0$", why="$g_1 = 0$, but $g_2 = 2$ is violated, which makes it infeasible."),
                                                         opt("interior", why="$g_2 > 0$ is a violation."), opt("feasible because one constraint holds", why="Feasibility needs *every* constraint.")])]),
        ]),

    concept(
        "c-relaxation", "Relaxation: drop a constraint, and the optimum can only improve or stay the same", 1, L3,
        r"""
Removing a constraint can only enlarge the feasible set ($\mathcal F\subset\mathcal F_{relaxed}$), so the relaxed optimum is at least as good: $f(\mathbf{x}^*_{relaxed})\le f(\mathbf{x}^*)$. Two theorems turn this into a test for activity (assuming unique global minimizers and monotonic functions):

- **Relaxation theorem:** if the relaxed minimizer *violates* the left-out constraint, that constraint is active in the original problem.
- **Activity theorem:** the left-out constraint is active **iff** $f(\mathbf{x}^*_{relaxed}) < f(\mathbf{x}^*)$.

Practical use: solve without a suspect constraint; if the answer breaks it, it must be active and you can treat it as an equality.
""",
        deeper=["c-feasibility"],
        math=[r"\mathcal F\subseteq\mathcal F_{relaxed}\ \Rightarrow\ f(\mathbf{x}^*_{relaxed})\le f(\mathbf{x}^*)"],
        analogy=analogy("Lifting a speed limit can only make your fastest trip faster or the same. If your new fastest trip breaks the old limit, the old limit was what slowed you down.",
                        "with multiple optima, or non-monotonic functions, the clean if-and-only-if version can fail; the lecture states it for unique minimizers."),
        exam="Use relaxation to *justify* activity in words: 'without $g_2$ the optimum violates it, so $g_2$ is active'. That's a complete argument.",
        source="Lecture 3, slides 11–12",
        problems=[
            problem("c-rel-1", "Read the relaxed solution",
                    r"Dropping constraint $g_3$ from a problem, the relaxed optimum has $g_3(\mathbf{x}^*_{relaxed}) = +0.4$.",
                    [choice("What can you conclude?", [opt("$g_3$ is active in the original problem", True), opt("$g_3$ is redundant", why="A redundant constraint could never be violated by the relaxed optimum."),
                                                       opt("The original problem is infeasible", why="It only says $g_3$ binds at the optimum."),
                                                       opt("Nothing", why="The relaxation theorem gives exactly this conclusion.")]),
                     choice(r"Compared with the original optimum, $f(\mathbf{x}^*_{relaxed})$ is…", [opt("strictly lower", True), opt("equal", why="Equality would mean $g_3$ wasn't active (activity theorem)."),
                                                                                                   opt("higher", why="A larger feasible set can't make the best value worse."), opt("unknown", why="It's lower, by the activity theorem.")])]),
        ]),

    concept(
        "c-constraint-activity", "A constraint is active if removing it changes the solution", 1, L3,
        r"""
Generally, an inequality constraint is **active** if its removal changes the solution (or the solvability) of the problem. At a smooth optimum this usually means $g_i(\mathbf{x}^*) = 0$: the constraint holds with equality.

Two examples show the difference:
- $\min x^2$ s.t. $x\ge a$: if $a > 0$, $x^* = a$ and the constraint is active; if $a\le0$, $x^* = 0$ and it's inactive.
- $\min x$ s.t. $x\ge a$: always active. Without it, the problem is unbounded.

Active constraints are what an optimum 'leans on'. They carry nonzero multipliers ([[c-kkt]]), and they are the bounds worth a parametric study ([[c-pareto]]).
""",
        deeper=["c-feasibility", "c-relaxation"],
        math=[r"g_i(\mathbf{x}^*) = 0\ \text{(active)},\qquad g_i(\mathbf{x}^*) < 0\ \text{(inactive)}"],
        analogy=analogy("A crowd pressed against a barrier: the barrier is active if moving it would let the crowd move. A barrier far behind everyone is inactive.",
                        "$g = 0$ is the usual sign but not the definition: a constraint can sit at $g = 0$ by coincidence and still not matter (a degenerate case)."),
        exam="In results, list each constraint with its value and 'active' or 'inactive', using a tolerance (e.g. $|g| < 10^{-4}$), as the course's notebooks do.",
        source="Lecture 1, slide 10; Lecture 3, slide 13",
        problems=[
            problem("c-act-1", "Active or not?",
                    r"$\min x^2$ subject to $x\ge a$.",
                    [num(r"$x^*$ when $a = 2$?", 2, ""), num(r"$x^*$ when $a = -1$?", 0, "", tol=0.001, explain="The unconstrained minimum $x = 0$ already satisfies $x\\ge-1$: the constraint is inactive.")]),
        ]),

    concept(
        "c-monotonicity", "Monotonicity analysis: every monotonic variable must be stopped by a constraint pulling the other way", 1, L3,
        r"""
$f$ is **monotonically increasing** in $x$, written $f(x^+)$, if increasing $x$ never decreases $f$; decreasing, $f(x^-)$, the reverse.

**Monotonicity Principle 1:** in a well-constrained problem, every variable that appears monotonically in the objective is bounded by at least one constraint with the **opposite** monotonicity in that variable. If the objective and all constraints share the same monotonicity in a variable, nothing stops it: the problem is not well constrained.

The payoff is that you can predict active constraints *before* solving. Build a table with a $+$, $-$ or blank for each function and variable. For each variable the objective wants to shrink (say $f(x_1^+)$), look down the column for constraints with $x_1^-$. If only one exists, it must be active.
""",
        deeper=["c-boundedness", "c-constraint-activity"],
        math=[r"f(x_1^+)\ \Rightarrow\ \exists\, g_j(x_1^-)\ \text{active}"],
        analogy=analogy("A tug of war: if the objective pulls a variable toward zero, some constraint must be pulling back, or the rope runs off the field.",
                        "it only works variable by variable for monotonic functions. Non-monotonic functions (with a bend) need more careful analysis."),
        exam="Draw the table neatly with a row per function and a column per variable, then write one sentence per variable naming the constraint that bounds it.",
        source="Lecture 3, slides 14–17",
        problems=[
            problem("c-mono-1", "Build the table",
                    r"$\min f = x_1 + x_2$ s.t. $g_1 = 4 - x_1x_2\le0$, $g_2 = x_1 - 3\le0$, with $x_1, x_2 > 0$.",
                    [choice(r"Monotonicity of $g_1$ in $x_1$ and in $x_2$?", [opt("decreasing in both: $g_1(x_1^-, x_2^-)$", True), opt("increasing in both", why="Larger $x_1$ (or $x_2$) makes $4 - x_1x_2$ smaller."),
                                                                             opt("decreasing in $x_1$, independent of $x_2$", why="$g_1$ depends on both."), opt("non-monotonic", why="For positive variables it's monotonic.")]),
                     choice(r"$f(x_1^+, x_2^+)$ wants both variables small. Which constraint bounds $x_2$ from below?",
                            [opt("$g_1$, the only constraint decreasing in $x_2$, so $g_1$ must be active", True), opt("$g_2$", why="$g_2$ doesn't involve $x_2$."),
                             opt("None: the problem is unbounded", why="$g_1$ has the opposite monotonicity in $x_2$, so it bounds it."), opt("Both", why="Only $g_1$ involves $x_2$.")]),
                     choice(r"Is $g_2$ ($x_1\le3$) needed to bound the objective?", [opt("No: it limits $x_1$ from above, but the objective wants $x_1$ small", True),
                                                                                   opt("Yes, it's the only bound on $x_1$", why="$f$ pushes $x_1$ down; $g_2$ only stops it going up."),
                                                                                   opt("Yes, it must be active", why="Here it has the same monotonicity as $f$ in $x_1$, so it can't be what bounds the optimum."),
                                                                                   opt("It makes the problem infeasible", why="It doesn't.")])]),
            problem("c-mono-2", "Order the analysis",
                    r"Monotonicity analysis before solving.",
                    [order("Put the steps in order.", [
                        "Write the problem in negative null form",
                        "Mark each function +, − or blank for each variable",
                        "For each variable, note which way the objective pushes it",
                        "Find constraints with the opposite monotonicity in that variable",
                        "If exactly one exists, declare it active; if none, add a bound",
                    ])]),
        ]),

    concept(
        "c-topography", "Interior or boundary, local or global: read the landscape before trusting an optimum", 1, L3,
        r"""
- An **interior optimum** has no active constraints: it's where the unconstrained minimum happens to be feasible.
- A **boundary optimum** has at least one active constraint; with several, it sits on their intersection.
- A **local** optimum beats its neighbours; a **global** one beats every feasible point. Gradient-based algorithms only guarantee local ones ([[c-convergence-termination]]).

How active constraints **interact** matters. With one active constraint, the objective's contour must be tangent to it: $-\nabla f\parallel\nabla g$. At a *vertex* of two or more, $-\nabla f$ just needs to lie in the **cone** spanned by the active constraints' gradients. That geometric statement is the KKT condition in disguise ([[c-kkt]]).
""",
        deeper=["c-constraint-activity", "p-gradient"],
        math=[r"-\nabla f(\mathbf{x}^*) = \sum_{i\in\mathcal A}\mu_i\nabla g_i(\mathbf{x}^*),\ \ \mu_i\ge0"],
        analogy=analogy("Hiking to the lowest point of a fenced park: if the lowest spot is in a hollow inside, the fence doesn't matter; if it's against the fence, the fence is what holds you there.",
                        "in fog you only know your neighbourhood. A local hollow can look like the lowest point when a deeper one lies across the park."),
        exam="State interior vs boundary and local vs global for every reported optimum, with the evidence (active set, convexity, multi-start).",
        widget={"type": "kkt"},
        source="Lecture 3, slides 18–22",
        problems=[
            problem("c-top-1", "When does the constraint bite?",
                    r"$\min (x_1-1)^2 + (x_2-1)^2$ s.t. $g = \dfrac{1}{a\,x_1x_2} - 1\le0$ (i.e. $x_1x_2\ge1/a$), $x > 0$.",
                    [num(r"Below what value of $a$ does the optimum move to the boundary?", 1, "",
                         explain="The unconstrained minimum $(1,1)$ is feasible iff $1\\ge1/a$, i.e. $a\\ge1$."),
                     num(r"For $a = 0.5$ the optimum is $x_1 = x_2 = \sqrt2$. What is $f^*$?", 2 * (math.sqrt(2) - 1)**2, "",
                         explain="$2(\\sqrt2 - 1)^2\\approx0.343$: by symmetry the closest point of $x_1x_2 = 2$ to $(1,1)$ has $x_1 = x_2$.")]),
            problem("c-top-2", "The cone at a vertex",
                    r"At a vertex $\mathbf{x}^*$, constraints $g_1$ and $g_2$ are both active.",
                    [choice("What must hold for $\\mathbf{x}^*$ to be optimal?", [opt("$-\\nabla f$ lies in the cone spanned by $\\nabla g_1$ and $\\nabla g_2$", True),
                                                                                 opt("$\\nabla f = 0$", why="That's for interior optima."),
                                                                                 opt("$-\\nabla f$ is parallel to $\\nabla g_1$", why="That's the single-constraint case; at a vertex the cone condition is enough."),
                                                                                 opt("$\\nabla g_1 = \\nabla g_2$", why="The constraint gradients just need to span a cone containing $-\\nabla f$.")])]),
        ]),
]
