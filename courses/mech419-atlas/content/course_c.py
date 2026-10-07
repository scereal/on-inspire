"""Layer 1, Lectures 7-10 and numerical integration."""
import math
import sympy as sp
from lib import *

G = 9.81
L7, L8, L9, L10, LN = ("Lecture 7–8 · Calculus of variations", "Lecture 8 · Hamilton's principle",
                       "Lecture 8–9 · Linearization", "Lecture 10 · Vibrations", "Numerical integration")

# Linearized cart-pendulum: check M_e and K by Hessians so the problem text can't drift from the math.
_CP_T = (M + m) * xd**2 / 2 + m * l**2 * thd**2 / 2 + m * xd * l * thd * sp.cos(th)
_CP_V = k * x**2 / 2 - m * g * l * sp.cos(th)
_Me = sp.hessian(_CP_T, (xd, thd)).subs(th, 0)
_K = sp.hessian(_CP_V, (x, th)).subs({x: 0, th: 0})
assert _Me == sp.Matrix([[M + m, m * l], [m * l, m * l**2]]) and _K == sp.Matrix([[k, 0], [0, m * g * l]])

# Euler-Lagrange checks for the variational problems.
def _el(F):
    """Euler-Lagrange expression d/dx(F_y') - F_y, with y' and y'' as symbols."""
    Fy, Fyp = sp.diff(F, y), sp.diff(F, yp)
    return sp.expand(sp.diff(Fyp, y) * yp + sp.diff(Fyp, yp) * ypp + sp.diff(Fyp, x) - Fy)

_BRACH_T_CYC = math.pi * math.sqrt(1 / G)
_BRACH_T_LINE = math.sqrt(math.pi**2 + 4) / math.sqrt(G)

