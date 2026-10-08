"""Layer 1, Chapters 7-9: shock waves, flows with shocks (nozzles, moving shocks), and applications
(pitot probes, supersonic inlets, wind tunnels, trains in tunnels)."""
import math
import sympy as sp
from lib import *
import gas

C7, C8, C9 = "Ch. 7 · Normal shock waves", "Ch. 8 · Flows with shocks", "Ch. 9 · Applications of shocks"
ATM = 101325.0
R288 = gas.R_of(28.8)

# 8.1.1 (notes): At = 1, shock at A = 2.0 m^2, exit A = 3.0 m^2, p0 = 1 atm, T0 = 300 K
_Mx = gas.M_from_AR(2.0, True)
_px, _Tx = 1 / gas.p0_p(_Mx), 300 / gas.T0_T(_Mx)
_My = gas.ns_M2(_Mx)
_py, _Ty = _px * gas.ns_p2p1(_Mx), _Tx * gas.ns_T2T1(_Mx)
_p0y = gas.ns_p02p01(_Mx)
_MC = gas.M_from_AR(3.0 * _p0y, False)
_pC = _p0y / gas.p0_p(_MC)
# 8.2.1 (notes): At = 1, Ae = 3, pb = 0.7 atm
_n3 = gas.nozzle(3.0, 0.7)
# Variant: At = 1, Ae = 2.5, p0 = 1 atm, pb = 0.75 atm
_n25 = gas.nozzle(2.5, 0.75)
# 8.4.1 (notes): Mach 3 shock into 1 atm, 300 K
_cx = gas.sound(300, R=R288)
_Vs = 3 * _cx
_vp = gas.piston_speed(3.0) * _cx
# Variant: piston at 400 m/s into air at 290 K
_c290 = gas.sound(290, R=287)
_Ms400 = gas.piston_shock_mach(400 / _c290)
# Pitot variant: pitot reads 450 kPa, static port 100 kPa
_ratio = 4.5
_Mpit = gas.bisect(lambda m: gas.pitot_ratio(m) - _ratio, 1.0, 10.0)
_Msub_pitot = gas.M_from_p0p(1.3)
# Inlet variant: design Mach 1.7
_Ai17 = gas.inlet_isentropic_ratio(1.7)
_Mst17 = gas.bisect(lambda m: gas.inlet_start_ratio(m) - _Ai17, 1.0001, 50)
_open17 = gas.inlet_start_ratio(1.7)
# Kantrowitz limit: the largest design Mach number that overspeeding can still start
_kant = gas.bisect(lambda m: gas.inlet_isentropic_ratio(m) - gas.inlet_start_ratio(1e6), 1.01, 10)
# Wind tunnel: Mach 2.5 test section
_wt = 1 / gas.ns_p02p01(2.5)
# Train variant: 90 m/s in air at 300 K (MW 28.8)
_Mstrain = gas.piston_shock_mach(90 / _cx)
_dptrain = gas.ns_p2p1(_Mstrain) - 1
_tunnel = 1 / (1 - 1 / gas.A_Astar(90 / _cx))

NOZZLE_HELPERS = '''import math

def p0_p(M, g=1.4):
    return (1 + (g - 1) / 2 * M * M) ** (g / (g - 1))

def area_ratio(M, g=1.4):
    return (1 / M) * ((2 / (g + 1)) * (1 + (g - 1) / 2 * M * M)) ** ((g + 1) / (2 * (g - 1)))

def bisect(f, a, b, n=200):
    fa = f(a)
    for i in range(n):
        m = 0.5 * (a + b)
        fm = f(m)
        if fa * fm <= 0:
            b = m
        else:
            a, fa = m, fm
    return 0.5 * (a + b)

def mach_from_area(ar, supersonic, g=1.4):
    if supersonic:
        return bisect(lambda M: area_ratio(M, g) - ar, 1.0, 50.0)
    return bisect(lambda M: area_ratio(M, g) - ar, 1e-6, 1.0)

def shock_p0_ratio(M, g=1.4):
    M2 = math.sqrt((1 + (g - 1) / 2 * M * M) / (g * M * M - (g - 1) / 2))
    pr = 1 + 2 * g / (g + 1) * (M * M - 1)
    return pr * p0_p(M2, g) / p0_p(M, g)

def shock_p_ratio(M, g=1.4):
    return 1 + 2 * g / (g + 1) * (M * M - 1)
'''
NOZZLE_SOLUTION = '''
def critical(AeAt):
    p3 = 1 / p0_p(mach_from_area(AeAt, False))
    Msup = mach_from_area(AeAt, True)
    pd = 1 / p0_p(Msup)
    p4 = pd * shock_p_ratio(Msup)
    return p3, p4, pd

def nozzle_regime(AeAt, pb):
    p3, p4, pd = critical(AeAt)
    if pb >= p3:
        return 'subsonic'
    if pb > p4:
        return 'shock'
    if abs(pb - pd) <= 1e-6 * pd:
        return 'design'
    if pb > pd:
        return 'overexpanded'
    return 'underexpanded'

def exit_pressure(AeAt, As):
    r = shock_p0_ratio(mach_from_area(As, True))
    Me = mach_from_area(AeAt * r, False)
    return r / p0_p(Me)

def shock_area(AeAt, pb):
    return bisect(lambda As: exit_pressure(AeAt, As) - pb, 1.0 + 1e-9, AeAt)
'''

