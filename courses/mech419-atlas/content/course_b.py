"""Layer 1, Lectures 4-6: constraints, energy structure, equilibrium, Hamiltonian."""
import math
import sympy as sp
from lib import *

G = 9.81
L4, L5, L6 = "Lecture 4 · Constraints and multipliers", "Lecture 5 · Kinetic energy and equilibrium", "Lecture 6–7 · Hamiltonian and conservation"

# Spring pendulum (Lecture 7) in canonical form.
SP_H = pr**2 / (2 * m) + pth**2 / (2 * m * r**2) - m * g * r * sp.cos(th) + k * (r - l0)**2 / 2

CONCEPTS = [
    concept(
        "c-constraint-types", "Holonomic constraints restrict where you can be; non-holonomic ones only how you can move", 1, L4,
        r"""
Constraints come as algebraic equations ($x^2 + y^2 + z^2 = R^2$, a bead on a sphere; $x^2 + y^2 - bz = 0$, a particle on a paraboloid), as time-varying ones, or as **differential** ones. A boat (or knife edge, or ice skate) can only move along its own axis: its velocity has no sideways component,

$$(\dot x\,\mathbf{i} + \dot y\,\mathbf{j})\cdot(-\sin\theta\,\mathbf{i} + \cos\theta\,\mathbf{j}) = -\dot x\sin\theta + \dot y\cos\theta = 0.$$

This can't be integrated into a relation among $x, y, \theta$.

- **Holonomic**: a relation among the coordinates, $f(q, t) = 0$.
- **Non-holonomic**: involves velocities and is **not integrable**.

Any holonomic constraint can be differentiated into a velocity form ($2x\dot x + 2y\dot y - b\dot z = 0$). The common format is the **Pfaffian form**:

$$\sum_{k=1}^{\hat n} a_{ik}\dot q_k + b_i = 0,\qquad i = 1, \ldots, C,$$

with $a_{ik}$, $b_i$ functions of the $q$'s (and $t$) only.
""",
        deeper=["c-dof", "p-chain-multi"],
        math=[r"\sum_{k=1}^{\hat n}a_{ik}\dot q_k + b_i = 0", r"-\dot x\sin\theta + \dot y\cos\theta = 0\ \ \text{(boat: non-holonomic)}"],
        analogy=analogy("Parallel parking: a car can't slide sideways, yet with enough back-and-forth it can reach any spot at any heading. The constraint limits velocities, not where you can end up.",
                        "a real car also has a minimum turning radius. The ideal knife edge doesn't, but that changes how long parking takes, not where you can park."),
        exam="To classify, try to integrate: if the Pfaffian form is the time derivative of some $f(q)$, it's holonomic. Rolling on a straight line ($\\dot x - r\\dot\\theta = 0$) integrates to $x = r\\theta$; the boat's doesn't.",
        widget={"type": "boat"},
        source="Lecture 4, pp. 1–2",
        problems=[
            problem("c-ct-1", "Pfaffian coefficients",
                    r"A particle on the paraboloid $x^2 + y^2 - bz = 0$, coordinates $(x, y, z)$.",
                    [choice(r"Writing $a_{1x}\dot x + a_{1y}\dot y + a_{1z}\dot z + b_1 = 0$, what are the coefficients?",
                            [opt(r"$a = (2x,\ 2y,\ -b)$, $b_1 = 0$", True),
                             opt(r"$a = (x^2,\ y^2,\ -bz)$, $b_1 = 0$", why="Differentiate the constraint in time first: $2x\\dot x + 2y\\dot y - b\\dot z = 0$."),
                             opt(r"$a = (2x,\ 2y,\ -b)$, $b_1 = -bz$", why="$b_1$ is the part with no $\\dot q$; here there's none."),
                             opt(r"$a = (2,\ 2,\ -b)$, $b_1 = 0$", why="$\\frac{d}{dt}x^2 = 2x\\dot x$: keep the $x$.")])],
                    fig={"type": "paraboloid"}),
            problem("c-ct-2", "Classify three constraints",
                    "Decide which are holonomic.",
                    [choice(r"The boat: $-\dot x\sin\theta + \dot y\cos\theta = 0$.",
                            [opt("Non-holonomic: it can't be integrated into a relation among $x, y, \\theta$", True),
                             opt("Holonomic, because it is written with velocities", why="Holonomic constraints can be written with velocities too; what matters is integrability."),
                             opt("Holonomic: it integrates to $y = x\\tan\\theta$", why="That would hold only if $\\theta$ were constant; with $\\theta$ changing, no such relation exists."),
                             opt("It isn't a constraint", why="It forbids sideways velocity, which is a constraint.")]),
                     choice(r"A disk rolling on a straight line: $\dot x - r\dot\theta = 0$.",
                            [opt("Holonomic: it integrates to $x = r\\theta + $ const", True),
                             opt("Non-holonomic, like all rolling constraints", why="Rolling on a straight line integrates. Rolling on a plane (a disk that can steer) generally doesn't."),
                             opt("Not a constraint: $x$ and $\\theta$ are independent", why="Without slip they're tied."),
                             opt("Non-holonomic because it involves $\\dot\\theta$", why="Integrability is the test, not the presence of rates.")])],
                    fig={"type": "boat"}),
        ]),

    concept(
        "c-multipliers", "Keep dependent coordinates and let λ carry the constraint force", 1, L4,
        r"""
Sometimes it's easier (or necessary, for non-holonomic constraints) to keep $\hat n$ **dependent** coordinates with $C = \hat n - n$ constraints in Pfaffian form. Then the constraint forces no longer drop out. They appear as generalized constraint forces $R_j$:

$$\frac{d}{dt}\Big(\frac{\partial T}{\partial\dot q_j}\Big) - \frac{\partial T}{\partial q_j} + \frac{\partial V}{\partial q_j} = Q_{j,nc} + R_j,\qquad R_j = \sum_{i=1}^C\lambda_i a_{ij}.$$

The $\lambda_i$ are unknown **Lagrange multipliers**. Unknowns: $\hat n$ accelerations + $C$ multipliers. Equations: $\hat n$ Lagrange equations + $C$ constraint equations at the acceleration level ([[c-accel-constraint]]).

A bonus: $R_j$ *are* the constraint forces. For the particle on the paraboloid, $(R_x, R_y, R_z) = \lambda(2x, 2y, -b)$, the surface's normal force (it points along the gradient of the constraint).
""",
        deeper=["c-constraint-types", "c-lagrangian", "c-gen-force"],
        math=[r"R_j = \sum_{i=1}^C\lambda_i a_{ij}", r"\text{unknowns: } \hat n + C"],
        analogy=analogy("A referee who enforces the rules by pushing back exactly as hard as needed: $\\lambda$ is how hard, and the constraint's gradient says which way.",
                        "a referee can react late. Constraint forces act instantly and exactly, with no give."),
        exam="Use multipliers when (a) the constraint is non-holonomic, or (b) the question asks for a constraint force. Otherwise eliminate the constraint and use independent coordinates: it's shorter.",
        widget={"type": "constraint"},
        source="Lecture 4, pp. 2–4",
        problems=[
            problem("c-mult-1", "Particle on a paraboloid",
                    r"$T = \tfrac12 m(\dot x^2 + \dot y^2 + \dot z^2)$, $V = mgz$, constraint $2x\dot x + 2y\dot y - b\dot z = 0$.",
                    [sym_choice("What is the $x$-equation?", m * xdd - lam * 2 * x,
                                [(m * xdd - 2 * x * lam, ""), (m * xdd, "With dependent coordinates the constraint force appears: add $\\lambda a_{1x} = 2x\\lambda$."),
                                 (m * xdd + 2 * x * lam, "$R_x = +\\lambda a_{1x}$ on the right side: $m\\ddot x = 2x\\lambda$."),
                                 (m * xdd - x * lam, "$a_{1x} = 2x$.")], eq=True),
                     sym_choice("What is the $z$-equation?", m * zdd + m * g + b * lam,
                                [(m * zdd + m * g + b * lam, ""), (m * zdd + m * g, "Add the constraint term $\\lambda a_{1z} = -b\\lambda$ on the right."),
                                 (m * zdd + m * g - b * lam, "$a_{1z} = -b$, so the right side is $-b\\lambda$."),
                                 (m * zdd - m * g + b * lam, "$\\partial V/\\partial z = +mg$ on the left.")], eq=True),
                     num("How many unknowns at one instant (accelerations and multipliers)?", 4, "",
                         explain="$\\ddot x, \\ddot y, \\ddot z, \\lambda_1$: three Lagrange equations plus the constraint at the acceleration level.")],
                    fig={"type": "paraboloid"}),
            problem("c-mult-2", "What λ means for a pendulum",
                    r"Pendulum in $(x, y)$ with $y$ downward: $m\ddot x = \lambda x$, $m\ddot y - mg = \lambda y$, $x^2 + y^2 = \ell^2$. The bob hangs at rest at the bottom ($x = 0$, $y = \ell$).",
                    [num(r"With $m = 1$ kg, $\ell = 1$ m, what is $\lambda$?", -1 * G / 1, "N/m",
                         explain="At rest at the bottom $\\ddot y = 0$, so $-mg = \\lambda\\ell$ and $\\lambda = -9.81$ N/m."),
                     choice(r"The constraint force is $\mathbf{R} = \lambda(x\mathbf{i} + y\mathbf{j})$. Physically it is…",
                            [opt("the rod tension, pulling the bob toward the pivot (magnitude $|\\lambda|\\ell = mg$)", True),
                             opt("gravity", why="Gravity is already in $V$."),
                             opt("a fictitious force with no physical meaning", why="Multipliers times constraint gradients are real constraint forces."),
                             opt("zero, because the bob is at rest", why="At rest the rod still holds the bob up.")])],
                    fig={"type": "pendulum-xy"}),
        ]),

    concept(
        "c-accel-constraint", "Differentiate the constraint once more to close the system, or get the wrong answer", 1, L4,
        r"""
The Pfaffian form is a **velocity-level** statement. The Lagrange equations contain accelerations, so to solve for $\ddot q$'s and $\lambda$'s together you differentiate the constraint once more. For the paraboloid:

$$2x\dot x + 2y\dot y - b\dot z = 0\ \xrightarrow{\ d/dt\ }\ 2\dot x^2 + 2x\ddot x + 2\dot y^2 + 2y\ddot y - b\ddot z = 0.$$

**What goes wrong without multipliers.** Lecture 4's warning: take a pendulum in dependent coordinates $(x, y)$ with $T = \tfrac12 m(\dot x^2 + \dot y^2)$ and $V = -mgy$, and blindly apply the independent-coordinate equations. You get $m\ddot x = 0$ and $m\ddot y = mg$: **free fall**. The rod has vanished because nothing told the equations about it. The correct set is $m\ddot x = \lambda x$, $m\ddot y = mg + \lambda y$, plus $\dot x^2 + x\ddot x + \dot y^2 + y\ddot y = 0$: three equations, three unknowns.
""",
        deeper=["c-multipliers", "p-chain-multi"],
        math=[r"\frac{d}{dt}\Big(\sum_k a_{ik}\dot q_k + b_i\Big) = 0"],
        analogy=analogy("A train timetable that only says 'trains must stay on the track' at the level of speed. To plan braking (accelerations) you need the rule restated for accelerations, which is the second derivative.",
                        "differentiating can let errors creep in during numerical integration (drift off the constraint), which simulation codes have to correct."),
        exam="Count before you solve: unknowns ($\\hat n$ accelerations + $C$ multipliers) must equal equations ($\\hat n$ + $C$). If they don't, you've forgotten the acceleration-level constraint.",
        widget={"type": "constraint", "wrong": True},
        source="Lecture 4, pp. 4–6",
        problems=[
            problem("c-ac-1", "Acceleration level",
                    r"Differentiate the paraboloid constraint $2x\dot x + 2y\dot y - b\dot z = 0$.",
                    [choice("What is the acceleration-level constraint?",
                            [opt(r"$2\dot x^2 + 2x\ddot x + 2\dot y^2 + 2y\ddot y - b\ddot z = 0$", True),
                             opt(r"$2x\ddot x + 2y\ddot y - b\ddot z = 0$", why="Product rule: $\\frac{d}{dt}(x\\dot x) = \\dot x^2 + x\\ddot x$."),
                             opt(r"$2\ddot x + 2\ddot y - b\ddot z = 0$", why="The coefficients $2x, 2y$ change in time and must be differentiated too."),
                             opt(r"$x^2 + y^2 - bz = 0$", why="That's the position level; we need to go up to accelerations.")])],
                    fig={"type": "paraboloid"}),
            problem("c-ac-2", "The free-falling pendulum",
                    r"Apply the plain Lagrange equations (no $\lambda$) to a pendulum in coordinates $(x, y)$.",
                    [choice("What do you get, and why?",
                            [opt("Free fall: $m\\ddot x = 0$, $m\\ddot y = mg$, because the equations never learned about the rod", True),
                             opt("The correct pendulum equation, just in different coordinates", why="The plain equations assume independent coordinates; $x, y$ aren't."),
                             opt("No equations at all: the system is singular", why="You do get equations; they're just the wrong ones."),
                             opt("Simple harmonic motion in $x$", why="$m\\ddot x = 0$ is uniform motion, not SHM.")])]),
            problem("c-ac-3", "Tension from λ",
                    r"Solving the three equations gives $\lambda = -m(v^2 + gy)/\ell^2$ (with $y$ down). The tension is $-\lambda\ell$.",
                    [num(r"For $m = 2$ kg, $\ell = 1$ m, at the bottom ($y = \ell$) with speed $v = 3$ m/s, what is the tension?", 2 * (9 + G * 1) / 1, "N",
                         explain="$T = m(v^2/\\ell + g) = 2(9 + 9.81) = 37.6$ N: weight plus the centripetal force $mv^2/\\ell$.")],
                    fig={"type": "pendulum-xy"}),
        ]),

    concept(
        "c-t2t1t0", "Kinetic energy splits by powers of q̇: T₂ + T₁ + T₀", 1, L5,
        r"""
Substitute $\dot{\mathbf{r}}_j = \sum_i\frac{\partial\mathbf{r}_j}{\partial q_i}\dot q_i + \frac{\partial\mathbf{r}_j}{\partial t}$ into $T = \tfrac12\sum m_j\dot{\mathbf{r}}_j\cdot\dot{\mathbf{r}}_j$ and sort the terms by how many $\dot q$'s they contain:

$$T = \underbrace{\tfrac12\sum_i\sum_k m_{ik}\dot q_i\dot q_k}_{T_2} + \underbrace{\sum_i b_i\dot q_i}_{T_1} + \underbrace{T_0}_{\text{no }\dot q},$$
$$m_{ik} = \sum_j m_j\frac{\partial\mathbf{r}_j}{\partial q_i}\cdot\frac{\partial\mathbf{r}_j}{\partial q_k},\quad b_i = \sum_j m_j\frac{\partial\mathbf{r}_j}{\partial q_i}\cdot\frac{\partial\mathbf{r}_j}{\partial t},\quad T_0 = \tfrac12\sum_j m_j\Big|\frac{\partial\mathbf{r}_j}{\partial t}\Big|^2.$$

$m_{ik}$ is symmetric: it's the **mass matrix**. If no position depends explicitly on time, $T_1 = T_0 = 0$ and $T = T_2$. $T_0$ and $T_1$ are the fingerprints of a driven system (prescribed rotation), and they control [[c-dynamic-eq]] and whether [[c-hamiltonian|H equals E]].

(Lecture 5 writes $T_0$ without the ½; the ½ is needed for $T_0 = \tfrac12 m\Omega^2x^2$ in the slot example to come out right.)
""",
        deeper=["c-r-of-q", "p-quadratic-form", "p-ke-rigid"],
        math=[r"T = T_2 + T_1 + T_0", r"m_{ik} = m_{ki} = m_{ik}(q, t)"],
        analogy=analogy("An energy bill with a usage charge ($T_2$, quadratic in your own speeds), a cross charge ($T_1$), and a fixed connection fee ($T_0$) that you pay simply because the stage you're on is moving.",
                        "$T_0$ isn't energy you can store or spend like $V$, but in the equations it behaves like a negative potential: $V - T_0$ is the landscape that matters."),
        exam="Sort $T$ by inspection: square terms in velocities go to $T_2$, terms with exactly one velocity to $T_1$, the rest to $T_0$. Then check the time-dependence of $\\mathbf{r}$ to confirm whether $T_1, T_0$ should exist.",
        widget={"type": "spin-disk"},
        source="Lecture 5, pp. 1–2",
        problems=[
            problem("c-t210-1", "Mass in a spinning slot",
                    r"A block moves along a slot in a disk spun at prescribed $\Omega$: $T = \tfrac12 m(\dot x^2 + \Omega^2x^2)$.",
                    [choice(r"Identify $T_2$, $T_1$, $T_0$.",
                            [opt(r"$T_2 = \tfrac12 m\dot x^2$, $T_1 = 0$, $T_0 = \tfrac12 m\Omega^2x^2$", True),
                             opt(r"$T_2 = \tfrac12 m(\dot x^2 + \Omega^2x^2)$, $T_1 = T_0 = 0$", why="$\\Omega$ is prescribed, not a generalized velocity. $\\tfrac12 m\\Omega^2x^2$ has no $\\dot x$, so it's $T_0$."),
                             opt(r"$T_2 = \tfrac12 m\dot x^2$, $T_1 = \tfrac12 m\Omega^2x^2$, $T_0 = 0$", why="$T_1$ terms are linear in $\\dot q$. This term has no $\\dot x$ at all."),
                             opt(r"$T_2 = 0$, $T_1 = m\Omega x\dot x$, $T_0 = \tfrac12 m\dot x^2$", why="$\\tfrac12 m\\dot x^2$ is quadratic in $\\dot x$: that's $T_2$.")])],
                    fig={"type": "slot-disk"}),
            problem("c-t210-2", "A turntable with two coordinates",
                    r"A puck at $(x, y)$ measured on a turntable spinning at $\Omega$. Its inertial velocity is $(\dot x - \Omega y,\ \dot y + \Omega x)$.",
                    [sym_choice(r"What is $T_1$?", m * Om * (x * yd - y * xd),
                                [(m * Om * (x * yd - y * xd), ""),
                                 (m * Om * (x * yd + y * xd), "Expand $(\\dot x - \\Omega y)^2$: the cross term is $-2\\Omega y\\dot x$."),
                                 (m * Om**2 * (x**2 + y**2) / 2, "That's $T_0$: it has no velocities."),
                                 (2 * m * Om * (x * yd - y * xd), "$\\tfrac12 m\\cdot 2\\Omega(x\\dot y - y\\dot x) = m\\Omega(x\\dot y - y\\dot x)$.")],
                                explain="$T_1$ is what produces the Coriolis terms in the equations of motion.")]),
            problem("c-t210-3", "When is T just T₂?",
                    "Look at the formulas for $b_i$ and $T_0$.",
                    [choice(r"$T_1 = T_0 = 0$ whenever…",
                            [opt(r"no position depends explicitly on time: $\partial\mathbf{r}_j/\partial t = 0$", True),
                             opt("the system is conservative", why="A spun slot with no friction is conservative but still has $T_0$."),
                             opt("there's only one degree of freedom", why="The slot example has 1 DOF and a $T_0$."),
                             opt("the coordinates are angles", why="It's about explicit time dependence, not coordinate type.")])]),
        ]),

    concept(
        "c-static-eq", "Static equilibrium: the slope of V balances the non-conservative pushes", 1, L5,
        r"""
In static equilibrium nothing moves: every $\dot q = \ddot q = 0$, so $T$ and all its derivatives in Lagrange's equations vanish (for $T = T_2$). What's left is

$$\frac{\partial V}{\partial q_i} = Q_{i,nc},\qquad i = 1,\ldots,n.$$

For a conservative system, $\partial V/\partial q_i = 0$: the potential energy is **stationary** (a minimum, maximum or inflection). Minima are the stable ones ([[p-extremum]]).
""",
        deeper=["c-lagrangian", "p-extremum"],
        math=[r"\frac{\partial V}{\partial q_i} = Q_{i,nc}", r"\text{conservative: } \frac{\partial V}{\partial q_i} = 0"],
        analogy=analogy("A ball at rest on hilly ground: wherever it can sit still, the ground is flat under it (or a steady push exactly cancels the slope).",
                        "flat isn't enough for staying put after a nudge: hilltops are equilibria too, just unstable ones."),
        exam="Static equilibrium needs no kinetic energy at all: if the question only asks for equilibrium positions, skip $T$ entirely and save time.",
        widget={"type": "spin-pendulum", "omega": 0},
        source="Lecture 5, p. 3",
        problems=[
            problem("c-se-1", "A pendulum pushed sideways",
                    r"A steady horizontal force $F$ acts on a pendulum bob: $V = -mg\ell\cos\theta$, $Q_{\theta,nc} = F\ell\cos\theta$.",
                    [choice("What is the equilibrium condition?",
                            [opt(r"$\tan\theta_e = F/(mg)$", True), opt(r"$\sin\theta_e = F/(mg)$", why="$mg\\ell\\sin\\theta = F\\ell\\cos\\theta$ gives a tangent."),
                             opt(r"$\theta_e = 0$", why="That's only when $F = 0$."), opt(r"$\cos\theta_e = F/(mg)$", why="Divide $mg\\ell\\sin\\theta = F\\ell\\cos\\theta$ by $\\cos\\theta$.")]),
                     num(r"With $F = 5$ N and $m = 1$ kg, what is $\theta_e$ in degrees?", deg(math.atan(5 / G)), "°", explain="$\\arctan(5/9.81)\\approx 27.0°$.")],
                    fig={"type": "pendulum", "force": True}),
        ]),

    concept(
        "c-dynamic-eq", "Dynamic equilibrium: coordinates sit still while the stage keeps moving", 1, L5,
        r"""
In a driven system the coordinates can stay constant while things still move, like a pendulum riding at a fixed angle on a spinning shaft. Then $q_i = q_{ie}$ and $\dot q_i = 0$, so $T_2 = T_1 = 0$ but $T_0 \ne 0$, and Lagrange's equations reduce to

$$-\frac{\partial T_0}{\partial q_i} + \frac{\partial V}{\partial q_i} = Q_{i,nc}.$$

$T_0$ acts like a negative potential: equilibria are stationary points of $U = V - T_0$. For a point pendulum on a shaft spinning at $\Omega$: $T_0 = \tfrac12 m\Omega^2\ell^2\sin^2\theta$, $V = -mg\ell\cos\theta$, so

$$m\ell\sin\theta(g - \Omega^2\ell\cos\theta) = 0\ \Rightarrow\ \theta_e = 0\ \text{ or }\ \cos\theta_e = \frac{g}{\Omega^2\ell}.$$

The second branch exists only when $\Omega^2 \ge g/\ell$. For a uniform rod it's $\cos\theta_e = 3g/(2\Omega^2\ell)$. Above the critical speed, the hanging position $\theta = 0$ becomes unstable (it's a maximum of $U$) and the pendulum flies out. This is a pitchfork bifurcation.
""",
        deeper=["c-t2t1t0", "c-static-eq", "p-extremum"],
        math=[r"-\frac{\partial T_0}{\partial q_i} + \frac{\partial V}{\partial q_i} = Q_{i,nc}", r"\cos\theta_e = \frac{g}{\Omega^2\ell}\ \ (\Omega^2\ge g/\ell)"],
        analogy=analogy("A chair-swing ride at a fair: the chairs hang straight at low speed, then swing out further the faster it spins.",
                        "real chairs also feel air drag and sway; the ideal pendulum sits exactly at $\\theta_e$."),
        exam="Write $U = V - T_0$ and differentiate once for equilibria and twice for stability. The '$\\Omega^2\\ge g/\\ell$' existence condition is an easy mark to forget.",
        widget={"type": "spin-pendulum", "omega": 5},
        source="Lecture 5, pp. 3–5",
        beyond=False,
        problems=[
            problem("c-de-1", "How far does it swing out?",
                    r"A point pendulum ($\ell = 0.5$ m) on a vertical shaft spinning at $\Omega$.",
                    [num(r"At $\Omega = 5$ rad/s, what is the swung-out angle $\theta_e$, in degrees?", deg(math.acos(G / (25 * 0.5))), "°",
                         explain="$\\cos\\theta_e = 9.81/(25\\times0.5) = 0.785$, so $\\theta_e\\approx 38.3°$."),
                     choice(r"At $\Omega = 4$ rad/s?",
                            [opt(r"Only $\theta_e = 0$: $g/(\Omega^2\ell) = 1.23 > 1$ has no solution", True),
                             opt(r"$\theta_e = \arccos(1.23)$", why="Cosine can't exceed 1."),
                             opt(r"$\theta_e = 90°$", why="It would need infinite spin rate to reach horizontal."),
                             opt(r"$\theta_e\approx 38°$ again: the angle doesn't depend on $\Omega$", why="$\\cos\\theta_e = g/(\\Omega^2\\ell)$ clearly does.")])],
                    fig={"type": "spin-pendulum"}),
            problem("c-de-2", "The spinning rod",
                    r"A uniform rod ($\ell = 0.6$ m) pinned at its top on a shaft spinning at $\Omega = 6$ rad/s. $T_0 = \tfrac16 m\ell^2\Omega^2\sin^2\theta$, $V = -mg\tfrac{\ell}{2}\cos\theta$.",
                    [num(r"What is the swung-out angle, in degrees?", deg(math.acos(3 * G / (2 * 36 * 0.6))), "°",
                         explain="$\\cos\\theta_e = 3g/(2\\Omega^2\\ell) = 29.43/43.2 = 0.681$, so $\\theta_e\\approx 47.1°$.")],
                    fig={"type": "spin-rod"}),
            problem("c-de-3", "Which equilibrium is stable?",
                    r"$U(\theta) = V - T_0 = -mg\ell\cos\theta - \tfrac12 m\Omega^2\ell^2\sin^2\theta$.",
                    [choice(r"When is the hanging position $\theta = 0$ stable?",
                            [opt(r"When $\Omega^2 < g/\ell$, since $U''(0) = mg\ell - m\Omega^2\ell^2 > 0$", True),
                             opt("Always: hanging straight down is always stable", why="Above the critical speed, $U''(0) < 0$: it becomes a hilltop of $U$."),
                             opt(r"When $\Omega^2 > g/\ell$", why="That's when it loses stability."),
                             opt("Never: a spinning system has no stable equilibria", why="Below the critical speed it's stable.")],
                            explain="Stability comes from the curvature of $V - T_0$, not $V$ alone.")],
                    fig={"type": "spin-pendulum"}),
        ]),

    concept(
        "c-hamiltonian", "H = Σ p q̇ − L, and it works out to T₂ − T₀ + V", 1, L6,
        r"""
Define the Hamiltonian $H = \sum_i p_i\dot q_i - L$. Using $p_i = \sum_j m_{ij}\dot q_j + b_i$ from the [[c-t2t1t0|energy split]]:

$$\sum_i p_i\dot q_i = 2T_2 + T_1\ \Rightarrow\ H = 2T_2 + T_1 - (T_2 + T_1 + T_0 - V) = T_2 - T_0 + V.$$

- If $T_0 = 0$: $H = T_2 + V$.
- If $T_1 = T_0 = 0$: $H = T + V = E$, the total mechanical energy.

So $H$ is the energy only when nothing is being driven. For the spinning slot, $H = \tfrac12(m\dot x^2 - m\Omega^2x^2 + kx^2)$ while $E = \tfrac12(m\dot x^2 + m\Omega^2x^2 + kx^2)$. They differ by the sign of the $\Omega^2$ term.
""",
        deeper=["c-t2t1t0", "c-gen-momentum", "c-lagrangian"],
        math=[r"H = \sum_i p_i\dot q_i - L = T_2 - T_0 + V"],
        analogy=analogy("$H$ is 'energy as seen from the moving stage': it counts the kinetic energy you'd notice riding along ($T_2$), takes off the stage's fixed fee ($T_0$), and adds $V$.",
                        "$H$ isn't always an energy at all. It's a conserved quantity under its own conditions, which can hold when $E$'s don't."),
        exam="Compute $H$ from $T_2 - T_0 + V$, not from the definition. It's faster and avoids sign errors, but state that $\\sum p\\dot q = 2T_2 + T_1$ (Euler's theorem on homogeneous functions) if asked why.",
        widget={"type": "spin-disk"},
        source="Lecture 6, pp. 1, 3",
        problems=[
            problem("c-ham-1", "H for the spinning slot",
                    r"$T = \tfrac12 m(\dot x^2 + \Omega^2x^2)$, $V = \tfrac12 kx^2$.",
                    [sym_choice("What is $H$?", (m * xd**2 - m * Om**2 * x**2 + k * x**2) / 2,
                                [((m * xd**2 - m * Om**2 * x**2 + k * x**2) / 2, ""),
                                 ((m * xd**2 + m * Om**2 * x**2 + k * x**2) / 2, "That's $E = T + V$. $H = T_2 - T_0 + V$ subtracts $T_0$."),
                                 ((m * xd**2 + k * x**2) / 2, "$T_0 = \\tfrac12 m\\Omega^2x^2$ doesn't vanish: it enters with a minus sign."),
                                 ((m * xd**2 - m * Om**2 * x**2 - k * x**2) / 2, "$V$ enters $H$ with a plus sign.")])],
                    fig={"type": "slot-disk"}),
            problem("c-ham-2", "When is H the energy?",
                    "Use $H = T_2 - T_0 + V$.",
                    [choice("$H = E$ exactly when…",
                            [opt("$T_1 = T_0 = 0$", True), opt("$T_0 = 0$", why="That gives $H = T_2 + V$; if $T_1\\ne0$, $E = T_2 + T_1 + V$ differs."),
                             opt("the system is conservative", why="The spinning slot is conservative ($Q_{nc} = 0$), yet $H\\ne E$."),
                             opt("always: $H$ is the total energy by definition", why="Only for systems without explicit time in $\\mathbf{r}$.")])]),
        ]),

    concept(
        "c-cyclic", "A coordinate missing from L has a conserved momentum", 1, L6,
        r"""
Lagrange's equation can be read as $\dot p_i = \frac{\partial L}{\partial q_i} + Q_{i,nc}$. If $q_i$ doesn't appear in $L$ (it's **cyclic** or ignorable) and $Q_{i,nc} = 0$, then

$$\dot p_i = 0\quad\Rightarrow\quad p_i = \text{constant}.$$

For a satellite, $L = \tfrac12 m(\dot r^2 + r^2\dot\theta^2) + \frac{GM_em}{r}$ contains $\dot\theta$ but not $\theta$, so $p_\theta = mr^2\dot\theta$ is constant: $r^2\dot\theta$ is fixed (Kepler's second law, equal areas in equal times). We learned this **without writing down, let alone solving, the equations of motion**.
""",
        deeper=["c-gen-momentum", "c-lagrangian", "p-polar"],
        math=[r"\frac{\partial L}{\partial q_i} = 0,\ Q_{i,nc} = 0\ \Rightarrow\ p_i = \text{const}", r"mr^2\dot\theta = \text{const}"],
        analogy=analogy("A road with no hills in one direction: nothing pushes you along it, so your momentum along it never changes.",
                        "the coordinate must be absent from $L$, not just from $V$. And a non-conservative force along that coordinate (thrusters) breaks it."),
        exam="Scan $L$ for missing coordinates before deriving any equations: each one is a free first integral and often the key to a 'find the speed at...' question.",
        widget={"type": "orbit"},
        source="Lecture 6, p. 2",
        problems=[
            problem("c-cyc-1", "Satellite spin-up",
                    "A satellite's distance from Earth's centre doubles between two points of its orbit.",
                    [num(r"What is the ratio $\dot\theta_2/\dot\theta_1$?", 0.25, "",
                         explain="$r^2\\dot\\theta$ is constant: doubling $r$ quarters $\\dot\\theta$.")],
                    fig={"type": "satellite"}),
            problem("c-cyc-2", "The free disk",
                    r"The slot disk now spins freely (no motor): coordinates $x, \theta$, $T = \tfrac12 m(\dot x^2 + x^2\dot\theta^2)$, $V = \tfrac12 kx^2$.",
                    [choice("Which coordinate is cyclic, and what's conserved?",
                            [opt(r"$\theta$: $p_\theta = mx^2\dot\theta$ is constant", True),
                             opt(r"$x$: $p_x = m\dot x$ is constant", why="$x$ appears in $L$ (in $x^2\\dot\\theta^2$ and $\\tfrac12kx^2$)."),
                             opt(r"$\theta$: $\dot\theta$ is constant", why="It's $p_\\theta = mx^2\\dot\\theta$ that's constant; as $x$ changes, $\\dot\\theta$ must change."),
                             opt("Neither: both appear through their rates", why="Appearing through $\\dot\\theta$ is fine. $\\theta$ itself is absent.")])],
                    fig={"type": "slot-disk"}),
        ]),

    concept(
        "c-h-conservation", "H is conserved when L has no explicit t and nothing non-conservative does work", 1, L6,
        r"""
Differentiate $H = \sum p_i\dot q_i - L$ along the motion and use $\dot p_i = \partial L/\partial q_i + Q_{i,nc}$. Everything cancels except

$$\dot H = \sum_i Q_{i,nc}\,\dot q_i - \frac{\partial L}{\partial t}.$$

If $L$ has no explicit $t$ and the non-conservative forces do no work, **$H$ is constant**.

The spinning slot shows the difference between $H$ and $E$ sharply. $L = \tfrac12 m(\dot x^2 + \Omega^2x^2) - \tfrac12 kx^2$ has no explicit $t$ and $Q_{x,nc} = 0$, so $H = \tfrac12(m\dot x^2 - m\Omega^2x^2 + kx^2)$ is conserved. But $E$ is **not**: the motor holding $\Omega$ constant pushes the block sideways as it slides in and out, doing real work on it. If the disk spins freely instead, $H = E$ and both are conserved.
""",
        deeper=["c-hamiltonian", "c-virtual-disp", "p-energy-conservation"],
        math=[r"\dot H = \sum_i Q_{i,nc}\dot q_i - \frac{\partial L}{\partial t}"],
        analogy=analogy("$E$ is the money in your wallet; $H$ is your net worth in the 'stage currency'. The motor keeps paying into your wallet, but in stage currency the books still balance.",
                        "the analogy gets tired quickly. The precise statement is just the formula: $H$ changes only through $Q_{nc}$ power or explicit time in $L$."),
        exam="Two separate yes/no checks: (1) explicit $t$ in $L$? (2) do $Q_{nc}$ forces do work? Write both, then conclude. And for $E$, ask whether anything external (a motor, a prescribed motion) does real work.",
        widget={"type": "spin-disk"},
        source="Lecture 6, pp. 3–5",
        problems=[
            problem("c-hc-1", "Why E drifts on the spinning slot",
                    "The slot disk is driven at constant $\\Omega$ by a motor; no friction.",
                    [choice("Why isn't $E = T + V$ conserved?",
                            [opt("The motor does real work: the slot wall pushes the block sideways as it moves in and out", True),
                             opt("Because of friction", why="There's no friction; the effect is purely the prescribed rotation."),
                             opt("Because $H$ is conserved instead, and only one can be", why="Both can be conserved (free disk). Here the motor's work breaks $E$."),
                             opt("It is conserved; $H$ is the one that drifts", why="$L$ has no explicit $t$ and $Q_{nc} = 0$, so $H$ is conserved.")])],
                    fig={"type": "slot-disk"}),
            problem("c-hc-2", "A damped oscillator",
                    r"$L = \tfrac12 m\dot x^2 - \tfrac12 kx^2$, $Q_{x,nc} = -c\dot x$.",
                    [sym_choice(r"What is $\dot H$?", -c * xd**2,
                                [(-c * xd**2, ""), (c * xd**2, "A damper removes energy: $Q\\dot x = (-c\\dot x)\\dot x$."),
                                 (-c * xd, "Multiply the generalized force by the velocity: $-c\\dot x\\cdot\\dot x$."),
                                 (sp.Integer(0), "The damper does work, so $H$ isn't constant.")])],
                    fig={"type": "smd"}),
        ]),

    concept(
        "c-canonical", "Hamilton's equations: 2n first-order equations from one function H(q, p)", 1, L6,
        r"""
Write $H$ as a function of coordinates and momenta, $H(q, p, t)$. Comparing two expressions for $\dot H$ gives Hamilton's canonical equations:

$$\dot q_i = \frac{\partial H}{\partial p_i},\qquad \dot p_i = -\frac{\partial H}{\partial q_i} + Q_{i,nc}.$$

That's $2n$ **first-order** ODEs instead of $n$ second-order ones. The catch: **$H$ must be written in terms of $p$, not $\dot q$**. For the pendulum on a spring, $p_r = m\dot r$ and $p_\theta = mr^2\dot\theta$, so substitute $\dot r = p_r/m$ and $\dot\theta = p_\theta/(mr^2)$:

$$H = \frac{p_r^2}{2m} + \frac{p_\theta^2}{2mr^2} - mgr\cos\theta + \tfrac12 k(r - \ell_0)^2.$$

Then $\dot p_r = \frac{p_\theta^2}{mr^3} + mg\cos\theta - k(r - \ell_0)$ and $\dot p_\theta = -mgr\sin\theta$.
""",
        deeper=["c-hamiltonian", "c-gen-momentum", "p-partial"],
        math=[r"\dot q_i = \frac{\partial H}{\partial p_i},\qquad \dot p_i = -\frac{\partial H}{\partial q_i} + Q_{i,nc}"],
        analogy=analogy("$H$ is a landscape over the $(q, p)$ map, and the state flows along its contour lines, like water running along level paths around a hill.",
                        "with $Q_{nc}$ the flow drifts across contours (energy is lost), so the contour picture holds only for conservative systems."),
        exam="Step zero is always inverting $p = \\partial L/\\partial\\dot q$ for $\\dot q$. If $H$ still contains a $\\dot q$ when you differentiate, the result is wrong. Say so explicitly in your answer.",
        widget={"type": "phase"},
        source="Lecture 6 pp. 5–6; Lecture 7 pp. 1–2",
        problems=[
            problem("c-can-1", "The spring pendulum in canonical form",
                    r"$T = \tfrac12 m(\dot r^2 + r^2\dot\theta^2)$, $V = -mgr\cos\theta + \tfrac12 k(r - \ell_0)^2$.",
                    [choice(r"Express $\dot\theta$ in terms of momenta.",
                            [opt(r"$\dot\theta = p_\theta/(mr^2)$", True), opt(r"$\dot\theta = p_\theta/m$", why="$p_\\theta = mr^2\\dot\\theta$."),
                             opt(r"$\dot\theta = p_\theta\, mr^2$", why="Divide, don't multiply."), opt(r"$\dot\theta = p_r/(mr)$", why="$p_r$ belongs to $r$.")]),
                     sym_choice(r"What is $H(r, \theta, p_r, p_\theta)$?", SP_H,
                                [(SP_H, ""),
                                 (pr**2 / (2 * m) + pth**2 / (2 * m * r**2) + m * g * r * sp.cos(th) + k * (r - l0)**2 / 2, "The gravity potential is $-mgr\\cos\\theta$ (the bob is below the pivot)."),
                                 (pr**2 / m + pth**2 / (m * r**2) - m * g * r * sp.cos(th) + k * (r - l0)**2 / 2, "$\\sum p\\dot q - L$ leaves $\\tfrac12$ on each kinetic term: $H = T + V$ here."),
                                 (pr**2 / (2 * m) + pth**2 / (2 * m) - m * g * r * sp.cos(th) + k * (r - l0)**2 / 2, "$\\tfrac12 mr^2\\dot\\theta^2 = p_\\theta^2/(2mr^2)$.")]),
                     sym_choice(r"What is $\dot p_r$?", -sp.diff(SP_H, r),
                                [(-sp.diff(SP_H, r), ""),
                                 (sp.diff(SP_H, r), "Hamilton's second equation has a minus sign: $\\dot p = -\\partial H/\\partial q$."),
                                 (pth**2 / (m * r**3) - k * (r - l0), "Gravity's $-mgr\\cos\\theta$ depends on $r$ too."),
                                 (-pth**2 / (m * r**3) + m * g * sp.cos(th) - k * (r - l0), "$\\frac{\\partial}{\\partial r}\\frac{p_\\theta^2}{2mr^2} = -\\frac{p_\\theta^2}{mr^3}$; with the minus sign it's positive.")],
                                explain="The $p_\\theta^2/(mr^3)$ term is the centrifugal pull that stretches the spring.")],
                    fig={"type": "spring-pendulum"}),
            problem("c-can-2", "Why p, not q̇?",
                    r"A student writes $H = \tfrac12 mr^2\dot\theta^2 + \ldots$ and computes $\partial H/\partial p_\theta$.",
                    [choice("What goes wrong?",
                            [opt(r"They get $0$, because $H$ written with $\dot\theta$ has no explicit $p_\theta$: $\dot\theta = \partial H/\partial p_\theta$ fails", True),
                             opt("Nothing: $\\dot\\theta$ and $p_\\theta$ are interchangeable", why="Partial derivatives depend on which variables are held fixed; $H$ must be a function of $(q, p)$."),
                             opt("They get $mr^2\\dot\\theta$", why="There's no $p_\\theta$ to differentiate in that form."),
                             opt("The equations become second order", why="The problem is the wrong variables, not the order.")])]),
        ]),
]