CONCEPTS = [
    concept(
        "c-state-space", "Any n second-order equations become 2n first-order ones", 1, L7,
        r"""
Introduce **states**: the coordinates and their rates. For $m\ddot x + c\dot x + k(x + ax^3) = 0$ (a nonlinear spring), let $x_1 = x$ and $x_2 = \dot x$:

$$\dot x_1 = x_2,\qquad \dot x_2 = \frac1m\big(-cx_2 - k(x_1 + ax_1^3)\big).$$

In general $\dot x_i = f_i(x_1, \ldots, x_{2n}, t)$. The Lagrangian route uses $2n$ states $(q, \dot q)$; the Hamiltonian route uses $(q, p)$. For the spring pendulum, $(x_1, x_2, x_3, x_4) = (r, \theta, p_r, p_\theta)$ and Hamilton's equations are already in this form. State form is what every numerical integrator ([[c-euler-method]]) needs.
""",
        deeper=["c-canonical", "p-ode-char"],
        math=[r"\dot{\mathbf{x}} = \mathbf{f}(\mathbf{x}, t)"],
        analogy=analogy("To predict where a car will be, you need where it is and how fast it's going, not just where it is. The state is the snapshot that makes the future computable.",
                        "systems with memory (delays, hysteresis) need more than this snapshot."),
        exam="State the state vector explicitly before writing $\\dot{\\mathbf{x}} = \\mathbf{f}$. Mixed-up ordering is the usual way these answers lose marks.",
        source="Lecture 7, pp. 2–3; Numerical Integration Intro",
        problems=[
            problem("c-ss-1", "A nonlinear spring in state form",
                    r"$m\ddot x + c\dot x + k(x + ax^3) = 0$, with $x_1 = x$, $x_2 = \dot x$.",
                    [choice(r"What is $\dot x_2$?",
                            [opt(r"$\big(-cx_2 - k(x_1 + ax_1^3)\big)/m$", True),
                             opt(r"$-cx_2 - k(x_1 + ax_1^3)$", why="Divide by $m$: $\\dot x_2 = \\ddot x$."),
                             opt(r"$x_1$", why="That would be $\\dot x_2 = x$; the first equation is $\\dot x_1 = x_2$."),
                             opt(r"$\big(-cx_1 - k(x_2 + ax_2^3)\big)/m$", why="The damper acts on the velocity ($x_2$), the spring on the position ($x_1$).")]),
                     num("How many states does the cart-pendulum (2 DOF) need?", 4, "", explain="$2n = 4$: $x, \\theta, \\dot x, \\dot\\theta$ (or $x, \\theta, p_x, p_\\theta$).")]),
            problem("c-ss-2", "Hamiltonian states",
                    r"Spring pendulum states $x_1 = r$, $x_2 = \theta$, $x_3 = p_r$, $x_4 = p_\theta$.",
                    [choice(r"What is $\dot x_2$?",
                            [opt(r"$x_4/(m x_1^2)$", True), opt(r"$x_4/m$", why="$\\dot\\theta = p_\\theta/(mr^2)$."),
                             opt(r"$x_3/m$", why="That's $\\dot r = \\dot x_1$."), opt(r"$-mg x_1\sin x_2$", why="That's $\\dot p_\\theta = \\dot x_4$.")])],
                    fig={"type": "spring-pendulum"}),
        ]),

    concept(
        "c-functional", "A functional takes a whole curve and returns one number", 1, L7,
        r"""
Ordinary calculus finds the *point* that extremizes a function. The calculus of variations finds the *function* $y(x)$ that extremizes a **functional**, an integral of a function of it:

$$I[y] = \int_{x_1}^{x_2}F(x, y, y')\,dx,\qquad y(x_1),\ y(x_2)\ \text{given}.$$

Compare the true $y(x)$ with a neighbour $\hat y(x) = y(x) + \epsilon\eta(x)$, where $\eta$ is any smooth function with $\eta(x_1) = \eta(x_2) = 0$ (the neighbour must hit the same endpoints) and $\epsilon\ll1$. Now $\hat I(\epsilon)$ is an ordinary function of one number. Since $y$ is an extremum, $\hat I$ must be flat at $\epsilon = 0$:

$$\lim_{\epsilon\to0}\frac{d\hat I}{d\epsilon} = 0\quad\text{for every }\eta.$$
""",
        deeper=["p-extremum"],
        math=[r"I[y] = \int_{x_1}^{x_2}F(x, y, y')\,dx", r"\hat y = y + \epsilon\eta,\ \ \eta(x_1) = \eta(x_2) = 0"],
        analogy=analogy("A judge scoring a gymnastics routine: the whole routine (the function) gets one score (the functional). The best routine is one where no small tweak changes the score, to first order.",
                        "'no tweak helps' is stationarity, not optimality. It also holds at the worst routine, or at a saddle."),
        exam="Turning a function-optimization into a one-variable problem in $\\epsilon$ is the move. If asked 'why can we set $d\\hat I/d\\epsilon = 0$?', say: $\\epsilon = 0$ recovers the true curve, an extremum of $\\hat I(\\epsilon)$.",
        widget={"type": "variation", "mode": "length"},
        source="Lecture 7, pp. 3–4",
        problems=[
            problem("c-fun-1", "Vary a straight line",
                    r"$I[y] = \int_0^1 (y')^2\,dx$ with $y(0) = 0$, $y(1) = 1$. Try $y = x$ varied by $\eta = x(1 - x)$.",
                    [choice(r"Expanding $\hat I(\epsilon) = \int_0^1(1 + \epsilon\eta')^2dx$, why does the $\epsilon$ term vanish?",
                            [opt(r"$\int_0^1\eta'\,dx = \eta(1) - \eta(0) = 0$", True),
                             opt(r"Because $\eta' = 0$ everywhere", why="$\\eta' = 1 - 2x$ isn't zero; its integral is."),
                             opt(r"Because $\epsilon$ is small", why="Smallness lets us drop $\\epsilon^2$, not the $\\epsilon$ term."),
                             opt("It doesn't vanish", why="It does: the endpoints are pinned.")]),
                     num(r"What is the coefficient of $\epsilon^2$ in $\hat I(\epsilon)$?", 1 / 3, "",
                         explain="$\\int_0^1(1 - 2x)^2dx = 1/3$, so $\\hat I = 1 + \\epsilon^2/3$: a valley at $\\epsilon = 0$.")]),
            problem("c-fun-2", "Why pin the ends?",
                    r"The variation $\eta$ must satisfy $\eta(x_1) = \eta(x_2) = 0$.",
                    [choice("Why?",
                            [opt("The neighbouring curves must meet the same boundary conditions as the true one", True),
                             opt("To make $\\eta$ small", why="$\\epsilon$ makes the variation small; the end conditions keep the endpoints fixed."),
                             opt("So that $\\hat I(\\epsilon) = 0$", why="The value of $\\hat I$ isn't zero; it's its slope at $\\epsilon = 0$."),
                             opt("It's just a convention", why="It's what kills the boundary term after integration by parts.")])]),
        ]),

    concept(
        "c-euler-lagrange", "The Euler–Lagrange equation: d/dx(∂F/∂y′) − ∂F/∂y = 0", 1, L7,
        r"""
Expand $F$ to first order in $\epsilon$ ([[p-taylor]]): $F(x, \hat y, \hat y') = F + \epsilon\big[\frac{\partial F}{\partial y}\eta + \frac{\partial F}{\partial y'}\eta'\big] + O(\epsilon^2)$. So

$$\frac{d\hat I}{d\epsilon}\Big|_0 = \int_{x_1}^{x_2}\Big[\frac{\partial F}{\partial y}\eta + \frac{\partial F}{\partial y'}\eta'\Big]dx = 0.$$

[[p-ibp|Integrate the second term by parts]]; the boundary term dies since $\eta = 0$ at the ends:

$$\int_{x_1}^{x_2}\eta\Big[\frac{\partial F}{\partial y} - \frac{d}{dx}\frac{\partial F}{\partial y'}\Big]dx = 0\ \text{ for every }\eta.$$

The only way an integral against *every* bump $\eta$ can vanish is if the bracket is zero everywhere (the fundamental lemma):

$$\frac{d}{dx}\Big(\frac{\partial F}{\partial y'}\Big) - \frac{\partial F}{\partial y} = 0.$$

With several functions $y_1, \ldots, y_n$, you get one such equation for each.
""",
        deeper=["c-functional", "p-ibp", "p-taylor", "p-partial"],
        math=[r"\frac{d}{dx}\Big(\frac{\partial F}{\partial y'}\Big) - \frac{\partial F}{\partial y} = 0"],
        analogy=analogy("The fundamental lemma is a metal detector you can sweep anywhere: if every bump $\\eta$ you try reads zero, there's nothing buried anywhere, so the bracket is zero.",
                        "it needs $\\eta$ to be truly arbitrary. With constraints on $\\eta$, the bracket needn't vanish, and that's where multipliers come back."),
        exam="The derivation is a common exam question. Its four moves: Taylor-expand, differentiate in $\\epsilon$, integrate by parts (boundary term zero), fundamental lemma.",
        widget={"type": "lemma"},
        source="Lecture 7 pp. 4–5; Lecture 8 p. 4",
        problems=[
            problem("c-el-1", "Apply it",
                    r"$F = (y')^2 + y^2$.",
                    [sym_choice("What does the Euler–Lagrange equation give?", _el(yp**2 + y**2),
                                [(ypp - y, ""), (ypp + y, "$\\partial F/\\partial y = 2y$ is subtracted: $2y'' - 2y = 0$."),
                                 (ypp, "Don't forget $-\\partial F/\\partial y = -2y$."), (2 * yp - 2 * y, "$\\frac{d}{dx}(2y') = 2y''$.")], eq=True,
                                explain="$y'' = y$, solved by $\\cosh$ and $\\sinh$.")]),
            problem("c-el-2", "The fundamental lemma",
                    r"We reach $\int\eta(x)\,g(x)\,dx = 0$ for every admissible $\eta$.",
                    [choice("Why does that force $g(x) = 0$?",
                            [opt("If $g$ were nonzero somewhere, a bump $\\eta$ placed just there would make the integral nonzero", True),
                             opt("Because $\\eta$ is small", why="Smallness is irrelevant; the argument is about where $\\eta$ is placed."),
                             opt("Because $\\eta$ vanishes at the endpoints", why="That only killed the boundary term."),
                             opt("It doesn't: $g$ can oscillate so the integral cancels", why="That cancellation can't survive every choice of $\\eta$.")])]),
        ]),

    concept(
        "c-special-cases", "Two shortcuts: no y means ∂F/∂y′ is constant; no x means F − y′∂F/∂y′ is constant", 1, L7,
        r"""
The Euler–Lagrange equation is second order, but two common situations give a first integral straight away.

**(i) $F$ doesn't contain $y$.** Then $\frac{d}{dx}\frac{\partial F}{\partial y'} = 0$, so $\frac{\partial F}{\partial y'}$ is constant.

**(ii) $F$ doesn't contain $x$.** Then $\frac{dF}{dx} = \frac{\partial F}{\partial y}y' + \frac{\partial F}{\partial y'}y''$. Substitute the E–L equation for $\frac{\partial F}{\partial y}$ and recognise a product rule:

$$\frac{dF}{dx} = \frac{d}{dx}\Big(y'\frac{\partial F}{\partial y'}\Big)\quad\Rightarrow\quad F - y'\frac{\partial F}{\partial y'} = \text{const}.$$

These are the variational twins of the conservation laws: (i) is a [[c-cyclic|cyclic coordinate]] (missing $q$ means conserved $p$), and (ii) is [[c-h-conservation|conservation of $H$]] (missing $t$ means $p\dot q - L$ is conserved; here $y'F_{y'} - F$ plays the role of $H$).
""",
        deeper=["c-euler-lagrange", "p-chain-multi"],
        math=[r"\text{(i) } \frac{\partial F}{\partial y'} = C", r"\text{(ii) } F - y'\frac{\partial F}{\partial y'} = C"],
        analogy=analogy("They're the calculus-of-variations versions of conserved momentum (a missing coordinate) and conserved energy (missing time).",
                        "the first-order form (ii) can admit extra solutions, such as constants $y' = 0$, that the full equation rejects. Check them."),
        exam="Before applying E–L, look for a missing $x$ or a missing $y$. Writing the first integral directly saves a whole page of algebra on the brachistochrone.",
        source="Lecture 7 p. 5; Lecture 8 p. 1",
        problems=[
            problem("c-sc-1", "Pick the shortcut",
                    "Decide which first integral applies.",
                    [choice(r"$F = \sqrt{1 + y'^2}/\sqrt{y}$ (brachistochrone).",
                            [opt(r"$x$ is missing: $F - y'\,\partial F/\partial y' = C$", True),
                             opt(r"$y$ is missing: $\partial F/\partial y' = C$", why="$y$ appears in $\\sqrt{y}$."),
                             opt("Neither applies", why="$x$ doesn't appear explicitly."),
                             opt("Both apply", why="$y$ appears.")]),
                     choice(r"$F = x\sqrt{1 + y'^2}$.",
                            [opt(r"$y$ is missing: $\dfrac{xy'}{\sqrt{1 + y'^2}} = C$", True),
                             opt(r"$x$ is missing: $F - y'F_{y'} = C$", why="$x$ multiplies the square root."),
                             opt("Neither applies", why="$y$ itself doesn't appear (only $y'$)."),
                             opt(r"$y$ is missing: $x\sqrt{1 + y'^2} = C$", why="The conserved quantity is $\\partial F/\\partial y'$, not $F$.")])]),
            problem("c-sc-2", "The mechanics connection",
                    r"With $x\to t$, $y\to q$, $F\to L$: case (ii) says $L - \dot q\,\partial L/\partial\dot q$ is constant.",
                    [choice("Which mechanics result is that?",
                            [opt("Conservation of $H$ when $L$ has no explicit time", True),
                             opt("Conservation of momentum for a cyclic coordinate", why="That's case (i): $q$ missing."),
                             opt("Static equilibrium", why="Equilibrium is about $\\partial V/\\partial q = 0$."),
                             opt("Lagrange's equation itself", why="It's a first integral of it, not the equation.")])]),
        ]),

    concept(
        "c-shortest-path", "The shortest path between two points is a straight line, now proved", 1, L7,
        r"""
The length of a curve is $S = \int ds$ with $ds = \sqrt{dx^2 + dy^2} = \sqrt{1 + y'^2}\,dx$. So $F = \sqrt{1 + y'^2}$, which doesn't contain $y$, and shortcut (i) applies:

$$\frac{\partial F}{\partial y'} = \frac{y'}{\sqrt{1 + y'^2}} = D\ \Rightarrow\ y'^2 = \frac{D^2}{1 - D^2} = C^2\ \Rightarrow\ y = Cx + b.$$

It's a reassuring first example: the machinery reproduces the answer everyone knows.
""",
        deeper=["c-special-cases"],
        math=[r"F = \sqrt{1 + y'^2}", r"y = Cx + b"],
        analogy=analogy("A taut string between two pins: pull it tight and it takes the straight line by itself.",
                        "that's a physical argument for a minimum. The variational result only shows stationarity; here it happens to be the minimum."),
        exam="This example is the template: identify $F$, check which variable is missing, write the first integral, solve the first-order ODE.",
        widget={"type": "variation", "mode": "length"},
        source="Lecture 7, pp. 5–6",
        problems=[
            problem("c-sp-1", "Run the machinery",
                    r"$F = \sqrt{1 + y'^2}$.",
                    [sym_choice(r"What is $\partial F/\partial y'$?", sp.diff(sp.sqrt(1 + yp**2), yp),
                                [(yp / sp.sqrt(1 + yp**2), ""), (1 / (2 * sp.sqrt(1 + yp**2)), "Chain rule: the inner derivative is $2y'$."),
                                 (2 * yp / sp.sqrt(1 + yp**2), "The ½ from the square root cancels the 2."),
                                 (yp * sp.sqrt(1 + yp**2), "$\\frac{d}{du}\\sqrt u = \\frac{1}{2\\sqrt u}$: the root goes in the denominator.")]),
                     num(r"The extremal through $(0, 0)$ and $(2, 1)$ is a straight line. How long is it?", math.sqrt(5), "",
                         explain="$\\sqrt{2^2 + 1^2} = \\sqrt5\\approx 2.236$. Any detour (say via $(1, 1)$: $\\sqrt2 + 1\\approx 2.414$) is longer.")]),
        ]),

    concept(
        "c-brachistochrone", "The brachistochrone: the fastest slide is a cycloid, not a straight line", 1, L8,
        r"""
A bead slides without friction from $(0, 0)$ to $(x_2, y_2)$ with $y$ measured **down**. Which wire shape gets it there fastest? Energy conservation fixes the speed at depth $y$: $v = \sqrt{2gy}$. Time is $\int ds/v$:

$$t_2 = \frac{1}{\sqrt{2g}}\int_0^{x_2}\frac{\sqrt{1 + y'^2}}{\sqrt y}\,dx,\qquad F(y, y') = \frac{\sqrt{1 + y'^2}}{\sqrt y}.$$

$F$ doesn't contain $x$, so $F - y'\frac{\partial F}{\partial y'} = C$, which simplifies to $\frac{1}{\sqrt y\sqrt{1 + y'^2}} = C$, i.e. $y(1 + y'^2) = D$. Substitute $y = D\sin^2u$ and integrate:

$$x = \tfrac D2(2u - \sin 2u),\qquad y = \tfrac D2(1 - \cos 2u):\quad\text{a cycloid.}$$

The trade-off: a steeper start loses distance but gains speed early, and that speed pays for the rest of the trip.
""",
        deeper=["c-special-cases", "p-energy-conservation", "c-shortest-path"],
        math=[r"F = \frac{\sqrt{1 + y'^2}}{\sqrt y}", r"y(1 + y'^2) = D", r"x = \tfrac D2(2u - \sin 2u),\ \ y = \tfrac D2(1 - \cos 2u)"],
        analogy=analogy("Johann Bernoulli's own insight (retold by 3Blue1Brown and Strogatz): light refracting through layers of glass that get faster as you go down bends exactly along this curve, because light also takes the quickest path.",
                        "light's speed is set by the medium; the bead's by its depth. The analogy works because both speeds depend only on $y$, through $\\sin(\\text{angle})/v = $ const."),
        exam="The steps with marks: $v = \\sqrt{2gy}$; $F$; 'no $x$, so Beltrami'; simplify to $y(1 + y'^2) = D$; the substitution $y = D\\sin^2u$. Note the substitution in your open-book notes.",
        widget={"type": "brachistochrone"},
        source="Lecture 8, pp. 2–3",
        problems=[
            problem("c-br-1", "Set it up",
                    r"Bead released from rest at the origin, $y$ measured downward.",
                    [choice("What is the speed at depth $y$?",
                            [opt(r"$\sqrt{2gy}$", True), opt(r"$2gy$", why="$\\tfrac12mv^2 = mgy$ gives $v^2 = 2gy$; take the root."),
                             opt(r"$\sqrt{gy}$", why="$\\tfrac12 mv^2 = mgy$: the 2 stays."), opt("It depends on the wire's shape", why="Energy conservation makes it depend only on depth.")]),
                     choice("What does Beltrami's identity reduce to?",
                            [opt(r"$y(1 + y'^2) = D$", True), opt(r"$y' = C$", why="That's the straight line, from $F = \\sqrt{1 + y'^2}$ with no $y$."),
                             opt(r"$y'/\sqrt{1 + y'^2} = C$", why="That's case (i); here $x$, not $y$, is missing."),
                             opt(r"$\sqrt{y}\,(1 + y'^2) = D$", why="Square $\\frac{1}{\\sqrt y\\sqrt{1 + y'^2}} = C$: $y(1 + y'^2) = 1/C^2$.")])],
                    fig={"type": "brachistochrone"}),
            problem("c-br-2", "Race it",
                    r"Target point $(\pi, 2)$ m: a cycloid with $D = 2$ passes through it at $u = \pi/2$ (its lowest point).",
                    [num("Time along the cycloid, $\\pi\\sqrt{(D/2)/g}$?", _BRACH_T_CYC, "s", explain="$\\pi\\sqrt{1/9.81}\\approx 1.003$ s."),
                     num("Time along the straight line to the same point?", _BRACH_T_LINE, "s",
                         explain="Length $L = \\sqrt{\\pi^2 + 4}\\approx 3.72$ m, acceleration $g\\cdot 2/L$: $t = L/\\sqrt g\\approx 1.189$ s. The cycloid wins by about 0.19 s.")]),
        ]),

    concept(
        "c-hamilton-principle", "Hamilton's principle: the true motion makes ∫L dt stationary", 1, L8,
        r"""
Of all paths a system could take from one configuration to another in a given time interval (consistent with its constraints), the actual path makes the **action**

$$I = \int_{t_1}^{t_2}L(q, \dot q, t)\,dt$$

stationary (often called least action). It's exactly the variational problem with $x\to t$, $y\to q$, $F\to L$, so the Euler–Lagrange equations **are** Lagrange's equations:

$$\frac{d}{dt}\Big(\frac{\partial L}{\partial\dot q_k}\Big) - \frac{\partial L}{\partial q_k} = 0.$$

It holds for conservative systems. The notes say 'minimizes'. Strictly, the action is only guaranteed stationary; over long enough intervals it can be a saddle. Feynman's lecture on least action is the classic intuitive account.
""",
        deeper=["c-euler-lagrange", "c-lagrangian"],
        math=[r"\delta\int_{t_1}^{t_2}L\,dt = 0"],
        analogy=analogy("Feynman's picture: a thrown ball balances 'getting up high where potential energy is large' against 'not moving so fast that kinetic energy is large', keeping the running total of $T - V$ as small as it can.",
                        "'least' is really 'stationary': for long times the true path can be a saddle point of the action, not a minimum."),
        exam="Expect: 'show that Hamilton's principle gives Lagrange's equations'. Answer: map $x\\to t$, $y\\to q$, $F\\to L$, quote Euler–Lagrange, done. One line, if you state the mapping clearly.",
        widget={"type": "variation", "mode": "action"},
        source="Lecture 8, p. 4",
        problems=[
            problem("c-hp-1", "The dictionary",
                    "Translate the calculus of variations into mechanics.",
                    [choice("Which mapping turns Euler–Lagrange into Lagrange's equations?",
                            [opt(r"$x\to t,\ y\to q,\ F\to L$", True), opt(r"$x\to q,\ y\to t,\ F\to L$", why="Time is the independent variable; the coordinate depends on it."),
                             opt(r"$x\to t,\ y\to q,\ F\to T + V$", why="The action integrates $T - V$."),
                             opt(r"$x\to t,\ y\to p,\ F\to H$", why="That's the Hamiltonian picture, not this mapping.")]),
                     choice(r"For a thrown ball, $L = \tfrac12 m\dot y^2 - mgy$ ($y$ up). What does stationary action give?",
                            [opt(r"$\ddot y = -g$", True), opt(r"$\ddot y = g$", why="$-\\partial L/\\partial y = +mg$, so $m\\ddot y + mg = 0$."),
                             opt(r"$\dot y = $ const", why="$y$ appears in $L$, so $p_y$ isn't conserved."),
                             opt(r"$y = 0$", why="The E–L equation is a differential equation, not a position.")])]),
        ]),

    concept(
        "c-extended-hamilton", "The extended Hamilton's principle: ∫(δT + δW) dt = 0", 1, L8,
        r"""
Non-conservative forces have no potential, so they can't go into $L$. The extension adds their virtual work directly:

$$\int_{t_1}^{t_2}(\delta T + \delta W)\,dt = 0,\qquad \delta W = -\delta V + \delta W_{nc},$$

or equivalently $\int_{t_1}^{t_2}(\delta L + \delta W_{nc})\,dt = 0$. Here $\delta W$ is the virtual work of **all working forces and moments**. Carrying the variation through gives Lagrange's equations with $Q_{i,nc}$ on the right: $\delta W_{nc} = \sum_i Q_{i,nc}\delta q_i$, the same generalized forces as [[c-gen-force]].
""",
        deeper=["c-hamilton-principle", "c-gen-force", "c-virtual-disp"],
        math=[r"\int_{t_1}^{t_2}(\delta L + \delta W_{nc})\,dt = 0"],
        analogy=analogy("The action is the conservative account; $\\delta W_{nc}$ is a ledger of the outside payments (friction, drives). The extended principle balances both.",
                        "there's no single 'non-conservative action' you can write down and minimize; the extension works at the level of variations only."),
        exam="This is the bridge used for continuous systems (beams, rods): if a later question asks for a beam's equation, it starts here.",
        source="Lecture 8, p. 5",
        problems=[
            problem("c-eh-1", "A damper",
                    r"$L = \tfrac12 m\dot x^2 - \tfrac12 kx^2$ and a damper with $\delta W_{nc} = -c\dot x\,\delta x$.",
                    [sym_choice("What equation of motion follows?", m * xdd + c * xd + k * x,
                                [(m * xdd + c * xd + k * x, ""), (m * xdd - c * xd + k * x, "$Q_{nc} = -c\\dot x$ goes on the right: $m\\ddot x + kx = -c\\dot x$."),
                                 (m * xdd + k * x, "The damper's virtual work must be included."), (m * xdd + c * xd - k * x, "The spring term comes from $-\\partial L/\\partial x = +kx$.")], eq=True)],
                    fig={"type": "smd"}),
            problem("c-eh-2", "Why not put friction in L?",
                    "Someone suggests adding a 'friction potential' to $V$.",
                    [choice("Why doesn't that work?",
                            [opt("Friction's work depends on the path, so no potential energy function exists for it", True),
                             opt("It would, but it's longer", why="No function $V(q)$ can reproduce a force that depends on $\\dot q$ and opposes motion both ways."),
                             opt("Because friction is internal", why="Friction can be external (ground on a block) and still have no potential."),
                             opt("Because $L$ must be quadratic", why="$L$ can be any function; the obstacle is that friction is non-conservative.")])]),
        ]),

    concept(
        "c-linearization", "Linearize: Taylor-expand V to second order and freeze M at equilibrium", 1, L9,
        r"""
For small motions about an equilibrium $q_{ie}$ (with no explicit time, so $T = T_2$ and static ≈ dynamic equilibrium), write $q_i = q_{ie} + \hat q_i$.

**Potential.** The Taylor expansion's first-order terms vanish because $\partial V/\partial q = 0$ at equilibrium, leaving
$$V \approx V_e + \tfrac12\mathbf{q}^T\mathbf{K}\mathbf{q},\qquad K_{ij} = \frac{\partial^2V}{\partial q_i\partial q_j}\Big|_e.$$

**Kinetic.** In $\frac{d}{dt}\frac{\partial T}{\partial\dot q_k} - \frac{\partial T}{\partial q_k}$, every term except $m_{kj}\ddot q_j$ is a product of small quantities (like $\dot q_r\dot q_j$), so it drops, and $m_{kj}$ can be evaluated at equilibrium.

$$\mathbf{M}_e\ddot{\mathbf{q}} + \mathbf{K}\mathbf{q} = \mathbf{Q}_{nc}.$$

For the cart-pendulum about $\theta = 0$: $\mathbf{M}_e = \begin{bmatrix}M+m & m\ell\\ m\ell & m\ell^2\end{bmatrix}$ and $\mathbf{K} = \begin{bmatrix}k & 0\\ 0 & mg\ell\end{bmatrix}$. You can read both off $T\approx\tfrac12\dot{\mathbf{q}}^T\mathbf{M}_e\dot{\mathbf{q}}$ and $V\approx V_e + \tfrac12\mathbf{q}^T\mathbf{K}\mathbf{q}$ without deriving the nonlinear equations at all.
""",
        deeper=["c-static-eq", "c-t2t1t0", "p-taylor", "p-quadratic-form", "c-lagrange-recipe"],
        math=[r"\mathbf{M}_e\ddot{\mathbf{q}} + \mathbf{K}\mathbf{q} = \mathbf{Q}_{nc}", r"K_{ij} = \frac{\partial^2V}{\partial q_i\partial q_j}\Big|_e"],
        analogy=analogy("Small vibrations only feel the bottom of the bowl, and the bottom of every smooth bowl is a parabola.",
                        "if the bowl's bottom is flat ($V'' = 0$) or the swings are big, the parabola misleads. Turn on the nonlinear overlay in the cart-pendulum widget and push the amplitude."),
        exam="The fastest route by far: expand $T$ and $V$ to quadratic order and read $\\mathbf{M}_e$, $\\mathbf{K}$ by inspection (Lecture 9's Note 1). Only derive the full nonlinear equations if they're asked for.",
        widget={"type": "cartpend", "linear": True},
        source="Lecture 8 p. 6; Lecture 9",
        problems=[
            problem("c-lin-1", "Linearize the cart-pendulum",
                    r"$T = \tfrac12(M+m)\dot x^2 + \tfrac12 m\ell^2\dot\theta^2 + m\ell\dot x\dot\theta\cos\theta$, $V = \tfrac12 kx^2 - mg\ell\cos\theta$, about $x = \theta = 0$.",
                    [choice(r"What is $\mathbf{M}_e$?",
                            [opt(r"$\begin{bmatrix}M+m & m\ell\\ m\ell & m\ell^2\end{bmatrix}$", True),
                             opt(r"$\begin{bmatrix}M+m & m\ell\cos\theta\\ m\ell\cos\theta & m\ell^2\end{bmatrix}$", why="That's $\\mathbf{M}(\\theta)$; evaluate it at $\\theta = 0$."),
                             opt(r"$\begin{bmatrix}M+m & 0\\ 0 & m\ell^2\end{bmatrix}$", why="The coupling $m\\ell\\dot x\\dot\\theta$ survives at $\\theta = 0$."),
                             opt(r"$\begin{bmatrix}M & m\ell\\ m\ell & m\ell^2\end{bmatrix}$", why="The bob moves with the cart: $M + m$.")]),
                     choice(r"What is $\mathbf{K}$?",
                            [opt(r"$\begin{bmatrix}k & 0\\ 0 & mg\ell\end{bmatrix}$", True),
                             opt(r"$\begin{bmatrix}k & 0\\ 0 & -mg\ell\end{bmatrix}$", why="$-mg\\ell\\cos\\theta\\approx -mg\\ell + \\tfrac12 mg\\ell\\theta^2$: positive stiffness."),
                             opt(r"$\begin{bmatrix}k & 0\\ 0 & \tfrac12 mg\ell\end{bmatrix}$", why="$V = \\tfrac12\\mathbf{q}^T\\mathbf{K}\\mathbf{q}$ already has the ½."),
                             opt(r"$\begin{bmatrix}k & 0\\ 0 & 0\end{bmatrix}$", why="Gravity gives the pendulum a restoring stiffness $mg\\ell$.")]),
                     choice(r"Why does the $-m\ell\dot\theta^2\sin\theta$ term vanish?",
                            [opt("It's a product of small quantities (third order), negligible next to the linear terms", True),
                             opt("Because $\\sin 0 = 0$ exactly, at all times", why="$\\theta$ isn't always zero; it's small. The term is $\\approx m\\ell\\dot\\theta^2\\theta$, third order."),
                             opt("Because $\\dot\\theta = 0$ at equilibrium", why="During vibration $\\dot\\theta\\ne0$; it's small, not zero."),
                             opt("It doesn't; it's part of the linear equations", why="Linear equations contain only first powers.")])],
                    fig={"type": "cart-pendulum", "spring": True}),
            problem("c-lin-2", "One pendulum",
                    r"Linearize $m\ell^2\ddot\theta + mg\ell\sin\theta = 0$ and find $\omega_n$ for $\ell = 0.5$ m.",
                    [num(r"$\omega_n$?", math.sqrt(G / 0.5), "rad/s", explain="$\\ddot\\theta + (g/\\ell)\\theta = 0$, so $\\omega_n = \\sqrt{9.81/0.5}\\approx 4.43$ rad/s.")],
                    fig={"type": "pendulum"}),
        ]),

    concept(
        "c-sdof-free", "Free vibration: the spring-mass system oscillates at ω_n = √(k/m)", 1, L10,
        r"""
$m\ddot x + kx = 0$, i.e. $\ddot x + \frac km x = 0$: a linear second-order ODE whose solution oscillates.

$$x(t) = x(0)\cos\omega_nt + \frac{\dot x(0)}{\omega_n}\sin\omega_nt,\qquad \omega_n = \sqrt{\frac km}\ \text{rad/s},\qquad P = \frac{2\pi}{\omega_n}.$$

The initial conditions set the constants: $A = x(0)$, $B = \dot x(0)/\omega_n$. Any linearized 1-DOF system ($\tfrac32m\ddot x + kx = 0$ for the rolling disk, $\ddot\theta + \frac g\ell\theta = 0$ for the pendulum) has the same form with an effective mass and stiffness.
""",
        deeper=["p-ode-char", "c-linearization"],
        math=[r"\omega_n = \sqrt{k/m}", r"x(t) = x_0\cos\omega_nt + \frac{\dot x_0}{\omega_n}\sin\omega_nt"],
        analogy=analogy("A child on a swing: the stiffer the restoring pull and the lighter the child, the quicker the rhythm, $\\sqrt{k/m}$.",
                        "a real swing slowly loses energy. The undamped model swings forever; add damping for that ([[c-damping-cases]])."),
        exam="Always reduce to $m_{eff}\\ddot q + k_{eff}q = 0$ and quote $\\omega_n = \\sqrt{k_{eff}/m_{eff}}$; it works for rotational and effective systems alike.",
        widget={"type": "damped", "zeta": 0},
        source="Lecture 10, p. 1",
        problems=[
            problem("c-sdof-1", "Spring-mass basics",
                    "A 2 kg mass on a 200 N/m spring.",
                    [num(r"$\omega_n$?", 10, "rad/s"), num("Period?", 2 * math.pi / 10, "s", explain="$2\\pi/10\\approx 0.628$ s.")],
                    fig={"type": "smd", "damper": False}),
            problem("c-sdof-2", "Initial conditions",
                    r"Same system, released from $x(0) = 0.02$ m with $\dot x(0) = 0.3$ m/s.",
                    [num(r"What is $B = \dot x(0)/\omega_n$?", 0.03, "m"),
                     num("What is the amplitude $\\sqrt{A^2 + B^2}$?", math.hypot(0.02, 0.03), "m", explain="$\\sqrt{0.02^2 + 0.03^2}\\approx 0.0361$ m.")]),
        ]),

    concept(
        "c-damping-cases", "Damping ratio ζ = c/(2mω_n) decides between creeping and ringing", 1, L10,
        r"""
A viscous damper adds a force $-c\dot x$: $m\ddot x + c\dot x + kx = 0$. Try $x = x_0e^{\lambda t}$ to get $m\lambda^2 + c\lambda + k = 0$. With $\frac km = \omega_n^2$ and the **damping ratio** $\zeta = \frac{c}{2m\omega_n}$ (dimensionless),

$$\lambda^2 + 2\zeta\omega_n\lambda + \omega_n^2 = 0\ \Rightarrow\ \lambda = \big(-\zeta\pm\sqrt{\zeta^2 - 1}\big)\omega_n.$$

- $\zeta > 1$, **overdamped**: two real negative roots, slow non-oscillatory return. The slow root $(-\zeta + \sqrt{\zeta^2-1})\omega_n$ sets the response speed.
- $\zeta = 1$, **critically damped**: the boundary. $c_{cr} = 2m\omega_n = 2\sqrt{km}$.
- $\zeta < 1$, **underdamped**: complex roots, decaying oscillation ([[c-underdamped]]).

$c$ has units N·s/m = kg/s.
""",
        deeper=["c-sdof-free", "p-ode-char", "p-complex-exp"],
        math=[r"\zeta = \frac{c}{2m\omega_n} = \frac{c}{c_{cr}},\quad c_{cr} = 2\sqrt{km}", r"\lambda = \big(-\zeta\pm\sqrt{\zeta^2-1}\big)\omega_n"],
        analogy=analogy("Car suspension: too little damping and the car keeps bouncing down the road; too much and it sinks back slowly; critical damping settles it fastest without overshoot.",
                        "real shocks are nonlinear (stiffer in rebound than compression); the linear model is a first approximation."),
        exam="Compute $\\zeta$ first, every time: it decides which of three solution forms to use.",
        widget={"type": "damped", "zeta": 0.2},
        source="Lecture 10, pp. 1–3",
        problems=[
            problem("c-dc-1", "Classify a system",
                    "$m = 2$ kg, $k = 200$ N/m, $c = 8$ N·s/m.",
                    [num(r"$\zeta$?", 8 / (2 * 2 * 10), "", explain="$\\omega_n = 10$, so $\\zeta = 8/(2\\cdot2\\cdot10) = 0.2$."),
                     choice("Which case?", [opt("Underdamped: it rings down", True), opt("Overdamped", why="$\\zeta = 0.2 < 1$."),
                                            opt("Critically damped", why="That needs $\\zeta = 1$."), opt("Undamped", why="$c\\ne0$.")]),
                     num(r"Critical damping $c_{cr}$?", 2 * math.sqrt(200 * 2), "N·s/m", explain="$2\\sqrt{km} = 2\\sqrt{400} = 40$ N·s/m.")],
                    fig={"type": "smd"}),
            problem("c-dc-2", "Overdamped speed",
                    r"$\omega_n = 10$ rad/s, $\zeta = 2$.",
                    [num("What is the decay rate of the slower root, $|\\lambda_1|$?", (2 - math.sqrt(3)) * 10, "1/s",
                         explain="$(2 - \\sqrt3)(10)\\approx 2.68$ s⁻¹. The other root, about 37.3 s⁻¹, dies out quickly; the slow one dominates.")]),
        ]),

    concept(
        "c-underdamped", "Underdamped motion: a cosine inside a shrinking envelope", 1, L10,
        r"""
For $\zeta < 1$ the roots are $\lambda = -\zeta\omega_n\pm i\omega_d$ with the **damped natural frequency** $\omega_d = \omega_n\sqrt{1 - \zeta^2}$. By [[p-complex-exp|Euler's formula]]:

$$x(t) = e^{-\zeta\omega_nt}\Big(x_0\cos\omega_dt + \frac{\dot x_0 + \zeta\omega_nx_0}{\omega_d}\sin\omega_dt\Big) = Ae^{-\zeta\omega_nt}\cos(\omega_dt - \phi).$$

The period of the damped oscillation is $P_d = 2\pi/\omega_d$, slightly longer than undamped, since $\omega_d$ decreases as $\zeta$ goes from 0 to 1.
""",
        deeper=["c-damping-cases", "p-complex-exp"],
        math=[r"\omega_d = \omega_n\sqrt{1 - \zeta^2}", r"x = e^{-\zeta\omega_nt}\Big(x_0\cos\omega_dt + \frac{\dot x_0 + \zeta\omega_nx_0}{\omega_d}\sin\omega_dt\Big)"],
        analogy=analogy("A plucked guitar string: it keeps the same note (nearly $\\omega_n$) while the sound fades exponentially.",
                        "real strings lose high harmonics faster than low ones; a single-DOF model has only one frequency to fade."),
        exam="The $D$ coefficient has the $\\zeta\\omega_nx_0$ term that people forget. Derive it once from $\\dot x(0)$ and keep it in your notes.",
        widget={"type": "damped", "zeta": 0.15},
        source="Lecture 10, p. 4",
        problems=[
            problem("c-ud-1", "Damped frequency and constants",
                    r"$\omega_n = 10$ rad/s, $\zeta = 0.2$, released from $x_0 = 0.05$ m at rest.",
                    [num(r"$\omega_d$?", 10 * math.sqrt(1 - 0.04), "rad/s", explain="$10\\sqrt{0.96}\\approx 9.80$ rad/s."),
                     num(r"$D = (\dot x_0 + \zeta\omega_nx_0)/\omega_d$?", (0 + 0.2 * 10 * 0.05) / (10 * math.sqrt(0.96)), "m",
                         explain="$0.1/9.80\\approx 0.0102$ m. It's nonzero even from rest: damping tilts the start of the curve."),
                     num("Damped period $P_d$?", 2 * math.pi / (10 * math.sqrt(0.96)), "s")]),
        ]),

    concept(
        "c-log-dec", "Logarithmic decrement: read the damping straight off two peaks", 1, L10,
        r"""
Successive peaks one damped period apart have ratio $\frac{X_1}{X_2} = e^{\zeta\omega_nP_d}$. Taking logs:

$$\Delta = \ln\frac{X_1}{X_2} = \frac{2\pi\zeta}{\sqrt{1 - \zeta^2}},\qquad \zeta = \frac{\Delta}{\sqrt{4\pi^2 + \Delta^2}}.$$

For lightly damped systems ($\zeta\approx0.01$, '1% of critical'), $\Delta\approx2\pi\zeta$. Over $n$ cycles, $\Delta = \frac1n\ln\frac{X_1}{X_{n+1}}$, which is more accurate with noisy data. This is the standard way to measure damping in a lab (MIT 2.003's notes treat it the same way).
""",
        deeper=["c-underdamped"],
        math=[r"\Delta = \ln\frac{X_1}{X_2} = \frac{2\pi\zeta}{\sqrt{1 - \zeta^2}}\approx 2\pi\zeta"],
        analogy=analogy("Compound interest in reverse: every cycle the amplitude loses the same fraction, so the log of the amplitude falls by the same amount each cycle.",
                        "only for linear viscous damping. Dry friction removes a fixed amount per cycle (a straight-line decay), not a fixed fraction."),
        exam="Remember the inversion formula $\\zeta = \\Delta/\\sqrt{4\\pi^2 + \\Delta^2}$: it's exact and avoids solving a quadratic under time pressure.",
        widget={"type": "damped", "zeta": 0.08, "peaks": True},
        source="Lecture 10, p. 5",
        problems=[
            problem("c-ld-a", "From two peaks",
                    "Two successive peaks measure 10 mm and 6 mm.",
                    [num(r"$\Delta$?", math.log(10 / 6), ""),
                     num(r"$\zeta$ (exact formula)?", math.log(10 / 6) / math.sqrt(4 * math.pi**2 + math.log(10 / 6)**2), "",
                         explain="$0.511/\\sqrt{39.48 + 0.26}\\approx 0.0810$; the small-$\\zeta$ estimate $\\Delta/2\\pi$ gives 0.0813.")]),
            problem("c-ld-b", "Over several cycles",
                    "The amplitude halves over 4 cycles.",
                    [num(r"$\zeta$?", (math.log(2) / 4) / math.sqrt(4 * math.pi**2 + (math.log(2) / 4)**2), "",
                         explain="$\\Delta = \\ln 2/4 = 0.173$, so $\\zeta\\approx 0.0276$.")]),
        ]),

    concept(
        "c-forced", "Forced vibration: after the transient dies, the mass follows the force at its frequency", 1, L10,
        r"""
$m\ddot x + c\dot x + kx = F_0\cos\Omega t$. The solution is $x = x_c + x_p$; the complementary part $x_c$ decays (it's the free damped motion), leaving the **steady state** $x_p$. With $D = d/dt$:

$$x_p = \frac{(F_0/m)\cos\Omega t}{D^2 + 2\zeta\omega_0D + \omega_0^2}.$$

Acting on $\cos\Omega t$, $D^2\to-\Omega^2$. Finishing the algebra (the next step after Lecture 10's notes) with frequency ratio $r = \Omega/\omega_n$:

$$x_p = X\cos(\Omega t - \phi),\quad X = \frac{F_0/k}{\sqrt{(1 - r^2)^2 + (2\zeta r)^2}},\quad \tan\phi = \frac{2\zeta r}{1 - r^2}.$$

At resonance ($r = 1$), $X = \frac{F_0/k}{2\zeta}$ and the response lags the force by 90°.
""",
        deeper=["c-underdamped", "p-complex-exp"],
        math=[r"X = \frac{F_0/k}{\sqrt{(1 - r^2)^2 + (2\zeta r)^2}}", r"\tan\phi = \frac{2\zeta r}{1 - r^2}"],
        analogy=analogy("Pushing a child on a swing: push at the swing's own rhythm and small pushes build huge swings; push at a random rhythm and you mostly fight it.",
                        "a swing pushed by a person gets impulses, not a smooth $\\cos\\Omega t$, and the person adapts their timing. The model's force is blind to the motion."),
        exam="Notes stop at the operator form, so the magnification and phase formulas are worth having on your formula sheet. Check limits: $r\\to0$ gives $F_0/k$ (static deflection); $r\\to\\infty$ gives 0.",
        widget={"type": "forced"},
        source="Lecture 10, p. 6",
        beyond=True,
        problems=[
            problem("c-forced-1", "The operator trick",
                    r"In $x_p = \frac{(F_0/m)\cos\Omega t}{D^2 + 2\zeta\omega_0D + \omega_0^2}$:",
                    [choice(r"What does $D^2$ become acting on $\cos\Omega t$?",
                            [opt(r"$-\Omega^2$", True), opt(r"$\Omega^2$", why="$\\frac{d^2}{dt^2}\\cos\\Omega t = -\\Omega^2\\cos\\Omega t$."),
                             opt(r"$-\Omega$", why="Two derivatives give two factors of $\\Omega$."), opt(r"$0$", why="Cosine isn't killed by differentiation.")]),
                     choice("Why can we ignore $x_c$ for the steady state?",
                            [opt("It's the free damped response, which decays as $e^{-\\zeta\\omega_nt}$", True),
                             opt("It's zero for these initial conditions", why="It's generally nonzero at first; it decays."),
                             opt("Because the force cancels it", why="The force drives $x_p$; $x_c$ dies on its own through damping."),
                             opt("It grows, so it's unphysical", why="With $\\zeta > 0$ it decays.")])],
                    fig={"type": "smd", "force": True}),
            problem("c-forced-2", "Response amplitudes",
                    r"$F_0 = 10$ N, $k = 1000$ N/m, $\zeta = 0.1$.",
                    [num(r"Amplitude at $r = 0.5$?", (10 / 1000) / math.sqrt((1 - 0.25)**2 + (2 * 0.1 * 0.5)**2), "m",
                         explain="$0.01/\\sqrt{0.5625 + 0.01}\\approx 0.0132$ m."),
                     num(r"Amplitude at resonance, $r = 1$?", (10 / 1000) / (2 * 0.1), "m", explain="$0.01/0.2 = 0.05$ m: five times the static deflection.")]),
        ]),

    concept(
        "c-euler-method", "Euler's method: step along the tangent, then repeat", 1, LN,
        r"""
Every equation of motion from Lagrange is linear in $\ddot q$: $\mathbf{M}\ddot{\mathbf{q}} = \mathbf{f}(\mathbf{q}, \dot{\mathbf{q}}, \mathbf{u}, t)$, but generally nonlinear in everything else, so we integrate numerically. Put it in [[c-state-space|state form]] $\dot y = f(y, t)$, choose a step $h$ and the initial condition $y_0$, then repeat:

$$\dot y_k = f(y_k, t_k),\qquad y_{k+1} = y_k + h\,\dot y_k.$$

For $\ddot x = f(x, \dot x, t)$: $v_{k+1} = v_k + h f(x_k, v_k, t_k)$ and $x_{k+1} = x_k + hv_k$. Methods are classified by order, explicit vs implicit, and fixed vs variable step size. Euler is first order and explicit: simple, but its error per step is $O(h^2)$, and on an undamped oscillator it **gains energy every step**, by a factor $1 + h^2\omega^2$, because the tangent always points slightly outside the true circular orbit.
""",
        deeper=["c-state-space", "p-ode-char"],
        math=[r"y_{k+1} = y_k + h f(y_k, t_k)"],
        analogy=analogy("Walking in the dark by compass: take a step in the direction you're facing now, look again, step again. On a circular track, each straight step drifts slightly outward.",
                        "better methods (Runge–Kutta, symplectic Euler) look ahead or alternate updates, which is like correcting your heading mid-step."),
        exam="Show one or two steps in a table ($k$, $t_k$, $y_k$, $\\dot y_k$). Marks are usually for the procedure and the state vector, not for a long run.",
        widget={"type": "euler"},
        source="Numerical Integration Intro",
        problems=[
            problem("c-eu-1", "Two steps by hand",
                    r"$\dot y = -2y$, $y(0) = 1$, $h = 0.1$.",
                    [num(r"$y_1$?", 1 + 0.1 * (-2), ""), num(r"$y_2$?", 0.8 + 0.1 * (-1.6), "", explain="$0.8 - 0.16 = 0.64$; the exact $e^{-0.4} = 0.670$."),
                     num("What is the largest step $h$ that keeps the numerical solution from growing?", 1, "",
                         explain="Each step multiplies by $1 - 2h$; $|1 - 2h|\\le1$ needs $h\\le1$. At $h = 1.5$, $y_1 = -2$: it explodes.")]),
            problem("c-eu-2", "An oscillator gains energy",
                    r"$\ddot x = -x$ with $x_0 = 1$, $v_0 = 0$, $h = 0.1$. Energy $E = \tfrac12(x^2 + v^2)$.",
                    [num(r"After one Euler step, $E_1/E_0$?", 1 + 0.01, "", explain="$x_1 = 1$, $v_1 = -0.1$: $E_1 = \\tfrac12(1.01)$, a factor $1 + h^2$."),
                     choice("Why does the energy grow?",
                            [opt("Each step moves along the tangent to the circular orbit, which lands slightly outside it", True),
                             opt("Rounding error in the computer", why="It happens in exact arithmetic too: it's the method, not the rounding."),
                             opt("The oscillator has negative damping", why="The ODE is undamped; the method adds the energy."),
                             opt("Because $h$ is too small", why="Smaller $h$ reduces the gain ($1 + h^2$) but never removes it.")])]),
        ]),
]
