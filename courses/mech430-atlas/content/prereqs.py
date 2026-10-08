"""Layer 0: what MECH 430 assumes from thermodynamics, Fluids 1, mechanics, calculus and programming."""
import math
import sympy as sp
from lib import *
import gas

TH, FL, ME, CA, PY = "Thermodynamics", "Fluids 1", "Mechanics", "Calculus and numerics", "Python"

_R_N2 = gas.R_of(28.0)
_rho = 14 * 101325 / (_R_N2 * 800)   # a nitrogen state used below

CONCEPTS = [
    concept(
        "p-ideal-gas", "The ideal gas: p = ρRT, with R = R_u / MW", 0, TH,
        r"""
For a gas far from condensing, pressure, density and temperature are tied by
$$p = \rho R T,\qquad R = \frac{R_u}{\mathrm{MW}},\quad R_u = 8314\ \mathrm{J/(kmol\,K)}.$$
Each gas has its own $R$: air (MW ≈ 28.8 in the notes) has $R\approx 287$ J/(kg·K); helium (MW 4) has $R = 2079$. **Temperatures are absolute** (kelvin), always. Specifying any two of $p$, $\rho$, $T$ fixes the third and every other property.

This is the *thermal* equation of state. MECH 430 also assumes a *calorically perfect* gas ([[p-calorically-perfect]]): constant $c_p$ and $c_v$.
""",
        math=[r"p = \rho R T", r"R = R_u/\mathrm{MW}"],
        analogy=analogy("A fixed budget split three ways: squeeze the gas (raise ρ) at fixed T and the pressure bill rises in proportion.",
                        "the budget picture fails near condensation or at extreme pressures, where molecules' own volume and attraction matter (real-gas effects)."),
        exam="Convert °C to K and atm to Pa before anything else; most arithmetic errors in this course are unit errors.",
        problems=[
            problem("p-ig-1", "Density of hot nitrogen",
                    r"Nitrogen (MW = 28) at 14 atm and 800 K. Take $R_u = 8314$ J/(kmol·K) and 1 atm = 101325 Pa.",
                    [num("$R$ for nitrogen, in J/(kg·K)?", _R_N2, "J/(kg·K)"),
                     num(r"Density $\rho$?", _rho, "kg/m³", explain="$\\rho = p/(RT) = 14\\times101325/(296.9\\times800)$.")]),
            problem("p-ig-2", "Which temperature?",
                    r"A student computes $\rho = p/(RT)$ with $T = -50$ (°C).",
                    [choice("What happens?", [opt("A negative density: T must be in kelvin, 223.15 K", True),
                                              opt("Nothing, the units cancel", why="Only absolute temperature appears in p = ρRT; Celsius has the wrong zero.")])]),
        ]),
    concept(
        "p-calorically-perfect", "Calorically perfect gas: h = c_p T, u = c_v T, γ = c_p/c_v", 0, TH,
        r"""
A **calorically perfect** gas has constant specific heats, so $h = c_pT$ and $u = c_vT$. Three identities do most of the work:
$$R = c_p - c_v,\qquad \gamma = \frac{c_p}{c_v},\qquad c_p = \frac{\gamma R}{\gamma - 1}.$$
Monatomic gases (He, Ar) have $\gamma = 5/3$; diatomic (N₂, O₂, air) $\gamma = 7/5$; complex molecules have $\gamma$ closer to 1 (CO₂ 1.28, SF₆ 1.09). The notes warn this breaks down above about Mach 5 shocks, when vibration, dissociation and ionization soak up energy ([[c-strong-weak-shocks]]).
""",
        deeper=["p-ideal-gas"],
        math=[r"c_p = \frac{\gamma R}{\gamma-1}", r"h = c_pT"],
        problems=[
            problem("p-cp-1", "c_p of air",
                    r"Air: $R = 287$ J/(kg·K), $\gamma = 1.4$.",
                    [num("$c_p$?", 1.4 * 287 / 0.4, "J/(kg·K)", explain="$c_p = \\gamma R/(\\gamma-1) = 1004.5$."),
                     expr(r"Type $c_v$ in terms of `R` and `gamma`.", R / (g - 1), ["R", "gamma"], ranges={"R": [200, 400], "gamma": [1.1, 1.7]})]),
        ]),
    concept(
        "p-first-law", "The first law, enthalpy and flow work", 0, TH,
        r"""
For a closed system, $\Delta E = Q + W$ (heat **to** and work **on** the system, the notes' sign convention). For an open system, pushing mass across the boundary is work too: the *flow work* $p/\rho$ per unit mass. That's why enthalpy $h = u + p/\rho$ appears whenever mass flows ([[c-cv-energy]]).
""",
        deeper=["p-calorically-perfect"],
        math=[r"\Delta E = Q + W", r"h = u + p/\rho"],
        problems=[
            problem("p-fl-1", "Why enthalpy?",
                    r"Mass flows into a control volume.",
                    [choice("Why does the energy equation for a control volume use $h$ instead of $u$?",
                            [opt("The $p/\\rho$ part of $h$ accounts for the work done pushing mass across the boundary", True),
                             opt("Because the flow is adiabatic", why="Flow work is there with or without heat transfer."),
                             opt("Because $h$ includes kinetic energy", why="Kinetic energy is added separately, as $V^2/2$.")])]),
        ]),
    concept(
        "p-entropy-isentropic", "Entropy and isentropic relations: p/ρ^γ = constant", 0, TH,
        r"""
The Gibbs ($Tds$) relations give, for a calorically perfect gas,
$$s_2 - s_1 = c_p\ln\frac{T_2}{T_1} - R\ln\frac{p_2}{p_1}.$$
**Isentropic** means adiabatic *and* reversible. Then
$$\frac{p_2}{p_1} = \left(\frac{\rho_2}{\rho_1}\right)^{\gamma} = \left(\frac{T_2}{T_1}\right)^{\gamma/(\gamma-1)}.$$
For an isolated system entropy can never decrease; that single fact rules out expansion shocks ([[c-shock-entropy]]).
""",
        deeper=["p-calorically-perfect"],
        math=[r"\frac{p_2}{p_1} = \left(\frac{T_2}{T_1}\right)^{\gamma/(\gamma-1)}"],
        problems=[
            problem("p-is-1", "Compress isentropically",
                    r"Air at 300 K is compressed isentropically to 10 times its pressure.",
                    [num("Final temperature?", 300 * 10 ** (0.4 / 1.4), "K", explain="$T_2 = 300\\times10^{0.2857}$."),
                     choice("If the same compression had friction (irreversible), the final temperature at the same pressure would be:",
                            [opt("Higher", True), opt("Lower", why="Irreversibility adds entropy; at fixed p, more entropy means higher T."),
                             opt("The same", why="Only an isentropic path gives the isentropic temperature.")])]),
        ]),
    concept(
        "p-bernoulli", "Bernoulli's equation from Fluids 1", 0, FL,
        r"""
For steady, inviscid, **incompressible** flow along a streamline (no gravity change),
$$p + \tfrac12\rho V^2 = p_0 = \text{constant}.$$
Its derivation integrates $dp + \rho V\,dV = 0$ with $\rho$ held constant. MECH 430's question is when that holding is allowed: below about Mach 0.3, the error is a couple of percent ([[c-compressibility]]).
""",
        math=[r"p + \tfrac{1}{2}\rho V^2 = p_0"],
        problems=[
            problem("p-be-1", "Dynamic pressure",
                    r"Air with $\rho = 1.2$ kg/m³ at 50 m/s.",
                    [num("$p_0 - p$ by Bernoulli?", 0.5 * 1.2 * 50 ** 2, "Pa")]),
        ]),
    concept(
        "p-momentum", "Newton's second law as a vector momentum balance", 0, ME,
        r"""
$\sum\mathbf{F} = d(m\mathbf{V})/dt$ is three equations, one per direction. Draw a free-body diagram, pick axes, and write one scalar equation per component. In MECH 430 the "body" becomes a control volume and the momentum carried in and out by the flow joins the bookkeeping ([[c-cv-momentum]]).
""",
        math=[r"\sum \mathbf{F} = \frac{d}{dt}(m\mathbf{V})"],
        problems=[
            problem("p-mo-1", "Components",
                    r"A force of 100 N acts at 30° above the $x$-axis.",
                    [num("Its $y$-component?", 50, "N"), num("Its $x$-component?", 100 * math.cos(math.radians(30)), "N")]),
        ]),
    concept(
        "p-galilean", "Changing reference frames: add the same velocity everywhere", 0, ME,
        r"""
A **Galilean transformation** adds one constant velocity to everything in the picture. Velocities change; pressures, densities and temperatures (the *static* properties) do not. MECH 430 uses this constantly: a moving sound wave or shock becomes a steady flow if you ride along with it ([[c-sound-derivation]], [[c-moving-shocks]]). *Stagnation* properties do depend on the frame, because they depend on velocity ([[c-stagnation]]).
""",
        math=[r"\mathbf{V}' = \mathbf{V} - \mathbf{V}_{\text{frame}}"],
        analogy=analogy("Walking down the aisle of a moving train: the person next to you sees you at walking pace; someone on the platform sees train speed plus walking speed. The temperature of your coffee is the same to both.",
                        "only true at speeds far below light; relativity is irrelevant here, but the frame you pick still changes every velocity and stagnation property."),
        problems=[
            problem("p-ga-1", "Ride the wave",
                    r"A wave moves right at 340 m/s into still air.",
                    [num("In the wave's frame, what speed does the still air approach at (magnitude)?", 340, "m/s"),
                     choice("Is the air's static pressure different in the two frames?",
                            [opt("No: static properties don't depend on the frame", True), opt("Yes, it's higher in the wave frame", why="Only velocities (and stagnation properties) change with frame.")])]),
        ]),
    concept(
        "p-log-differentiation", "Differentials and logarithmic differentiation", 0, CA,
        r"""
For a product like $\rho VA = $ constant, take logs and differentiate:
$$\ln\rho + \ln V + \ln A = \text{const}\ \Rightarrow\ \frac{d\rho}{\rho} + \frac{dV}{V} + \frac{dA}{A} = 0.$$
The fractional changes add. MECH 430 derives every "how does the flow respond" result this way ([[c-1d-differential]]), then reads off signs.
""",
        math=[r"d\ln(\rho V A) = \frac{d\rho}{\rho} + \frac{dV}{V} + \frac{dA}{A}"],
        problems=[
            problem("p-ld-1", "Fractional changes",
                    r"$\rho VA$ is constant. Density drops 2% and area grows 1%.",
                    [num("Fractional change in $V$, in percent?", 1, "%", explain="$dV/V = -d\\rho/\\rho - dA/A = 2\\% - 1\\%$.")]),
            problem("p-ld-2", "Differentiate a power",
                    r"$T_0/T = 1 + \frac{\gamma-1}{2}M^2$ with $T_0$ constant.",
                    [expr(r"Type $dT/T$ divided by $dM$ (that is, $\frac{1}{T}\frac{dT}{dM}$) in terms of `M` and `gamma`.",
                          -(g - 1) * M / (1 + (g - 1) / 2 * M ** 2), ["M", "gamma"], ranges={"M": [0.2, 3], "gamma": [1.1, 1.7]})]),
        ]),
    concept(
        "p-root-finding", "Root finding: bisection and Newton", 0, CA,
        r"""
Many compressible-flow relations can't be inverted by hand: given $A/A^*$, find $M$. You bracket a root and shrink the bracket (**bisection**), or follow the tangent (**Newton**). Bisection never fails once you have a sign change; Newton is faster but can jump to the wrong branch. The notes iterate by hand ("try $M_3 = 0.31$..."); the Code track has you write the solver ([[c-area-ratio]]).
""",
        math=[r"x_{n+1} = x_n - \frac{f(x_n)}{f'(x_n)}"],
        problems=[
            problem("p-rf-1", "Bisection by hand",
                    r"$f(M) = M^2 - 2$ on $[1, 2]$.",
                    [num("After one bisection step, what is the new bracket's upper end?", 1.5, explain="$f(1.5) = 0.25 > 0$, so the root is in $[1, 1.5]$."),
                     num("After two steps, the midpoint you'd test next is:", 1.375)]),
            problem("p-rf-2", "Write bisection",
                    r"You'll reuse this solver all course.",
                    [code("Write `bisect(f, a, b)` that returns a root of `f` in `[a, b]` (assume `f(a)` and `f(b)` have opposite signs) to within 1e-10.",
                          starter="def bisect(f, a, b, tol=1e-10):\n    # halve [a, b] until it is shorter than tol\n    pass\n",
                          solution="def bisect(f, a, b, tol=1e-10):\n    fa = f(a)\n    while b - a > tol:\n        m = 0.5 * (a + b)\n        if fa * f(m) <= 0:\n            b = m\n        else:\n            a = m\n            fa = f(m)\n    return 0.5 * (a + b)\n",
                          tests="import math\ncheck('sqrt 2', bisect(lambda x: x*x - 2, 1, 2), math.sqrt(2), 1e-8)\ncheck('cos root', bisect(math.cos, 1, 2), math.pi/2, 1e-8)\ncheck('decreasing f', bisect(lambda x: 3 - x, 0, 10), 3.0, 1e-8)\n",
                          wrong=["def bisect(f, a, b, tol=1e-10):\n    return 0.5 * (a + b)\n",
                                 "def bisect(f, a, b, tol=1e-10):\n    while b - a > tol:\n        m = 0.5 * (a + b)\n        if f(m) > 0:\n            b = m\n        else:\n            a = m\n    return m\n"],
                          hints=["Keep the half where the sign changes: if f(a)·f(m) ≤ 0 the root is in [a, m].",
                                 "The second wrong version assumes f increases; your test should work for decreasing f too."],
                          fn="bisect")]),
        ]),
    concept(
        "p-pdes", "Elliptic, parabolic and hyperbolic PDEs", 0, CA,
        r"""
Second-order PDEs come in three families: **elliptic** (Laplace: every boundary influences every point, smooth solutions), **parabolic** (heat equation: diffusion forward in time), **hyperbolic** (wave equation: information travels at a finite speed along *characteristics*, and jumps can survive). Subsonic flow is elliptic; supersonic flow is hyperbolic ([[c-pde-types]]).
""",
        math=[r"B^2 - AC\ \begin{cases}<0 & \text{elliptic}\\=0 & \text{parabolic}\\>0 & \text{hyperbolic}\end{cases}"],
        problems=[
            problem("p-pd-1", "Classify",
                    r"The wave equation $\phi_{tt} = c^2\phi_{xx}$.",
                    [choice("Its type?", [opt("Hyperbolic: disturbances travel at speed c along characteristics", True),
                                          opt("Elliptic", why="Laplace's equation is elliptic; the wave equation has real characteristics."),
                                          opt("Parabolic", why="That's the heat equation, first order in time.")])]),
        ]),
    concept(
        "p-python", "Python functions, loops and the math module", 0, PY,
        r"""
The coding exercises in this atlas run real Python in your browser. You need: `def` to define a function, `return`, `if`/`else`, a `while` or `for` loop, and `import math` for `math.sqrt`, `math.log`, `math.sin` (radians!), `math.degrees`, `math.radians`. Plain floats only: no NumPy here, so the functions you write are exactly the formulas.

```python
import math

def sound_speed(T, gamma=1.4, R=287.0):
    return math.sqrt(gamma * R * T)
```
""",
        math=[],
        problems=[
            problem("p-py-1", "Degrees or radians",
                    r"`math.sin(30)`",
                    [choice("What does it return?", [opt("sin of 30 radians, about −0.988", True), opt("0.5", why="math.sin takes radians; use math.sin(math.radians(30)).")])]),
            problem("p-py-2", "Your first function",
                    r"The speed of sound in an ideal gas is $c = \sqrt{\gamma R T}$.",
                    [code("Complete `sound_speed(T, gamma, R)`.",
                          starter="import math\n\ndef sound_speed(T, gamma=1.4, R=287.0):\n    pass\n",
                          solution="import math\n\ndef sound_speed(T, gamma=1.4, R=287.0):\n    return math.sqrt(gamma * R * T)\n",
                          tests=f"check('air 300 K', sound_speed(300), {gas.sound(300):.6f}, 1e-6)\ncheck('helium 293 K', sound_speed(293.15, 1.67, 2078.5), {gas.sound(293.15, 1.67, 2078.5):.6f}, 1e-6)\n",
                          wrong=["import math\n\ndef sound_speed(T, gamma=1.4, R=287.0):\n    return math.sqrt(gamma * R * (T + 273.15))\n",
                                 "import math\n\ndef sound_speed(T, gamma=1.4, R=287.0):\n    return gamma * R * T\n"],
                          hints=["T is already in kelvin.", "Use math.sqrt."], fn="sound_speed")]),
        ]),
]
