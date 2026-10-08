"""Layer 1, Chapters 5-6: isentropic 1-D flow (area change, stagnation and sonic states, choking, A/A*)
and its applications (converging and converging-diverging nozzles, rockets)."""
import math
import sympy as sp
from lib import *
import gas

C5, C6 = "Ch. 5 · Isentropic flow", "Ch. 6 · Nozzles and rockets"
ATM = 101325.0
R = 287.0

# ---- Problem Set 2-style variants (new numbers) ----
# P2: stagnation temperature at M = 1 and M = 5 for -50 C and 25 C.
_Ts = {"cold": 273.15 - 50, "warm": 298.15}
# P3: duct flow, 500 m/s, 10 C, 80 kPa; elsewhere 35 kPa.
_T3, _V3, _p3 = 283.15, 500.0, 80.0
_M3 = _V3 / gas.sound(_T3)
_T03, _p03 = _T3 * gas.T0_T(_M3), _p3 * gas.p0_p(_M3)
_M3b = gas.M_from_p0p(_p03 / 35.0)
_T3b = _T03 / gas.T0_T(_M3b)
_V3b = _M3b * gas.sound(_T3b)
# P4: argon (MW 40, gamma 5/3), 250 m/s, 40 C, 60 kPa -> 20 kPa elsewhere.
_gA, _RA = 5 / 3, gas.R_of(40.0)
_TA = 313.15
_MA = 250 / gas.sound(_TA, _gA, _RA)
_p0A = 60 * gas.p0_p(_MA, _gA)
_MA2 = gas.M_from_p0p(_p0A / 20, _gA)
_TA2 = _TA * gas.T0_T(_MA, _gA) / gas.T0_T(_MA2, _gA)
# P5: converging nozzle from 400 K, 1.8 atm into 1 atm, exit 20 cm^2 (air)
_T05, _p05, _Ae5 = 400.0, 1.8 * ATM, 20e-4
_Me5 = gas.M_from_p0p(1.8)
_Te5 = _T05 / gas.T0_T(_Me5)
_Ve5 = _Me5 * gas.sound(_Te5)
_mdot5 = (_p05 / gas.p0_p(_Me5)) / (R * _Te5) * _Ve5 * _Ae5
_Vmax5 = gas.sound(_T05 / gas.T0_T(1))
_mmax5 = gas.mdot_choked(_p05, _T05, _Ae5)
# P9: 8 kg/s of air at 2.5 atm, 600 C through 200 cm^2; downstream M = 1.5
_p9, _T9, _A9, _m9 = 2.5 * ATM, 873.15, 200e-4, 8.0
assert _m9 / (_p9 / (R * _T9) * _A9) / gas.sound(_T9) < 1, 'variant must start subsonic'
_M9 = _m9 / (_p9 / (R * _T9) * _A9) / gas.sound(_T9)
_A9s = _A9 / gas.A_Astar(_M9)
_A9b = _A9s * gas.A_Astar(1.5)
_p9b = _p9 * gas.p0_p(_M9) / gas.p0_p(1.5)
_T9b = _T9 * gas.T0_T(_M9) / gas.T0_T(1.5)

# ---- Problem Set 3-style variants (new numbers) ----
# P1: Bernoulli vs compressible from 1 bar, 300 K stagnation, accelerated to 100, 300, 450 m/s
def _dp(V):
    T = 300 - V * V / (2 * 1004.5)
    M = V / gas.sound(T)
    p = 1e5 / gas.p0_p(M)
    rho0 = 1e5 / (R * 300)
    return 1e5 - p, 0.5 * rho0 * V * V
_dps = {V: _dp(V) for V in (100, 300, 450)}
# P2: air nozzle p0 = 3 MPa, T0 = 1200 K, ambient 50 kPa, 4 kg/s
_p0r, _T0r, _pa, _mr = 3e6, 1200.0, 50e3, 4.0
_Mer = gas.M_from_p0p(_p0r / _pa)
_Ver = gas.exit_velocity(_T0r, _pa / _p0r)
_Atr = _mr / gas.mdot_choked(_p0r, _T0r, 1.0)
_Aer = _Atr * gas.A_Astar(_Mer)
# P4: CD nozzle At = 1 m^2, Ae = 4 m^2, To = 300 K, ambient 1 atm fixed
_nz = gas.nozzle(4.0, 0.5)
_p0_choke = ATM / _nz["p3"]
_p0_design = ATM / _nz["pd"]
# P5: maximum velocity at T0 = 2500 K, helium vs hydrogen (as gamma 1.4)
_vHe = gas.v_max(2500, 5 / 3, gas.R_of(4.0))
_vH2 = gas.v_max(2500, 1.4, gas.R_of(2.0))

# ---- Problem Set 4-style variant: nozzle optimized for sea level, operated in space (gamma 1.25, R 350) ----
_g4, _R4, _p04, _T04 = 1.25, 350.0, 3.0e6, 2000.0
_pr4 = ATM / _p04
_Me4 = gas.M_from_p0p(1 / _pr4, _g4)
_eps4 = gas.A_Astar(_Me4, _g4)
_cstar = math.sqrt(_R4 * _T04) / gas.mass_flux(1.0, _g4)       # p0 At / mdot
_ve4 = gas.exit_velocity(_T04, _pr4, _g4, _R4)
_F_sl = _ve4                                                   # per unit mdot, matched at sea level
_F_sp = _ve4 + _eps4 * _cstar * _pr4                           # (Ae/mdot) pe = eps * c* * (pe/p0)
_F_max = gas.v_max(_T04, _g4, _R4)

