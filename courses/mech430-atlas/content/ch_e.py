"""Layer 1, Chapters 12-15: oblique shocks and their reflection, Prandtl-Meyer expansions, nozzle exhaust
patterns, and the method of characteristics."""
import math
import sympy as sp
from lib import *
import gas

C12, C13, C14, C15 = ("Ch. 12 · Oblique shock waves", "Ch. 13 · Prandtl–Meyer expansions", "Ch. 14 · Nozzle exhaust",
                      "Ch. 15 · Method of characteristics")

# 12.2.1 / 12.3.1 (notes)
_o = gas.ob_after(3.0, 10.0)
_r = gas.ob_after(_o["M2"], 10.0)
# Variant: Mach 2.5, 15 degree wedge
_v = gas.ob_after(2.5, 15.0)
_vs = gas.ob_after(2.5, 15.0, strong=True)
_dm2 = gas.ob_max(2.0)
# 12.3.2 / 12.5 (notes): Mach 3, 30 degree wedge -> Mach reflection; polar intersection
_o30 = gas.ob_after(3.0, 30.0)
_dmax_behind = gas.ob_max(_o30["M2"])[0]


def _mr(d4):
    return gas.ob_after(3.0, 30 - d4, True)["p2p1"] - _o30["p2p1"] * gas.ob_after(_o30["M2"], d4)["p2p1"]


_d4 = gas.bisect(_mr, 8.0, _dmax_behind - 1e-6)
_d3 = 30 - _d4
_p34 = gas.ob_after(3.0, _d3, True)["p2p1"]
assert abs(_d3 - 21.4) < 0.05 and abs(_d4 - 8.6) < 0.05
# Prandtl-Meyer: notes M = 2 turned 10 deg; variant M = 1.5 turned 20 deg
_Mpm = gas.pm_M(gas.pm_nu(2.0) + 10)
_ppm = gas.p0_p(2.0) / gas.p0_p(_Mpm)
_Mpm2 = gas.pm_M(gas.pm_nu(1.5) + 20)
_ppm2 = gas.p0_p(1.5) / gas.p0_p(_Mpm2)
_fan1, _fan2 = gas.mach_angle(1.5), gas.mach_angle(_Mpm2) - 20   # fan edges measured from the original flow direction
# Underexpanded jet variant: design Mach 2.5 nozzle exhausting at pe/pb = 3
_Mj = gas.M_from_p0p(gas.p0_p(2.5) * 3.0)
_turn = gas.pm_nu(_Mj) - gas.pm_nu(2.5)
# MOC (notes)
_CI = gas.pm_nu(2.0) + 20
_CII = gas.pm_nu(2.1) - 5
_nu3, _th3, _M3 = gas.moc_interior(_CI, _CII)
# wall point: CII from point 1 meets a wall at 13 degrees
_nu4 = (gas.pm_nu(2.0) - 20) + 13
_M4 = gas.pm_M(_nu4)

