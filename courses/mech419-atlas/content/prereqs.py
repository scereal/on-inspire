"""Layer 0: what MECH 419 assumes you already own, from earlier courses."""
import math
import sympy as sp
from lib import *

G = 9.81
V_ = "Vectors and kinematics"
C_ = "Calculus"
M_ = "Mechanics"
L_ = "Linear algebra"
O_ = "Differential equations"

CONCEPTS = [
    concept(
        "p-dot", "A dot product measures how much of one vector points along another", 0, V_,
        r"""
The dot product $\mathbf{F}\cdot\mathbf{u} = |\mathbf{F}||\mathbf{u}|\cos\varphi$ keeps only the part of $\mathbf{F}$ that lines up with $\mathbf{u}$. If $\mathbf{u}$ is a unit vector, the answer is simply *the component of $\mathbf{F}$ along $\mathbf{u}$*.

That is the whole idea behind work: $dW = \mathbf{F}\cdot d\mathbf{r}$ counts only the push along the motion. A force at right angles to the motion does no work at all. Analytical mechanics leans on this constantly: a [[c-gen-force|generalized force]] is $\mathbf{F}\cdot\partial\mathbf{r}/\partial q$, the part of the force that lies along the direction the point moves when $q$ changes. Constraint forces vanish from Lagrange's equations precisely because they are perpendicular to every allowed motion.
""",
        math=[r"\mathbf{F}\cdot\mathbf{u} = F_x u_x + F_y u_y + F_z u_z = |\mathbf{F}||\mathbf{u}|\cos\varphi"],
        analogy=analogy("Pushing a shopping cart: only the forward part of your push moves it. Leaning straight down on the handle does nothing for its speed.",
                        "in a real cart, pressing down changes the wheel friction. In the ideal dot product, perpendicular means exactly zero effect."),
        exam="You can look up the formula. What you can't look up is the reflex: whenever you see $\\mathbf{F}\\cdot(\\ldots)$, ask 'which part of this force lies along that direction?' That reflex finds zero terms before you compute them.",
        widget={"type": "dot"},
        problems=[
            problem("p-dot-1", "Project a force three ways",
                    r"A force $\mathbf{F} = 3\mathbf{i} + 4\mathbf{j}$ N acts on a point. Find how much of it lies along each direction.",
                    [num(r"Along $\mathbf{u} = \mathbf{i}$: what is $\mathbf{F}\cdot\mathbf{u}$?", 3, "N",
                         explain="Only the $x$ part survives: $3(1) + 4(0) = 3$ N."),
                     num(r"Along $\mathbf{u} = 0.6\mathbf{i} + 0.8\mathbf{j}$?", 3 * 0.6 + 4 * 0.8, "N",
                         explain=r"$1.8 + 3.2 = 5$ N, the full magnitude $|\mathbf{F}| = 5$: this $\mathbf{u}$ points exactly along $\mathbf{F}$."),
                     choice(r"Along $\mathbf{u} = -0.8\mathbf{i} + 0.6\mathbf{j}$, $\mathbf{F}\cdot\mathbf{u} = 0$. What does that tell you?",
                            [opt("A point moving in that direction gets no work from $\\mathbf{F}$", True),
                             opt("$\\mathbf{F}$ has no effect on the body at all", why="It still pushes; it just does no work for motion in that particular direction."),
                             opt("The force must be zero in that direction's frame", why="The force is unchanged; only its projection onto this direction is zero."),
                             opt("The calculation went wrong: a nonzero force can't give zero", why="Perpendicular vectors always give zero: $-2.4 + 2.4 = 0$.")],
                            explain="Zero projection means perpendicular. This is the test that kills constraint forces in Lagrange's equations.")],
                    fig={"type": "vectors"}),
            problem("p-dot-2", "The tension that never works",
                    r"A simple pendulum swings. The rod tension $\mathbf{T}$ points from the bob toward the pivot; the bob's velocity is tangent to its circular path.",
                    [choice("What is the power $\\mathbf{T}\\cdot\\mathbf{v}$ delivered by the tension?",
                            [opt("Zero, at every instant", True),
                             opt("Positive on the way down, negative on the way up", why="That describes gravity's power, not the tension's. Tension is along the rod; velocity is across it."),
                             opt("Equal to $Tv$", why="That would need $\\mathbf{T}$ and $\\mathbf{v}$ to be parallel. They are perpendicular."),
                             opt("It depends on the amplitude", why="Perpendicularity holds for every angle and every amplitude.")],
                            explain="The rod's pull is always across the motion. That is why Lagrange's method never needs the tension: it does no work, so it drops out.")],
                    fig={"type": "pendulum", "show": ["T", "v"]}),
        ]),

    concept(
        "p-cross-omega", "ω × r turns a spin into the velocity of a point", 0, V_,
        r"""
A rigid body spinning with angular velocity $\boldsymbol{\omega}$ carries each of its points around the axis. A point at position $\mathbf{r}$ from a point on the axis moves with velocity $\boldsymbol{\omega}\times\mathbf{r}$: its speed is $\omega$ times its distance from the axis, and its direction is perpendicular to both $\boldsymbol{\omega}$ and $\mathbf{r}$ (right-hand rule).

In the plane, $\boldsymbol{\omega} = \omega\mathbf{k}$, and the cross product just turns $\mathbf{r}$ a quarter-turn counter-clockwise and scales it by $\omega$. The order matters: $\mathbf{r}\times\boldsymbol{\omega}$ points the opposite way. MECH 419 uses this inside [[p-relative-velocity]] and in the rolling-wheel examples, where a sign slip flips the friction's generalized force.
""",
        math=[r"\mathbf{v} = \boldsymbol{\omega}\times\mathbf{r},\quad |\mathbf{v}| = \omega\, d_{\perp}",
              r"\mathbf{i}\times\mathbf{j} = \mathbf{k},\ \ \mathbf{j}\times\mathbf{k} = \mathbf{i},\ \ \mathbf{k}\times\mathbf{i} = \mathbf{j}"],
        analogy=analogy("A merry-go-round: the farther out you stand, the faster you move, always sideways to the line joining you to the centre.",
                        "the formula gives velocity relative to the axis point. If the axis itself moves (a rolling wheel's centre), add the axis velocity too."),
        exam="Write $\\boldsymbol{\\omega}$ with its sign from the sketch before multiplying (clockwise is $-\\mathbf{k}$). Most rolling-wheel sign errors start here.",
        problems=[
            problem("p-cross-1", "The bottom of a clockwise wheel",
                    r"A wheel turns clockwise with angle $\theta$ (so $\boldsymbol{\omega} = -\dot{\theta}\mathbf{k}$). The contact point $P$ sits at $\mathbf{r}_{P/C} = -r\mathbf{j}$ from the centre $C$.",
                    [choice(r"What is $\boldsymbol{\omega}\times\mathbf{r}_{P/C}$?",
                            [opt(r"$-r\dot{\theta}\,\mathbf{i}$", True),
                             opt(r"$+r\dot{\theta}\,\mathbf{i}$", why=r"That is $\mathbf{r}\times\boldsymbol{\omega}$: the order is reversed. $(-\dot\theta\mathbf{k})\times(-r\mathbf{j}) = r\dot\theta(\mathbf{k}\times\mathbf{j}) = -r\dot\theta\,\mathbf{i}$."),
                             opt(r"$-r\dot{\theta}\,\mathbf{j}$", why="The result must be perpendicular to $\\mathbf{r}$, which is along $\\mathbf{j}$."),
                             opt(r"$\mathbf{0}$", why="Only the axis point has zero spin velocity. $P$ is a distance $r$ from it.")],
                            explain=r"So $\mathbf{v}_P = \dot{x}\mathbf{i} - r\dot{\theta}\mathbf{i} = (\dot{x} - r\dot{\theta})\mathbf{i}$, exactly the expression in the Lecture 3 rolling example.")],
                    fig={"type": "rolling-disk"}),
            problem("p-cross-2", "Speed from spin",
                    "A disk spins at 4 rad/s about its fixed centre.",
                    [num("How fast does a point 0.25 m from the centre move?", 4 * 0.25, "m/s",
                         explain="$v = \\omega d = 4 \\times 0.25 = 1$ m/s.")]),
        ]),

    concept(
        "p-relative-velocity", "Velocity of one point = velocity of another + the spin carrying it around", 0, V_,
        r"""
For two points $A$ and $B$ on the same rigid body, $\mathbf{v}_B = \mathbf{v}_A + \boldsymbol{\omega}\times\mathbf{r}_{B/A}$. A pendulum hanging from a moving cart is the standard MECH 419 case: the bob's velocity is the cart's velocity plus its swing about the pivot.

With $\theta$ measured from the downward vertical, $x$ to the right and $y$ up, the swing adds $\ell\dot\theta(\cos\theta\,\mathbf{i} + \sin\theta\,\mathbf{j})$:

$$\mathbf{v}_m = (\dot x + \ell\dot\theta\cos\theta)\,\mathbf{i} + \ell\dot\theta\sin\theta\,\mathbf{j}.$$

Squaring gives $v_m^2 = \dot x^2 + 2\dot x\ell\dot\theta\cos\theta + \ell^2\dot\theta^2$. The cross term is where the cart and the pendulum *talk to each other*: it couples the two equations of motion. Lagrange needs only this velocity kinematics, never accelerations ([[c-vector-vs-analytical]]).
""",
        deeper=["p-cross-omega"],
        math=[r"\mathbf{v}_B = \mathbf{v}_A + \boldsymbol{\omega}\times\mathbf{r}_{B/A}"],
        analogy=analogy("Walking down the aisle of a moving train: your ground velocity is the train's velocity plus your walking velocity.",
                        "here the 'walking' is a swing, so its direction turns with $\\theta$. That is why the cross term carries $\\cos\\theta$ and isn't constant."),
        exam="Draw the two velocity arrows tip to tail and read off the angle between them: the cross term is $2|\\mathbf{v}_A||\\mathbf{v}_{rel}|\\cos(\\text{angle})$. That catches a wrong sin/cos instantly.",
        problems=[
            problem("p-relvel-1", "Speed of the bob on a moving cart",
                    r"A cart moves with $\dot x$; a pendulum of length $\ell$ hangs from it at angle $\theta$ from the downward vertical.",
                    [sym_choice(r"What is $v_m^2$, the bob's speed squared?",
                                xd**2 + 2 * xd * l * thd * sp.cos(th) + l**2 * thd**2,
                                [(xd**2 + 2 * xd * l * thd * sp.cos(th) + l**2 * thd**2, ""),
                                 (xd**2 + l**2 * thd**2, "This assumes the cart's motion and the swing are always perpendicular. They are only perpendicular when the rod is horizontal."),
                                 (xd**2 + 2 * xd * l * thd * sp.sin(th) + l**2 * thd**2, "The swing velocity's horizontal part is $\\ell\\dot\\theta\\cos\\theta$ (at the bottom, $\\theta = 0$, the swing is fully horizontal)."),
                                 ((xd + l * thd)**2, "Adding speeds as numbers only works when the two velocities are parallel.")],
                                explain="The cross term $2\\dot x\\ell\\dot\\theta\\cos\\theta$ is what couples the cart and pendulum equations.")],
                    fig={"type": "cart-pendulum"}),
            problem("p-relvel-2", "Two moments of the swing",
                    r"Take $\dot x = 1$ m/s, $\ell = 0.5$ m, $\dot\theta = 2$ rad/s.",
                    [num(r"At $\theta = 0$ (bob straight below), how fast is the bob moving?", 1 + 0.5 * 2, "m/s",
                         explain="Both velocities point right: $1 + 1 = 2$ m/s."),
                     num(r"At $\theta = 90°$ (rod horizontal), how fast is it moving?", math.sqrt(1 + 1), "m/s",
                         explain="Now the swing is vertical, perpendicular to the cart: $\\sqrt{1^2 + 1^2} \\approx 1.414$ m/s.")]),
        ]),

    concept(
        "p-polar", "In polar coordinates, velocity has a stretch part and a swing part", 0, V_,
        r"""
Write a position as $\mathbf{r} = r\,\mathbf{e}_r$. The unit vector $\mathbf{e}_r$ turns as the point moves, and $\dot{\mathbf{e}}_r = \dot\theta\,\mathbf{e}_\theta$. So

$$\dot{\mathbf{r}} = \dot r\,\mathbf{e}_r + r\dot\theta\,\mathbf{e}_\theta,\qquad v^2 = \dot r^2 + r^2\dot\theta^2.$$

The first part stretches the radius; the second swings around. They are perpendicular, so their squares simply add. MECH 419 uses this for the satellite (Lecture 6), the pendulum with a stretchy string (Lecture 7) and the mass in a spinning slot.
""",
        deeper=["p-relative-velocity"],
        math=[r"\dot{\mathbf{r}} = \dot r\,\mathbf{e}_r + r\dot\theta\,\mathbf{e}_\theta"],
        analogy=analogy("Swinging a lasso while letting rope out: paying out rope ($\\dot r$) and swinging it ($r\\dot\\theta$) are perpendicular motions.",
                        "$\\mathbf{e}_r$ and $\\mathbf{e}_\\theta$ turn as you move, so you can't treat them like fixed $\\mathbf{i}, \\mathbf{j}$ when you differentiate again. Accelerations get extra terms."),
        exam="Check units: $r\\dot\\theta$ is a speed, $\\dot\\theta$ alone is not. A missing $r$ in $T$ is the most common polar error.",
        problems=[
            problem("p-polar-1", "Kinetic energy of a stretchy pendulum",
                    r"A mass $m$ hangs on a spring of length $r$ at angle $\theta$.",
                    [sym_choice("What is its kinetic energy $T$?", m * (rd**2 + r**2 * thd**2) / 2,
                                [(m * (rd**2 + r**2 * thd**2) / 2, ""),
                                 (m * (rd**2 + r * thd**2) / 2, "Check units: $r\\dot\\theta^2$ isn't a speed squared. The swing speed is $r\\dot\\theta$, so it's squared as $r^2\\dot\\theta^2$."),
                                 (m * (rd**2 + thd**2) / 2, "$\\dot\\theta$ is an angular rate, not a speed. Multiply by $r$."),
                                 (m * r**2 * thd**2 / 2, "This drops the stretching motion $\\dot r$.")])],
                    fig={"type": "spring-pendulum"}),
            problem("p-polar-2", "Stretch and swing together",
                    r"At some instant $r = 2$ m, $\dot r = 3$ m/s and $\dot\theta = 2$ rad/s.",
                    [num("What is the speed?", math.hypot(3, 4), "m/s",
                         explain="$\\sqrt{3^2 + (2\\cdot 2)^2} = 5$ m/s.")]),
        ]),

    concept(
        "p-rolling", "Rolling without slipping: the contact point is momentarily at rest", 0, V_,
        r"""
A wheel rolls without slipping when the point touching the ground has zero velocity. With centre speed $\dot x$ and spin rate $\dot\theta$ (radius $r$):

$$v_P = \dot x - r\dot\theta = 0\quad\Rightarrow\quad x = r\theta.$$

Two consequences matter in MECH 419. First, the no-slip condition is a constraint, so it removes a degree of freedom ([[c-dof]]). Second, friction at the contact point acts on a point that isn't moving, so **it does no work**. That is why it disappears from the generalized forces in [[c-rolling-lagrange]]. If the wheel slips, $\dot x \ne r\dot\theta$ and friction does work.
""",
        deeper=["p-cross-omega"],
        math=[r"v_P = \dot x - r\dot\theta",
              r"\text{no slip: } \dot x = r\dot\theta,\ \ v_{\text{top}} = 2\dot x"],
        analogy=analogy("A walking foot: while it's planted, it doesn't move, so the ground's grip on it does no work even though it pushes.",
                        "a foot stays planted for a while. The wheel's contact point is at rest for only an instant: a new point touches down at every moment."),
        exam="Before writing $Q_{nc}$ for friction, compute the contact point's velocity. If it's zero, friction drops out and you can stop there.",
        widget={"type": "rolling"},
        problems=[
            problem("p-roll-1", "A rolling wheel's points",
                    "A wheel of radius 0.3 m rolls without slipping at 6 m/s.",
                    [num("What is its spin rate?", 6 / 0.3, "rad/s", explain="$\\dot\\theta = \\dot x / r = 20$ rad/s."),
                     num("How fast is the top of the wheel moving?", 12, "m/s",
                         explain="Centre speed plus spin: $6 + 0.3\\times 20 = 12$ m/s, twice the centre speed."),
                     num("How fast is the contact point moving?", 0, "m/s", tol=0.001,
                         explain="$6 - 0.3\\times 20 = 0$. That is the definition of no slip.")],
                    fig={"type": "rolling-disk"}),
            problem("p-roll-2", "When the wheel slips",
                    r"The centre moves at $\dot x = 2$ m/s but $r\dot\theta = 1.5$ m/s.",
                    [num("How fast does the contact point slide over the ground?", 0.5, "m/s"),
                     choice("Does the friction force do work now?",
                            [opt("Yes, negative work: it opposes the sliding", True),
                             opt("No, friction at a contact point never does work", why="Only when the contact point is at rest. Here it slides at 0.5 m/s."),
                             opt("Yes, positive work: it speeds the wheel up", why="Kinetic friction opposes the sliding, so it removes energy overall."),
                             opt("Only if the ground is moving", why="The ground is fixed; the contact point itself is moving.")],
                            explain="That's why the slipping wheel in Lecture 3 has $Q_{x,nc} = -f$ and $Q_{\\theta,nc} = fr$: friction enters the equations.")]),
        ]),

    concept(
        "p-partial", "A partial derivative wiggles one input and freezes the rest", 0, C_,
        r"""
$\partial f/\partial x$ asks how $f$ changes when only $x$ moves and every other input is held fixed. In Lagrangian mechanics, $T(q, \dot q)$ is treated as a function of **two independent sets of inputs**: the coordinates $q$ and the speeds $\dot q$. So $\partial T/\partial\dot\theta$ freezes $\theta$, and $\partial T/\partial\theta$ freezes $\dot\theta$.

This feels odd, because $\dot\theta$ *is* the time derivative of $\theta$. But at a single instant, position and speed are independent facts: knowing where a pendulum is says nothing about how fast it's moving. Time only links them later, through the total derivative $d/dt$ ([[p-chain-multi]]).
""",
        math=[r"T = \tfrac12(M+m)\dot x^2 + \tfrac12 m\ell^2\dot\theta^2 + m\dot x\ell\dot\theta\cos\theta",
              r"\frac{\partial T}{\partial\theta} = -m\dot x\ell\dot\theta\sin\theta,\qquad \frac{\partial T}{\partial\dot\theta} = m\ell^2\dot\theta + m\dot x\ell\cos\theta"],
        analogy=analogy("A mixing desk: the partial derivative is how the sound changes when you move one fader with your hands off all the others.",
                        "in a real song the faders move together over time. That combined change is the total derivative, not the partial."),
        exam="Before differentiating, underline every place the variable appears. $\\theta$ often hides inside a $\\cos\\theta$ multiplying velocities, and that term is easy to miss.",
        problems=[
            problem("p-partial-1", "Differentiate the cart-pendulum energy",
                    r"$T = \tfrac12(M+m)\dot x^2 + \tfrac12 m\ell^2\dot\theta^2 + m\dot x\ell\dot\theta\cos\theta$.",
                    [sym_choice(r"What is $\partial T/\partial\theta$?", -m * xd * l * thd * sp.sin(th),
                                [(-m * xd * l * thd * sp.sin(th), ""),
                                 (m * xd * l * thd * sp.sin(th), "The derivative of $\\cos\\theta$ is $-\\sin\\theta$."),
                                 (sp.Integer(0), "$T$ depends on $\\theta$ through $\\cos\\theta$ in the coupling term."),
                                 (-m * xd * l * thd * sp.sin(th) + m * l**2 * thd, "$\\dot\\theta$ is held fixed: $\\tfrac12 m\\ell^2\\dot\\theta^2$ has no $\\theta$ in it.")]),
                     sym_choice(r"What is $\partial T/\partial\dot\theta$?", m * l**2 * thd + m * xd * l * sp.cos(th),
                                [(m * l**2 * thd + m * xd * l * sp.cos(th), ""),
                                 (m * l**2 * thd, "The coupling term $m\\dot x\\ell\\dot\\theta\\cos\\theta$ also contains $\\dot\\theta$."),
                                 (m * l**2 * thd + m * xd * l * sp.cos(th) - m * xd * l * thd * sp.sin(th), "$\\theta$ is frozen here, so $\\cos\\theta$ is a constant. Don't differentiate it."),
                                 (m * l**2 * thd / 2 + m * xd * l * sp.cos(th), "$\\frac{d}{d\\dot\\theta}\\tfrac12\\dot\\theta^2 = \\dot\\theta$: the ½ cancels.")])],
                    fig={"type": "cart-pendulum"}),
        ]),

    concept(
        "p-chain-multi", "A total time derivative adds up every route by which time sneaks in", 0, C_,
        r"""
If $f$ depends on $q(t)$, $\dot q(t)$ and $t$ itself, then

$$\frac{df}{dt} = \sum_i\frac{\partial f}{\partial q_i}\dot q_i + \sum_i\frac{\partial f}{\partial\dot q_i}\ddot q_i + \frac{\partial f}{\partial t}.$$

Each term is one route through which time changes $f$. This is exactly how $\frac{d}{dt}\left(\frac{\partial T}{\partial\dot q}\right)$ produces both the $\ddot q$ terms and the velocity-squared terms (centripetal-like terms such as $m\ell\dot\theta^2\sin\theta$) in Lagrange's equations. Forgetting a route is the classic way to lose a term.
""",
        deeper=["p-partial"],
        math=[r"\frac{d}{dt}\big[m\ell\dot\theta\cos\theta\big] = m\ell\ddot\theta\cos\theta - m\ell\dot\theta^2\sin\theta"],
        analogy=analogy("The temperature you feel on a road trip changes because you drive somewhere warmer (the route terms) and because the day heats up (the explicit $\\partial/\\partial t$).",
                        "here the routes aren't independent: $q$ and $\\dot q$ are tied by time, which is why a $\\ddot q$ appears when $\\dot q$ itself changes."),
        exam="Count factors: every term from differentiating $\\cos\\theta$ with respect to time must carry a $\\dot\\theta$. A term with $\\sin\\theta$ but no extra $\\dot\\theta$ is a lost chain factor.",
        problems=[
            problem("p-chain-1", "The time derivative inside the x-equation",
                    r"Differentiate $p_x = (M+m)\dot x + m\ell\dot\theta\cos\theta$ with respect to time.",
                    [sym_choice(r"What is $\dot p_x$?",
                                (M + m) * xdd + m * l * thdd * sp.cos(th) - m * l * thd**2 * sp.sin(th),
                                [((M + m) * xdd + m * l * thdd * sp.cos(th) - m * l * thd**2 * sp.sin(th), ""),
                                 ((M + m) * xdd + m * l * thdd * sp.cos(th), "$\\cos\\theta$ also changes with time: it contributes $-\\sin\\theta\\,\\dot\\theta$ times $m\\ell\\dot\\theta$."),
                                 ((M + m) * xdd + m * l * thdd * sp.cos(th) + m * l * thd**2 * sp.sin(th), "$\\frac{d}{dt}\\cos\\theta = -\\sin\\theta\\,\\dot\\theta$: the sign is negative."),
                                 ((M + m) * xdd + m * l * thdd * sp.cos(th) - m * l * thd * sp.sin(th), "Chain rule: $\\frac{d}{dt}\\cos\\theta = -\\sin\\theta\\cdot\\dot\\theta$. The extra $\\dot\\theta$ makes it $\\dot\\theta^2$.")],
                                explain="The $-m\\ell\\dot\\theta^2\\sin\\theta$ term is the pendulum's centripetal pull showing up in the cart's equation.")]),
        ]),

    concept(
        "p-taylor", "Near a point, every smooth function looks like a parabola", 0, C_,
        r"""
Taylor's theorem: $f(q) \approx f(a) + f'(a)(q-a) + \tfrac12 f''(a)(q-a)^2 + \ldots$ The closer you stay to $a$, the better the first few terms do.

Two expansions do most of the work in MECH 419: $\cos\theta\approx 1 - \theta^2/2$ and $\sin\theta\approx\theta$. In [[c-linearization]], the potential energy is expanded to second order about equilibrium. The first-order term vanishes (equilibrium means zero slope), so what's left is a parabola, $V\approx V_e + \tfrac12 K q^2$, whose slope $Kq$ is a *linear* restoring force. The calculus of variations derivation ([[c-euler-lagrange]]) uses the same first-order expansion on $F(x, y, y')$.
""",
        math=[r"\cos\theta = 1 - \frac{\theta^2}{2!} + \frac{\theta^4}{4!} - \cdots", r"-mg\ell\cos\theta \approx -mg\ell + \tfrac12 mg\ell\,\theta^2"],
        analogy=analogy("A street map of your neighbourhood is flat even though the Earth is round: zoomed in far enough, curvature is invisible.",
                        "walk far enough (swing to large angles) and the flat map misleads. A real pendulum's period grows with amplitude; the linear model's doesn't."),
        exam="When linearizing, expand to second order in $V$ but only first order in the forces. If your $V$ has a $\\theta^2$ term with no ½ check the $2!$ in the denominator.",
        widget={"type": "taylor"},
        problems=[
            problem("p-taylor-1", "The pendulum's potential near the bottom",
                    r"$V(\theta) = -mg\ell\cos\theta$, with the datum at the pivot.",
                    [sym_choice(r"What is $V$ to second order in $\theta$?", -m * g * l + m * g * l * th**2 / 2,
                                [(-m * g * l + m * g * l * th**2 / 2, ""),
                                 (-m * g * l + m * g * l * th**2, "$\\cos\\theta\\approx 1 - \\theta^2/2$: the $2!$ gives the ½."),
                                 (-m * g * l - m * g * l * th**2 / 2, "Minus times minus: $-mg\\ell(1 - \\theta^2/2) = -mg\\ell + \\tfrac12 mg\\ell\\theta^2$."),
                                 (m * g * l * th, "That's a first-order guess; $\\cos$ has no linear term about 0.")],
                                explain="So the stiffness is $K = mg\\ell$: the pendulum acts like a spring of that stiffness for small swings.")]),
            problem("p-taylor-2", "How wrong is sin θ ≈ θ?",
                    r"At $\theta = 0.5$ rad (about 29°), compare $\sin\theta$ with $\theta$.",
                    [num("What is the relative error $(\\theta - \\sin\\theta)/\\sin\\theta$, in percent?",
                         100 * (0.5 - math.sin(0.5)) / math.sin(0.5), "%", tol=0.02,
                         explain="$\\sin 0.5 = 0.4794$, so the error is about 4.3%. At 0.1 rad it's under 0.2%.")]),
        ]),

    concept(
        "p-ibp", "Integration by parts moves a derivative to the other factor, for a toll at the boundary", 0, C_,
        r"""
$$\int_{x_1}^{x_2} u\,v'\,dx = \Big[u\,v\Big]_{x_1}^{x_2} - \int_{x_1}^{x_2} u'\,v\,dx.$$

In [[c-euler-lagrange]], the variation brings a term $\int \frac{\partial F}{\partial y'}\eta'\,dx$, with a derivative on the arbitrary bump $\eta$. Integration by parts moves the derivative onto $\partial F/\partial y'$, so that every term multiplies $\eta$ itself. The boundary term $\big[\eta\,\partial F/\partial y'\big]$ vanishes because the endpoints are pinned: $\eta(x_1) = \eta(x_2) = 0$.
""",
        math=[r"\int_{x_1}^{x_2}\frac{\partial F}{\partial y'}\eta'\,dx = \Big[\eta\frac{\partial F}{\partial y'}\Big]_{x_1}^{x_2} - \int_{x_1}^{x_2}\eta\frac{d}{dx}\Big(\frac{\partial F}{\partial y'}\Big)dx"],
        analogy=analogy("Passing a hot potato: the derivative can be handed to the other factor, but you pay a toll at each border. Pin the borders ($\\eta = 0$) and the toll is zero.",
                        "if an endpoint is free, the toll doesn't vanish, and setting it to zero becomes an extra 'natural' boundary condition."),
        exam="Say out loud why the boundary term dies. Examiners often ask exactly that sentence.",
        problems=[
            problem("p-ibp-1", "Move the derivative off η",
                    r"Let $\eta(0) = \eta(1) = 0$. Simplify $\displaystyle\int_0^1 \eta'(x)\,2x\,dx$.",
                    [choice("What does integration by parts give?",
                            [opt(r"$-\displaystyle\int_0^1 2\eta\,dx$", True),
                             opt(r"$\displaystyle\int_0^1 2\eta\,dx$", why="The formula has a minus sign: $[uv] - \\int u'v$."),
                             opt(r"$0$, always", why="Only the boundary term is zero. The remaining integral depends on $\\eta$."),
                             opt(r"$\big[2x\eta\big]_0^1$ only", why="That boundary term is zero; the integral $-\\int 2\\eta\\,dx$ remains.")],
                            explain="$[2x\\eta]_0^1 = 0$ because $\\eta$ vanishes at both ends, leaving $-\\int_0^1 2\\eta\\,dx$.")]),
        ]),

    concept(
        "p-extremum", "At a smooth peak or valley the slope is zero; curvature tells you which", 0, C_,
        r"""
A smooth function has $f'(a) = 0$ at every peak, valley and flat inflection. The second derivative decides: $f''(a) > 0$ is a valley (minimum), $f''(a) < 0$ a peak (maximum), and $f''(a) = 0$ is inconclusive.

For a conservative mechanical system, the equilibria are where $\partial V/\partial q = 0$ ([[c-static-eq]]). Valleys are stable: nudge the system and it returns. Peaks are unstable. In a spinning system the landscape to inspect is $V - T_0$ ([[c-dynamic-eq]]), not $V$ alone.
""",
        math=[r"f'(a) = 0,\quad f''(a) > 0 \Rightarrow \text{minimum (stable)}"],
        analogy=analogy("A marble on hilly ground comes to rest only on flat spots: in a dip it stays, on a hilltop the slightest breath rolls it away.",
                        "with rotation, the 'ground' the marble feels is $V - T_0$, which can turn the bottom of the valley into a hilltop."),
        exam="Always report stability with the equilibrium: the second derivative takes one line and often earns a separate mark.",
        problems=[
            problem("p-ext-1", "Pendulum equilibria",
                    r"$V(\theta) = -mg\ell\cos\theta$.",
                    [choice("Where is $dV/d\\theta = 0$?",
                            [opt(r"$\theta = 0$ and $\theta = \pi$", True),
                             opt(r"$\theta = 0$ only", why="$mg\\ell\\sin\\theta = 0$ also at $\\theta = \\pi$ (balanced upside-down)."),
                             opt(r"$\theta = \pm\pi/2$", why="There $\\sin\\theta = \\pm 1$, the slope is largest."),
                             opt("Everywhere: gravity is conservative", why="Conservative doesn't mean flat. Equilibria are only where the slope vanishes.")]),
                     choice(r"Which is stable?",
                            [opt(r"$\theta = 0$, because $V'' = mg\ell\cos 0 > 0$", True),
                             opt(r"$\theta = \pi$, because $V$ is highest there", why="Highest $V$ is a peak: unstable."),
                             opt("Both, because $V' = 0$ at both", why="$V' = 0$ finds equilibria; $V''$ decides stability."),
                             opt("Neither: a pendulum always oscillates", why="Oscillating about $\\theta = 0$ is what stability means.")])],
                    fig={"type": "pendulum"}),
            problem("p-ext-2", "Find the valley",
                    r"$V(x) = x^3 - 3x$.",
                    [num("At which $x$ is the stable equilibrium?", 1, "",
                         explain="$V' = 3x^2 - 3 = 0$ at $x = \\pm1$; $V'' = 6x > 0$ only at $x = 1$.")]),
        ]),

    concept(
        "p-newton", "Newton: net force equals mass times acceleration, body by body", 0, M_,
        r"""
The vectorial approach: isolate each body, draw its free-body diagram with every force (including the unknown constraint and reaction forces), and write $m\mathbf{a} = \sum\mathbf{F}$. Internal forces appear in equal and opposite pairs on the two bodies they connect.

Its strength is that every force comes out of the calculation. Its cost is more unknowns, and you need **acceleration** kinematics. Lecture 1's comparison ([[c-vector-vs-analytical]]) is a comparison against this method. D'Alembert's trick rewrites it as $\sum\mathbf{F} + (-m\mathbf{a}) = 0$: treat $-m\mathbf{a}$ as an 'inertia force' and the dynamics problem becomes a statics problem.
""",
        math=[r"m_j\ddot{\mathbf{r}}_j = \mathbf{F}_j", r"\textstyle\sum\mathbf{F} + (-m\mathbf{a}) = \mathbf{0}\ \text{(D'Alembert)}"],
        analogy=analogy("Bookkeeping every account separately: each transfer between two accounts shows up twice, once as a debit, once as a credit (action and reaction).",
                        "Lagrange is like consolidated accounts: internal transfers cancel and never need recording, but then you can't read them off either."),
        exam="On an open-book exam, a Newton check of one equation (say the pendulum's tangential equation) is a fast way to catch a sign error in a Lagrange derivation.",
        problems=[
            problem("p-newton-1", "Pendulum by Newton",
                    "A simple pendulum of length $\\ell$ swings at angle $\\theta$. Use the tangential component of $m\\mathbf{a} = \\sum\\mathbf{F}$.",
                    [sym_choice("What is the equation of motion?", l * thdd + g * sp.sin(th),
                                [(l * thdd + g * sp.sin(th), ""),
                                 (l * thdd - g * sp.sin(th), "Gravity's tangential part pulls back toward $\\theta = 0$: it is $-mg\\sin\\theta$."),
                                 (l * thdd + g * th, "That's the small-angle version. The exact equation keeps $\\sin\\theta$."),
                                 (thdd + g * sp.sin(th), "Tangential acceleration is $\\ell\\ddot\\theta$, not $\\ddot\\theta$.")], eq=True)],
                    fig={"type": "pendulum"}),
            problem("p-newton-2", "Counting unknowns",
                    "Solve the cart-pendulum with Newton: the cart (rolling on a smooth floor) and the bob, connected by a massless rod.",
                    [num("How many unknowns at an instant? (accelerations plus unknown forces)", 4, "",
                         explain="$\\ddot x$, $\\ddot\\theta$, the rod force and the floor's normal force. Lagrange needs only 2 equations for $\\ddot x$ and $\\ddot\\theta$.",
                         hint="The rod force and the floor force are unknown too.")],
                    fig={"type": "cart-pendulum"}),
        ]),

    concept(
        "p-work", "Work is force times distance moved along it; a moment works through an angle", 0, M_,
        r"""
$W = \int\mathbf{F}\cdot d\mathbf{r}$ for a force and $W = \int M\,d\theta$ for a moment in planar motion. The rate of working is the power, $P = \mathbf{F}\cdot\mathbf{v}$.

Two consequences carry MECH 419. A force applied at a point that doesn't move does no work (rolling contact, a fixed pin). A force perpendicular to its point's motion does no work (a smooth surface's normal force, a rod's tension). [[c-gen-force|Virtual work]] is the same idea applied to imagined displacements.
""",
        deeper=["p-dot"],
        math=[r"W = \int\mathbf{F}\cdot d\mathbf{r},\qquad W = \int_{\theta_1}^{\theta_2}M\,d\theta,\qquad P = \mathbf{F}\cdot\mathbf{v}"],
        analogy=analogy("A taxi meter that ticks only for distance travelled in the direction of the push.",
                        "the meter can run backwards: moving against the force earns negative work."),
        exam="List every force on the FBD and mark which ones do no work. Those are the ones Lagrange lets you ignore.",
        problems=[
            problem("p-work-1", "Work of a moment",
                    "A constant moment of 5 N·m turns a body through 0.4 rad.",
                    [num("How much work does it do?", 2, "J", explain="$W = M\\Delta\\theta = 5\\times 0.4 = 2$ J.")]),
            problem("p-work-2", "Which forces do work?",
                    "A block slides down a fixed, rough incline.",
                    [choice("Which force does no work?",
                            [opt("The normal force", True),
                             opt("Gravity", why="Gravity has a component along the incline, the direction of motion."),
                             opt("Friction", why="Friction acts along the motion (against it): it does negative work."),
                             opt("None of them: all three do work", why="The normal force is perpendicular to the motion.")])]),
        ]),

    concept(
        "p-potential", "A conservative force is the downhill slope of a potential energy", 0, M_,
        r"""
A force is conservative when its work depends only on the start and end points. Then it can be written as the downhill slope of a potential: $\mathbf{F} = -\nabla V$. In generalized coordinates, its generalized force is $Q_c = -\partial V/\partial q$.

The two potentials you'll use most: gravity, $V_g = mgh$ (height measured up from any datum), and a linear spring, $V_s = \tfrac12 k\,(\text{stretch})^2$. The datum is free: adding a constant to $V$ changes nothing, because only derivatives of $V$ enter the equations.
""",
        deeper=["p-work"],
        math=[r"\mathbf{F} = -\nabla V,\qquad Q_{c} = -\frac{\partial V}{\partial q}", r"V_g = mgh,\qquad V_s = \tfrac12 k\,\delta^2"],
        analogy=analogy("Water on a contour map flows down the steepest slope, faster where the contour lines bunch up. A conservative force is the slope of a map like that.",
                        "friction has no such map: its work depends on the route, so no $V$ exists for it, and it stays in $Q_{nc}$."),
        exam="State your datum next to every $V$. Then a sign check is quick: $V$ must increase as the mass rises or the spring stretches.",
        problems=[
            problem("p-pot-1", "Pendulum potential from the pivot",
                    r"A pendulum bob hangs at angle $\theta$ from the downward vertical. Use the pivot as the datum for gravity.",
                    [sym_choice("What is $V_g$?", -m * g * l * sp.cos(th),
                                [(-m * g * l * sp.cos(th), ""),
                                 (m * g * l * sp.cos(th), "The bob is below the pivot, so its height is $-\\ell\\cos\\theta$."),
                                 (m * g * l * (1 - sp.cos(th)), "That is the potential with the datum at the lowest point, also valid, but the question fixed the datum at the pivot."),
                                 (-m * g * l * sp.sin(th), "The height below the pivot is $\\ell\\cos\\theta$ when $\\theta$ is measured from the vertical.")]),
                     sym_choice(r"So what is $Q_{\theta,c} = -\partial V/\partial\theta$?", -m * g * l * sp.sin(th),
                                [(-m * g * l * sp.sin(th), ""),
                                 (m * g * l * sp.sin(th), "Gravity pulls the pendulum back toward $\\theta = 0$, so for $\\theta > 0$ the generalized force is negative."),
                                 (-m * g * sp.sin(th), "A generalized force for an angle has units of moment: N·m. Keep the $\\ell$."),
                                 (m * g * l * sp.cos(th), "Differentiate: $\\frac{d}{d\\theta}(-mg\\ell\\cos\\theta) = mg\\ell\\sin\\theta$, then take the minus sign.")])],
                    fig={"type": "pendulum"}),
            problem("p-pot-2", "The spring's stretch",
                    r"A pendulum hangs on a spring of natural length $\ell_0$; its current length is $r$.",
                    [sym_choice("What is the spring's potential energy?", k * (r - l0)**2 / 2,
                                [(k * (r - l0)**2 / 2, ""),
                                 (k * r**2 / 2, "The spring stores energy only for its stretch beyond the natural length, $r - \\ell_0$."),
                                 (k * (r - l0) / 2, "Spring energy is quadratic in the stretch."),
                                 (k * (r**2 - l0**2) / 2, "Square the stretch, not the difference of squares.")])],
                    fig={"type": "spring-pendulum"}),
        ]),

    concept(
        "p-ke-rigid", "A rigid body's kinetic energy = moving its centre + spinning about it", 0, M_,
        r"""
For planar motion, $T = \tfrac12 m v_G^2 + \tfrac12 I_G\omega^2$: one bill for the centre of mass flying along, one for the spin about it. In 3D about a fixed point $O$, $T = \tfrac12\boldsymbol{\omega}^T\mathbf{I}_O\boldsymbol{\omega}$, which Lecture 5 uses for the spinning rod.

A rolling disk without slip (radius $r$, $I_G = \tfrac12 mr^2$, $\omega = \dot x/r$) has $T = \tfrac12 m\dot x^2 + \tfrac14 m\dot x^2 = \tfrac34 m\dot x^2$. The spin adds half again to the translational energy.
""",
        deeper=["p-inertia", "p-rolling"],
        math=[r"T = \tfrac12 m v_G^2 + \tfrac12 I_G\omega^2", r"T = \tfrac12\boldsymbol{\omega}^T\mathbf{I}_O\boldsymbol{\omega}\ \ (\text{fixed point } O)"],
        analogy=analogy("A thrown frisbee pays two energy bills: one for flying, one for spinning.",
                        "the clean split works only about the centre of mass (or a fixed point). About any other moving point there's an extra cross term."),
        exam="Write $T$ term by term with each body labelled. Most errors are a forgotten spin term or the wrong $I$.",
        problems=[
            problem("p-ke-1", "Rolling disk energy",
                    r"A uniform disk (mass $m$, radius $r$) rolls without slipping with centre speed $\dot x$.",
                    [sym_choice("What is $T$?", sp.Rational(3, 4) * m * xd**2,
                                [(sp.Rational(3, 4) * m * xd**2, ""),
                                 (m * xd**2 / 2, "That's only the translation. The disk also spins at $\\dot x/r$."),
                                 (m * xd**2, "That uses $I = mr^2$ (a hoop). A uniform disk has $I_G = \\tfrac12 mr^2$."),
                                 (m * xd**2 / 4, "That's only the spin part; add the translation $\\tfrac12 m\\dot x^2$.")])],
                    fig={"type": "rolling-disk"}),
            problem("p-ke-2", "A rod swinging about its end",
                    r"A uniform rod (mass $m$, length $\ell$) pivots about one end at rate $\dot\theta$.",
                    [sym_choice("What is $T$?", m * l**2 * thd**2 / 6,
                                [(m * l**2 * thd**2 / 6, ""),
                                 (m * l**2 * thd**2 / 2, "That treats all the mass as sitting at the tip."),
                                 (m * l**2 * thd**2 / 24, "That's spin about the centre only; the centre also moves at $\\tfrac{\\ell}{2}\\dot\\theta$."),
                                 (m * l**2 * thd**2 / 3, "$T = \\tfrac12 I_O\\dot\\theta^2$ with $I_O = \\tfrac13 m\\ell^2$: don't drop the ½.")])]),
        ]),

    concept(
        "p-inertia", "Moment of inertia: mass weighted by squared distance from the axis", 0, M_,
        r"""
$I = \int d^2\,dm$, where $d$ is each bit of mass's distance from the axis. Far-out mass counts much more. The parallel-axis theorem shifts the axis: $I_O = I_G + m d^2$.

Standard values used in MECH 419: uniform disk about its centre, $\tfrac12 mr^2$; uniform rod about its end, $\tfrac13 m\ell^2$ ($\tfrac1{12}m\ell^2$ about its centre). A thin rod about its own long axis has $I\approx 0$, which is why the bar-fixed inertia matrix in Lecture 5 has a zero in its first entry.
""",
        math=[r"I_O = I_G + m d^2", r"I_{\text{rod, end}} = \tfrac1{12}m\ell^2 + m\big(\tfrac{\ell}{2}\big)^2 = \tfrac13 m\ell^2"],
        analogy=analogy("A figure skater pulling her arms in: the same mass, closer to the axis, means less inertia and a faster spin.",
                        "the skater changes $I$ by moving mass; a rigid body's $I$ about a given axis is fixed."),
        exam="Keep a table of the 4–5 standard $I$ values in your notes; the parallel-axis shift is where marks get lost, so write $md^2$ explicitly.",
        problems=[
            problem("p-inertia-1", "Shift the axis to the end",
                    "A uniform rod has mass 3 kg and length 2 m.",
                    [num("What is its moment of inertia about one end?", 3 * 4 / 3, "kg·m²",
                         explain="$\\tfrac1{12}(3)(4) + 3(1)^2 = 1 + 3 = 4$ kg·m²."),
                     choice("What is its moment of inertia about its own long axis (treat it as thin)?",
                            [opt("About zero", True),
                             opt("$\\tfrac13 m\\ell^2$", why="That's about a perpendicular axis through the end."),
                             opt("$\\tfrac1{12}m\\ell^2$", why="That's about a perpendicular axis through the centre."),
                             opt("$m\\ell^2$", why="All the mass lies on the long axis, at zero distance from it.")],
                            explain="That's why $\\mathbf{I}_O$ for the spinning rod in Lecture 5 has a 0 in the bar-axis entry.")]),
        ]),

    concept(
        "p-energy-conservation", "When only conservative forces do work, T + V stays constant", 0, M_,
        r"""
The work–energy theorem says $\Delta T = W$. Split the work into a conservative part ($-\Delta V$) and the rest: $\Delta(T + V) = W_{nc}$. If nothing non-conservative does work, $E = T + V$ is constant.

The brachistochrone (Lecture 8) starts here: a bead released from rest and dropping a height $y$ has $\tfrac12 mv^2 = mgy$, so $v = \sqrt{2gy}$ whatever path it takes. In spinning systems, $E$ can fail to be conserved even with no friction, because a motor keeping the spin rate fixed does work; [[c-h-conservation]] covers this.
""",
        deeper=["p-potential", "p-work"],
        math=[r"\Delta(T + V) = W_{nc}", r"v = \sqrt{2gy}"],
        analogy=analogy("A bank account with only internal transfers between 'checking' ($T$) and 'savings' ($V$): the total never changes.",
                        "if the bank charges fees (friction) or someone keeps topping up (a motor holding a disk at fixed $\\Omega$), the total moves."),
        exam="Use energy as a check on any equation of motion: multiply the EOM by $\\dot q$ and see whether it's $\\frac{d}{dt}(T+V) = 0$.",
        problems=[
            problem("p-energy-1", "Speed after a frictionless drop",
                    "A bead starts from rest and slides 0.8 m down (vertically) along a frictionless wire of any shape.",
                    [num("How fast is it moving?", math.sqrt(2 * G * 0.8), "m/s", explain="$v = \\sqrt{2(9.81)(0.8)}\\approx 3.96$ m/s.")],
                    fig={"type": "brachistochrone"}),
            problem("p-energy-2", "Pendulum at the bottom",
                    "A 1 m pendulum is released from rest at 60°.",
                    [num("How fast is the bob moving at the bottom?", math.sqrt(2 * G * 1 * (1 - math.cos(math.radians(60)))), "m/s",
                         explain="It drops $\\ell(1 - \\cos 60°) = 0.5$ m, so $v = \\sqrt{2(9.81)(0.5)}\\approx 3.13$ m/s.")],
                    fig={"type": "pendulum"}),
        ]),

    concept(
        "p-quadratic-form", "A quadratic form ½qᵀKq packs every squared and cross term into one symmetric matrix", 0, L_,
        r"""
$\tfrac12\mathbf{q}^T\mathbf{K}\mathbf{q} = \tfrac12\sum_i\sum_j K_{ij}q_iq_j$ with $\mathbf{K}$ symmetric. The diagonal entries carry the squared terms. A cross term $c\,q_1q_2$ is split equally between $K_{12}$ and $K_{21}$, so each equals $c$ (the ½ in front and the two copies cancel). The gradient is $\partial V/\partial\mathbf{q} = \mathbf{K}\mathbf{q}$.

[[c-linearization]] writes $V \approx V_e + \tfrac12\mathbf{q}^T\mathbf{K}\mathbf{q}$ and $T\approx\tfrac12\dot{\mathbf{q}}^T\mathbf{M}\dot{\mathbf{q}}$. Reading $\mathbf{M}$ and $\mathbf{K}$ off by inspection is a core exam skill.
""",
        math=[r"\tfrac12\mathbf{q}^T\mathbf{K}\mathbf{q} = \tfrac12(K_{11}q_1^2 + 2K_{12}q_1q_2 + K_{22}q_2^2)"],
        analogy=analogy("A bowl's shape recorded as a small table: the diagonal says how steep the bowl is along each axis, the off-diagonal how twisted it is.",
                        "the table only describes bowl (quadratic) shapes. A real $V$ is bowl-shaped only near equilibrium."),
        exam="For each cross term, write the coefficient in front of $q_iq_j$ and put it straight in $K_{ij}$; don't halve it.",
        problems=[
            problem("p-qf-1", "Read the mass matrix off T",
                    r"Near $\theta = 0$, $T = \tfrac12(M+m)\dot x^2 + \tfrac12 m\ell^2\dot\theta^2 + m\ell\dot x\dot\theta$.",
                    [choice(r"Writing $T = \tfrac12\dot{\mathbf{q}}^T\mathbf{M}\dot{\mathbf{q}}$ with $\mathbf{q} = (x, \theta)$, what is $M_{12}$?",
                            [opt(r"$m\ell$", True),
                             opt(r"$2m\ell$", why=r"$\tfrac12(M_{12} + M_{21})\dot x\dot\theta = M_{12}\dot x\dot\theta$, so $M_{12}$ is the coefficient itself."),
                             opt(r"$\tfrac12 m\ell$", why="The ½ in front of $\\dot{\\mathbf{q}}^T\\mathbf{M}\\dot{\\mathbf{q}}$ is cancelled by the two copies $M_{12}$ and $M_{21}$."),
                             opt(r"$m\ell^2$", why="That's $M_{22}$.")])]),
            problem("p-qf-2", "Evaluate a quadratic form",
                    r"$\mathbf{K} = \begin{bmatrix}3 & 1\\ 1 & 2\end{bmatrix}$, $\mathbf{q} = (1, 2)$.",
                    [num(r"What is $\tfrac12\mathbf{q}^T\mathbf{K}\mathbf{q}$?", 0.5 * (3 + 2 * 1 * 2 + 2 * 4), "",
                         explain="$\\tfrac12(3\\cdot1 + 2\\cdot1\\cdot2 + 2\\cdot4) = \\tfrac12(15) = 7.5$.")]),
        ]),

    concept(
        "p-ode-char", "Guess e^{λt}: a linear ODE becomes an algebra problem", 0, O_,
        r"""
For $m\ddot x + c\dot x + kx = 0$, try $x = e^{\lambda t}$. Each derivative just multiplies by $\lambda$, so the ODE becomes $(m\lambda^2 + c\lambda + k)e^{\lambda t} = 0$, and $e^{\lambda t}$ is never zero. The **characteristic equation** $m\lambda^2 + c\lambda + k = 0$ decides everything.

Two real negative roots: smooth decay. A repeated root: decay with an extra $te^{\lambda t}$. A complex pair: decaying oscillation ([[p-complex-exp]]). Lecture 10 is this idea applied to vibration.
""",
        math=[r"m\lambda^2 + c\lambda + k = 0", r"x(t) = Ae^{\lambda_1 t} + Be^{\lambda_2 t}"],
        analogy=analogy("A key that fits every lock of this shape: exponentials keep their shape when differentiated, so every term becomes the same shape times a number.",
                        "repeated roots need the extra $te^{\\lambda t}$, and forcing terms need a different guess."),
        exam="Divide by $m$ first: $\\lambda^2 + 2\\zeta\\omega_n\\lambda + \\omega_n^2 = 0$ lets you read $\\omega_n$ and $\\zeta$ straight off.",
        widget={"type": "damped", "zeta": 0.3},
        problems=[
            problem("p-ode-1", "Real roots",
                    r"$\ddot x + 5\dot x + 6x = 0$.",
                    [choice("What are the roots of the characteristic equation?",
                            [opt(r"$-2$ and $-3$", True), opt(r"$2$ and $3$", why="$\\lambda^2 + 5\\lambda + 6 = (\\lambda+2)(\\lambda+3)$."),
                             opt(r"$-1$ and $-6$", why="Those multiply to 6 but sum to $-7$, not $-5$."),
                             opt(r"$-\tfrac52 \pm \tfrac{i}{2}$", why="The discriminant $25 - 24 = 1$ is positive: the roots are real.")],
                            explain="Both negative and real: the motion decays without oscillating.")]),
            problem("p-ode-2", "Imaginary roots",
                    r"$\ddot x + 4x = 0$.",
                    [num("The roots are $\\pm i\\omega$. What is $\\omega$?", 2, "rad/s", explain="$\\lambda^2 = -4$, so $\\lambda = \\pm 2i$: oscillation at 2 rad/s.")]),
        ]),

    concept(
        "p-complex-exp", "e^{(a+ib)t} is a spiral: a sets the decay, b sets the spin", 0, O_,
        r"""
Euler's formula, $e^{i\phi} = \cos\phi + i\sin\phi$, turns a complex root pair $\lambda = a\pm ib$ into a real motion:

$$x(t) = e^{at}\big(C\cos bt + D\sin bt\big).$$

The real part $a$ (negative for damping) sets how fast the envelope shrinks; the imaginary part $b$ sets the oscillation frequency. In Lecture 10, $a = -\zeta\omega_n$ and $b = \omega_d = \omega_n\sqrt{1 - \zeta^2}$.
""",
        deeper=["p-ode-char"],
        math=[r"e^{(a+ib)t} = e^{at}(\cos bt + i\sin bt)"],
        analogy=analogy("A clock hand that spins while it shrinks: its shadow on a wall is a decaying oscillation.",
                        "only the shadow (the real part) is the physical motion; the imaginary part is bookkeeping."),
        exam="Read the decay time straight off the real part: the envelope halves every $\\ln 2/|a|$ seconds.",
        problems=[
            problem("p-cexp-1", "From roots to motion",
                    r"The characteristic roots are $\lambda = -1 \pm 3i$.",
                    [choice("Which motion is it?",
                            [opt(r"$x = e^{-t}(C\cos 3t + D\sin 3t)$", True),
                             opt(r"$x = e^{-3t}(C\cos t + D\sin t)$", why="The real part ($-1$) sets the decay; the imaginary part (3) sets the oscillation."),
                             opt(r"$x = Ce^{-t} + De^{3t}$", why="Complex roots give oscillation, not two exponentials."),
                             opt(r"$x = C\cos 3t + D\sin 3t$", why="The real part $-1$ adds a decaying envelope $e^{-t}$.")]),
                     num("How long does the envelope take to halve?", math.log(2), "s", explain="$e^{-t} = \\tfrac12$ at $t = \\ln 2\\approx 0.693$ s.")]),
        ]),
]