# ---- Notes worked examples ----
_A3sub, _A3sup = gas.M_from_AR(1.5 / 0.746, False), gas.M_from_AR(1.5 / 0.746, True)

CONCEPTS = [
    concept(
        "c-area-velocity", "Area change: subsonic and supersonic flows respond in opposite ways", 1, C5,
        r"""
Combine the differential continuity and momentum equations with $dp/d\rho = c^2$ (isentropic):
$$\frac{dV}{V} = -\frac{1}{1 - M^2}\,\frac{dA}{A},\qquad \frac{dp}{\rho V^2} = \frac{1}{1 - M^2}\,\frac{dA}{A}.$$
- **Subsonic** ($M<1$): a converging duct speeds the flow up (a nozzle); diverging slows it (a diffuser). Familiar.
- **Supersonic** ($M>1$): the opposite. Density falls faster than velocity rises, so a diverging duct is needed to accelerate it. That's why rocket nozzles are bells.
- **Mach 1** is allowed only where $dA = 0$: at a throat (a minimum of area).

Pressure always moves opposite to velocity; density follows pressure. Master this table before anything else in the course.
""",
        deeper=["c-1d-differential", "c-sound-ideal-gas"],
        math=[r"\frac{dV}{V} = \frac{-1}{1-M^2}\frac{dA}{A}"],
        widget={"type": "areavel"},
        analogy=analogy("Subsonic flow is a crowd that hears the narrowing ahead and hurries through. Supersonic flow is a crowd moving so fast it can't hear the walls; give it room and it spreads out, thins and races faster.",
                        "the 'thinning' is literal: in supersonic flow the density drop outpaces the velocity rise, which no crowd of incompressible people can do."),
        exam="Never accelerate a subsonic flow past Mach 1 with a converging duct alone: it chokes at the exit.",
        source="Notes, Section 5.1",
        problems=[
            problem("c-av-1", "Fill in the table",
                    r"Use $\dfrac{dV}{V} = \dfrac{-1}{1 - M^2}\dfrac{dA}{A}$ and $dp = -\rho V\,dV$.",
                    [choice("Supersonic flow, diverging duct ($dA>0$). Velocity:", [opt("Increases", True), opt("Decreases", why="With M > 1, 1 − M² < 0, so dV has the same sign as dA.")]),
                     choice("Same flow. Pressure:", [opt("Decreases", True), opt("Increases", why="Pressure always moves opposite to velocity in inviscid flow.")]),
                     choice("Subsonic flow, converging duct. Density:", [opt("Decreases", True), opt("Increases", why="Velocity rises, pressure falls, and density follows pressure.")]),
                     num("At Mach 0.5, a 1% decrease in area changes the velocity by what percent?", 1 / (1 - 0.25), "%")]),
            problem("c-av-2", "Why only at a throat?",
                    r"At $M = 1$, the coefficient $1/(1-M^2)$ blows up.",
                    [choice("For a finite $dV$, what must happen there?", [opt("$dA = 0$: sonic flow occurs only at a minimum (or maximum) of area", True),
                                                                          opt("The flow must be unsteady", why="Steady flow is fine; it just needs dA = 0 at M = 1."),
                                                                          opt("Nothing special", why="Otherwise dV would be infinite.")]),
                     choice("Which kind of extremum can actually be sonic in a steady accelerating flow?", [opt("A minimum of area (a throat)", True),
                                                                                                        opt("A maximum of area", why="A subsonic flow decelerates toward a maximum, away from Mach 1.")])]),
        ]),
    concept(
        "c-stagnation", "Stagnation (total) conditions: the state if the flow were brought to rest", 1, C5,
        r"""
Decelerate a sample of the flow to rest **isentropically** and you get its stagnation state, written with subscript $o$ (or 0). From the energy equation alone (adiabatic flow):
$$\frac{T_0}{T} = 1 + \frac{\gamma-1}{2}M^2.$$
If the deceleration is also reversible (isentropic):
$$\frac{p_0}{p} = \left(1 + \frac{\gamma-1}{2}M^2\right)^{\frac{\gamma}{\gamma-1}},\qquad \frac{\rho_0}{\rho} = \left(1 + \frac{\gamma-1}{2}M^2\right)^{\frac{1}{\gamma-1}}.$$
$T_0$ stays constant in any adiabatic flow (shocks and friction included); $p_0$ stays constant only if the flow is isentropic. **Static** properties are what a thermometer riding with the flow reads, and they're the same in every frame. **Stagnation** properties depend on the frame: for someone moving with the gas, $p_0 = p$.
""",
        deeper=["c-cv-energy", "c-mach-number", "p-entropy-isentropic"],
        math=[r"\frac{T_0}{T} = 1 + \frac{\gamma - 1}{2}M^2", r"\frac{p_0}{p} = \left(\frac{T_0}{T}\right)^{\gamma/(\gamma-1)}"],
        widget={"type": "tables", "preset": "isentropic"},
        analogy=analogy("The value of your car if you sold it today (static) versus what you paid (stagnation): the stagnation number is a reference that stays on the books even while the car is being driven.",
                        "unlike money, stagnation pressure can only be lost, never made back without work or heat (it's the flow's entropy ledger)."),
        exam="Static is what the flow feels; stagnation is a reference. When in doubt about the frame, ask: brought to rest relative to whom?",
        source="Notes, Section 5.2; Problem Set 2, Problems 2–3; Problem Set 3, Problem 3",
        terms=["stagnation conditions", "static conditions"],
        problems=[
            problem("c-st-1", "From a reservoir (notes example 5.2.1)",
                    r"A quiescent reservoir at 5 atm, 500 K feeds an isentropic duct flow of air.",
                    [choice("What are $p_0$ and $T_0$ everywhere in the duct?", [opt("5 atm and 500 K: the reservoir is already at rest", True),
                                                                               opt("They have to be computed at each station", why="T0 is constant in adiabatic flow and p0 in isentropic flow, so the reservoir values hold everywhere.")]),
                     num("Static pressure where $M = 0.75$?", 5 / gas.p0_p(0.75), "atm"),
                     num("Static temperature where $M = 2$?", 500 / gas.T0_T(2.0), "K"),
                     num("Static pressure where $M = 2$?", 5 / gas.p0_p(2.0), "atm")],
                    kind="notes"),
            problem("c-st-2", "Stagnation temperature on the nose (new numbers)",
                    r"Air, γ = 1.4. Problem Set 2 asks this for the Bell X-1 and Thrust SSC; here, two other conditions.",
                    [num("At −50 °C and Mach 1, $T_0$?", _Ts["cold"] * gas.T0_T(1.0), "K"),
                     num("At 25 °C and Mach 1, $T_0$?", _Ts["warm"] * gas.T0_T(1.0), "K"),
                     num("At −50 °C and Mach 5, $T_0$?", _Ts["cold"] * gas.T0_T(5.0), "K",
                         explain="At Mach 5, $T_0/T = 6$: the nose tip of a hypersonic vehicle gets very hot.")],
                    kind="variant"),
            problem("c-st-3", "Whose stagnation pressure?",
                    r"A balloon floats at rest in air at $p = 35$ kPa while an airliner passes at Mach 0.8. (Problem Set 3 asks the same with other numbers.)",
                    [num("Stagnation pressure in the balloon's frame?", 35, "kPa", explain="The air is at rest relative to the balloon, so p₀ = p."),
                     num("Stagnation pressure in the airliner's frame?", 35 * gas.p0_p(0.8), "kPa"),
                     num("Static pressure in the airliner's frame?", 35, "kPa", explain="Static properties don't depend on the frame.")],
                    kind="variant"),
            problem("c-st-4", "Code the isentropic ratios",
                    r"Your first three gas-table functions.",
                    [code("Complete `T0_T`, `p0_p` and `rho0_rho` for a calorically perfect gas.",
                          starter="def T0_T(M, g=1.4):\n    pass\n\ndef p0_p(M, g=1.4):\n    pass\n\ndef rho0_rho(M, g=1.4):\n    pass\n",
                          solution="def T0_T(M, g=1.4):\n    return 1 + (g - 1) / 2 * M * M\n\ndef p0_p(M, g=1.4):\n    return T0_T(M, g) ** (g / (g - 1))\n\ndef rho0_rho(M, g=1.4):\n    return T0_T(M, g) ** (1 / (g - 1))\n",
                          tests=f"check('T0/T at M=2', T0_T(2.0), {gas.T0_T(2.0)}, 1e-9)\ncheck('p0/p at M=2', p0_p(2.0), {gas.p0_p(2.0):.10f}, 1e-9)\ncheck('p0/p at M=0.75', p0_p(0.75), {gas.p0_p(0.75):.10f}, 1e-9)\ncheck('rho0/rho argon M=1.5', rho0_rho(1.5, 5/3), {gas.r0_r(1.5, 5/3):.10f}, 1e-9)\n",
                          wrong=["def T0_T(M, g=1.4):\n    return 1 + (g - 1) / 2 * M * M\n\ndef p0_p(M, g=1.4):\n    return T0_T(M, g) ** ((g - 1) / g)\n\ndef rho0_rho(M, g=1.4):\n    return T0_T(M, g) ** (1 / (g - 1))\n",
                                 "def T0_T(M, g=1.4):\n    return 1 + (g - 1) / 2 * M\n\ndef p0_p(M, g=1.4):\n    return T0_T(M, g) ** (g / (g - 1))\n\ndef rho0_rho(M, g=1.4):\n    return T0_T(M, g) ** (1 / (g - 1))\n"],
                          hints=["p0/p = (T0/T)^(γ/(γ−1)).", "Square the Mach number in T0/T."], fn="T0_T")]),
        ]),
    concept(
        "c-sonic-reference", "Sonic (critical) conditions: the reference state at Mach 1", 1, C5,
        r"""
Bring the flow isentropically to $M = 1$ instead of to rest and you get the **sonic** or **critical** state, marked with $^*$. For γ = 1.4 these are worth memorising:
$$\frac{T^*}{T_0} = \frac{2}{\gamma+1} = 0.8333,\qquad \frac{p^*}{p_0} = 0.5283,\qquad \frac{\rho^*}{\rho_0} = 0.6339.$$
Like $p_0$ and $T_0$, the sonic state is constant throughout an isentropic flow, whether or not the flow ever reaches Mach 1. (Some books' $M^*$ means $V/c^*$, not 1; the notes avoid it.)
""",
        deeper=["c-stagnation"],
        math=[r"\frac{T^*}{T_0} = \frac{2}{\gamma+1}", r"\frac{p^*}{p_0} = \left(\frac{2}{\gamma+1}\right)^{\gamma/(\gamma-1)}"],
        source="Notes, Section 5.3; Problem Set 2, Problem 1",
        terms=["sonic conditions"],
        problems=[
            problem("c-sr-1", "Memorise, then check",
                    r"γ = 1.4.",
                    [num("$p^*/p_0$?", 1 / gas.p0_p(1.0), tol=0.002), num("$T^*/T_0$?", 1 / gas.T0_T(1.0), tol=0.002),
                     num("For helium (γ = 5/3), $p^*/p_0$?", 1 / gas.p0_p(1.0, 5 / 3), tol=0.002)]),
        ]),
    concept(
        "c-choking", "Choking: the mass flow through an area peaks at Mach 1", 1, C5,
        r"""
Write the mass flow per unit area in terms of the fixed stagnation state and the local Mach number:
$$\frac{\dot m}{A} = \frac{p_0}{\sqrt{RT_0}}\,\sqrt{\gamma}\,M\left(1 + \frac{\gamma-1}{2}M^2\right)^{-\frac{\gamma+1}{2(\gamma-1)}}.$$
It's largest at **M = 1**. Going faster doesn't help: past Mach 1, density falls faster than velocity rises. So once the flow at the smallest area is sonic, lowering the back pressure further can't raise $\dot m$: the news can't travel upstream through sonic flow. That's **choking**. For air (SI), $\dot m_{max} = 0.0404\,p_0A^*/\sqrt{T_0}$ (**Fliegner's formula**, found by experiment in the 19th century). Choking happens only at the global minimum area.
""",
        deeper=["c-sonic-reference", "c-area-velocity"],
        math=[r"\dot m_{max} = \frac{p_0A^*}{\sqrt{RT_0}}\sqrt{\gamma}\left(\frac{2}{\gamma+1}\right)^{\frac{\gamma+1}{2(\gamma-1)}}"],
        widget={"type": "massflux"},
        analogy=analogy("A crowded room emptying through one door: even with an empty patio outside, people can only squeeze through so fast. Draining a SCUBA tank with a vacuum pump doesn't make it empty any faster.",
                        "a crowd's limit is how fast people walk; a gas's limit is that pressure news travels at c, so once the door flow is sonic the room can't 'hear' the lower pressure outside."),
        exam="Check for choking first: compare the back pressure with p* = 0.528 p0 (converging nozzle).",
        source="Notes, Section 5.4; Problem Set 2, Problem 1 (choking)",
        terms=["choking"],
        problems=[
            problem("c-ch-1", "Choked or not?",
                    r"Air in a tank at 2.5 atm discharges through a converging nozzle to 1 atm.",
                    [choice("Is the nozzle choked?", [opt("Yes: 1/2.5 = 0.4 is below 0.528", True), opt("No", why="The back-to-stagnation ratio 0.4 is below p*/p0 = 0.528, so the exit is sonic.")]),
                     num("Exit static pressure?", 2.5 / gas.p0_p(1.0), "atm", explain="Choked: the exit sits at p* = 0.528 × 2.5 atm, above ambient."),
                     dial("Set the Mach number at which the mass flux is 90% of its maximum (subsonic branch).", "mass_flux", 0.9,
                          0.05, 1.0, 0.001, gas.bisect(lambda m: gas.mass_flux(m) / gas.mass_flux(1.0) - 0.9, 0.05, 1.0), var="M", tol=0.003)]),
            problem("c-ch-2", "Fliegner",
                    r"Air from a reservoir at 500 kPa, 350 K through a 2 cm² choked throat.",
                    [num("Mass flow?", gas.mdot_choked(5e5, 350, 2e-4), "kg/s", explain="$\\dot m = 0.0404\\,p_0A^*/\\sqrt{T_0}$."),
                     num("If the reservoir pressure doubles, by what factor does the mass flow change?", 2.0)]),
        ]),
    concept(
        "c-area-ratio", "A/A*: two Mach numbers for every area ratio", 1, C5,
        r"""
Mass flow is the same at any section and at the (possibly imaginary) sonic section, so
$$\frac{A}{A^*} = \frac{1}{M}\left[\frac{2}{\gamma+1}\left(1 + \frac{\gamma-1}{2}M^2\right)\right]^{\frac{\gamma+1}{2(\gamma-1)}}.$$
$A/A^*\ge1$ always: no section can be smaller than the sonic area. For each ratio above 1 there are **two** answers, one subsonic and one supersonic. Which one happens depends on whether the flow went through a throat, and later on back pressure. Inverting needs iteration (the notes guess-and-interpolate; you'll write a solver).
""",
        deeper=["c-choking", "p-root-finding", "p-python"],
        math=[r"\frac{A}{A^*} = \frac{1}{M}\left[\frac{2}{\gamma+1}\left(1+\frac{\gamma-1}{2}M^2\right)\right]^{\frac{\gamma+1}{2(\gamma-1)}}"],
        widget={"type": "tables", "preset": "area"},
        exam="Always write both roots unless the problem tells you the branch (a throat upstream, a shock, supersonic inflow...).",
        source="Notes, Section 5.4",
        problems=[
            problem("c-ar-1", "Both branches",
                    r"$A/A^* = 2$, γ = 1.4.",
                    [num("Subsonic Mach number?", gas.M_from_AR(2.0, False), tol=0.002), num("Supersonic Mach number?", gas.M_from_AR(2.0, True), tol=0.002),
                     dial("Slide M until A/A* = 3 on the supersonic branch.", "A_Astar", 3.0, 1.0, 4.0, 0.001, gas.M_from_AR(3.0, True), var="M", tol=0.002)]),
            problem("c-ar-2", "Code A/A* and invert it",
                    r"The function every nozzle problem needs.",
                    [code("Write `area_ratio(M, g)` and `mach_from_area(ar, supersonic, g)`. Use bisection on [1e-6, 1] or [1, 50].",
                          starter="def area_ratio(M, g=1.4):\n    pass\n\ndef mach_from_area(ar, supersonic, g=1.4):\n    # find M with area_ratio(M) = ar on the requested branch\n    pass\n",
                          solution="def area_ratio(M, g=1.4):\n    return (1 / M) * ((2 / (g + 1)) * (1 + (g - 1) / 2 * M * M)) ** ((g + 1) / (2 * (g - 1)))\n\ndef mach_from_area(ar, supersonic, g=1.4):\n    if supersonic:\n        a, b = 1.0, 50.0\n    else:\n        a, b = 1e-6, 1.0\n    f = lambda M: area_ratio(M, g) - ar\n    for i in range(200):\n        m = 0.5 * (a + b)\n        if f(a) * f(m) <= 0:\n            b = m\n        else:\n            a = m\n    return 0.5 * (a + b)\n",
                          tests=f"check('A/A* at M=2', area_ratio(2.0), {gas.A_Astar(2.0):.10f}, 1e-9)\ncheck('A/A* at M=0.3', area_ratio(0.3), {gas.A_Astar(0.3):.10f}, 1e-9)\ncheck('sub root of 2', mach_from_area(2.0, False), {gas.M_from_AR(2.0, False):.10f}, 1e-7)\ncheck('sup root of 2', mach_from_area(2.0, True), {gas.M_from_AR(2.0, True):.10f}, 1e-7)\ncheck('sup root, helium', mach_from_area(3.0, True, 5/3), {gas.M_from_AR(3.0, True, 5/3):.10f}, 1e-7)\n",
                          wrong=["def area_ratio(M, g=1.4):\n    return (1 / M) * ((2 / (g + 1)) * (1 + (g - 1) / 2 * M * M)) ** ((g + 1) / (2 * (g - 1)))\n\ndef mach_from_area(ar, supersonic, g=1.4):\n    a, b = 1e-6, 50.0\n    f = lambda M: area_ratio(M, g) - ar\n    for i in range(200):\n        m = 0.5 * (a + b)\n        if f(a) * f(m) <= 0:\n            b = m\n        else:\n            a = m\n    return 0.5 * (a + b)\n",
                                 "def area_ratio(M, g=1.4):\n    return M * ((2 / (g + 1)) * (1 + (g - 1) / 2 * M * M)) ** ((g + 1) / (2 * (g - 1)))\n\ndef mach_from_area(ar, supersonic, g=1.4):\n    return 1.0\n"],
                          hints=["The bracket decides the branch: the function is not monotonic over [0, 50].",
                                 "A/A* has 1/M in front, so it blows up as M → 0."],
                          fn="mach_from_area")]),
        ]),
    concept(
        "c-reference-state-method", "The method: find the reference states, then the new Mach number", 1, C5,
        r"""
Every isentropic problem in the notes is solved the same way:
1. From what you're given at one station, find $M$ and the **reference states**: $p_0$, $T_0$, $\rho_0$ and $A^*$.
2. These hold for the whole isentropic flow. At the new station, get the new $M$ from whatever you know there ($A$, $p$, $T$, or $V$).
3. Use the new $M$ with the reference states for everything else.

The reference states may be imaginary: the flow need not ever stagnate or reach sonic. When a flow passes through a shock, friction or heating, some reference states change and some don't ([[c-shock-in-nozzle]], [[q-what-survives]]).
""",
        deeper=["c-area-ratio", "c-stagnation"],
        math=[],
        source="Notes, Section 5.5",
        problems=[
            problem("c-rm-1", "The notes' duct (example 5.5.1)",
                    r"An isentropic air flow has $p_0 = 1$ atm and $A^* = 0.746$ m² (found from station 1).",
                    [num("At station 2, $M = 0.8$. Pressure?", 1 / gas.p0_p(0.8), "atm"),
                     num("Station 3 has $A = 1.5$ m². Subsonic Mach number?", _A3sub, tol=0.003),
                     num("And its pressure?", 1 / gas.p0_p(_A3sub), "atm"),
                     num("The supersonic solution's Mach number?", _A3sup, tol=0.003),
                     choice("Which one actually occurs?", [opt("Can't tell without knowing whether the flow passed a throat in between", True),
                                                           opt("The subsonic one, always", why="If there was a throat and a low enough back pressure, the supersonic branch is reached.")])],
                    kind="notes"),
            problem("c-rm-2", "Order the method",
                    r"Problem Set 2 style: given $V$, $T$, $p$ at one point, find $M$, $T$ and $V$ where $p$ is lower.",
                    [order("Put the steps in order:",
                           ["Find $c = \\sqrt{\\gamma RT}$ and $M = V/c$ at the known point",
                            "Find $T_0$ and $p_0$ from $M$",
                            "At the new point, get $M$ from $p_0/p$",
                            "Get $T$ from $T_0/T$, then $V = M\\sqrt{\\gamma RT}$"])]),
            problem("c-rm-3", "A duct (new numbers)",
                    rf"Air moves isentropically through a duct. At one section $V = {_V3:g}$ m/s, $T = 10$ °C, $p = {_p3:g}$ kPa. Elsewhere $p = 35$ kPa.",
                    [num("Mach number at the first section?", _M3, tol=0.003), num("$T_0$?", _T03, "K"), num("$p_0$?", _p03, "kPa"),
                     num("Mach number where $p = 35$ kPa?", _M3b, tol=0.003), num("Temperature there?", _T3b, "K"), num("Velocity there?", _V3b, "m/s")],
                    kind="variant"),
            problem("c-rm-4", "Another gas (new numbers)",
                    r"Argon (MW 40, γ = 5/3) flows isentropically. At one point $V = 250$ m/s, $T = 40$ °C, $p = 60$ kPa. Elsewhere $p = 20$ kPa.",
                    [num("Mach number at the first point?", _MA, tol=0.003), num("Mach number where $p = 20$ kPa?", _MA2, tol=0.003), num("Temperature there?", _TA2, "K")],
                    kind="variant"),
            problem("c-rm-5", "Which shape? (new numbers)",
                    rf"8 kg/s of air flows isentropically. At one section $p = 2.5$ atm, $T = 600$ °C, $A = 200$ cm². Downstream, $M = 1.5$.",
                    [num("Mach number at the first section?", _M9, tol=0.003),
                     choice("Shape of the duct between them?", [opt("Converging–diverging: the flow must pass a sonic throat to reach Mach 1.5", True),
                                                                opt("Converging only", why="A converging duct alone can't take flow past Mach 1."),
                                                                opt("Diverging only", why="A subsonic flow slows down in a diverging duct.")]),
                     num("Downstream area?", _A9b * 1e4, "cm²"), num("Downstream pressure?", _p9b / ATM, "atm"), num("Downstream temperature?", _T9b, "K")],
                    kind="variant"),
        ]),
    concept(
        "c-compressibility", "When does Bernoulli break? The compressibility error", 1, C5,
        r"""
Expand the exact isentropic $p_0/p$ in powers of $M^2$ (binomial series):
$$\frac{p_0 - p}{\tfrac12\rho V^2} = 1 + \frac{M^2}{4} + \frac{2-\gamma}{24}M^4 + \dots$$
The leading 1 *is* Bernoulli. The rest is the compressibility correction: about 2% at Mach 0.3, 6% at 0.5, 28% at Mach 1. So below Mach 0.3, incompressible analysis (with a correction factor) is common in aircraft design; for supersonic flow, Bernoulli is simply wrong.
""",
        deeper=["c-stagnation", "p-bernoulli", "p-log-differentiation"],
        math=[r"\frac{p_0 - p}{\tfrac12\rho V^2} = 1 + \frac{M^2}{4} + \frac{2-\gamma}{24}M^4 + \cdots"],
        widget={"type": "compress"},
        exam="Quote the error at the given Mach number: (p0/p − 1)/(γM²/2) − 1.",
        source="Notes, Section 5.6; Problem Set 3, Problem 1 skills",
        problems=[
            problem("c-co-1", "Compare the two (new speeds)",
                    r"Air from rest at 1 bar, 300 K is accelerated isentropically. For Bernoulli, use the stagnation density $\rho_0 = p_0/(RT_0)$. Problem Set 3 asks this at other speeds.",
                    [num("At 100 m/s, exact $p_0 - p$?", _dps[100][0], "Pa"), num("At 100 m/s, Bernoulli's $\\tfrac12\\rho_0V^2$?", _dps[100][1], "Pa"),
                     num("At 300 m/s, exact $p_0 - p$?", _dps[300][0], "Pa"), num("At 300 m/s, Bernoulli?", _dps[300][1], "Pa"),
                     choice("At 450 m/s?", [opt("Bernoulli's number is far off: the flow is supersonic by then", True),
                                            opt("Still within a few percent", why=f"Exact gives {_dps[450][0]/1000:.1f} kPa against Bernoulli's {_dps[450][1]/1000:.1f} kPa.")])],
                    kind="variant"),
            problem("c-co-2", "The series",
                    r"$\dfrac{p_0 - p}{\tfrac12\rho V^2} = 1 + \dfrac{M^2}{4} + \dots$",
                    [num("Percent error of Bernoulli at Mach 0.4, from the first correction term only?", 100 * 0.4 ** 2 / 4, "%")]),
        ]),
    concept(
        "c-converging-nozzle", "The converging nozzle: back pressure controls it until it chokes", 1, C6,
        r"""
A reservoir at $p_0, T_0$ discharges through a converging nozzle into a chamber at $p_b$.
- $p_b = p_0$: no flow.
- $p_0 > p_b > p^*$: subsonic everywhere, and the **exit pressure equals the back pressure**. (A subsonic jet at a different pressure would keep expanding or contracting, which isn't physical.)
- $p_b = p^* = 0.528\,p_0$: exit just sonic, mass flow at its maximum.
- $p_b < p^*$: **choked**. Exit stays sonic at $p^*$, mass flow is fixed, and the jet expands outside the nozzle.
""",
        deeper=["c-choking", "c-reference-state-method"],
        math=[r"p_e = \max(p_b,\ 0.528\,p_0)"],
        widget={"type": "nozzle", "preset": "converging"},
        source="Notes, Section 6.1; Problem Set 2, Problem 5 skills",
        problems=[
            problem("c-cn-1", "A converging nozzle (new numbers)",
                    rf"Air from a large chamber at 400 K and 1.8 atm discharges through a converging nozzle (exit area 20 cm²) into 1 atm.",
                    [choice("Is the exit choked?", [opt("No: 1/1.8 = 0.556 is above 0.528, so the exit pressure matches 1 atm", True),
                                                    opt("Yes", why="Choking needs p_b/p0 ≤ 0.528; here it's 0.556.")]),
                     num("Exit velocity?", _Ve5, "m/s"), num("Mass flow?", _mdot5, "kg/s"),
                     num("Maximum exit velocity if the back pressure is lowered?", _Vmax5, "m/s", explain="Sonic at T* = 0.833 T0."),
                     num("Maximum mass flow?", _mmax5, "kg/s")],
                    kind="variant"),
        ]),
    concept(
        "c-cd-nozzle-isentropic", "The converging-diverging nozzle: two isentropic answers", 1, C6,
        r"""
Add a diverging section after the throat. As $p_b$ drops, flow speeds up until the throat goes sonic (choked). Beyond the throat there are then exactly two isentropic possibilities:
- the **subsonic** branch: the flow slows back down; exit pressure $p_3$ (for "case 3");
- the **supersonic** branch: the flow keeps accelerating to the **design** exit Mach number and pressure $p_d$.

For back pressures between $p_3$ and $p_d$ no isentropic solution exists: shocks appear ([[c-back-pressure-regimes]]). Below $p_d$ the nozzle is underexpanded and the jet expands outside ([[c-over-under-expanded]]). This "nozzle with variable back pressure" is the canonical problem of the course; you'll revisit it with every new tool.
""",
        deeper=["c-converging-nozzle", "c-area-ratio"],
        math=[r"\frac{A_e}{A_t} \Rightarrow M_{e,\text{sub}},\ M_{e,\text{sup}}\ \Rightarrow\ p_3,\ p_d"],
        widget={"type": "nozzle"},
        exam="Compute p3 and pd for the given area ratio before anything else; they bracket the regimes.",
        source="Notes, Section 6.2; Problem Set 3, Problem 4 skills",
        problems=[
            problem("c-cd-1", "Critical back pressures (new nozzle)",
                    r"A converging–diverging nozzle with $A_t = 1$ m² and $A_e = 4$ m² exhausts air to 1 atm (fixed). Problem Set 3 uses another area ratio.",
                    [num("Subsonic exit Mach number for a sonic throat?", _nz["Me_sub"], tol=0.003),
                     num("Lowest reservoir pressure that chokes the throat?", _p0_choke / ATM, "atm"),
                     num("Design (supersonic) exit Mach number?", _nz["Me_sup"], tol=0.003),
                     num("Reservoir pressure for supersonic isentropic flow all the way to the exit?", _p0_design / ATM, "atm"),
                     choice("Both are choked. Are their mass flows equal?", [opt("No: choked mass flow is proportional to p0, which is much higher in the second case", True),
                                                                            opt("Yes, choked flow is choked flow", why="ṁ = 0.0404 p0 A*/√T0: same A* and T0, different p0.")])],
                    kind="variant"),
        ]),
    concept(
        "c-rocket-thrust", "Rocket thrust: momentum flux plus a pressure term", 1, C6,
        r"""
Put the rocket in a control volume. Propellant enters with negligible x-momentum; exhaust leaves at $V_e$ through $A_e$ at $p_e$; the atmosphere pushes everywhere else at $p_{amb}$:
$$F = \dot m V_e + (p_e - p_{amb})A_e.$$
With isentropic expansion from chamber conditions,
$$F = \dot m\sqrt{\frac{2\gamma}{\gamma-1}RT_0\left[1 - \left(\frac{p_e}{p_0}\right)^{\frac{\gamma-1}{\gamma}}\right]} + A_e(p_e - p_{amb}).$$
Supersonic exhaust need not match ambient pressure, so both terms matter. The **specific impulse** $I_{sp} = F/\dot m$ is the rocket's fuel economy (m/s; divide by $g_0 = 9.81$ for seconds).
""",
        deeper=["c-cv-momentum", "c-cd-nozzle-isentropic"],
        math=[r"F = \dot m V_e + (p_e - p_{amb})A_e", r"I_{sp} = F/\dot m"],
        widget={"type": "rocket"},
        source="Notes, Section 6.3; Problem Set 4, Problem 2 skills",
        problems=[
            problem("c-rt-1", "Nuclear thermal rocket (notes example 6.3.4)",
                    r"Hydrogen (MW 2, modelled with γ = 1.4) at 3000 K and 30 atm in the chamber.",
                    [num("Exit Mach number for a nozzle matched at sea level ($p_e = 1$ atm)?", gas.M_from_p0p(30.0), tol=0.003),
                     num("Its $I_{sp}$ at sea level (= $V_e$)?", gas.exit_velocity(3000, 1 / 30, R=gas.R_of(2.0)), "m/s"),
                     num("The same nozzle in vacuum: add $A_ep_e/\\dot m$. New $I_{sp}$?", gas.exit_velocity(3000, 1 / 30, R=gas.R_of(2.0)) + gas._Ae_mdot * ATM, "m/s", tol=0.005),
                     num("Ideal maximum, expanding to zero pressure?", gas.v_max(3000, R=gas.R_of(2.0)), "m/s")],
                    kind="notes"),
            problem("c-rt-2", "Exit conditions for a sea-level nozzle (new numbers)",
                    rf"Air expands from $p_0 = 3$ MPa, $T_0 = 1200$ K to an ambient of 50 kPa at 4 kg/s. (Problem Set 3 uses nitrogen with other numbers.)",
                    [num("Exit Mach number for optimum thrust ($p_e = p_{amb}$)?", _Mer, tol=0.003), num("Exhaust velocity?", _Ver, "m/s"),
                     num("Throat area?", _Atr * 1e4, "cm²"), num("Exit area?", _Aer * 1e4, "cm²")],
                    kind="variant"),
        ]),
    concept(
        "c-optimal-expansion", "Optimal thrust: expand until the exit pressure equals ambient", 1, C6,
        r"""
Lengthen the nozzle by $dA_e$ with chamber conditions fixed. The momentum term grows (faster exhaust) but the pressure term shrinks. Using $\dot m\,dV_e = -A_e\,dp_e$ (inviscid momentum), the two changes nearly cancel and
$$\frac{dF}{dA_e} = p_e - p_{amb}.$$
So adding area helps while $p_e > p_{amb}$ (**underexpanded**) and hurts once $p_e < p_{amb}$ (**overexpanded**): the extremum is $p_e = p_{amb}$, all thrust from momentum. (Problem Set 4 asks you to prove it's a maximum.) A nozzle optimal at sea level is underexpanded in space, and vice versa.
""",
        deeper=["c-rocket-thrust"],
        math=[r"\frac{dF}{dA_e} = p_e - p_{amb}"],
        widget={"type": "rocket", "preset": "optimal"},
        source="Notes, Section 6.3.1; Problem Set 4, Problems 1 and 3 skills",
        problems=[
            problem("c-oe-1", "Grow the nozzle?",
                    r"A rocket at altitude has $p_e = 40$ kPa with $p_{amb} = 25$ kPa.",
                    [choice("Should a slightly longer nozzle (larger $A_e$) increase thrust?", [opt("Yes: dF/dA_e = p_e − p_amb > 0", True),
                                                                                                opt("No: the pressure term would fall", why="It falls, but the momentum gain is larger while p_e > p_amb.")])]),
            problem("c-oe-2", "Sea-level nozzle in space (new numbers)",
                    rf"A nozzle is designed for $p_e = 1$ atm with $p_0 = 3$ MPa, $T_0 = 2000$ K, γ = 1.25, $R = 350$ J/(kg·K). (Problem Set 4 has γ = 1.4 and other numbers.)",
                    [num("Exit Mach number?", _Me4, tol=0.003), num("Expansion ratio $A_e/A_t$?", _eps4, tol=0.005),
                     num("Thrust ratio, sea level to vacuum, same nozzle?", _F_sl / _F_sp, tol=0.003,
                         explain="Per unit mass flow: sea level gives $V_e$; vacuum adds $A_ep_e/\\dot m = \\epsilon\\,c^*\\,p_e/p_0$ with $c^* = p_0A_t/\\dot m$."),
                     num("Vacuum thrust with this nozzle as a fraction of the infinite-expansion maximum?", _F_sp / _F_max, tol=0.003)],
                    kind="variant"),
        ]),
    concept(
        "c-isp-max-velocity", "The fastest steady flow: V_max = c₀ √(2/(γ−1))", 1, C6,
        r"""
Expand all the way to zero pressure and all thermal energy becomes kinetic: $c_pT_0 = V_{max}^2/2$, so
$$V_{max} = \sqrt{\frac{2\gamma}{\gamma-1}RT_0} = c_0\sqrt{\frac{2}{\gamma-1}}.$$
The best propellant has a **high initial sound speed**: hot and light. Hydrogen (MW 2) heated without burning it with oxygen (which would add heavy water vapour) is the reason for nuclear thermal rockets like NERVA. A steady expansion can't beat $V_{max}$; an *unsteady* expansion can (the notes point to Chapter 16).
""",
        deeper=["c-rocket-thrust", "c-sound-ideal-gas"],
        math=[r"V_{max} = c_0\sqrt{\frac{2}{\gamma - 1}}"],
        source="Notes, Section 6.3.2; Problem Set 3, Problem 5 skills",
        problems=[
            problem("c-im-1", "Pick the propellant (new temperature)",
                    r"A chamber limited to 2500 K. Compare helium (MW 4, γ = 5/3) and hydrogen (MW 2, γ = 1.4).",
                    [num("$V_{max}$ for helium?", _vHe, "m/s"), num("$V_{max}$ for hydrogen?", _vH2, "m/s"),
                     choice("Which wins, and why?", [opt("Hydrogen: its low molecular weight more than offsets its lower γ", True),
                                                    opt("Helium: higher γ always wins", why="2γ/(γ−1) is 5 for helium against 7 for hydrogen, and hydrogen's R is twice helium's.")])],
                    kind="variant"),
            problem("c-im-2", "Derive it",
                    r"Start from $h_0 = h + V^2/2$.",
                    [expr(r"With $h = c_pT$ and $T\to0$, type $V_{max}$ in terms of `c_p` and `T0`.", sp.sqrt(2 * cp * T0), ["c_p", "T0"], ranges={"c_p": [500, 15000], "T0": [300, 3500]}),
                     expr(r"Now in terms of the stagnation sound speed `c` (meaning $c_0$) and `gamma`.", c * sp.sqrt(2 / (g - 1)), ["c", "gamma"], ranges={"c": [300, 2000], "gamma": [1.1, 1.7]})]),
        ]),
    concept(
        "c-altitude-compensation", "One nozzle can't be optimal at every altitude", 1, C6,
        r"""
A launch vehicle climbs from 1 atm to vacuum, but a fixed nozzle is optimal at only one ambient pressure. Engineers say they "live and die by the third significant digit of $I_{sp}$" (payload depends exponentially on it). Solutions in the notes:
- **Staging by nozzle**: the Atlas fired sea-level "boosters" and a high-altitude "sustainer", then dropped the boosters.
- **Aerospike**: no outer wall; the jet's outer boundary is set by ambient pressure, so it adapts as the rocket climbs. Ground-tested in the 1960s; the X-33 flight test was cancelled.

Overexpanded at sea level badly enough and a shock moves *into* the nozzle, wrecking performance ([[c-back-pressure-regimes]]).
""",
        deeper=["c-optimal-expansion"],
        math=[],
        source="Notes, Section 6.3.5",
        problems=[
            problem("c-ac-1", "Why the aerospike?",
                    r"An aerospike replaces the bell's outer wall with a free boundary.",
                    [choice("What sets that boundary's shape?", [opt("The ambient pressure, which the jet edge must match", True),
                                                                opt("The chamber pressure", why="The chamber sets the flow; the free boundary adjusts to ambient pressure."),
                                                                opt("Nothing: it's fixed at manufacture", why="That's exactly what a bell nozzle does, and why it's only optimal at one altitude.")])]),
        ]),
]