CONCEPTS = [
    concept(
        "c-shock-formation", "Compression waves catch up and steepen into a shock", 1, C7,
        r"""
Push a piston into a tube in a series of nudges. Each nudge sends a compression wave. Every later wave travels through gas that's **warmer** (so $c$ is higher) and **already moving** toward it (so it rides on that velocity). Later waves are faster and catch up with earlier ones. They can't pass through, so they merge: the pressure rise becomes finite and abrupt, a **shock wave**. It's only a few mean free paths thick (under a micron): effectively a discontinuity.

On an $x$–$t$ diagram (time up, slope = 1/speed), the compression waves from an accelerating piston converge into a shock. Pull the piston out instead and the rarefaction waves fan *apart*: expansions never form shocks.
""",
        deeper=["c-sound-derivation", "c-sound-ideal-gas"],
        math=[r"\text{later wave speed} = c_{later} + \textstyle\sum dV > \text{earlier wave speed}"],
        widget={"type": "xt"},
        analogy=analogy("Cars accelerating onto a highway one by one, each a bit faster than the last: the platoon bunches up from behind until it's bumper to bumper.",
                        "cars can brake; waves can't. The bunching becomes a true jump in pressure, not just tight spacing."),
        exam="Read x–t diagrams by slope: steep = slow, shallow = fast. Converging lines mean a shock is forming.",
        source="Notes, Section 7.1",
        problems=[
            problem("c-sf-1", "Why do they catch up?",
                    r"A piston accelerates into still gas, sending a train of compression waves.",
                    [choice("Which two effects make the later waves faster?", [opt("They travel through gas that is warmer and already moving in their direction", True),
                                                                             opt("They carry more energy", why="Speed relative to the gas depends on the gas temperature, not the wave's energy."),
                                                                             opt("The piston is faster, so its waves are", why="Waves don't inherit the source's speed; they move at c relative to the gas.")]),
                     choice("What happens with a train of rarefaction waves (piston pulled out)?", [opt("They spread apart into a fan", True),
                                                                                                   opt("They also steepen into an expansion shock", why="Each later rarefaction moves through cooler gas moving away from it, so it falls behind.")])]),
        ]),
    concept(
        "c-normal-shock-relations", "The normal shock relations", 1, C7,
        r"""
In the shock's own frame the flow is steady, adiabatic, frictionless and constant-area on the scale of a micron-thin control volume. Continuity, $p + \rho V^2$, and $h + V^2/2$ give (upstream $x$, downstream $y$):
$$M_y^2 = \frac{1 + \frac{\gamma-1}{2}M_x^2}{\gamma M_x^2 - \frac{\gamma-1}{2}},\qquad \frac{p_y}{p_x} = 1 + \frac{2\gamma}{\gamma+1}(M_x^2 - 1),$$
$$\frac{\rho_y}{\rho_x} = \frac{V_x}{V_y} = \frac{(\gamma+1)M_x^2}{(\gamma-1)M_x^2 + 2},\qquad \frac{T_y}{T_x} = \frac{p_y/p_x}{\rho_y/\rho_x},\qquad T_{0y} = T_{0x}.$$
Upstream must be supersonic and downstream is subsonic. Because the control volume is so thin, the relations hold for moving, decelerating and curved shocks too (locally), and they're trusted enough to calibrate pressure gauges.
""",
        deeper=["c-1d-integral", "c-stagnation"],
        math=[r"\frac{p_y}{p_x} = 1 + \frac{2\gamma}{\gamma+1}(M_x^2 - 1)", r"M_y^2 = \frac{1 + \frac{\gamma-1}{2}M_x^2}{\gamma M_x^2 - \frac{\gamma-1}{2}}"],
        widget={"type": "shock"},
        exam="Shocks: T0 constant, p0 drops, A* grows. Never use the differential equations across one.",
        source="Notes, Section 7.2",
        problems=[
            problem("c-ns-1", "A Mach 2.5 shock",
                    r"Air, γ = 1.4, $M_x = 2.5$.",
                    [num("$M_y$?", gas.ns_M2(2.5), tol=0.002), num("$p_y/p_x$?", gas.ns_p2p1(2.5), tol=0.002),
                     num("$T_y/T_x$?", gas.ns_T2T1(2.5), tol=0.002), num("$\\rho_y/\\rho_x$?", gas.ns_r2r1(2.5), tol=0.002),
                     num("$p_{0y}/p_{0x}$?", gas.ns_p02p01(2.5), tol=0.002),
                     dial("Set the shock Mach number that loses exactly half the stagnation pressure.", "ns_p02p01", 0.5, 1.0, 5.0, 0.001,
                          gas.ns_M1_from_p02p01(0.5), var="Mₓ", tol=0.002)]),
            problem("c-ns-2", "Code the normal shock",
                    r"One function returns everything a normal-shock table gives.",
                    [code("Write `normal_shock(M1, g)` returning `(M2, p2_p1, T2_T1, p02_p01)`.",
                          starter="import math\n\ndef normal_shock(M1, g=1.4):\n    # return M2, p2/p1, T2/T1, p02/p01\n    pass\n",
                          solution="import math\n\ndef normal_shock(M1, g=1.4):\n    M2 = math.sqrt((1 + (g - 1) / 2 * M1 ** 2) / (g * M1 ** 2 - (g - 1) / 2))\n    pr = 1 + 2 * g / (g + 1) * (M1 ** 2 - 1)\n    rr = (g + 1) * M1 ** 2 / ((g - 1) * M1 ** 2 + 2)\n    p0 = lambda M: (1 + (g - 1) / 2 * M * M) ** (g / (g - 1))\n    return M2, pr, pr / rr, pr * p0(M2) / p0(M1)\n",
                          tests=f"r = normal_shock(2.0)\ncheck('M2 at 2', r[0], {gas.ns_M2(2.0):.10f}, 1e-8)\ncheck('p2/p1 at 2', r[1], 4.5, 1e-9)\ncheck('T2/T1 at 2', r[2], {gas.ns_T2T1(2.0):.10f}, 1e-8)\ncheck('p02/p01 at 2', r[3], {gas.ns_p02p01(2.0):.10f}, 1e-8)\nr = normal_shock(3.0, 5/3)\ncheck('helium p02/p01 at 3', r[3], {gas.ns_p02p01(3.0, 5/3):.10f}, 1e-8)\n",
                          wrong=["import math\n\ndef normal_shock(M1, g=1.4):\n    M2 = math.sqrt((1 + (g - 1) / 2 * M1 ** 2) / (g * M1 ** 2 - (g - 1) / 2))\n    pr = 1 + 2 * g / (g + 1) * (M1 ** 2 - 1)\n    rr = (g + 1) * M1 ** 2 / ((g - 1) * M1 ** 2 + 2)\n    return M2, pr, pr / rr, 1.0\n",
                                 "import math\n\ndef normal_shock(M1, g=1.4):\n    M2 = math.sqrt((1 + (g - 1) / 2 * M1 ** 2) / (g * M1 ** 2 - (g - 1) / 2))\n    pr = 1 + 2 * g / (g + 1) * (M1 ** 2 - 1)\n    rr = (g + 1) * M1 ** 2 / ((g - 1) * M1 ** 2 + 2)\n    p0 = lambda M: (1 + (g - 1) / 2 * M * M) ** (g / (g - 1))\n    return M2, pr, pr * rr, pr * p0(M2) / p0(M1)\n"],
                          hints=["p02/p01 = (p2/p1) · (p02/p2) / (p01/p1).", "T = p/(ρR), so T2/T1 = (p2/p1)/(ρ2/ρ1)."], fn="normal_shock")]),
        ]),
    concept(
        "c-shock-entropy", "Entropy decides: only compression shocks exist, and they cost stagnation pressure", 1, C7,
        r"""
The algebra has two branches: supersonic-to-subsonic (compression) and subsonic-to-supersonic (expansion). The second is just the first played backwards, like a film of a waterfall in reverse. The second law settles it:
$$\frac{s_y - s_x}{R} = -\ln\frac{p_{0y}}{p_{0x}},$$
which is negative for $M_x < 1$: an adiabatic expansion shock would destroy entropy. So only **compression shocks** happen, and every one lowers stagnation pressure. That's why engineers talk about "total pressure loss": you can't buy an entropy meter, but you can measure $p_0$ with a pitot probe ([[c-pitot]]). The sonic area grows across the shock: $A^*_y/A^*_x = p_{0x}/p_{0y}$.
""",
        deeper=["c-normal-shock-relations", "p-entropy-isentropic"],
        math=[r"\frac{\Delta s}{R} = -\ln\frac{p_{0y}}{p_{0x}}", r"\frac{A^*_y}{A^*_x} = \frac{p_{0x}}{p_{0y}}"],
        source="Notes, Section 7.2",
        problems=[
            problem("c-se-1", "Entropy and the sonic area",
                    r"A Mach 2 normal shock in air.",
                    [num("$\\Delta s/R$?", gas.ns_ds_R(2.0), tol=0.003), num("$A^*_y/A^*_x$?", 1 / gas.ns_p02p01(2.0), tol=0.002),
                     choice("A student finds $\\Delta s < 0$ for $M_x = 0.8$. Conclusion?", [opt("That branch is impossible: expansion shocks would violate the second law", True),
                                                                                       opt("A small entropy decrease is fine for a weak shock", why="Any decrease in an adiabatic process violates the second law.")])]),
        ]),
    concept(
        "c-strong-weak-shocks", "Strong and weak limits", 1, C7,
        r"""
**Strong** ($M_x\to\infty$): $M_y\to\sqrt{(\gamma-1)/2\gamma} = 0.378$ and $\rho_y/\rho_x\to(\gamma+1)/(\gamma-1) = 6$. A shock can't compress a gas without limit, but pressure and temperature rise like $M_x^2$, until (around Mach 5) vibration, dissociation and ionization absorb energy and the gas stops being calorically perfect (hypersonic flow; "non-perfect gas," not "real gas").

**Weak** ($M_x$ near 1): the entropy rise goes as $(M_x^2 - 1)^3$, so below about $M_x = 1.3$ a normal shock is nearly isentropic. That's why "normal-shock inlets" are acceptable at low supersonic speeds ([[c-supersonic-inlet]]).
""",
        deeper=["c-shock-entropy", "p-calorically-perfect"],
        math=[r"\lim_{M_x\to\infty}\frac{\rho_y}{\rho_x} = \frac{\gamma+1}{\gamma-1}", r"\frac{\Delta s}{R}\approx\frac{2\gamma}{3(\gamma+1)^2}(M_x^2-1)^3"],
        source="Notes, Sections 7.3–7.4",
        problems=[
            problem("c-sw-1", "The limits",
                    r"γ = 1.4.",
                    [num("Limiting density ratio across a very strong shock?", (1.4 + 1) / 0.4), num("Limiting downstream Mach number?", math.sqrt(0.4 / 2.8), tol=0.002),
                     num("Stagnation pressure ratio across a Mach 1.2 shock?", gas.ns_p02p01(1.2), tol=0.001,
                         explain="Over 99%: a weak shock is nearly isentropic.")]),
        ]),
    concept(
        "c-shock-in-nozzle", "A shock in the nozzle: patch two isentropic flows, and update the reference states", 1, C8,
        r"""
The recipe from the notes:
1. Find the reference states upstream. A shock in the diverging part means the flow was supersonic there, so the throat was sonic: $A^*_x = A_t$.
2. Solve the isentropic flow up to the shock (supersonic branch of $A/A^*$).
3. Apply the normal shock relations.
4. Downstream, **use the new reference states**: $T_0$ unchanged, but $p_{0y} = p_{0x}\cdot(p_{0y}/p_{0x})$ and $A^*_y = A^*_x\,p_{0x}/p_{0y}$. Take the **subsonic** branch (subsonic flow in a diverging duct only decelerates).
""",
        deeper=["c-normal-shock-relations", "c-shock-entropy", "c-reference-state-method"],
        math=[r"T_{0y} = T_{0x},\quad p_{0y} < p_{0x},\quad A^*_y = A^*_x\frac{p_{0x}}{p_{0y}}"],
        source="Notes, Section 8.1",
        problems=[
            problem("c-sn-1", "The notes' nozzle (example 8.1.1)",
                    r"Air, $p_0 = 1$ atm, $T_0 = 300$ K. Throat 1 m², a normal shock where $A = 2.0$ m², exit 3.0 m².",
                    [num("Mach number just before the shock?", _Mx, tol=0.003), num("Pressure just before?", _px, "atm"),
                     num("Mach number just after?", _My, tol=0.003), num("Pressure just after?", _py, "atm"),
                     num("New stagnation pressure $p_{0y}$?", _p0y, "atm"), num("Exit Mach number?", _MC, tol=0.003), num("Exit pressure?", _pC, "atm")],
                    kind="notes"),
            problem("c-sn-2", "What changes across the shock?",
                    r"Sort the reference states.",
                    [choice("Which stays the same across a normal shock?", [opt("$T_0$", True), opt("$p_0$", why="p0 drops: the shock generates entropy."),
                                                                           opt("$A^*$", why="A* grows by p0x/p0y.")]),
                     spot("A student's downstream step. Which line is wrong?",
                          [("Downstream stagnation pressure: $p_{0y} = 0.628$ atm", False, ""),
                           ("Downstream sonic area: $A^*_y = A_t = 1$ m²", True, "A* grows across the shock: $A^*_y = A_t/0.628 = 1.59$ m²."),
                           ("Take the subsonic root of $A/A^*_y$ at the exit", False, ""),
                           ("$T_0 = 300$ K throughout", False, "")])]),
        ]),
    concept(
        "c-back-pressure-regimes", "The nozzle with variable back pressure: every regime", 1, C8,
        r"""
With $A_e/A_t$ fixed, compute three critical back pressures: $p_3$ (sonic throat, subsonic exit), $p_d$ (design, fully supersonic), and $p_4$ (normal shock standing at the exit: $p_4 = p_d\cdot p_y/p_x$ at $M_{e,sup}$).
- $p_b \ge p_3$: subsonic diverging section.
- $p_3 > p_b > p_4$: a **normal shock inside** the diverging section. Lower $p_b$ pushes it downstream and makes it stronger. Find it by trial positions until the exit pressure matches $p_b$ (subsonic exit must match).
- $p_4 > p_b > p_d$: **overexpanded**, oblique shocks outside.
- $p_b = p_d$: design.  $p_b < p_d$: **underexpanded**, expansion fans outside ([[c-over-under-expanded]]).

Below $p_3$ the mass flow is choked and fixed.
""",
        deeper=["c-shock-in-nozzle", "c-cd-nozzle-isentropic"],
        math=[r"p_4 = p_d\left[1 + \frac{2\gamma}{\gamma+1}\left(M_{e,sup}^2 - 1\right)\right]"],
        widget={"type": "nozzle", "preset": "shock"},
        exam="Compute p3, p4 and pd first. Then where p_b falls tells you the regime without any iteration.",
        source="Notes, Section 8.2",
        problems=[
            problem("c-bp-1", "The notes' nozzle (example 8.2.1)",
                    r"$A_t = 1$ m², $A_e = 3$ m², $p_0 = 1$ atm, $p_b = 0.7$ atm.",
                    [num("$p_3/p_0$?", _n3["p3"], tol=0.003), num("$p_d/p_0$?", _n3["pd"], tol=0.003), num("$p_4/p_0$?", _n3["p4"], tol=0.003),
                     choice("So the flow has:", [opt("A normal shock inside the diverging section", True), opt("Oblique shocks outside", why="That needs p4 > p_b > pd; here p_b is between p3 and p4."),
                                                 opt("Subsonic flow throughout", why="p_b is below p3.")]),
                     num("Exact shock location $A_s$ (the notes interpolate to about 1.67 m²)?", _n3["As"], "m²", tol=0.005),
                     dial("Slide the back pressure until the shock sits at $A = 2.0$ m².", "nozzle_shock", 2.0, _n3["p4"] + 0.005, _n3["p3"] - 0.005, 0.0005,
                          gas.bisect(lambda pb: gas.nozzle(3.0, pb)["As"] - 2.0, _n3["p4"] + 1e-6, _n3["p3"] - 1e-6), args={"AeAt": 3.0}, var="p_b/p₀", tol=0.003)],
                    kind="notes"),
            problem("c-bp-2", "A different nozzle",
                    r"$A_e/A_t = 2.5$, $p_b/p_0 = 0.75$.",
                    [num("$p_3/p_0$?", _n25["p3"], tol=0.003), num("$p_4/p_0$?", _n25["p4"], tol=0.003),
                     num("Shock location $A_s/A_t$?", _n25["As"], tol=0.005), num("Exit Mach number?", _n25["Me"], tol=0.005)]),
            problem("c-bp-3", "Code the whole nozzle",
                    r"The capstone of the 1-D course: classify the regime and locate the shock. Helper functions are provided.",
                    [code("Complete `nozzle_regime(AeAt, pb)`: return `'subsonic'`, `'shock'`, `'overexpanded'`, `'design'` or `'underexpanded'` (use a relative tolerance of 1e-6 for 'design'). Then `shock_area(AeAt, pb)`, which finds the shock area by bisection.",
                          starter=NOZZLE_HELPERS + "\ndef nozzle_regime(AeAt, pb):\n    pass\n\ndef shock_area(AeAt, pb):\n    # assumes the regime is 'shock'\n    pass\n",
                          solution=NOZZLE_HELPERS + NOZZLE_SOLUTION,
                          tests=f"check('notes regime', 1 if nozzle_regime(3.0, 0.7) == 'shock' else 0, 1, 1e-9)\ncheck('subsonic', 1 if nozzle_regime(3.0, 0.98) == 'subsonic' else 0, 1, 1e-9)\ncheck('over', 1 if nozzle_regime(3.0, 0.2) == 'overexpanded' else 0, 1, 1e-9)\ncheck('under', 1 if nozzle_regime(3.0, 0.02) == 'underexpanded' else 0, 1, 1e-9)\ncheck('notes shock area', shock_area(3.0, 0.7), {_n3['As']:.8f}, 1e-5)\ncheck('2.5 nozzle shock area', shock_area(2.5, 0.75), {_n25['As']:.8f}, 1e-5)\n",
                          wrong=[NOZZLE_HELPERS + NOZZLE_SOLUTION.replace("mach_from_area(AeAt * r, False)", "mach_from_area(AeAt / r, False)"),
                                 NOZZLE_HELPERS + NOZZLE_SOLUTION.replace("if pb > p4:", "if pb > pd:")],
                          hints=["p3 = 1/p0_p(subsonic exit Mach), pd = 1/p0_p(supersonic exit Mach), p4 = pd times the normal-shock pressure ratio at the supersonic exit Mach.",
                                 "After a shock, A*₂ = A_t/(p02/p01), so A_e/A*₂ = (A_e/A_t)(p02/p01).",
                                 "Exit pressure for a trial shock area: p02/p01 divided by p0_p(exit Mach). Bisect on the shock area between 1 and A_e/A_t."],
                          fn="shock_area")]),
        ]),
    concept(
        "c-moving-shocks", "Moving shocks and pistons: change frames, solve, change back", 1, C8,
        r"""
A shock running into still gas is unsteady. Add $-V_s$ to every velocity: now gas approaches the shock at $V_x = V_s$ and leaves at $V_y$; apply the normal-shock relations; then add $V_s$ back. The gas behind moves at $V_p' = V_x - V_y$, which is also the speed of the piston that could drive the shock. In terms of the shock Mach number $M_s = V_s/c_x$:
$$\frac{V_p'}{c_x} = \frac{2}{\gamma+1}\left(M_s - \frac{1}{M_s}\right),\qquad M_s = \frac{\gamma+1}{4}\frac{V_p'}{c_x} + \sqrt{\left(\frac{\gamma+1}{4}\frac{V_p'}{c_x}\right)^2 + 1}.$$
Behind an unsteady shock the flow can be **supersonic** in the lab frame (for $M_s$ above about 2): "downstream is subsonic" is true only in the shock's frame. A very fast piston drives a shock $(\gamma+1)/2 = 1.2$ times faster than itself.
""",
        deeper=["c-normal-shock-relations", "p-galilean"],
        math=[r"\frac{V_p'}{c_x} = \frac{2}{\gamma+1}\left(M_s - \frac{1}{M_s}\right)"],
        widget={"type": "xt", "preset": "piston"},
        source="Notes, Section 8.4",
        problems=[
            problem("c-ms-1", "Mach 3 shock into still air (notes example 8.4.1)",
                    r"1 atm, 300 K air (MW 28.8, so $c_x = 348$ m/s).",
                    [num("Shock speed?", _Vs, "m/s"), num("Pressure behind it?", gas.ns_p2p1(3.0), "atm"), num("Temperature behind?", 300 * gas.ns_T2T1(3.0), "K"),
                     num("Gas (piston) velocity behind it, lab frame?", _vp, "m/s"),
                     num("Mach number of that gas in the lab frame (use the hot gas's sound speed)?", _vp / gas.sound(300 * gas.ns_T2T1(3.0), R=R288), tol=0.003,
                         explain="Above 1: supersonic flow behind a shock, possible only because the shock moves.")],
                    kind="notes"),
            problem("c-ms-2", "Piston-driven shock (new numbers)",
                    r"A piston is suddenly pushed at 400 m/s into air at 290 K ($R = 287$).",
                    [num("Shock Mach number?", _Ms400, tol=0.003), num("Shock speed?", _Ms400 * _c290, "m/s"),
                     dial("Slide the piston speed to drive a Mach 2 shock into this gas.", "piston", 2.0, 50.0, 1200.0, 0.5, gas.piston_speed(2.0) * _c290,
                          args={"c": _c290}, var="V_p", unit="m/s", tol=0.003)]),
        ]),
    concept(
        "c-pitot", "Pitot probes: easy in subsonic flow, a shock in supersonic flow", 1, C9,
        r"""
A **pitot probe** stagnates the flow at its tip; a static port on its side reads $p$. In subsonic flow it measures $p_0$ directly, and $p_0/p$ gives $M$. In supersonic flow a bow shock stands in front of the tip, so the probe reads $p_{0y}$ (behind a normal shock) while the side port still reads roughly $p_x$ (the flow re-accelerates past the tip). The **Rayleigh pitot formula** combines the two:
$$\frac{p_{0y}}{p_x} = \frac{p_{0y}}{p_{0x}}\cdot\frac{p_{0x}}{p_x} = \left[\frac{(\gamma+1)^2M_x^2}{4\gamma M_x^2 - 2(\gamma-1)}\right]^{\frac{\gamma}{\gamma-1}}\frac{1 - \gamma + 2\gamma M_x^2}{\gamma+1}.$$
""",
        deeper=["c-normal-shock-relations", "c-stagnation"],
        math=[r"\frac{p_{0y}}{p_x} = \frac{p_{0y}}{p_{0x}}\frac{p_{0x}}{p_x}"],
        source="Notes, Section 9.1",
        problems=[
            problem("c-pi-1", "Read a pitot-static probe",
                    r"Air.",
                    [num("Subsonic: the probe reads $p_0/p = 1.3$. Mach number?", _Msub_pitot, tol=0.003),
                     num("Supersonic: the pitot reads 450 kPa and the static port 100 kPa. Mach number?", _Mpit, tol=0.003),
                     choice("If you wrongly used the subsonic formula $p_0/p = 4.5$ there, you'd get:", [opt(f"M ≈ {gas.M_from_p0p(4.5):.2f}, too high, because you ignored the shock's p₀ loss", True),
                                                                                                     opt("The same answer", why="Behind the bow shock the probe reads p0y < p0x, so the subsonic formula overestimates M.")])]),
        ]),
    concept(
        "c-supersonic-inlet", "Supersonic inlets: starting, unstarting and the Kantrowitz limit", 1, C9,
        r"""
An ideal supersonic diffuser is a converging–diverging nozzle run backwards: decelerate to Mach 1 at a throat sized $A_t = A^*$, then subsonically. Isentropic, so perfectly efficient, and **unstable**: slow down slightly and the sonic area exceeds the throat, the throat can't pass the flow, and the inlet violently **disgorges** a normal shock ("unstart").

Accelerating from subsonic, the inlet is unstarted before it ever starts: a normal shock sits in front, and because $A^*$ grows across it, the throat is too small. You must **overspeed** until the post-shock sonic area fits the throat; then the shock is swallowed in milliseconds. For a Mach 1.5 design ($A_t/A_i = 0.850$) that means Mach 1.83. Between design and starting Mach number the inlet can be either started or unstarted (**hysteresis**). Above a design Mach number of about 2 (the **Kantrowitz limit**), overspeeding can never start a fixed inlet: use a variable throat.
""",
        deeper=["c-shock-entropy", "c-area-ratio", "c-strong-weak-shocks"],
        math=[r"\left(\frac{A_t}{A_i}\right)_{start} = \frac{A^*_y}{A_i} = \frac{1}{(A/A^*)_{M_y}}", r"\left(\frac{A_t}{A_i}\right)_{isentropic} = \frac{1}{(A/A^*)_{M}}"],
        widget={"type": "inlet"},
        analogy=analogy("Swallowing too big a bite: the inlet 'vomits' the shock out (the notes' own image). To get it down you have to open wider (variable throat) or take the bite at a higher speed (overspeed).",
                        "a person can choose to swallow; the inlet's state depends only on its history, which is why the same Mach number can give two outcomes."),
        exam="Two curves: isentropic design ratio and starting ratio. Between them, ask which side you came from.",
        source="Notes, Section 9.2",
        problems=[
            problem("c-si-1", "A Mach 1.7 inlet (new numbers)",
                    r"The notes work Mach 1.5; here, design Mach 1.7.",
                    [num("Throat-to-inlet area ratio for isentropic operation?", _Ai17, tol=0.003),
                     num("Flight Mach number needed to start it by overspeeding?", _Mst17, tol=0.003),
                     num("Or open the throat at Mach 1.7 to what fraction of the inlet area?", _open17, tol=0.003),
                     num("Kantrowitz limit: largest design Mach number that overspeeding can still start?", _kant, tol=0.005)]),
            problem("c-si-2", "Hysteresis",
                    r"The Mach 1.7 inlet is flying at Mach 1.8.",
                    [choice("Is it started?", [opt("It depends on its history: started if it came down from above the starting Mach number, unstarted if it came up from below", True),
                                               opt("Yes, it's above the design Mach number", why="Above design, the inlet can still be unstarted if it never reached the starting Mach number.")])]),
        ]),
    concept(
        "c-wind-tunnel", "Supersonic wind tunnels need a second throat that can swallow the starting shock", 1, C9,
        r"""
A continuous supersonic tunnel: nozzle (throat 1), test section, diffuser (throat 2), compressor. To start, a normal shock must travel through the test section. When it sits at the test-section entrance at the design Mach number, the second throat must pass the post-shock sonic area:
$$\frac{A_{t2}}{A_{t1}} \ge \frac{A^*_y}{A^*_x} = \frac{p_{0x}}{p_{0y}}\Big|_{M_{test}}.$$
If throat 2 chokes first, the tunnel is blocked. Once started, the shock can be pushed back toward throat 2 to weaken it, but force it upstream past the throat and the tunnel unstarts. Variable second throats ease starting.
""",
        deeper=["c-supersonic-inlet", "c-shock-in-nozzle"],
        math=[r"\frac{A_{t2}}{A_{t1}}\ge\frac{p_{0x}}{p_{0y}}"],
        source="Notes, Section 9.3; Problem Set 2, Problem 8 (suck-down tunnel) skills",
        problems=[
            problem("c-wt-1", "Second throat for Mach 2.5",
                    r"A tunnel designed for a Mach 2.5 test section.",
                    [num("Minimum $A_{t2}/A_{t1}$ to start?", _wt, tol=0.003),
                     num("Test-section to first-throat area ratio?", gas.A_Astar(2.5), tol=0.003)]),
            problem("c-wt-2", "A suck-down tunnel (new numbers)",
                    r"Atmospheric air (300 K, 101 kPa) is drawn through a nozzle into a vacuum tank; Mach 3 in the test section. (Problem Set 2 uses Mach 4.)",
                    [num("Test-section static temperature?", 300 / gas.T0_T(3.0), "K"), num("Static pressure?", 101 / gas.p0_p(3.0), "kPa"),
                     num("Test-section to throat area ratio?", gas.A_Astar(3.0), tol=0.003),
                     choice("Why can't it simulate flight at Mach 3 and 26 kPa ambient?", [opt("Its stagnation pressure is fixed at 1 atm, so the test-section pressure is far below 26 kPa", True),
                                                                                         opt("It can, with a bigger tank", why="Tank size sets run time, not the stagnation state.")])],
                    kind="variant"),
        ]),
    concept(
        "c-shinkansen", "A high-speed train in a tunnel is a piston", 1, C9,
        r"""
In open air a Shinkansen at 300 km/h (Mach 0.24) is safely incompressible. In a tight tunnel it's a **piston**: air ahead is pushed along at the train's speed, so a shock runs ahead ([[c-moving-shocks]]): at 83.3 m/s, $M_s = 1.154$ with a 39% pressure rise, enough to damage hearing at the far portal. Ways out, from the notes' estimates:
- slow down to about 165 km/h (keeps the overpressure under 3 psi);
- leave a gap so air can squeeze past (a "leaky piston"; the gap flow chokes). A tunnel about 22% larger than the train keeps the shock weak;
- make the gap large enough to swallow the approaching flow isentropically: tunnel area about 66% larger than the train means no shock in this model.

Real tunnels already meet that, yet "tunnel booms" persist: the model is simple, and any startling pressure wave is unpleasant.
""",
        deeper=["c-moving-shocks", "c-choking"],
        math=[r"M_s = \frac{\gamma+1}{4}\frac{V_{train}}{c} + \sqrt{\left(\frac{\gamma+1}{4}\frac{V_{train}}{c}\right)^2 + 1}"],
        widget={"type": "train"},
        source="Notes, Section 9.4",
        problems=[
            problem("c-sk-1", "A faster train (new numbers)",
                    r"A train at 90 m/s enters a tight-fitting tunnel; air at 300 K, $c = 348$ m/s.",
                    [num("Shock Mach number?", _Mstrain, tol=0.003), num("Pressure rise, as a percent of ambient?", 100 * _dptrain, "%"),
                     num("Tunnel-to-train area ratio that avoids a shock in the isentropic model?", _tunnel, tol=0.005)]),
        ]),
]

