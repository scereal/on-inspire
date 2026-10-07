"""Layer 2: exam-style 'why' questions that need several ideas at once."""
import math
import sympy as sp
from lib import *

G = 9.81
Q = "Questions that join the ideas"

# Two-DOF frequencies of the linearized cart-pendulum: det(K - w^2 M) = 0.
_Mn, _mn, _ln, _kn = 2.0, 1.0, 0.5, 50.0
_Mm = [[_Mn + _mn, _mn * _ln], [_mn * _ln, _mn * _ln**2]]
_Kk = [[_kn, 0.0], [0.0, _mn * G * _ln]]
_a = _Mm[0][0] * _Mm[1][1] - _Mm[0][1] ** 2
_b = -(_Kk[0][0] * _Mm[1][1] + _Kk[1][1] * _Mm[0][0])
_c = _Kk[0][0] * _Kk[1][1]
_w2 = sorted([(-_b - math.sqrt(_b * _b - 4 * _a * _c)) / (2 * _a), (-_b + math.sqrt(_b * _b - 4 * _a * _c)) / (2 * _a)])
_W = sp.Symbol("w")
_check = sp.Matrix(_Kk) - _W * sp.Matrix(_Mm)
assert all(abs(float(_check.det().subs(_W, w))) < 1e-6 for w in _w2)