CONCEPTS = [
    concept(
        "c-oblique-from-normal", "An oblique shock is a normal shock seen by a sliding observer", 1, C12,
        r"""
Take a normal shock and add a velocity $V_T$ **parallel** to it. Nothing physical changes (it's a frame change), but now the flow crosses the shock at an angle and gets turned. Conversely, at any oblique shock:
- the **tangential** velocity is unchanged (tangential momentum has no force acting);
- the **normal** component obeys the normal-shock relations exactly, with $M_{n1} = M_1\sin\sigma$.

So $p_2/p_1$, $\rho_2/\rho_1$, $T_2/T_1$ and $p_{02}/p_{01}$ come straight from the normal-shock relations at $M_{n1}$, and the downstream Mach number is $M_2 = M_{n2}/\sin(\sigma - \delta)$, where $\sigma$ is the shock angle and $\delta$ the deflection. The notes' mnemonic: sigma for shock, delta for deflection.
""",
        deeper=["c-normal-shock-relations", "p-galilean"],
        math=[r"M_{n1} = M_1\sin\sigma", r"M_2 = \frac{M_{n2}}{\sin(\sigma-\delta)}"],
        exam="Find σ first, then do everything with M_n1 in the normal-shock table, then convert M_n2 back.",
        source="Notes, Sections 12.1–12.2",
        problems=[
            problem("c-on-1", "Decompose",
                    r"Mach 3 flow meets an oblique shock at $\sigma = 30°$.",
                    [num("Normal Mach number $M_{n1}$?", 3 * math.sin(math.radians(30)), tol=0.002),
                     num("Pressure ratio across the shock?", gas.ns_p2p1(1.5), tol=0.002),
                     choice("What happens to the velocity component along the shock?", [opt("Unchanged", True), opt("Drops like the normal component", why="No force acts along the shock, so tangential momentum is conserved.")])]),
        ]),
    concept(
        "c-theta-beta-mach", "The δ–σ–M relation: weak and strong shocks, and detachment", 1, C12,
        r"""
Geometry plus the normal-shock relations tie the three together:
$$\tan\delta = 2\cot\sigma\,\frac{M_1^2\sin^2\sigma - 1}{M_1^2(\gamma + \cos2\sigma) + 2}.$$
For fixed $M_1$, $\sigma$ runs from the Mach angle $\mu$ (a sound wave, $\delta = 0$) to 90° (a normal shock, $\delta = 0$), and $\delta$ peaks in between at $\delta_{max}$ (34.1° at Mach 3). Below the peak each $\delta$ has two shocks: **weak** (usually observed, usually supersonic behind) and **strong** (subsonic behind; only forced by downstream conditions). Above $\delta_{max}$ no attached shock exists: the shock **detaches** into a curved bow shock.

As $M\to\infty$, $\delta_{max}\to\sin^{-1}(1/\gamma) = 45.58°$. (The notes quote 45.37°; the exact limit is 45.58° for γ = 1.4.) In practice you read $\sigma$ off the chart and refine by iteration.
""",
        deeper=["c-oblique-from-normal", "c-mach-cone", "p-root-finding"],
        math=[r"\tan\delta = 2\cot\sigma\,\frac{M_1^2\sin^2\sigma - 1}{M_1^2(\gamma+\cos2\sigma)+2}"],
        widget={"type": "wedge"},
        exam="Assume the weak solution unless told otherwise. If δ > δmax, the shock detaches.",
        source="Notes, Section 12.2",
        problems=[
            problem("c-tb-1", "The notes' wedge (example 12.2.1)",
                    r"Mach 3 air at 1 atm meets a 10° wedge.",
                    [num("Weak shock angle σ?", _o["sigma"], "°", tol=0.003), num("$M_{n1}$?", _o["Mn1"], tol=0.003),
                     num("Downstream Mach number?", _o["M2"], tol=0.003), num("Downstream pressure?", _o["p2p1"], "atm", tol=0.003),
                     dial("Slide σ until the deflection is 10° (weak branch, below the δ_max angle of 65°).", "ob_delta", 10.0, 20.0, 65.0, 0.01, _o["sigma"], args={"M": 3.0}, var="σ", unit="°", tol=0.002)],
                    kind="notes"),
            problem("c-tb-2", "A new wedge",
                    r"Mach 2.5, 15° wedge, γ = 1.4.",
                    [num("Weak σ?", _v["sigma"], "°", tol=0.003), num("Weak-shock $M_2$?", _v["M2"], tol=0.003), num("Weak-shock $p_2/p_1$?", _v["p2p1"], tol=0.003),
                     num("Strong-shock σ?", _vs["sigma"], "°", tol=0.003),
                     choice("Flow behind the strong shock is:", [opt("Subsonic", True), opt("Supersonic", why=f"Its Mach number is {_vs['M2']:.2f}.")]),
                     num("Largest attached deflection at Mach 2?", _dm2[0], "°", tol=0.003)]),
            problem("c-tb-3", "Code the oblique shock",
                    r"Write the relation, then invert it.",
                    [code("Write `deflection(M, sigma_deg, g)` returning δ in degrees, and `weak_sigma(M, delta_deg, g)` that finds the weak shock angle by bisection between the Mach angle and the angle of maximum deflection (`sigma_max` is given).",
                          starter="import math\n\ndef deflection(M, sigma_deg, g=1.4):\n    pass\n\ndef sigma_max(M, g=1.4):\n    # angle of maximum deflection, by golden-section search (provided)\n    a, b = math.degrees(math.asin(1 / M)), 90.0\n    phi = (math.sqrt(5) - 1) / 2\n    for i in range(100):\n        c, d = b - phi * (b - a), a + phi * (b - a)\n        if deflection(M, c, g) > deflection(M, d, g):\n            b = d\n        else:\n            a = c\n    return 0.5 * (a + b)\n\ndef weak_sigma(M, delta_deg, g=1.4):\n    pass\n",
                          solution="import math\n\ndef deflection(M, sigma_deg, g=1.4):\n    s = math.radians(sigma_deg)\n    t = 2 / math.tan(s) * (M * M * math.sin(s) ** 2 - 1) / (M * M * (g + math.cos(2 * s)) + 2)\n    return math.degrees(math.atan(t))\n\ndef sigma_max(M, g=1.4):\n    a, b = math.degrees(math.asin(1 / M)), 90.0\n    phi = (math.sqrt(5) - 1) / 2\n    for i in range(100):\n        c, d = b - phi * (b - a), a + phi * (b - a)\n        if deflection(M, c, g) > deflection(M, d, g):\n            b = d\n        else:\n            a = c\n    return 0.5 * (a + b)\n\ndef weak_sigma(M, delta_deg, g=1.4):\n    a, b = math.degrees(math.asin(1 / M)) + 1e-9, sigma_max(M, g)\n    f = lambda s: deflection(M, s, g) - delta_deg\n    for i in range(200):\n        m = 0.5 * (a + b)\n        if f(a) * f(m) <= 0:\n            b = m\n        else:\n            a = m\n    return 0.5 * (a + b)\n",
                          tests=f"check('delta(3, 30 deg)', deflection(3.0, 30.0), {gas.ob_delta(3.0, 30.0):.10f}, 1e-8)\ncheck('notes sigma', weak_sigma(3.0, 10.0), {_o['sigma']:.8f}, 1e-6)\ncheck('variant sigma', weak_sigma(2.5, 15.0), {_v['sigma']:.8f}, 1e-6)\n",
                          wrong=["import math\n\ndef deflection(M, sigma_deg, g=1.4):\n    s = sigma_deg\n    t = 2 / math.tan(s) * (M * M * math.sin(s) ** 2 - 1) / (M * M * (g + math.cos(2 * s)) + 2)\n    return math.degrees(math.atan(t))\n\ndef sigma_max(M, g=1.4):\n    return 60.0\n\ndef weak_sigma(M, delta_deg, g=1.4):\n    return 30.0\n",
                                 "import math\n\ndef deflection(M, sigma_deg, g=1.4):\n    s = math.radians(sigma_deg)\n    t = 2 / math.tan(s) * (M * M * math.sin(s) ** 2 - 1) / (M * M * (g + math.cos(2 * s)) + 2)\n    return math.degrees(math.atan(t))\n\ndef sigma_max(M, g=1.4):\n    return 90.0\n\ndef weak_sigma(M, delta_deg, g=1.4):\n    a, b = 45.0, 90.0\n    f = lambda s: deflection(M, s, g) - delta_deg\n    for i in range(200):\n        m = 0.5 * (a + b)\n        if f(a) * f(m) <= 0:\n            b = m\n        else:\n            a = m\n    return 0.5 * (a + b)\n"],
                          hints=["math.tan and math.sin take radians: convert σ first.", "Two roots exist; the weak one lies between the Mach angle and the angle of maximum deflection."],
                          fn="weak_sigma")]),
        ]),
    concept(
        "c-shock-reflection", "Regular reflection: the wall turns the flow back with a second, weaker shock", 1, C12,
        r"""
An oblique shock hitting a straight wall reflects, but not like light: the reflected shock is set by the flow *behind* the incident shock and the requirement that the flow end up parallel to the wall. Solve it as a second oblique-shock problem: the post-shock flow (at $M_2$) meets a "wedge" of the same deflection $\delta$, back toward the wall. The reflected shock is weaker (the flow is already slower) and its angle to the wall differs from the incident angle. The pair decelerates and compresses the flow, much like an isentropic converging duct would, with small stagnation-pressure losses.
""",
        deeper=["c-theta-beta-mach"],
        math=[r"\delta_{reflected} = \delta_{incident}\ \text{(flow returns parallel to the wall)}"],
        source="Notes, Section 12.3",
        problems=[
            problem("c-rf-1", "Reflection of the notes' shock (example 12.3.1)",
                    r"The Mach 3, 10° shock (behind it: $M_2 = 2.50$, $p_2 = 2.055$ atm) reflects from a parallel wall.",
                    [num("Reflected shock angle (relative to the flow approaching it)?", _r["sigma"], "°", tol=0.003),
                     num("Mach number behind the reflected shock?", _r["M2"], tol=0.006),
                     num("Pressure behind it?", _o["p2p1"] * _r["p2p1"], "atm", tol=0.003)],
                    kind="notes"),
        ]),
    concept(
        "c-shock-polars", "Shock polars: every oblique shock from one state, as pressure vs. deflection", 1, C12,
        r"""
Sweep $\sigma$ from $\mu$ to 90° and plot $p_2/p_1$ against $\delta$: a **shock polar**, a loop reaching from (0°, 1) through $\delta_{max}$ to the normal-shock pressure at $\delta = 0$. Two flows that meet must share **pressure and direction**, so shock interactions become geometry: intersect polars. For a reflection, draw the incident polar from the free stream, and from the post-shock point draw the reflected polar, turning the other way. Where it crosses $\delta = 0$ is the regular reflection. If it can't reach $\delta = 0$, regular reflection is impossible.
""",
        deeper=["c-theta-beta-mach", "c-shock-reflection"],
        math=[r"\left(\delta(\sigma),\ \frac{p_2}{p_1}(\sigma)\right),\quad \mu\le\sigma\le 90°"],
        widget={"type": "polar"},
        source="Notes, Section 12.5",
        problems=[
            problem("c-sp-1", "Read the polar",
                    r"The polar for Mach 3.",
                    [num("Pressure ratio where the polar crosses $\\delta = 0$ at the top (σ = 90°)?", gas.ns_p2p1(3.0), tol=0.002),
                     choice("At $\\delta = 10°$ the polar gives two pressures. Which is usually observed?", [opt("The lower one: the weak shock", True),
                                                                                                          opt("The higher one", why="The strong branch is only forced by downstream conditions.")])]),
        ]),
    concept(
        "c-mach-reflection", "Mach reflection: a triple point, a Mach stem and a slip line", 1, C12,
        r"""
If the flow behind the incident shock needs more turning than its own $\delta_{max}$ allows, no regular reflection exists. Nature builds three shocks meeting at a **triple point**: the incident shock, a reflected shock, and a near-normal **Mach stem** reaching the wall, plus a **slip line** separating gas that crossed two shocks from gas that crossed one (same pressure and direction, different velocity and entropy). Ernst Mach found it in 1875 with soot-coated glass.

On polars: the incident polar is also the Mach stem's polar; the solution is where the reflected polar crosses the incident polar's **strong** branch. Which reflection occurs between the "von Neumann" (mechanical equilibrium) and "detachment" criteria is still debated, and shows **hysteresis**, like inlet starting.
""",
        deeper=["c-shock-polars"],
        math=[r"p_3 = p_4,\quad \delta_2 - \delta_4 = \delta_3"],
        widget={"type": "polar", "preset": "mach"},
        source="Notes, Sections 12.4–12.7",
        problems=[
            problem("c-mr-1", "Mach 3, 30° wedge (notes example 12.3.2)",
                    r"The incident shock leaves Mach 1.41 flow, which would have to turn back 30°.",
                    [num("Largest deflection available behind the incident shock?", _dmax_behind, "°", tol=0.01),
                     choice("So the reflection is:", [opt("Mach reflection", True), opt("Regular", why=f"30° exceeds the {_dmax_behind:.1f}° that Mach {_o30['M2']:.2f} flow can turn through one oblique shock.")]),
                     num("From the polar intersection: deflection across the Mach stem?", _d3, "°", tol=0.005),
                     num("And across the reflected shock?", _d4, "°", tol=0.01),
                     num("Pressure behind the triple point, $p/p_1$?", _p34, tol=0.005)],
                    kind="notes"),
            problem("c-mr-2", "What's a slip line?",
                    r"Behind the triple point.",
                    [choice("What is equal across the slip line?", [opt("Pressure and flow direction", True), opt("Velocity", why="The two streams crossed different shocks, so their speeds and entropies differ."),
                                                                     opt("Entropy", why="The stream through the Mach stem gained more entropy.")])]),
        ]),
    concept(
        "c-expansion-fan", "Expansions spread into fans: they never coalesce", 1, C13,
        r"""
At a gently curved **compressive** corner, successive Mach waves steepen (each turns the flow into the next and lowers the Mach number, widening the Mach angle), so they converge into an oblique shock: the steady 2-D cousin of the accelerating piston. At an **expansive** corner, each wave turns the flow away and *raises* the Mach number, narrowing the next Mach angle: the waves spread apart. The flow stays isentropic through a smooth **expansion fan**. A sharp corner gives a **centred Prandtl–Meyer fan**.
""",
        deeper=["c-mach-cone", "c-shock-formation"],
        math=[r"\mu = \sin^{-1}(1/M)\ \text{falls as } M \text{ rises}"],
        source="Notes, Ch. 13",
        problems=[
            problem("c-ef-1", "Why no expansion shocks in 2-D either?",
                    r"Supersonic flow turns away from itself around a corner.",
                    [choice("Each successive Mach wave makes a ____ angle with the local flow:", [opt("Smaller, because M has increased", True), opt("Larger", why="That happens in a compressive corner; here the flow accelerates.")])]),
        ]),
    concept(
        "c-prandtl-meyer", "The Prandtl–Meyer function: turning angle ↔ Mach number", 1, C13,
        r"""
Across a single weak Mach wave the tangential velocity is unchanged, giving $d\nu = \sqrt{M^2-1}\,dV/V$. Integrating from Mach 1:
$$\nu(M) = \sqrt{\frac{\gamma+1}{\gamma-1}}\tan^{-1}\sqrt{\frac{\gamma-1}{\gamma+1}(M^2-1)} - \tan^{-1}\sqrt{M^2-1}.$$
$\nu$ is the angle a sonic flow must turn to reach $M$. For a flow at $M_1$ turned through $\theta$: $\nu(M_2) = \nu(M_1) + \theta$; then isentropic relations give $p_2$, $T_2$ ($p_0$ and $T_0$ unchanged). The maximum, as $M\to\infty$, is $\nu_{max} = 90°(\sqrt{(\gamma+1)/(\gamma-1)} - 1) = 130.45°$: past that, the flow can't follow the wall and a vacuum region forms.
""",
        deeper=["c-expansion-fan", "c-stagnation"],
        math=[r"\nu(M_2) = \nu(M_1) + \theta", r"\nu_{max} = \frac{\pi}{2}\left(\sqrt{\frac{\gamma+1}{\gamma-1}} - 1\right)"],
        widget={"type": "pmfan"},
        source="Notes, Section 13.1",
        problems=[
            problem("c-pm-1", "The notes' corner",
                    r"Mach 2 air turns 10° away around a corner.",
                    [num("$\\nu(2)$?", gas.pm_nu(2.0), "°", tol=0.002), num("Downstream Mach number?", _Mpm, tol=0.003), num("$p_2/p_1$?", 1 / _ppm, tol=0.003)],
                    kind="notes"),
            problem("c-pm-2", "A new corner",
                    r"Mach 1.5 air turns 20° away.",
                    [num("$\\nu(1.5)$?", gas.pm_nu(1.5), "°", tol=0.003), num("Downstream Mach number?", _Mpm2, tol=0.003), num("$p_2/p_1$?", 1 / _ppm2, tol=0.003),
                     num("Angle of the fan's first wave from the original flow direction?", _fan1, "°", tol=0.003),
                     num("Angle of the last wave from the original flow direction?", _fan2, "°", tol=0.005, explain="The local Mach angle minus the 20° the flow has turned."),
                     dial("Slide M until ν = 30°.", "pm_nu", 30.0, 1.0, 4.0, 0.001, gas.pm_M(30.0), var="M", tol=0.002)]),
            problem("c-pm-3", "Code Prandtl–Meyer",
                    r"Function and inverse.",
                    [code("Write `pm_nu(M, g)` in degrees and `pm_mach(nu_deg, g)` by bisection on [1, 50].",
                          starter="import math\n\ndef pm_nu(M, g=1.4):\n    pass\n\ndef pm_mach(nu_deg, g=1.4):\n    pass\n",
                          solution="import math\n\ndef pm_nu(M, g=1.4):\n    k = math.sqrt((g + 1) / (g - 1))\n    return math.degrees(k * math.atan(math.sqrt((M * M - 1) / (k * k))) - math.atan(math.sqrt(M * M - 1)))\n\ndef pm_mach(nu_deg, g=1.4):\n    a, b = 1.0, 50.0\n    for i in range(200):\n        m = 0.5 * (a + b)\n        if (pm_nu(a, g) - nu_deg) * (pm_nu(m, g) - nu_deg) <= 0:\n            b = m\n        else:\n            a = m\n    return 0.5 * (a + b)\n",
                          tests=f"check('nu(2)', pm_nu(2.0), {gas.pm_nu(2.0):.10f}, 1e-8)\ncheck('nu(3)', pm_nu(3.0), {gas.pm_nu(3.0):.10f}, 1e-8)\ncheck('M from 36.38', pm_mach({gas.pm_nu(2.0) + 10:.10f}), {_Mpm:.10f}, 1e-7)\n",
                          wrong=["import math\n\ndef pm_nu(M, g=1.4):\n    k = math.sqrt((g + 1) / (g - 1))\n    return k * math.atan(math.sqrt((M * M - 1) / (k * k))) - math.atan(math.sqrt(M * M - 1))\n\ndef pm_mach(nu_deg, g=1.4):\n    return 2.0\n",
                                 "import math\n\ndef pm_nu(M, g=1.4):\n    k = math.sqrt((g + 1) / (g - 1))\n    return math.degrees(k * math.atan(math.sqrt((M * M - 1) * k * k)) - math.atan(math.sqrt(M * M - 1)))\n\ndef pm_mach(nu_deg, g=1.4):\n    return 2.0\n"],
                          hints=["math.atan returns radians; convert with math.degrees.", "Inside the first arctan, divide (M² − 1) by (γ+1)/(γ−1)."], fn="pm_mach")]),
        ]),
    concept(
        "c-over-under-expanded", "Nozzle exhaust: oblique shocks when overexpanded, fans when underexpanded", 1, C14,
        r"""
The nozzle story's last two regimes:
- **Overexpanded** ($p_4 > p_b > p_d$): supersonic all the way, but the exit pressure is too low. Oblique shocks attached to the nozzle lip turn the jet inward and raise its pressure to $p_b$.
- **Underexpanded** ($p_b < p_d$): exit pressure too high. Prandtl–Meyer fans at the lip turn the jet outward to expand to $p_b$. At high altitude the turn can approach 90° (the Saturn I's billowing plume), and the sideways velocity is wasted thrust.

Shocks reflect off the jet's centreline (or form Mach reflections in round jets) and come back off the free boundary as expansions, then compressions: the repeating **Mach diamonds** (shock bottles) seen in jet and rocket exhaust.
""",
        deeper=["c-back-pressure-regimes", "c-prandtl-meyer", "c-mach-reflection", "c-optimal-expansion"],
        math=[r"\nu(M_j) = \nu(M_e) + \theta\ \text{(underexpanded lip)}"],
        widget={"type": "nozzle", "preset": "plume"},
        source="Notes, Section 14.1",
        problems=[
            problem("c-ou-1", "An underexpanded jet",
                    r"A Mach 2.5 nozzle exits at three times the ambient pressure.",
                    [choice("What forms at the lip?", [opt("A Prandtl–Meyer expansion fan, turning the jet outward", True), opt("An oblique shock", why="That's the overexpanded case, where the jet needs compressing.")]),
                     num("Jet Mach number after expanding to ambient?", _Mj, tol=0.003),
                     num("Angle the boundary turns outward?", _turn, "°", tol=0.005)]),
            problem("c-ou-2", "Name the regime",
                    r"A nozzle has $p_3/p_0 = 0.96$, $p_4/p_0 = 0.43$, $p_d/p_0 = 0.064$.",
                    [choice("$p_b/p_0 = 0.2$:", [opt("Overexpanded: oblique shocks outside the nozzle", True), opt("A normal shock inside", why="That needs p_b between p4 and p3."),
                                                  opt("Underexpanded", why="That needs p_b below pd.")]),
                     choice("$p_b/p_0 = 0.03$:", [opt("Underexpanded: expansion fans at the lip", True), opt("Overexpanded", why="p_b is below pd, so the jet must expand further.")])]),
        ]),
    concept(
        "c-pde-types", "Subsonic flow is elliptic, supersonic flow is hyperbolic", 1, C15,
        r"""
For steady, 2-D, **irrotational** and isentropic flow, a velocity potential $\phi$ ($\mathbf{V} = \nabla\phi$) turns continuity and momentum into one equation:
$$\left(1 - \frac{u^2}{c^2}\right)\phi_{xx} - \frac{2uv}{c^2}\phi_{xy} + \left(1 - \frac{v^2}{c^2}\right)\phi_{yy} = 0.$$
Its type flips with Mach number: **elliptic** when subsonic (every boundary is felt everywhere; Laplace's equation in the low-speed limit) and **hyperbolic** when supersonic (influence confined to Mach cones; jumps can survive). Irrotational excludes boundary layers and flow behind **curved** shocks: by Crocco's theorem, an entropy gradient means vorticity.
""",
        deeper=["p-pdes", "c-mach-cone"],
        math=[r"B^2 - AC = M^2 - 1"],
        source="Notes, Sections 15.1–15.2",
        problems=[
            problem("c-pt-1", "Classify by Mach number",
                    r"The potential equation with $u = V$, $v = 0$: $(1 - M^2)\phi_{xx} + \phi_{yy} = 0$.",
                    [choice("At Mach 0.5 it is:", [opt("Elliptic", True), opt("Hyperbolic", why="1 − M² > 0 gives the same sign as φ_yy: Laplace-like.")]),
                     choice("At Mach 2 it is:", [opt("Hyperbolic, with characteristics at the Mach angle", True), opt("Elliptic", why="1 − M² < 0: a wave equation in x.")]),
                     choice("Why can't the method of characteristics handle the flow behind a curved bow shock (without changes)?",
                            [opt("Different streamlines cross different shock strengths, so entropy varies and the flow is rotational", True),
                             opt("The flow is subsonic everywhere behind it", why="Behind a curved shock part of the flow can be supersonic; the issue is the vorticity.")])]),
        ]),
    concept(
        "c-characteristics", "Characteristics: Mach lines that carry ν + θ and ν − θ", 1, C15,
        r"""
In supersonic 2-D flow, derivatives become indeterminate along two families of lines at angle $\pm\mu$ to the local flow: they're **Mach lines**, and they're the **characteristics**. Along them the PDE collapses to an ODE that integrates to the Prandtl–Meyer function:
$$C_I:\ \nu + \theta = \text{const along right-running}\ (\theta - \mu)\qquad C_{II}:\ \nu - \theta = \text{const along left-running}\ (\theta + \mu).$$
Each tiny disturbance sends one of each, carrying its constant through the flow. "Characteristics are real": scratches on a tunnel wall make them visible in schlieren photographs.
""",
        deeper=["c-pde-types", "c-prandtl-meyer"],
        math=[r"C_I = \nu + \theta", r"C_{II} = \nu - \theta"],
        source="Notes, Section 15.2",
        problems=[
            problem("c-ct-1", "Carry the constants",
                    r"At a point the flow is at Mach 2 and θ = 20°.",
                    [num("$C_I = \\nu + \\theta$ carried by its right-running characteristic?", _CI, "°", tol=0.002),
                     num("$C_{II} = \\nu - \\theta$ carried by its left-running characteristic?", gas.pm_nu(2.0) - 20, "°", tol=0.003),
                     num("Angle of the left-running characteristic to the horizontal (θ + μ)?", 20 + gas.mach_angle(2.0), "°", tol=0.002)]),
        ]),
    concept(
        "c-moc-unit-processes", "Unit processes: an interior point and a wall point", 1, C15,
        r"""
**Interior point**: the right-running characteristic from point 1 meets the left-running one from point 2 at point 3. Both constants hold there, so
$$\nu_3 = \frac{(C_I)_1 + (C_{II})_2}{2},\qquad \theta_3 = \frac{(C_I)_1 - (C_{II})_2}{2}.$$
**Wall point**: a characteristic hits a wall; the wall fixes $\theta$, so one constant plus $\theta_{wall}$ gives $\nu$. Then $M$ from the Prandtl–Meyer table, and $p$, $T$ from isentropic relations. Locate points by drawing straight segments at $\theta\pm\mu$ (averages improve it). March from a known supersonic data line (not the sonic throat) and keep a table: that's all a characteristics solver is.
""",
        deeper=["c-characteristics"],
        math=[r"\nu_3 = \tfrac12\left[(C_I)_1 + (C_{II})_2\right]", r"\theta_3 = \tfrac12\left[(C_I)_1 - (C_{II})_2\right]"],
        widget={"type": "moc"},
        source="Notes, Sections 15.3–15.4",
        problems=[
            problem("c-mu-1", "The notes' interior point",
                    r"Point 1: $M = 2$, θ = 20°. Point 2: $M = 2.1$, θ = 5°. The $C_I$ from 1 meets the $C_{II}$ from 2 at point 3.",
                    [num("$(C_{II})_2$?", _CII, "°", tol=0.003), num("$\\theta_3$?", _th3, "°", tol=0.003), num("$\\nu_3$?", _nu3, "°", tol=0.003),
                     num("$M_3$?", _M3, tol=0.003),
                     choice("$M_3$ is higher than at points 1 and 2. Why does that make sense?", [opt("The flow is supersonic and spreading (θ decreasing downward), like a diverging duct", True),
                                                                                                 opt("Characteristics always accelerate the flow", why="They carry information; the geometry decides.")])],
                    kind="notes"),
            problem("c-mu-2", "A wall point",
                    r"The $C_{II}$ characteristic from point 1 (θ = 20°, M = 2) reaches a wall inclined at 13°.",
                    [num("$\\nu$ at the wall?", _nu4, "°", tol=0.005), num("Mach number at the wall?", _M4, tol=0.005)],
                    kind="notes"),
            problem("c-mu-3", "Code the unit process",
                    r"Interior point in a few lines (a Prandtl–Meyer inverse is provided).",
                    [code("Write `interior(CI, CII)` returning `(theta, nu, M)`.",
                          starter="import math\n\ndef pm_nu(M, g=1.4):\n    k = math.sqrt((g + 1) / (g - 1))\n    return math.degrees(k * math.atan(math.sqrt((M * M - 1) / (k * k))) - math.atan(math.sqrt(M * M - 1)))\n\ndef pm_mach(nu):\n    a, b = 1.0, 50.0\n    for i in range(200):\n        m = 0.5 * (a + b)\n        if (pm_nu(a) - nu) * (pm_nu(m) - nu) <= 0:\n            b = m\n        else:\n            a = m\n    return 0.5 * (a + b)\n\ndef interior(CI, CII):\n    pass\n",
                          solution="import math\n\ndef pm_nu(M, g=1.4):\n    k = math.sqrt((g + 1) / (g - 1))\n    return math.degrees(k * math.atan(math.sqrt((M * M - 1) / (k * k))) - math.atan(math.sqrt(M * M - 1)))\n\ndef pm_mach(nu):\n    a, b = 1.0, 50.0\n    for i in range(200):\n        m = 0.5 * (a + b)\n        if (pm_nu(a) - nu) * (pm_nu(m) - nu) <= 0:\n            b = m\n        else:\n            a = m\n    return 0.5 * (a + b)\n\ndef interior(CI, CII):\n    nu = (CI + CII) / 2\n    theta = (CI - CII) / 2\n    return theta, nu, pm_mach(nu)\n",
                          tests=f"r = interior({_CI:.10f}, {_CII:.10f})\ncheck('theta3', r[0], {_th3:.8f}, 1e-7)\ncheck('nu3', r[1], {_nu3:.8f}, 1e-7)\ncheck('M3', r[2], {_M3:.8f}, 1e-6)\n",
                          wrong=["import math\n\ndef pm_nu(M, g=1.4):\n    k = math.sqrt((g + 1) / (g - 1))\n    return math.degrees(k * math.atan(math.sqrt((M * M - 1) / (k * k))) - math.atan(math.sqrt(M * M - 1)))\n\ndef pm_mach(nu):\n    return 2.0\n\ndef interior(CI, CII):\n    nu = (CI - CII) / 2\n    theta = (CI + CII) / 2\n    return theta, nu, pm_mach(nu)\n"],
                          hints=["Add the two constants for ν, subtract for θ, and halve both."], fn="interior")]),
        ]),
    concept(
        "c-moc-breakdown", "When the method breaks: crossing characteristics and sonic flow", 1, C15,
        r"""
March until one of two things happens:
- **Characteristics of the same family cross**: they coalesce into an oblique shock. The flow is no longer isentropic or irrotational. A weak shock can be fudged as a characteristic; a strong one can't.
- **Sonic or subsonic flow appears**: $\mu$ is undefined at $M = 1$ and the equation turns elliptic.

Modern CFD has largely replaced hand characteristics, but the ideas underpin many solvers. A computer version with many characteristics reproduces 1-D isentropic $A/A^*$ results in a gently diverging channel: a check of both methods.
""",
        deeper=["c-moc-unit-processes", "c-shock-formation"],
        math=[],
        source="Notes, Sections 15.6–15.8",
        problems=[
            problem("c-mb-1", "Stop or continue?",
                    r"While marching a characteristics solution you find two right-running characteristics crossing.",
                    [choice("What does that mean?", [opt("A shock is forming: isentropic, irrotational assumptions are failing there", True),
                                                    opt("A bookkeeping error, always", why="It can be an error, but in a compressive region it's physics: characteristics coalesce into shocks.")])]),
        ]),
]
