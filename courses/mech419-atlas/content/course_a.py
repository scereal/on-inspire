"""Layer 1, Lectures 1-3: from coordinates to Lagrange's equations."""
import math
import sympy as sp
from lib import *

G = 9.81
L1, L2, L3 = "Lecture 1 · Coordinates and DOF", "Lecture 2 · Virtual work", "Lecture 3 · Lagrange's equations"

# The cart-pendulum is the course's running example (Lectures 2, 3, 9).
CP_T = (M + m) * xd**2 / 2 + m * l**2 * thd**2 / 2 + m * xd * l * thd * sp.cos(th)
CP_V = k * x**2 / 2 - m * g * l * sp.cos(th)
CP_X, CP_TH = lagrange(CP_T, CP_V, [(x, xd, xdd), (th, thd, thdd)])

CONCEPTS = [
    concept(
        "c-vector-vs-analytical", "Two roads to the same equations: forces on each body, or energy of the whole", 1, L1,
        r"""
Dynamics grew along two lines. The **vectorial** line (Newton 1687, D'Alembert 1743, Euler 1765) writes vector equations of motion: $\frac{d}{dt}(m\mathbf{v}) = \sum\mathbf{F}$ and $\frac{d\mathbf{H}}{dt} = \sum\mathbf{M}$ for each body. The **analytical** line (Lagrange 1788, Hamilton ~1830, Gibbs–Appell ~1900, Kane 1961) writes scalar equations from energies of the whole system.

| Vectorial | Analytical |
|---|---|
| Isolate each body, draw its FBD | Treat the whole system at once |
| Constraint and reaction forces must be included | Ideal internal constraint forces never appear |
| More unknowns (action/reaction pairs) | Fewer unknowns: one equation per DOF |
| Needs acceleration kinematics | Needs only velocity kinematics |
| Internal forces come out for free | Internal forces take extra work (multipliers) |

D'Alembert's bridge between them: move $m\mathbf{a}$ across as an 'inertia force', $\sum\mathbf{F} + (-m\mathbf{a}) = 0$, and dynamics looks like statics. Analytical mechanics then applies the statics tool of **virtual work** ([[c-virtual-disp]]) to that balance, and that is exactly where constraint forces drop out.
""",
        deeper=["p-newton", "p-work"],
        analogy=analogy("Vectorial is auditing every invoice; analytical is reading the balance sheet. The balance sheet is shorter and harder to get wrong.",
                        "if you need one specific internal transaction (the pin force, to size a bolt), the balance sheet hides it. Then you need multipliers or a separate FBD."),
        exam="Expect a 'which method and why' question. Answer with the table's trade-off that matters for *that* problem: unknowns, kinematics level, or whether an internal force is required.",
        source="Lecture 1, pp. 1–2",
        problems=[
            problem("c-vva-1", "Pick the tool",
                    "You need the force in the rod of a cart-pendulum to check whether it will buckle.",
                    [choice("Which approach gives that force most directly?",
                            [opt("Vectorial: the rod force appears on the FBDs and is solved for", True),
                             opt("Plain Lagrange with $x, \\theta$: it gives every force", why="Ideal constraint forces drop out of Lagrange's equations; you'd need extra work (multipliers) to recover them."),
                             opt("Hamilton's canonical equations", why="Those are still analytical: constraint forces still drop out."),
                             opt("Either: both list internal forces automatically", why="Only the vectorial approach computes internal forces as part of the solution.")])],
                    fig={"type": "cart-pendulum"}),
            problem("c-vva-2", "Which kinematics does each need?",
                    "Compare what you must compute before writing equations.",
                    [choice("Which approach needs only velocities, never accelerations, of the points?",
                            [opt("Analytical (Lagrange)", True),
                             opt("Vectorial (Newton–Euler)", why="Newton's law needs $\\mathbf{a}$ for every body."),
                             opt("Both need accelerations", why="Lagrange builds $T$ from velocities; differentiating $T$ produces the accelerations for you."),
                             opt("Neither: both work from positions only", why="$T$ needs velocities.")],
                            explain="Lagrange's $\\frac{d}{dt}(\\partial T/\\partial\\dot q)$ does the acceleration kinematics automatically.")]),
            problem("c-vva-3", "D'Alembert's inertia force",
                    "A 2 kg block accelerates to the right at 3 m/s².",
                    [choice("What inertia force makes it a statics problem?",
                            [opt("6 N to the left", True), opt("6 N to the right", why="The inertia force is $-m\\mathbf{a}$: opposite to the acceleration."),
                             opt("1.5 N to the left", why="$m a = 2\\times 3 = 6$ N."),
                             opt("Zero: inertia isn't a force", why="It's fictitious, but D'Alembert adds it precisely so that the sum of forces is zero.")])]),
        ]),

    concept(
        "c-gen-coords", "Generalized coordinates: any set of numbers that pins down where everything is", 1, L1,
        r"""
Cartesian $(x, y, z)$, cylindrical $(r, \theta, z)$ and spherical $(R, \theta, \phi)$ are all just choices. A **generalized coordinate** is any variable that, together with the others, fixes the configuration. It needn't be a length or an angle: the vibrating beam $w(x,t) = \sum_k a_k(t)\sin\frac{k\pi x}{\ell}$ uses the mode amplitudes $a_k(t)$.

**There's no unique choice.** For a pendulum you can use $\theta$, $x$, $y$, or even $\xi = |y|/x$: knowing any one at a given time gives the others. If you choose both $x$ and $y$, they're **not independent**, because $x^2 + y^2 = \ell^2$ ties them. Independent coordinates are what the basic Lagrange equations need; dependent ones need [[c-multipliers]].
""",
        deeper=["p-polar"],
        math=[r"w(x,t) = \sum_{k=1}^{N} a_k(t)\sin\frac{k\pi x}{\ell}", r"x^2 + y^2 = \ell^2 \ \text{(dependent!)}"],
        analogy=analogy("Directions to a friend's house: a street address, GPS coordinates, or 'third house past the church' all pin down the same spot. Pick whichever makes the conversation easiest.",
                        "some descriptions fail in places. Knowing only $x$ for a pendulum leaves $y = \\pm\\sqrt{\\ell^2 - x^2}$ ambiguous: it works only if the bob never rises above the pivot."),
        exam="Before writing anything, state your coordinates on the sketch with their zero and positive direction. Half the sign errors in Lagrange problems come from an unstated convention.",
        widget={"type": "dof"},
        source="Lecture 1, pp. 3–5",
        problems=[
            problem("c-gc-1", "A valid set for the dumbbell",
                    "Two particles joined by a massless rigid rod move in a plane (3 DOF).",
                    [choice("Which is a valid set of independent generalized coordinates?",
                            [opt(r"$(x_1, y_1, \theta)$", True),
                             opt(r"$(x_1, y_1, x_2, y_2)$", why="Four coordinates for 3 DOF: they're tied by $(x_2-x_1)^2 + (y_2-y_1)^2 = \\ell^2$."),
                             opt(r"$(x_1, y_1)$", why="That fixes particle 1 but not the rod's direction."),
                             opt(r"$(\theta)$", why="That fixes only the orientation, not where the rod is.")])],
                    fig={"type": "dumbbell"}),
            problem("c-gc-2", "Why mode amplitudes count",
                    r"For the beam, $w(x,t) = \sum a_k(t)\sin(k\pi x/\ell)$.",
                    [choice("Why are the $a_k(t)$ legitimate generalized coordinates?",
                            [opt("Once they're known, the displacement at every point of the beam is known", True),
                             opt("Because each one is a physical displacement you can measure with a ruler", why="They're amplitudes of shapes, not positions; generalized coordinates needn't be measurable lengths."),
                             opt("Because they are Cartesian coordinates of the beam", why="They're coefficients of a sum, not Cartesian coordinates."),
                             opt("They aren't: only lengths and angles qualify", why="Any set that fixes the configuration qualifies.")])]),
            problem("c-gc-3", "When one coordinate isn't enough information",
                    r"A pendulum of length 1 m. You're told only $x = 0.6$ m.",
                    [choice("What can you conclude about $y$?",
                            [opt(r"$y = \pm 0.8$ m: $x$ alone can't tell whether the bob is below or above the pivot", True),
                             opt(r"$y = -0.8$ m exactly", why="That assumes the bob is below; $x^2 + y^2 = 1$ allows $+0.8$ too."),
                             opt("$y$ can be anything", why="The constraint $x^2 + y^2 = \\ell^2$ fixes $|y|$."),
                             opt(r"$y = 0.4$ m", why="Use $x^2 + y^2 = \\ell^2$, not $x + y = \\ell$.")],
                            explain="That's why $\\theta$ is usually the better choice: it is single-valued around the whole circle.")],
                    fig={"type": "pendulum-xy"}),
        ]),

    concept(
        "c-dof", "Degrees of freedom = coordinates you'd need minus constraints that tie them", 1, L1,
        r"""
The number of DOF, $n$, is the number of **independent** generalized coordinates. Count it by giving each piece its free budget and subtracting one for every constraint:

- particle: 3 in space, 2 in a plane;
- rigid body: 6 in space, 3 in a plane.

$$n = 3N_P + 6N_R - C\quad\text{(3-D)},\qquad n = 2N_P + 3N_R - C\quad\text{(planar)}.$$

A pendulum in 3-D: one particle, two constraints ($z = 0$, $x^2 + y^2 = \ell^2$), so $n = 1$. A planar two-link robot: 2 rigid bodies (6) minus 4 constraints (pinned base point, two link-attachment conditions...), so $n = 2$.
""",
        deeper=["c-gen-coords"],
        math=[r"n = 3N - C", r"n = 3N_P + 6N_R - C,\qquad n = 2N_P + 3N_R - C"],
        analogy=analogy("Each part arrives with a freedom budget (3 for a particle in space, 6 for a rigid body). Every constraint is a tax that takes one freedom away.",
                        "redundant constraints (one implied by others) mustn't be taxed twice, and non-holonomic constraints restrict velocities without reducing this count."),
        exam="Show the count as 'budget − constraints = n' with each constraint written out. It's quick, it earns method marks, and it tells you how many Lagrange equations to expect.",
        source="Lecture 1 p. 4–5; Lecture 2 p. 1",
        problems=[
            problem("c-dof-1", "Two particles and a rod",
                    "Two particles joined by a massless rod, moving in the plane of the paper. Count in 3-D.",
                    [num("How many constraints?", 3, "", explain="$z_1 = 0$, $z_2 = 0$, and the fixed length: $C = 3$."),
                     num("How many DOF?", 3, "", explain="$n = 3(2) - 3 = 3$.")],
                    fig={"type": "dumbbell"}),
            problem("c-dof-2", "The cart-pendulum",
                    "A cart slides on a horizontal track (it can't lift or rotate); a pendulum bob (particle) hangs from it on a rigid rod. Planar.",
                    [num("Count the planar budget before constraints: cart (rigid body) + bob (particle).", 3 + 2, ""),
                     num("How many DOF?", 2, "", explain="Constraints: cart $y$ fixed, cart rotation fixed, rod length fixed: $5 - 3 = 2$ ($x$ and $\\theta$).",
                         hint="Three constraints: two on the cart, one for the rod.")],
                    fig={"type": "cart-pendulum"}),
            problem("c-dof-3", "Rolling disk",
                    "A disk rolls along a straight line in a vertical plane without slipping.",
                    [num("How many DOF?", 1, "", explain="Planar rigid body: 3. Centre height fixed: −1. No slip $x = r\\theta$: −1. $n = 1$.")],
                    fig={"type": "rolling-disk"}),
            problem("c-dof-4", "Double pendulum",
                    "Two particles hang in a chain on two rigid rods from a fixed pivot, moving in a plane.",
                    [num("How many DOF?", 2, "", explain="$2(2) - 2 = 2$: two rod lengths. Use $\\theta_1, \\theta_2$.")]),
        ]),

    concept(
        "c-r-of-q", "Write every position as a function of the coordinates; velocities follow automatically", 1, L2,
        r"""
Once coordinates $q_1, \ldots, q_n$ are chosen, every particle's position is a function of them (and maybe time): $\mathbf{r}_j = \mathbf{r}_j(q_1, \ldots, q_n, t)$. Differentiating with the chain rule ([[p-chain-multi]]) gives the velocity:

$$\dot{\mathbf{r}}_j = \sum_{i=1}^n\frac{\partial\mathbf{r}_j}{\partial q_i}\dot q_i + \frac{\partial\mathbf{r}_j}{\partial t}.$$

Each $\partial\mathbf{r}_j/\partial q_i$ is a direction: where the particle goes if only $q_i$ changes. The $\dot q_i$ are the **generalized velocities**. The last term exists only when the geometry is driven in time (a disk spun at a prescribed $\Omega$), and it's what later produces $T_1$ and $T_0$ ([[c-t2t1t0]]).
""",
        deeper=["c-gen-coords", "p-chain-multi", "p-partial"],
        math=[r"\mathbf{r}_2 = (x + \ell\sin\theta)\,\mathbf{i} - \ell\cos\theta\,\mathbf{j}",
              r"\dot{\mathbf{r}}_2 = (\dot x + \ell\dot\theta\cos\theta)\,\mathbf{i} + \ell\dot\theta\sin\theta\,\mathbf{j}"],
        analogy=analogy("A marionette: the strings (coordinates) fix every limb, and how fast a limb moves depends on how it's tied to each string ($\\partial\\mathbf{r}/\\partial q$).",
                        "if the puppeteer's stage itself moves (explicit $t$), the limbs move even with the strings held still. That's the $\\partial\\mathbf{r}/\\partial t$ term."),
        exam="Write $\\mathbf{r}_j$ for every mass and every point where a force acts. Everything else (velocities, $T$, generalized forces) is differentiation.",
        source="Lecture 2, pp. 2–3",
        problems=[
            problem("c-rq-1", "Position of the bob",
                    r"Cart at $x$ (origin at the unstretched spring position), pendulum angle $\theta$ from the downward vertical, $y$ up, pivot at height 0.",
                    [choice(r"What is $\mathbf{r}_2$, the bob's position?",
                            [opt(r"$(x + \ell\sin\theta)\,\mathbf{i} - \ell\cos\theta\,\mathbf{j}$", True),
                             opt(r"$(x + \ell\cos\theta)\,\mathbf{i} - \ell\sin\theta\,\mathbf{j}$", why="$\\theta$ is from the vertical: the horizontal offset is $\\ell\\sin\\theta$."),
                             opt(r"$\ell\sin\theta\,\mathbf{i} - \ell\cos\theta\,\mathbf{j}$", why="The pivot rides on the cart at $x$."),
                             opt(r"$(x + \ell\sin\theta)\,\mathbf{i} + \ell\cos\theta\,\mathbf{j}$", why="The bob hangs below the pivot, so its $y$ is negative.")]),
                     choice(r"What is $\partial\mathbf{r}_2/\partial\theta$?",
                            [opt(r"$\ell\cos\theta\,\mathbf{i} + \ell\sin\theta\,\mathbf{j}$", True),
                             opt(r"$\ell\cos\theta\,\mathbf{i} - \ell\sin\theta\,\mathbf{j}$", why="$\\frac{\\partial}{\\partial\\theta}(-\\ell\\cos\\theta) = +\\ell\\sin\\theta$."),
                             opt(r"$\mathbf{i} + \ell\cos\theta\,\mathbf{i}$", why="$x$ is held fixed in a partial derivative with respect to $\\theta$."),
                             opt(r"$-\ell\sin\theta\,\mathbf{i} + \ell\cos\theta\,\mathbf{j}$", why="That differentiates the wrong trig functions: $\\frac{d}{d\\theta}\\sin = \\cos$.")],
                            explain="It's tangent to the swing circle: the direction the bob moves when only $\\theta$ changes.")],
                    fig={"type": "cart-pendulum"}),
            problem("c-rq-2", "Spot the explicit time",
                    r"A bead slides in a straight tube spun at a prescribed rate $\Omega$: $\mathbf{r} = x(\cos\Omega t\,\mathbf{i} + \sin\Omega t\,\mathbf{j})$.",
                    [choice(r"Is $\partial\mathbf{r}/\partial t$ zero?",
                            [opt(r"No: it's $x\Omega(-\sin\Omega t\,\mathbf{i} + \cos\Omega t\,\mathbf{j})$, the tube carrying the bead around", True),
                             opt("Yes: only $x$ is a coordinate, so time doesn't appear", why="Time appears explicitly through $\\Omega t$; the tube's motion is prescribed, not a coordinate."),
                             opt(r"No: it equals $\dot x$", why="The partial with respect to $t$ holds $x$ fixed."),
                             opt("Yes, because $\\Omega$ is constant", why="Constant $\\Omega$ still makes the angle $\\Omega t$ change with time.")],
                            explain="An explicit-time position is the signature of a driven system. Expect $T_1$ or $T_0$ terms and $H \\ne E$.")],
                    fig={"type": "slot-disk"}),
        ]),

    concept(
        "c-dots", "Cancellation of dots: ∂ṙ/∂q̇ = ∂r/∂q", 1, L2,
        r"""
Look at the velocity expansion again: $\dot{\mathbf{r}}_j = \sum_i\frac{\partial\mathbf{r}_j}{\partial q_i}\dot q_i + \frac{\partial\mathbf{r}_j}{\partial t}$. It is **linear in the $\dot q_i$**, and the coefficient of $\dot q_k$ is $\partial\mathbf{r}_j/\partial q_k$. Differentiating with respect to $\dot q_k$ simply picks out that coefficient:

$$\frac{\partial\dot{\mathbf{r}}_j}{\partial\dot q_k} = \frac{\partial\mathbf{r}_j}{\partial q_k}.$$

It looks like the dots 'cancel', hence the name. It's used twice: to show generalized forces can be computed from velocities, $Q_i = \sum\mathbf{F}_k\cdot\partial\dot{\mathbf{r}}_k/\partial\dot q_i$, and in the [[c-lagrange-derivation|derivation of Lagrange's equations]], where it turns $m\dot{\mathbf{r}}\cdot\partial\mathbf{r}/\partial q$ into $\partial T/\partial\dot q$.
""",
        deeper=["c-r-of-q", "p-partial"],
        math=[r"\frac{\partial\dot{\mathbf{r}}_j}{\partial\dot q_k} = \frac{\partial\mathbf{r}_j}{\partial q_k}"],
        analogy=analogy("If your bike's speed is (gear ratio) × (pedal rate), then 'extra speed per unit of pedal rate' is just the gear ratio: the same number as 'extra distance per pedal turn'.",
                        "it works only because velocity is exactly linear in the $\\dot q$'s. It isn't a general calculus rule you can apply to any expression with dots."),
        exam="Use the velocity form for generalized forces when you already have $\\dot{\\mathbf{r}}$ written out: read the coefficient of $\\dot q_i$ and dot it with the force.",
        source="Lecture 2, pp. 2–3",
        problems=[
            problem("c-dots-1", "Check it on the cart-pendulum",
                    r"$\dot{\mathbf{r}}_2 = (\dot x + \ell\dot\theta\cos\theta)\,\mathbf{i} + \ell\dot\theta\sin\theta\,\mathbf{j}$.",
                    [choice(r"What is $\partial\dot{\mathbf{r}}_2/\partial\dot\theta$?",
                            [opt(r"$\ell\cos\theta\,\mathbf{i} + \ell\sin\theta\,\mathbf{j}$", True),
                             opt(r"$\ell\dot\theta\cos\theta\,\mathbf{i} + \ell\dot\theta\sin\theta\,\mathbf{j}$", why="Differentiating with respect to $\\dot\\theta$ removes the $\\dot\\theta$."),
                             opt(r"$-\ell\sin\theta\,\mathbf{i} + \ell\cos\theta\,\mathbf{j}$", why="$\\theta$ is frozen; only the $\\dot\\theta$ is differentiated."),
                             opt(r"$\mathbf{i} + \ell\cos\theta\,\mathbf{i}$", why="$\\dot x$ is a separate input, frozen here.")],
                            explain="It matches $\\partial\\mathbf{r}_2/\\partial\\theta$ from the position, exactly as the identity says.")]),
            problem("c-dots-2", "Which identity is it?",
                    "Several identities with dots appear in Lecture 2–3.",
                    [choice("Which one is the cancellation of dots?",
                            [opt(r"$\dfrac{\partial\dot{\mathbf{r}}}{\partial\dot q} = \dfrac{\partial\mathbf{r}}{\partial q}$", True),
                             opt(r"$\dfrac{\partial\dot{\mathbf{r}}}{\partial q} = \dfrac{\partial\mathbf{r}}{\partial\dot q}$", why="$\\mathbf{r}$ doesn't depend on $\\dot q$ at all, so the right side is zero."),
                             opt(r"$\dfrac{d}{dt}\dfrac{\partial\mathbf{r}}{\partial q} = \dfrac{\partial\mathbf{r}}{\partial q}$", why="Time differentiation changes $\\partial\\mathbf{r}/\\partial q$ in general."),
                             opt(r"$\dfrac{\partial T}{\partial\dot q} = \dfrac{\partial T}{\partial q}$", why="Those are different and both appear in Lagrange's equation.")])]),
        ]),

    concept(
        "c-virtual-disp", "A virtual displacement is an imagined nudge, frozen in time, that respects the constraints", 1, L2,
        r"""
$\delta\mathbf{r}_j$ is an **instantaneous** displacement, imagined with time frozen, and **consistent with the constraints**. In terms of coordinates,

$$\delta\mathbf{r}_j = \sum_{i=1}^n\frac{\partial\mathbf{r}_j}{\partial q_i}\delta q_i.$$

There's no $\partial\mathbf{r}/\partial t\,\delta t$ term: time is frozen. That's the subtle point. A real displacement over $dt$ includes the motion of any driven parts; a virtual one doesn't. So a hoop spun at a prescribed rate can do real work on a bead (it speeds it up), yet its normal force does **zero virtual work**, because every virtual nudge stays on the frozen hoop, perpendicular to the normal force.

Ideal constraint forces (smooth surfaces, rigid rods, rolling contact) do no virtual work. That single fact is why they disappear from Lagrange's equations.
""",
        deeper=["c-r-of-q", "p-dot", "p-work"],
        math=[r"\delta\mathbf{r}_j = \sum_i\frac{\partial\mathbf{r}_j}{\partial q_i}\delta q_i"],
        analogy=analogy("Pause the video and ask: if I nudged this piece right now, which ways could it slide without breaking anything?",
                        "real motion over $dt$ also includes the stage moving ($\\partial\\mathbf{r}/\\partial t\\,dt$). Virtual nudges ignore it, which is why driven constraints can do real work but no virtual work."),
        exam="When asked 'does force X appear in Lagrange's equations?', test $\\mathbf{F}\\cdot\\delta\\mathbf{r}$ at its point of application. Zero means it drops out.",
        widget={"type": "virtual"},
        source="Lecture 2, p. 3",
        problems=[
            problem("c-vd-1", "Nudge the pendulum",
                    r"A pendulum bob at $\mathbf{r} = \ell\sin\theta\,\mathbf{i} - \ell\cos\theta\,\mathbf{j}$ gets a virtual $\delta\theta$.",
                    [choice(r"What is $\delta\mathbf{r}$?",
                            [opt(r"$\ell\,\delta\theta\,(\cos\theta\,\mathbf{i} + \sin\theta\,\mathbf{j})$", True),
                             opt(r"$\ell\,\delta\theta\,(\sin\theta\,\mathbf{i} - \cos\theta\,\mathbf{j})$", why="That's along the rod, which would stretch it: not consistent with the constraint."),
                             opt(r"$\delta\theta\,(\cos\theta\,\mathbf{i} + \sin\theta\,\mathbf{j})$", why="A displacement needs length units: multiply by $\\ell$."),
                             opt(r"$\mathbf{0}$, because time is frozen", why="Freezing time doesn't freeze the coordinate; we imagine changing $\\theta$.")]),
                     choice("What virtual work does the rod tension do?",
                            [opt("Zero: $\\delta\\mathbf{r}$ is perpendicular to the rod", True),
                             opt("$T\\ell\\,\\delta\\theta$", why="That would need the tension to point along the swing."),
                             opt("$-T\\ell\\,\\delta\\theta$", why="Tension and $\\delta\\mathbf{r}$ are perpendicular."),
                             opt("It depends on whether the pendulum is moving", why="Virtual work uses the frozen geometry; the velocity doesn't enter.")])],
                    fig={"type": "pendulum"}),
            problem("c-vd-2", "Bead on a spun hoop",
                    "A bead slides on a smooth hoop that a motor spins about a vertical diameter at constant $\\Omega$.",
                    [choice("Does the hoop's normal force on the bead do *virtual* work?",
                            [opt("No: virtual nudges stay on the frozen hoop, perpendicular to the normal force", True),
                             opt("Yes, because the hoop is moving", why="Virtual displacements freeze time, so the hoop doesn't move in them."),
                             opt("Yes, it equals the motor's power", why="That's real work over $dt$, not virtual work."),
                             opt("Only if the bead is sliding", why="Perpendicularity to the frozen hoop doesn't depend on the bead's motion.")]),
                     choice("Can it do *real* work on the bead?",
                            [opt("Yes: the moving hoop pushes the bead around and can change its energy", True),
                             opt("No: normal forces never do work", why="On a moving surface, the contact point moves along the force's direction."),
                             opt("No, the hoop is smooth", why="Smooth removes tangential friction; the normal force still pushes the bead around with the hoop."),
                             opt("Only if $\\Omega$ changes", why="Even at constant $\\Omega$, the normal push in the azimuthal direction works on the bead as it moves out.")],
                            explain="This is why the bead's total energy $E$ isn't conserved but the Hamiltonian is ([[c-h-conservation]]).")]),
        ]),

    concept(
        "c-gen-force", "Generalized force: whatever multiplies δq in the virtual work", 1, L2,
        r"""
Add up the virtual work of all applied forces, $\delta W = \sum_k\mathbf{F}_k\cdot\delta\mathbf{r}_k$, substitute $\delta\mathbf{r}_k = \sum_i\frac{\partial\mathbf{r}_k}{\partial q_i}\delta q_i$, and regroup by $\delta q_i$:

$$\delta W = \sum_i Q_i\,\delta q_i,\qquad Q_i = \sum_k\mathbf{F}_k\cdot\frac{\partial\mathbf{r}_k}{\partial q_i} = \sum_k\mathbf{F}_k\cdot\frac{\partial\dot{\mathbf{r}}_k}{\partial\dot q_i}.$$

The units of $Q_i$ follow $q_i$: force for a length coordinate, moment for an angle. On the cart-pendulum with a spring $k$ on the cart and a horizontal force $F$ at the bob, the five forces collapse into two numbers:

$$Q_x = -kx + F,\qquad Q_\theta = -m_2g\ell\sin\theta + F\ell\cos\theta.$$

Gravity and the normal force on the cart contribute nothing to $Q_x$ because they are vertical and $\partial\mathbf{r}/\partial x = \mathbf{i}$.
""",
        deeper=["c-virtual-disp", "c-r-of-q", "p-dot", "c-dots"],
        math=[r"Q_i = \sum_k\mathbf{F}_k\cdot\frac{\partial\mathbf{r}_k}{\partial q_i}"],
        analogy=analogy("An exchange rate: each force is foreign currency, and $\\partial\\mathbf{r}/\\partial q$ converts it into 'coordinate currency'. $Q_i$ is the total after conversion.",
                        "unlike money, the rate changes with position ($\\cos\\theta$), so it must be re-evaluated at every configuration."),
        exam="Fastest method under time pressure: imagine increasing only $q_i$ by $\\delta q_i$, write the work done by each force, and divide by $\\delta q_i$. Check units at the end.",
        widget={"type": "virtual"},
        source="Lecture 2, pp. 3–5",
        problems=[
            problem("c-gf-1", "Cart-pendulum generalized forces",
                    r"Spring $k$ on the cart (mass $m_1$), horizontal force $F$ at the bob (mass $m_2$), smooth floor. Coordinates $x$, $\theta$.",
                    [sym_choice(r"What is $Q_x$?", -k * x + F,
                                [(-k * x + F, ""),
                                 (-k * x + F - m2 * g, "$\\partial\\mathbf{r}/\\partial x = \\mathbf{i}$ for both masses, and gravity is vertical: it adds nothing to $Q_x$."),
                                 (-k * x, "$F$ acts on the bob, but moving the cart by $\\delta x$ moves the bob by $\\delta x$ too, so $F$ does work."),
                                 (-k * x + F * sp.cos(th), "Increasing $x$ alone moves the bob purely horizontally, along $F$: the factor is 1.")]),
                     sym_choice(r"What is $Q_\theta$?", -m2 * g * l * sp.sin(th) + F * l * sp.cos(th),
                                [(-m2 * g * l * sp.sin(th) + F * l * sp.cos(th), ""),
                                 (m2 * g * l * sp.sin(th) + F * l * sp.cos(th), "Raising the bob (increasing $\\theta$) moves it against gravity: negative work."),
                                 (F * l * sp.sin(th) - m2 * g * l * sp.cos(th), "$\\partial\\mathbf{r}_2/\\partial\\theta = \\ell\\cos\\theta\\,\\mathbf{i} + \\ell\\sin\\theta\\,\\mathbf{j}$: $F$ pairs with $\\cos\\theta$, gravity with $\\sin\\theta$."),
                                 (-m2 * g * sp.sin(th) + F * sp.cos(th), "A generalized force for an angle has units of moment: keep the $\\ell$.")]),
                     choice(r"What are the units of $Q_\theta$?",
                            [opt("N·m", True), opt("N", why="$\\delta W = Q_\\theta\\,\\delta\\theta$ and $\\delta\\theta$ is dimensionless, so $Q_\\theta$ has units of work: N·m."),
                             opt("N/m", why="Work divided by a dimensionless angle is work."), opt("rad/s", why="That's an angular rate, not a force.")])],
                    fig={"type": "cart-pendulum", "spring": True, "force": True}),
            problem("c-gf-2", "Put numbers in",
                    r"$F = 10$ N, $\ell = 0.5$ m, $m_2 = 1$ kg, $\theta = 30°$.",
                    [num(r"What is $Q_\theta$?", -1 * G * 0.5 * math.sin(math.radians(30)) + 10 * 0.5 * math.cos(math.radians(30)), "N·m",
                         explain="$-9.81(0.5)(0.5) + 10(0.5)(0.866) = -2.45 + 4.33\\approx 1.88$ N·m. $F$ wins: $\\theta$ tends to increase.")]),
        ]),

    concept(
        "c-gen-force-moment", "A moment's generalized force is M · ∂ω/∂q̇", 1, L3,
        r"""
A moment does work through rotation: $W = \int M\,d\theta$, so its virtual work is $\delta W = M\,\delta\theta$ in planar motion. For a rigid body with absolute angular velocity $\boldsymbol{\omega}$ under an applied moment $\mathbf{M}$, the general rule mirrors the force rule with $\boldsymbol{\omega}$ in place of $\dot{\mathbf{r}}$:

$$Q_j = \mathbf{M}\cdot\frac{\partial\boldsymbol{\omega}}{\partial\dot q_j}.$$

The *absolute* angular velocity matters. A motor between two links applies $+\boldsymbol\tau$ to one and $-\boldsymbol\tau$ to the other, and both enter.
""",
        deeper=["c-gen-force", "p-work", "c-dots"],
        math=[r"\delta W = M\,\delta\theta,\qquad Q_j = \mathbf{M}\cdot\frac{\partial\boldsymbol{\omega}}{\partial\dot q_j}"],
        analogy=analogy("The same exchange-rate idea as for forces, with rotation as the currency: $\\partial\\boldsymbol\\omega/\\partial\\dot q$ says how much the body spins per unit of $\\dot q$.",
                        "3-D rotations can't be added up into a single angle vector, which is why the rule uses rates ($\\boldsymbol\\omega$) rather than angles."),
        exam="For motors between bodies, list the torque on each body separately with its sign before computing $Q$.",
        source="Lecture 3, p. 6",
        problems=[
            problem("c-gfm-1", "A motor at the elbow",
                    r"A planar two-link arm uses $\theta_1$ (link 1 from horizontal) and $\theta_2$ (link 2 relative to link 1). An elbow motor applies $+\tau\mathbf{k}$ to link 2 and $-\tau\mathbf{k}$ to link 1. So $\boldsymbol\omega_1 = \dot\theta_1\mathbf{k}$ and $\boldsymbol\omega_2 = (\dot\theta_1 + \dot\theta_2)\mathbf{k}$.",
                    [choice(r"What is $Q_{\theta_1}$ from the motor?",
                            [opt("$0$", True), opt(r"$\tau$", why="Link 1 also feels $-\\tau$, and $\\partial\\boldsymbol\\omega_1/\\partial\\dot\\theta_1 = \\mathbf{k}$: $\\tau - \\tau = 0$."),
                             opt(r"$-\tau$", why="Link 2's $+\\tau$ also counts: $\\partial\\boldsymbol\\omega_2/\\partial\\dot\\theta_1 = \\mathbf{k}$."),
                             opt(r"$2\tau$", why="The two torques are opposite, not equal.")],
                            explain="An internal motor can't turn the whole arm about the shoulder: it does no net work for a rigid rotation."),
                     choice(r"What is $Q_{\theta_2}$?",
                            [opt(r"$\tau$", True), opt("$0$", why="Only link 2 rotates when $\\theta_2$ changes: $\\partial\\boldsymbol\\omega_2/\\partial\\dot\\theta_2 = \\mathbf{k}$."),
                             opt(r"$-\tau$", why="$+\\tau\\mathbf{k}\\cdot\\mathbf{k} = \\tau$."), opt(r"$2\tau$", why="Link 1 doesn't rotate with $\\theta_2$.")])],
                    fig={"type": "two-link"}),
            problem("c-gfm-2", "Torque on a rolling wheel",
                    r"A wheel (radius $r$) rolls without slipping, coordinate $x$ to the right, so $\boldsymbol\omega = -\dot x/r\,\mathbf{k}$. A drive torque $\mathbf{M} = -M\mathbf{k}$ (clockwise) is applied.",
                    [choice("What is $Q_x$?",
                            [opt(r"$M/r$", True), opt(r"$-M/r$", why="$(-M\\mathbf{k})\\cdot(-\\tfrac1r\\mathbf{k}) = +M/r$: a clockwise torque drives the wheel to the right."),
                             opt(r"$Mr$", why="$\\partial\\omega/\\partial\\dot x = 1/r$, so divide by $r$."), opt(r"$M$", why="$Q_x$ must have units of force.")])],
                    fig={"type": "rolling-disk"}),
        ]),

    concept(
        "c-gen-momentum", "Generalized momentum p = ∂T/∂q̇", 1, L3,
        r"""
$p_i = \partial T/\partial\dot q_i$, and with the cancellation of dots $p_i = \sum_j m_j\dot{\mathbf{r}}_j\cdot\partial\mathbf{r}_j/\partial q_i$: each particle's momentum projected onto the direction $q_i$ moves it. For a length coordinate it's a linear momentum; for an angle it's an angular momentum.

In coupled systems $p_i$ includes the motion of other coordinates. For the cart-pendulum, $p_x = (M+m)\dot x + m\ell\dot\theta\cos\theta$, not just $(M+m)\dot x$. Generalized momentum is the first half of Lagrange's equation ($\dot p_i = Q_i + \partial T/\partial q_i$), the conserved quantity for cyclic coordinates ([[c-cyclic]]), and a state variable in [[c-canonical|Hamilton's equations]].
""",
        deeper=["p-partial", "c-dots"],
        math=[r"p_i = \frac{\partial T}{\partial\dot q_i}"],
        analogy=analogy("'Momentum along a coordinate': how much the energy bill rises per unit of speed in that coordinate.",
                        "for coupled systems it's not 'mass × that velocity': $p_x$ picks up the pendulum's swing through the cross term."),
        exam="$p_i$ is just the partial you take on the way to Lagrange's equation; write it down as its own line, since it's reused for conservation laws and $H$.",
        source="Lecture 2 p. 6; Lecture 3 p. 1",
        problems=[
            problem("c-gm-1", "Cart momentum",
                    r"$T = \tfrac12(M+m)\dot x^2 + \tfrac12 m\ell^2\dot\theta^2 + m\dot x\ell\dot\theta\cos\theta$.",
                    [sym_choice(r"What is $p_x$?", sp.diff(CP_T, xd),
                                [(sp.diff(CP_T, xd), ""),
                                 ((M + m) * xd, "The cross term $m\\dot x\\ell\\dot\\theta\\cos\\theta$ also contains $\\dot x$."),
                                 ((M + m) * xd + m * l * thd * sp.cos(th) - m * xd * l * thd * sp.sin(th), "$\\theta$ is frozen in a partial with respect to $\\dot x$."),
                                 ((M + m) * xd / 2 + m * l * thd * sp.cos(th), "$\\partial(\\tfrac12 a\\dot x^2)/\\partial\\dot x = a\\dot x$.")]),
                     choice(r"Physically, $p_x$ is…",
                            [opt("the total horizontal momentum of cart plus bob", True),
                             opt("the cart's momentum only", why="The bob's horizontal velocity $\\dot x + \\ell\\dot\\theta\\cos\\theta$ also counts."),
                             opt("the bob's angular momentum about the pivot", why="That's $p_\\theta$."),
                             opt("the system's kinetic energy divided by $\\dot x$", why="$p = \\partial T/\\partial\\dot q$ is a derivative, not a ratio.")])],
                    fig={"type": "cart-pendulum"}),
            problem("c-gm-2", "Satellite momentum",
                    r"$T = \tfrac12 m(\dot r^2 + r^2\dot\theta^2)$.",
                    [sym_choice(r"What is $p_\theta$?", m * r**2 * thd,
                                [(m * r**2 * thd, ""), (m * r * thd, "Differentiate $\\tfrac12 mr^2\\dot\\theta^2$: $mr^2\\dot\\theta$."),
                                 (m * r**2 * thd**2 / 2, "That's the kinetic energy term itself; differentiate with respect to $\\dot\\theta$."),
                                 (m * rd, "That's $p_r$.")]),
                     choice(r"Its units are…", [opt("kg·m²/s (angular momentum)", True), opt("kg·m/s", why="$mr^2\\dot\\theta$ has an extra metre: angular momentum."),
                                                opt("J", why="That's energy."), opt("N·m", why="That's a moment, the rate of change of $p_\\theta$.")])],
                    fig={"type": "satellite"}),
        ]),

    concept(
        "c-lagrange-derivation", "Lagrange's equations are Newton's law projected onto each coordinate", 1, L3,
        r"""
Start from Newton for each particle, $m_j\ddot{\mathbf{r}}_j = \mathbf{F}_j$, and dot both sides with $\partial\mathbf{r}_j/\partial q_i$, then sum. The right side becomes $Q_i$, and ideal constraint forces drop out because they're perpendicular to $\partial\mathbf{r}/\partial q_i$. The left side is rearranged with the product rule:

$$\dot p_i = \sum m_j\ddot{\mathbf{r}}_j\cdot\frac{\partial\mathbf{r}_j}{\partial q_i} + \sum m_j\dot{\mathbf{r}}_j\cdot\frac{d}{dt}\frac{\partial\mathbf{r}_j}{\partial q_i} = Q_i + \frac{\partial T}{\partial q_i},$$

where the cancellation of dots made $p_i = \partial T/\partial\dot q_i$, and $\frac{d}{dt}\frac{\partial\mathbf{r}}{\partial q} = \frac{\partial\dot{\mathbf{r}}}{\partial q}$ made the second term $\partial T/\partial q_i$. So

$$\frac{d}{dt}\Big(\frac{\partial T}{\partial\dot q_i}\Big) - \frac{\partial T}{\partial q_i} = Q_i,\qquad i = 1,\ldots,n.$$

One scalar equation per DOF, built from the scalar $T$ and the generalized forces. The $-\partial T/\partial q_i$ term carries the centripetal and Coriolis effects that Newton would need acceleration kinematics to find.
""",
        deeper=["c-gen-momentum", "c-gen-force", "c-dots", "p-newton", "p-chain-multi"],
        math=[r"\frac{d}{dt}\Big(\frac{\partial T}{\partial\dot q_i}\Big) - \frac{\partial T}{\partial q_i} = Q_i"],
        analogy=analogy("Shadow puppetry: Newton's 3-D vector equation casts a shadow onto each coordinate direction, and Lagrange's equation is that shadow. Constraint forces stand perpendicular to the wall, so they cast no shadow.",
                        "shadows lose information: you can't get the constraint forces back from them alone."),
        exam="If asked to derive it, the marks are in three moves: dot with $\\partial\\mathbf{r}/\\partial q$; product rule backwards; cancellation of dots. Name each move.",
        source="Lecture 3, pp. 1–2",
        problems=[
            problem("c-ld-1", "Where the constraint forces go",
                    "In the derivation you dot $m\\ddot{\\mathbf{r}} = \\mathbf{F}$ with $\\partial\\mathbf{r}/\\partial q_i$.",
                    [choice("Why does a rigid rod's tension vanish from the result?",
                            [opt("It's perpendicular to every $\\partial\\mathbf{r}/\\partial q_i$, so its projection is zero", True),
                             opt("Because the rod is massless", why="A massless rod still pushes and pulls. It drops out because of its direction."),
                             opt("Because it's an internal force, and internal forces always cancel", why="Pairs cancel in a sum over bodies, but the reason it vanishes from each $Q_i$ is perpendicularity to the allowed motion."),
                             opt("Because $T$ doesn't include it", why="$T$ never includes forces; it's the right-hand side $Q_i$ where it would appear.")])]),
            problem("c-ld-2", "A particle in polar coordinates",
                    r"A free particle in the plane: $T = \tfrac12 m(\dot r^2 + r^2\dot\theta^2)$, with generalized force $Q_r$.",
                    [sym_choice("What is the $r$-equation?",
                                lagrange(m * (rd**2 + r**2 * thd**2) / 2, 0, [(r, rd, rdd), (th, thd, thdd)])[0] - sp.Symbol("Q_r"),
                                [(m * rdd - m * r * thd**2 - sp.Symbol("Q_r"), ""),
                                 (m * rdd - sp.Symbol("Q_r"), "That drops $-\\partial T/\\partial r = -mr\\dot\\theta^2$, the centripetal term."),
                                 (m * rdd + m * r * thd**2 - sp.Symbol("Q_r"), "$\\partial T/\\partial r = mr\\dot\\theta^2$ enters with a minus sign."),
                                 (m * rdd - 2 * m * r * thd**2 - sp.Symbol("Q_r"), "$\\partial(\\tfrac12 mr^2\\dot\\theta^2)/\\partial r = mr\\dot\\theta^2$: the ½ cancels the 2.")], eq=True,
                                explain="The $-mr\\dot\\theta^2$ is the centripetal acceleration, found without any acceleration kinematics.")],
                    fig={"type": "satellite"}),
        ]),

    concept(
        "c-lagrangian", "Fold the conservative forces into V: L = T − V", 1, L3,
        r"""
Split each generalized force: $Q_i = Q_{i,c} + Q_{i,nc}$. The conservative part is the slope of the potential energy, $Q_{i,c} = -\partial V/\partial q_i$. Since $V$ doesn't depend on $\dot q$, define the **Lagrangian** $L = T - V$ and Lagrange's equations become

$$\frac{d}{dt}\Big(\frac{\partial L}{\partial\dot q_i}\Big) - \frac{\partial L}{\partial q_i} = Q_{i,nc}.$$

For a conservative system, $Q_{i,nc} = 0$. Gravity and springs go into $V$; friction, damping and applied forces go on the right. **Never both.**
""",
        deeper=["c-lagrange-derivation", "p-potential"],
        math=[r"L = T - V", r"\frac{d}{dt}\Big(\frac{\partial L}{\partial\dot q_i}\Big) - \frac{\partial L}{\partial q_i} = Q_{i,nc}"],
        analogy=analogy("Pre-paid forces: gravity and springs are paid for in advance through $V$; only the 'cash' forces (friction, applied loads, damping) still appear on the right-hand side.",
                        "pay twice (put a spring in $V$ and also in $Q$) and you double its stiffness. It's a classic exam error."),
        exam="Make a two-column list before you start: 'in $V$' and 'in $Q_{nc}$'. Every force goes in exactly one column, or in neither if it does no work.",
        source="Lecture 3, p. 2",
        problems=[
            problem("c-lag-1", "Which column?",
                    r"A mass on a spring $k$, with a damper $c$ and an applied force $F(t)$, coordinate $x$. $V = \tfrac12 kx^2$.",
                    [choice(r"What is $Q_{x,nc}$?",
                            [opt(r"$-c\dot x + F(t)$", True), opt(r"$-kx - c\dot x + F(t)$", why="The spring is already in $V$; adding $-kx$ counts it twice."),
                             opt(r"$F(t)$", why="The damper is non-conservative and does work: it belongs in $Q_{nc}$."),
                             opt(r"$-c\dot x$", why="The applied force does work too.")])],
                    fig={"type": "smd", "force": True}),
            problem("c-lag-2", "The simple pendulum from L",
                    r"$L = \tfrac12 m\ell^2\dot\theta^2 + mg\ell\cos\theta$.",
                    [sym_choice("What is the equation of motion?", lagrange(m * l**2 * thd**2 / 2, -m * g * l * sp.cos(th), [(th, thd, thdd)])[0],
                                [(m * l**2 * thdd + m * g * l * sp.sin(th), ""),
                                 (m * l**2 * thdd - m * g * l * sp.sin(th), "$-\\partial L/\\partial\\theta = +mg\\ell\\sin\\theta$: the restoring term is positive on the left."),
                                 (m * l**2 * thdd + m * g * l * sp.cos(th), "$\\frac{d}{d\\theta}\\cos\\theta = -\\sin\\theta$."),
                                 (m * l * thdd + m * g * l * sp.sin(th), "$\\partial L/\\partial\\dot\\theta = m\\ell^2\\dot\\theta$.")], eq=True)],
                    fig={"type": "pendulum"}),
        ]),

    concept(
        "c-lagrange-recipe", "The recipe: coordinates, then T and V, then differentiate", 1, L3,
        r"""
For the cart (mass $M$, spring $k$) with a pendulum (mass $m$, length $\ell$), coordinates $x$ and $\theta$:

1. **Kinematics**: $\mathbf{v}_m = (\dot x + \ell\dot\theta\cos\theta)\mathbf{i} + \ell\dot\theta\sin\theta\,\mathbf{j}$.
2. **Energies**: $T = \tfrac12(M+m)\dot x^2 + \tfrac12 m\ell^2\dot\theta^2 + m\dot x\ell\dot\theta\cos\theta$ and $V = \tfrac12kx^2 - mg\ell\cos\theta$.
3. **Differentiate** for each coordinate:

$$(M+m)\ddot x + m\ell\ddot\theta\cos\theta - m\ell\dot\theta^2\sin\theta + kx = 0$$
$$m\ell^2\ddot\theta + m\ell\ddot x\cos\theta + mg\ell\sin\theta = 0$$

They're **second-order, nonlinear and coupled**. In the $\theta$ equation, the $m\dot x\ell\dot\theta\sin\theta$ terms from $\frac{d}{dt}\frac{\partial T}{\partial\dot\theta}$ and from $-\frac{\partial T}{\partial\theta}$ cancel, a cancellation worth expecting.
""",
        deeper=["c-lagrangian", "p-relative-velocity", "p-chain-multi", "p-partial", "p-potential"],
        math=[r"(M+m)\ddot x + m\ell\ddot\theta\cos\theta - m\ell\dot\theta^2\sin\theta + kx = 0",
              r"m\ell^2\ddot\theta + m\ell\ddot x\cos\theta + mg\ell\sin\theta = 0"],
        analogy=analogy("A recipe with one technique (differentiate) applied to two ingredients ($T$ and $V$): once the ingredients are right, the dish is automatic.",
                        "the recipe can't fix bad ingredients. Nearly every wrong EOM traces back to a wrong $T$ (usually the cross term)."),
        exam="Check each EOM in two limits: freeze the cart ($\\ddot x = 0$) and you should see the simple pendulum; remove the pendulum ($m = 0$) and you should see a mass on a spring.",
        widget={"type": "cartpend"},
        source="Lecture 3, pp. 3–4",
        problems=[
            problem("c-rec-1", "Build the cart-pendulum equations",
                    r"Cart $M$ on spring $k$; pendulum $m$, length $\ell$. Coordinates $x$, $\theta$; gravity datum at the pivot.",
                    [sym_choice("What is $T$?", CP_T,
                                [(CP_T, ""),
                                 ((M + m) * xd**2 / 2 + m * l**2 * thd**2 / 2, "The bob's velocity has a cross term $2\\dot x\\ell\\dot\\theta\\cos\\theta$."),
                                 (M * xd**2 / 2 + m * l**2 * thd**2 / 2 + m * xd * l * thd * sp.cos(th), "The bob also moves with the cart: its $\\tfrac12 m\\dot x^2$ is missing."),
                                 ((M + m) * xd**2 / 2 + m * l**2 * thd**2 / 2 + m * xd * l * thd * sp.sin(th), "The swing's horizontal part is $\\ell\\dot\\theta\\cos\\theta$.")]),
                     sym_choice("What is the $x$-equation?", CP_X,
                                [(CP_X, ""),
                                 ((M + m) * xdd + m * l * thdd * sp.cos(th) + k * x, "$\\frac{d}{dt}(m\\ell\\dot\\theta\\cos\\theta)$ also gives $-m\\ell\\dot\\theta^2\\sin\\theta$."),
                                 ((M + m) * xdd + m * l * thdd * sp.cos(th) + m * l * thd**2 * sp.sin(th) + k * x, "$\\frac{d}{dt}\\cos\\theta = -\\dot\\theta\\sin\\theta$."),
                                 ((M + m) * xdd + m * l * thdd * sp.cos(th) - m * l * thd**2 * sp.sin(th) - k * x, "$+\\partial V/\\partial x = +kx$ on the left.")], eq=True),
                     sym_choice(r"What is the $\theta$-equation?", CP_TH,
                                [(CP_TH, ""),
                                 (m * l**2 * thdd + m * l * xdd * sp.cos(th) - m * l * xd * thd * sp.sin(th) + m * g * l * sp.sin(th), "$-\\partial T/\\partial\\theta = +m\\dot x\\ell\\dot\\theta\\sin\\theta$ cancels the matching term from $\\frac{d}{dt}$."),
                                 (m * l**2 * thdd + m * g * l * sp.sin(th), "The cart's acceleration drives the pendulum through $m\\ell\\ddot x\\cos\\theta$."),
                                 (m * l**2 * thdd + m * l * xdd * sp.cos(th) - m * g * l * sp.sin(th), "Gravity restores: $+\\partial V/\\partial\\theta = +mg\\ell\\sin\\theta$.")], eq=True)],
                    fig={"type": "cart-pendulum", "spring": True}),
        ]),

    concept(
        "c-rolling-lagrange", "Rolling: whether the wheel slips decides the DOF and whether friction does work", 1, L3,
        r"""
A disk (mass $m$, $I_C = \tfrac12 mr^2$) on a spring $k$.

**Rolls without slipping**: $x = r\theta$ is a constraint, so 1 DOF. $T = \tfrac12 m\dot x^2 + \tfrac12 I_C(\dot x/r)^2 = \tfrac34 m\dot x^2$, $V = \tfrac12 kx^2$. Friction acts at the contact point $P$, whose velocity is zero, so it contributes nothing to $Q_{x,nc}$:

$$\tfrac32 m\ddot x + kx = 0.$$

**Rolls with slipping**: $x$ and $\theta$ are independent, 2 DOF. Now $\dot{\mathbf{r}}_P = (\dot x - r\dot\theta)\mathbf{i} \ne 0$, and friction $-f\mathbf{i}$ gives $Q_{x,nc} = -f$ and $Q_{\theta,nc} = fr$:

$$m\ddot x + kx = -f,\qquad \tfrac{mr^2}{2}\ddot\theta = fr.$$
""",
        deeper=["c-lagrangian", "p-rolling", "p-ke-rigid", "c-gen-force", "c-dof"],
        math=[r"\text{no slip: } \tfrac32 m\ddot x + kx = 0", r"\text{slip: } m\ddot x + kx = -f,\ \ \tfrac{mr^2}{2}\ddot\theta = fr"],
        analogy=analogy("The no-slip disk is like a geared wheel on a toothed rack: the teeth force $x = r\\theta$ and transmit force without doing work.",
                        "real tyres creep a little, so even 'rolling' contact dissipates some energy (rolling resistance), which the ideal model ignores."),
        exam="Decide slip or no slip first: it sets the DOF, the coordinates and whether friction is in the equations. An exam question often hinges on this one sentence.",
        widget={"type": "rolling"},
        source="Lecture 3, pp. 4–5",
        problems=[
            problem("c-roll-1", "No slip",
                    r"A uniform disk (mass $m$, radius $r$) on a spring $k$ rolls without slipping. Coordinate $x$.",
                    [sym_choice("What is the equation of motion?", lagrange(sp.Rational(3, 4) * m * xd**2, k * x**2 / 2, [(x, xd, xdd)])[0],
                                [(sp.Rational(3, 2) * m * xdd + k * x, ""),
                                 (m * xdd + k * x, "The disk also spins: its rotational energy adds $\\tfrac14 m\\dot x^2$ to $T$, giving an effective mass $\\tfrac32 m$."),
                                 (2 * m * xdd + k * x, "That uses $I = mr^2$ (a hoop)."),
                                 (sp.Rational(3, 2) * m * xdd + k * x + sp.Symbol("f"), "At the contact point $\\dot{\\mathbf{r}}_P = 0$, so friction does no work and doesn't appear.")], eq=True),
                     num(r"With $k = 300$ N/m and $m = 2$ kg, what is the natural frequency $\omega_n$?", math.sqrt(2 * 300 / (3 * 2)), "rad/s",
                         explain="$\\omega_n = \\sqrt{k/(\\tfrac32 m)} = \\sqrt{300/3} = 10$ rad/s.")],
                    fig={"type": "rolling-disk", "spring": True}),
            problem("c-roll-2", "With slip",
                    r"Same disk, now slipping, friction force $-f\mathbf{i}$ at $P$. $\dot{\mathbf{r}}_P = (\dot x - r\dot\theta)\mathbf{i}$.",
                    [choice(r"What is $Q_{\theta,nc}$?",
                            [opt(r"$fr$", True), opt(r"$-fr$", why="$(-f\\mathbf{i})\\cdot\\partial\\dot{\\mathbf{r}}_P/\\partial\\dot\\theta = (-f\\mathbf{i})\\cdot(-r\\mathbf{i}) = +fr$."),
                             opt("$0$", why="With slip, the contact point moves, so friction does work."),
                             opt(r"$-f$", why="That's $Q_{x,nc}$.")])],
                    fig={"type": "rolling-disk", "spring": True}),
        ]),
]