CONCEPTS = [
    concept(
        "q-pipeline", "From a sketch to natural frequencies: the whole MECH 419 pipeline on one system", 2, Q,
        r"""
Most exam problems chain the course end to end, so it pays to rehearse the chain on one system. For the cart (mass $M$, spring $k$) with a pendulum (mass $m$, length $\ell$):

1. **DOF and coordinates**: $5 - 3 = 2$; choose $x$, $\theta$ ([[c-dof]], [[c-gen-coords]]).
2. **Kinematics → $T$, $V$**: one velocity diagram gives $T$ with its cross term; $V = \tfrac12kx^2 - mg\ell\cos\theta$ ([[p-relative-velocity]]).
3. **Lagrange → nonlinear EOM** ([[c-lagrange-recipe]]).
4. **Equilibrium**: $\partial V/\partial q = 0$ gives $x = 0$, $\theta = 0$ ([[c-static-eq]]).
5. **Linearize**: read $\mathbf{M}_e$ and $\mathbf{K}$ off the quadratic parts ([[c-linearization]]).
6. **Frequencies**: try $\mathbf{q} = \mathbf{u}\cos\omega t$, so $(\mathbf{K} - \omega^2\mathbf{M}_e)\mathbf{u} = 0$, which has nonzero solutions only if $\det(\mathbf{K} - \omega^2\mathbf{M}_e) = 0$. (Step 6 extends Lecture 10's single-DOF $\omega_n = \sqrt{k/m}$ to two DOF.)

The point of seeing it whole: each step's output is the next step's input, and an error early (a missing cross term in $T$) propagates to the very end.
""",
        deeper=["c-dof", "c-lagrange-recipe", "c-static-eq", "c-linearization", "c-sdof-free"],
        analogy=analogy("An assembly line: each station takes the previous station's part and adds one operation. The final product (frequencies) is only as good as the first weld ($T$).",
                        "on an exam you can sometimes skip stations: the linearized $\\mathbf{M}$ and $\\mathbf{K}$ can come straight from $T$ and $V$, without step 3."),
        exam="If a problem asks only for the linear frequencies, go 1 → 2 → 5 → 6 and skip the nonlinear equations. Say you're doing that; it shows understanding.",
        widget={"type": "cartpend", "linear": True},
        beyond=True,
        problems=[
            problem("q-pipe-1", "Natural frequencies of the cart-pendulum",
                    rf"$M = {_Mn:g}$ kg, $m = {_mn:g}$ kg, $\ell = {_ln:g}$ m, $k = {_kn:g}$ N/m, $g = 9.81$ m/s².",
                    [num("How many DOF?", 2, ""),
                     num(r"$M_{e,12}$ (the coupling entry of the mass matrix)?", _mn * _ln, "kg·m", explain="$m\\ell = 0.5$."),
                     num(r"$K_{22}$?", _mn * G * _ln, "N·m", explain="$mg\\ell = 4.905$ N·m."),
                     num(r"Lower natural frequency $\omega_1$?", math.sqrt(_w2[0]), "rad/s",
                         explain=f"$\\det(\\mathbf{{K}} - \\omega^2\\mathbf{{M}}_e) = 0$ gives $0.5\\omega^4 - 27.2\\omega^2 + 245.3 = 0$, so $\\omega^2 = {_w2[0]:.2f}$ or ${_w2[1]:.2f}$.",
                         hint="Expand $(50 - 3w)(4.905 - 0.25w) - (0.5w)^2 = 0$ with $w = \\omega^2$."),
                     num(r"Higher natural frequency $\omega_2$?", math.sqrt(_w2[1]), "rad/s")],
                    fig={"type": "cart-pendulum", "spring": True}),
        ]),

    concept(
        "q-no-constraint-forces", "Why do constraint forces vanish from Lagrange's equations, and when don't they?", 2, Q,
        r"""
Because Lagrange's equations are Newton's law **projected onto the allowed motions** ([[c-lagrange-derivation]]), and an ideal constraint force is perpendicular to every allowed motion, so its projection is zero. In virtual-work language: ideal constraint forces do no virtual work ([[c-virtual-disp]]), so they contribute nothing to any $Q_i$ ([[c-gen-force]]).

Three situations bring them back:
- **Rolling with slip**: the contact point moves, so friction works ([[c-rolling-lagrange]]).
- **Dependent coordinates**: the coordinates themselves can violate the constraint, so the constraint force must appear, as $\lambda a_{ij}$ ([[c-multipliers]]).
- **You want them**: multipliers give you the force as a by-product.
""",
        deeper=["c-lagrange-derivation", "c-virtual-disp", "c-gen-force", "c-rolling-lagrange", "c-multipliers", "p-dot"],
        analogy=analogy("Lagrange's equations are like a train schedule written only in terms of stations along the track: the rails' sideways push never appears, because it never moves the train along the track.",
                        "if you describe the train with ordinary $(x, y)$ coordinates instead of distance along the track, the rails' push must be written back in (that's $\\lambda$)."),
        exam="A one-paragraph answer: projection onto $\\partial\\mathbf{r}/\\partial q$; perpendicular, so zero virtual work; exceptions are slip and dependent coordinates.",
        problems=[
            problem("q-ncf-1", "Which forces appear?",
                    "A disk rolls *without slipping* on a fixed incline; a rod pins its centre to a hanging pendulum. You use independent coordinates.",
                    [choice("Which forces appear in the generalized forces (outside $V$)?",
                            [opt("None of the contact or pin forces: the friction at the contact, the normal force and the pin force all do no virtual work", True),
                             opt("Friction, because the incline is rough", why="Rough but not slipping: the contact point is at rest, so friction does no work."),
                             opt("The pin force, because it's internal", why="Internal pin forces between rigid bodies do no net virtual work."),
                             opt("The normal force, because it's perpendicular to the incline", why="Perpendicular to the motion is exactly why it does no work.")])],
                    fig={"type": "rolling-disk"}),
            problem("q-ncf-2", "Bring it back",
                    "You need the normal force between the disk and the incline.",
                    [choice("What's the most direct analytical route?",
                            [opt("Keep the disk's height as a coordinate, impose the contact constraint with a multiplier, and read off $\\lambda a_{ij}$", True),
                             opt("It's impossible with Lagrange's method", why="Multipliers recover constraint forces."),
                             opt("Take $\\partial T/\\partial q$ of the normal direction", why="With independent coordinates there's no normal coordinate to differentiate."),
                             opt("Use Hamilton's equations instead", why="They also drop ideal constraint forces.")])]),
        ]),

    concept(
        "q-velocities-only", "Why does Lagrange need only velocities when Newton needs accelerations?", 2, Q,
        r"""
Newton needs $\mathbf{a}$ for each body: the hard part of rigid-body kinematics, with Coriolis and centripetal terms. Lagrange's method builds the scalar $T$ from **velocities** and then *differentiates*: the $\frac{d}{dt}\frac{\partial T}{\partial\dot q}$ term generates $\ddot q$ terms and velocity-product terms, and $-\frac{\partial T}{\partial q}$ adds the centripetal-type terms. The acceleration kinematics is done by calculus, not by hand.

Why that's legitimate: the [[c-lagrange-derivation|derivation]] shows $\sum m\ddot{\mathbf{r}}\cdot\frac{\partial\mathbf{r}}{\partial q} = \frac{d}{dt}\frac{\partial T}{\partial\dot q} - \frac{\partial T}{\partial q}$ identically, using the [[c-dots|cancellation of dots]].
""",
        deeper=["c-lagrange-derivation", "c-dots", "p-relative-velocity", "p-chain-multi", "c-vector-vs-analytical"],
        analogy=analogy("Instead of computing every acceleration by hand, you hand $T$ to a machine (differentiation) that computes them for you, including the awkward terms.",
                        "the machine only works on correct input: an error in a velocity still becomes an error in the accelerations."),
        exam="Point to one term in your EOM (e.g. $-m\\ell\\dot\\theta^2\\sin\\theta$) and say where it came from; it shows the examiner you know what the method does.",
        problems=[
            problem("q-vo-1", "Where did the centripetal term come from?",
                    r"In the cart's equation, $(M+m)\ddot x + m\ell\ddot\theta\cos\theta - m\ell\dot\theta^2\sin\theta + kx = 0$.",
                    [choice(r"Which operation produced $-m\ell\dot\theta^2\sin\theta$?",
                            [opt(r"Differentiating $\cos\theta$ inside $\frac{d}{dt}\frac{\partial T}{\partial\dot x}$ with the chain rule", True),
                             opt(r"The $-\partial T/\partial x$ term", why="$T$ doesn't contain $x$, so that term is zero."),
                             opt(r"The potential energy", why="$V$ gives $kx$ only."),
                             opt("An acceleration diagram", why="That's the Newtonian route; Lagrange never drew one.")])],
                    fig={"type": "cart-pendulum"}),
        ]),

    concept(
        "q-h-not-e", "Why is H conserved but not E on the spinning disk?", 2, Q,
        r"""
On the slot disk spun at fixed $\Omega$: $T = \tfrac12 m(\dot x^2 + \Omega^2x^2)$ has $T_0 = \tfrac12 m\Omega^2x^2$ ([[c-t2t1t0]]), so

- $H = T_2 - T_0 + V = \tfrac12(m\dot x^2 - m\Omega^2x^2 + kx^2)$, conserved because $L$ has no explicit $t$ and $Q_{nc} = 0$ ([[c-h-conservation]]);
- $E = T + V = \tfrac12(m\dot x^2 + m\Omega^2x^2 + kx^2)$, **not** conserved.

Physically, the motor holding $\Omega$ fixed does real work through the slot wall as the block moves in and out; that work changes $E$. $H$ is blind to it because the prescribed motion lives inside $T_0$, which $H$ subtracts. Let the disk spin freely and $\theta$ becomes a coordinate: then $T_0 = 0$, $H = E$, and both are conserved.
""",
        deeper=["c-hamiltonian", "c-h-conservation", "c-t2t1t0", "c-virtual-disp"],
        analogy=analogy("$E$ is your wallet, and a motor keeps topping it up. $H$ is your account measured in the disk's own currency, where the motor's top-ups are built into the exchange rate.",
                        "it's only an analogy. The real reason is the formula $\\dot H = \\sum Q_{nc}\\dot q - \\partial L/\\partial t$."),
        exam="Answer with two checks for $H$ (explicit $t$? $Q_{nc}$ work?) and one physical sentence for $E$ (the motor works). That's the full-marks shape.",
        widget={"type": "spin-disk"},
        problems=[
            problem("q-hne-1", "Numbers on the spinning slot",
                    r"$m = 1$ kg, $k = 25$ N/m, $\Omega = 3$ rad/s. At one instant $x = 0.2$ m, $\dot x = 0$.",
                    [num("$H$ at that instant?", 0.5 * (0 - 1 * 9 * 0.04 + 25 * 0.04), "J", explain="$\\tfrac12(0 - 0.36 + 1.0) = 0.32$ J."),
                     num("$E$ at that instant?", 0.5 * (0 + 9 * 0.04 + 25 * 0.04), "J", explain="$\\tfrac12(0.36 + 1.0) = 0.68$ J."),
                     choice("Later the block passes $x = 0$. What's conserved between the two instants?",
                            [opt("$H$ only", True), opt("$E$ only", why="$E$ changes because the motor works on the block."),
                             opt("Both", why="Only if the disk spun freely."), opt("Neither", why="$L$ has no explicit time and there's no friction: $H$ is conserved.")]),
                     num(r"So what is $\dot x$ at $x = 0$?", math.sqrt(2 * 0.32 / 1), "m/s", explain="$\\tfrac12 m\\dot x^2 = H = 0.32$, so $\\dot x = 0.8$ m/s.")],
                    fig={"type": "slot-disk"}),
        ]),

    concept(
        "q-spin-out", "Why does a spinning pendulum swing out only above √(g/ℓ)?", 2, Q,
        r"""
In dynamic equilibrium, the effective potential is $U(\theta) = V - T_0 = -mg\ell\cos\theta - \tfrac12m\Omega^2\ell^2\sin^2\theta$ ([[c-dynamic-eq]]). Near $\theta = 0$,

$$U \approx \text{const} + \tfrac12(mg\ell - m\Omega^2\ell^2)\theta^2.$$

Gravity's stiffness $mg\ell$ competes with a 'centrifugal anti-stiffness' $m\Omega^2\ell^2$. Below $\Omega^2 = g/\ell$, gravity wins: $\theta = 0$ is the bottom of a bowl ([[p-extremum]]). Above it, the curvature flips sign: the bottom becomes a hilltop, and two new valleys appear at $\cos\theta_e = g/(\Omega^2\ell)$. The pendulum rolls into one of them. That's a supercritical pitchfork bifurcation, the same mechanism as the bead on a rotating hoop in Strogatz's *Nonlinear Dynamics and Chaos*.
""",
        deeper=["c-dynamic-eq", "p-extremum", "c-linearization", "p-taylor"],
        analogy=analogy("A tug of war between gravity, which pulls the bob down to the axis, and spin, which flings it outward. Below the critical speed gravity always wins near the axis; above it, they settle at a draw away from the axis.",
                        "the 'centrifugal force' is really the $T_0$ term of a rotating description, not a real force in the inertial frame."),
        exam="Show the curvature sign change: $U''(0) = mg\\ell - m\\Omega^2\\ell^2$. That single line answers 'why' rigorously.",
        widget={"type": "spin-pendulum", "omega": 4.4},
        problems=[
            problem("q-so-1", "The critical speed",
                    r"A point pendulum with $\ell = 0.5$ m.",
                    [num(r"Critical spin rate $\Omega_{cr}$?", math.sqrt(G / 0.5), "rad/s", explain="$\\sqrt{g/\\ell} = \\sqrt{19.62}\\approx 4.43$ rad/s."),
                     choice(r"Above $\Omega_{cr}$, which equilibria are stable?",
                            [opt(r"The swung-out ones, $\cos\theta_e = g/(\Omega^2\ell)$", True),
                             opt(r"$\theta = 0$ only", why="$U''(0) < 0$ above the critical speed: it's a hilltop."),
                             opt("All of them", why="At most the valleys of $U$ are stable."),
                             opt("None", why="The new branches are valleys of $U$.")])],
                    fig={"type": "spin-pendulum"}),
        ]),

    concept(
        "q-cycloid", "Why does the cycloid beat the straight line, the shortest path?", 2, Q,
        r"""
Shortest is not fastest. The bead's speed depends only on how far it has dropped ($v = \sqrt{2gy}$, [[p-energy-conservation]]), so dropping steeply at the start buys speed that pays off over the rest of the trip. The straight line wastes the early part of the trip at low speed. Minimizing $\int ds/v$ ([[c-brachistochrone]]), not $\int ds$ ([[c-shortest-path]]), balances extra distance against extra speed exactly, and the balance point is a cycloid.

Bernoulli's own argument treats the bead like light refracting through layers that get faster as you go down: Snell's law, $\sin\alpha/v = $ const, applied continuously, produces the same curve.
""",
        deeper=["c-brachistochrone", "c-shortest-path", "c-special-cases", "p-energy-conservation"],
        analogy=analogy("A lifeguard running along the beach before swimming: she doesn't head straight for the swimmer, she runs further on fast sand to spend less time in slow water.",
                        "the lifeguard has two speeds; the bead's speed changes continuously with depth, so the 'kink' smooths into a curve."),
        exam="The quantitative race (straight line versus cycloid to $(\\pi, 2)$: 1.19 s versus 1.00 s) is a strong one-line justification.",
        widget={"type": "brachistochrone"},
        problems=[
            problem("q-cy-1", "Two functionals",
                    "Compare the integrands.",
                    [choice("What's the essential difference between the brachistochrone and shortest-path integrands?",
                            [opt(r"Dividing by $\sqrt{y}$: the brachistochrone weights each piece of path by $1/v$", True),
                             opt("The brachistochrone uses $y'^2$ instead of $y'$", why="Both contain $\\sqrt{1 + y'^2}$."),
                             opt("Nothing: both give straight lines", why="The $1/\\sqrt y$ weight changes the answer to a cycloid."),
                             opt("The brachistochrone has free endpoints", why="Both have fixed endpoints.")])],
                    fig={"type": "brachistochrone"}),
        ]),

    concept(
        "q-dependent-wrong", "Why do the wrong Lagrange equations make a pendulum fall freely?", 2, Q,
        r"""
The plain form $\frac{d}{dt}\frac{\partial L}{\partial\dot q} - \frac{\partial L}{\partial q} = Q_{nc}$ was derived by assuming the $\delta q_i$ are **independent** ([[c-lagrange-derivation]]), so each coefficient must vanish separately. With $(x, y)$ for a pendulum, $\delta x$ and $\delta y$ aren't independent: $x\delta x + y\delta y = 0$. Applying the plain form anyway treats the bob as a free particle, so it falls freely. The rod's force vanished because nothing in $L$ mentions the rod.

The fix: add $\lambda_i a_{ij}$ ([[c-multipliers]]) and the acceleration-level constraint ([[c-accel-constraint]]). This puts back exactly the force needed to keep $x^2 + y^2 = \ell^2$.
""",
        deeper=["c-multipliers", "c-accel-constraint", "c-lagrange-derivation", "c-gen-coords"],
        analogy=analogy("Describing a dog on a leash only by its $x$ and $y$: unless someone tells the equations about the leash, they'll let the dog run anywhere.",
                        "the leash can go slack; the rod can't. The multiplier enforces an exact equality, not an inequality."),
        exam="Count: 2 coordinates, 1 DOF. If coordinates > DOF, you must have multipliers. Write that inequality in your answer.",
        widget={"type": "constraint", "wrong": True},
        problems=[
            problem("q-dw-1", "Spot the error",
                    r"A student uses $(x, y)$, $T = \tfrac12m(\dot x^2 + \dot y^2)$, $V = -mgy$ ($y$ down), and gets $m\ddot y = mg$.",
                    [choice("What's the underlying mistake?",
                            [opt("Using the independent-coordinate form with dependent coordinates", True),
                             opt("A sign error in $V$", why="$V = -mgy$ is right for $y$ downward."),
                             opt("Forgetting $T_0$", why="Nothing is driven; $T_0 = 0$."),
                             opt("The pendulum has 2 DOF, so it should be fine", why="It has 1 DOF; $x$ and $y$ are tied by the rod.")])],
                    fig={"type": "pendulum-xy"}),
        ]),

    concept(
        "q-euler-energy", "Why does Euler's method make a frictionless pendulum gain energy?", 2, Q,
        r"""
An undamped oscillator moves around a closed loop in the $(x, v)$ state plane ([[c-state-space]]), with $E = T + V$ constant ([[p-energy-conservation]]). Euler's step $\mathbf{y}_{k+1} = \mathbf{y}_k + h\mathbf{f}(\mathbf{y}_k)$ moves along the **tangent** to that loop ([[c-euler-method]]), and a tangent line to a circle lies outside it. Every step lands a little further out, so the energy is multiplied by $1 + h^2\omega^2$ each step.

Over $N$ steps, $E_N = E_0(1 + h^2\omega^2)^N$: the error compounds. A smaller $h$ helps but never cures it; 'symplectic' variants (update $v$ first, then use the new $v$ for $x$) keep the energy bounded.
""",
        deeper=["c-euler-method", "c-state-space", "p-energy-conservation", "c-canonical"],
        analogy=analogy("Steering around a circular track by always heading straight along your current direction for a moment: each straight segment drifts outward, and you spiral out.",
                        "on a track that curves inward (a damped system), Euler's drift can be hidden or even helpful; it's a method error, not a law."),
        exam="Show the energy factor after one step algebraically: $x_1^2 + v_1^2 = (1 + h^2\\omega^2)(x_0^2 + v_0^2)$ for $\\omega = 1$. It's a three-line proof.",
        widget={"type": "euler"},
        problems=[
            problem("q-ee-1", "Compounding error",
                    r"$\ddot x = -x$, Euler with $h = 0.1$.",
                    [num("After 100 steps (t = 10 s), by what factor has the energy grown?", 1.01**100, "",
                         explain="$(1.01)^{100}\\approx 2.70$: the amplitude has grown by $\\sqrt{2.70}\\approx 1.64$."),
                     num("With $h = 0.01$ over the same 10 s (1000 steps)?", 1.0001**1000, "",
                         explain="$(1.0001)^{1000}\\approx 1.105$: better, but still drifting.")]),
        ]),

    concept(
        "q-action-newton", "Why does 'stationary action' give the same equations as F = ma?", 2, Q,
        r"""
Two derivations reach the same equation by different roads:

- **From Newton** ([[c-lagrange-derivation]]): project $m\ddot{\mathbf{r}} = \mathbf{F}$ onto each $\partial\mathbf{r}/\partial q$; you get $\frac{d}{dt}\frac{\partial T}{\partial\dot q} - \frac{\partial T}{\partial q} = Q$, and with $Q_c = -\partial V/\partial q$ this is the equation for $L = T - V$.
- **From Hamilton's principle** ([[c-hamilton-principle]]): demand that $\int L\,dt$ be stationary; the Euler–Lagrange equation ([[c-euler-lagrange]]) with $x\to t$, $y\to q$ is the same equation.

So they agree because the Euler–Lagrange operator applied to $T - V$ is exactly Newton's law in disguise. For a particle, $\frac{d}{dt}(m\dot x) + \frac{dV}{dx} = 0$ is $m\ddot x = -V'(x) = F$. The variational view adds something Newton doesn't: the equations hold in **any** coordinates, because a stationary integral doesn't care how you label the path.
""",
        deeper=["c-hamilton-principle", "c-euler-lagrange", "c-lagrange-derivation"],
        analogy=analogy("Two maps of the same city, one drawn street by street (Newton, local forces), one from a single rule like 'water takes the quickest way downhill' (action). They agree because both describe the same terrain.",
                        "the action view needs the forces to come from a potential (or the extended principle); Newton's view doesn't."),
        exam="If asked to connect them, do it for one particle in one line: E–L on $\\tfrac12m\\dot x^2 - V(x)$ gives $m\\ddot x = -V'$.",
        widget={"type": "variation", "mode": "action"},
        problems=[
            problem("q-an-1", "One line",
                    r"$L = \tfrac12m\dot x^2 - V(x)$.",
                    [choice("What does the Euler–Lagrange equation give?",
                            [opt(r"$m\ddot x = -V'(x)$, which is Newton's law with $F = -V'$", True),
                             opt(r"$m\ddot x = V'(x)$", why="$-\\partial L/\\partial x = +V'(x)$ on the left, so $m\\ddot x + V' = 0$."),
                             opt(r"$m\dot x = $ const", why="$x$ appears in $L$ through $V$."),
                             opt(r"$\tfrac12m\dot x^2 + V = $ const only", why="That's a first integral (energy), not the equation of motion itself.")])]),
        ]),
]
