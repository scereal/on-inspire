"""Layer 1, Chapters 10-11: frictional flow (Fanno) and flow with heat transfer (Rayleigh) in constant-area ducts."""
import math
import sympy as sp
from lib import *
import gas

C10, C11 = "Ch. 10 · Friction (Fanno flow)", "Ch. 11 · Heat transfer (Rayleigh flow)"
CP = 1.4 * 287 / 0.4

# 10.2.1 (notes): M = 0.5, 1 atm, 300 K, D = 5 cm, f = 0.005
_f, _D = 0.005, 0.05
_Ls = gas.fanno_fL(0.5) * _D / (4 * _f)
_ps, _Ts = 1 / gas.fanno_p(0.5), 300 / gas.fanno_T(0.5) * 1.0  # T* from T/T* at 0.5
_Ts = 300 / gas.fanno_T(0.5)
_fl2 = gas.fanno_fL(0.5) - 4 * _f * 1.5 / _D
_M2 = gas.fanno_M(_fl2, False)
_p2 = _ps * gas.fanno_p(_M2)
_p01 = gas.p0_p(0.5)
_p02 = _ps * gas.p0_p(1.0) * gas.fanno_p0(_M2)  # p0* = p* (p0/p)* ; p0 = p0* (p0/p0*)

# 10.4.1 (notes): supersonic inflow M = 2, 101.3 kPa, L = 3.5 m, D = 0.3 m, f = 0.005, pb = 350 kPa
_k = 4 * 0.005 / 0.3
_pst = 101.3 / gas.fanno_p(2.0)
_Lstar2 = gas.fanno_fL(2.0) / _k
_Me_sup = gas.fanno_M(gas.fanno_fL(2.0) - _k * 3.5, True)
_pe_sup = _pst * gas.fanno_p(_Me_sup)


def _pexit(x):
    Mx = gas.fanno_M(gas.fanno_fL(2.0) - _k * x, True)
    My = gas.ns_M2(Mx)
    py = _pst * gas.fanno_p(Mx) * gas.ns_p2p1(Mx)
    Me = gas.fanno_M(gas.fanno_fL(My) - _k * (3.5 - x), False)
    return py / gas.fanno_p(My) * gas.fanno_p(Me), Me


_pe_entry, _pe_exitshock = _pexit(0.0)[0], _pexit(3.5 - 1e-9)[0]
_xs = gas.bisect(lambda x: _pexit(x)[0] - 350.0, 0.0, 3.5 - 1e-9)
_Mex = _pexit(_xs)[1]
assert abs(_pe_entry - 408) < 1.5 and abs(_pe_exitshock - 331) < 1.5 and abs(_pe_sup - 177) < 1.5

# Fanno variant: air at M = 0.3, 300 K, 2 atm into a 10 cm pipe with f = 0.004; how long until it chokes?
_Lv = gas.fanno_fL(0.3) * 0.10 / (4 * 0.004)

# 11.2.1 (notes): M = 0.7, 300 K, 1 atm
_T01 = 300 * gas.T0_T(0.7)
_T0s = _T01 / gas.ray_T0(0.7)
_qs = CP * (_T0s - _T01) / 1000
_Tstar = 300 / gas.ray_T(0.7)
_pstar = 1 / gas.ray_p(0.7)
_T02b = _T0s * gas.ray_T0(0.5)
_qb = CP * (_T02b - _T01) / 1000
_T2b = _Tstar * gas.ray_T(0.5)
_p2b = _pstar * gas.ray_p(0.5)

# Rayleigh variant: a combustor, air in at M = 0.25, 500 K; add 600 kJ/kg
_T0c = 500 * gas.T0_T(0.25)
_T0cs = _T0c / gas.ray_T0(0.25)
_qmax = CP * (_T0cs - _T0c) / 1000
_T0c2 = _T0c + 600e3 / CP
_Mc2 = gas.ray_M(_T0c2 / _T0cs, False)

CONCEPTS = [
    concept(
        "c-fanno-effects", "Friction drives a flow toward Mach 1, like a converging duct", 1, C10,
        r"""
Long constant-area ducts (pipelines, many diameters long) with wall shear $\tau_w = f\cdot\tfrac12\rho V^2$ (Fanning $f$, typically 0.001–0.05) and no heat transfer: **Fanno flow**. The differential relations give
$$\frac{dM^2}{M^2} = \frac{\gamma M^2\left(1 + \frac{\gamma-1}{2}M^2\right)}{1 - M^2}\,4f\frac{dx}{D_H}.$$
- **Subsonic**: friction *accelerates* the flow, and $p$ and $T$ fall (a large pressure gradient pushes it).
- **Supersonic**: friction decelerates it, and $p$, $T$ rise.

Either way, toward Mach 1, exactly like a converging area. The boundary layers really do narrow the core flow. The difference: friction is irreversible, so $p_0$ always falls ($T_0$ stays constant: still adiabatic). Hydraulic diameter $D_H = 4A/P$ (a circle's diameter, a square's side).
""",
        deeper=["c-area-velocity", "c-1d-differential"],
        math=[r"\frac{dM^2}{M^2} = \frac{\gamma M^2\left(1+\frac{\gamma-1}{2}M^2\right)}{1-M^2}\,\frac{4f\,dx}{D_H}", r"D_H = \frac{4A}{P}"],
        widget={"type": "ts", "preset": "fanno"},
        analogy=analogy("Friction is a slowly narrowing pipe that you can't see: boundary layers thicken along the wall, squeezing the core flow, which then behaves like flow in a converging nozzle.",
                        "a real converging nozzle is reversible; friction always costs stagnation pressure, even while it speeds a subsonic flow up."),
        exam="Subsonic Fanno flow speeds up and cools down. If your answer slows a subsonic pipe flow, check your signs.",
        source="Notes, Section 10.1",
        problems=[
            problem("c-fe-1", "Which way?",
                    r"Constant-area adiabatic duct with friction.",
                    [choice("Subsonic flow. Mach number along the pipe:", [opt("Increases toward 1", True), opt("Decreases", why="Friction acts like a converging area: subsonic flow accelerates.")]),
                     choice("Subsonic flow. Static temperature:", [opt("Decreases", True), opt("Increases, because friction heats", why="With T0 fixed and V rising, T must fall; the friction heating shows up as lost p0, not higher T.")]),
                     choice("Stagnation pressure:", [opt("Decreases, always", True), opt("Increases in supersonic flow", why="Friction is irreversible in both regimes; p0 falls either way.")]),
                     num("Hydraulic diameter of a 4 cm × 4 cm square duct?", 4.0, "cm")]),
        ]),
    concept(
        "c-fanno-relations", "Fanno relations: L* is the length to choke, the analogue of A*", 1, C10,
        r"""
Integrating to the sonic point defines the reference length $L^*$ (the duct length that would just choke the flow):
$$\frac{4fL^*}{D} = \frac{1-M^2}{\gamma M^2} + \frac{\gamma+1}{2\gamma}\ln\frac{(\gamma+1)M^2}{2 + (\gamma-1)M^2},$$
$$\frac{T}{T^*} = \frac{\gamma+1}{2+(\gamma-1)M^2},\quad \frac{p}{p^*} = \frac{1}{M}\sqrt{\frac{T}{T^*}},\quad \frac{p_0}{p_0^*} = \frac{1}{M}\left[\frac{2+(\gamma-1)M^2}{\gamma+1}\right]^{\frac{\gamma+1}{2(\gamma-1)}}.$$
**Method**: from the inlet Mach number, find $L^*_1$; a duct of length $L$ leaves $L^*_2 = L^*_1 - L$; invert for $M_2$; relate everything through the (possibly imaginary) sonic state.
""",
        deeper=["c-fanno-effects", "c-reference-state-method"],
        math=[r"\frac{4f L^*}{D}(M)", r"\frac{4fL^*_2}{D} = \frac{4fL^*_1}{D} - \frac{4fL}{D}"],
        widget={"type": "tables", "preset": "fanno"},
        source="Notes, Section 10.2",
        problems=[
            problem("c-fr-1", "Subsonic pipe (notes example 10.2.1)",
                    r"Air enters a pipe at Mach 0.5, 1 atm, 300 K. Diameter 5 cm, $f = 0.005$.",
                    [num("$4fL^*/D$ at the inlet?", gas.fanno_fL(0.5), tol=0.002), num("Length to choke, $L^*$?", _Ls, "m"),
                     num("Pressure at the sonic end, $p^*$?", _ps, "atm"),
                     num("If the pipe is only 1.5 m long, exit Mach number?", _M2, tol=0.003), num("Exit pressure?", _p2, "atm")],
                    kind="notes"),
            problem("c-fr-2", "How long until it chokes? (new numbers)",
                    r"Air enters a 10 cm pipe at Mach 0.3 with $f = 0.004$.",
                    [num("Length to choke?", _Lv, "m"),
                     choice("At Mach 3 instead, the choking length is:", [opt("Much shorter: supersonic flow chokes within a few dozen diameters", True),
                                                                          opt("Longer", why="4fL*/D at Mach 3 is about 0.52, versus 5.3 at Mach 0.3.")])]),
            problem("c-fr-3", "Code Fanno flow",
                    r"Two functions turn a Fanno table into code.",
                    [code("Write `fanno_fL(M, g)` (4fL*/D) and `fanno_mach(fL, supersonic, g)` that inverts it by bisection on [1e-6, 1] or [1, 100].",
                          starter="import math\n\ndef fanno_fL(M, g=1.4):\n    pass\n\ndef fanno_mach(fL, supersonic, g=1.4):\n    pass\n",
                          solution="import math\n\ndef fanno_fL(M, g=1.4):\n    return (1 - M * M) / (g * M * M) + (g + 1) / (2 * g) * math.log((g + 1) * M * M / (2 + (g - 1) * M * M))\n\ndef fanno_mach(fL, supersonic, g=1.4):\n    a, b = (1.0, 100.0) if supersonic else (1e-6, 1.0)\n    fa = fanno_fL(a, g) - fL\n    for i in range(200):\n        m = 0.5 * (a + b)\n        fm = fanno_fL(m, g) - fL\n        if fa * fm <= 0:\n            b = m\n        else:\n            a, fa = m, fm\n    return 0.5 * (a + b)\n",
                          tests=f"check('4fL*/D at 0.5', fanno_fL(0.5), {gas.fanno_fL(0.5):.10f}, 1e-9)\ncheck('4fL*/D at 2', fanno_fL(2.0), {gas.fanno_fL(2.0):.10f}, 1e-9)\ncheck('notes exit Mach', fanno_mach({_fl2:.12f}, False), {_M2:.10f}, 1e-7)\ncheck('supersonic', fanno_mach(0.2, True), {gas.fanno_M(0.2, True):.10f}, 1e-7)\n",
                          wrong=["import math\n\ndef fanno_fL(M, g=1.4):\n    return (1 - M * M) / (g * M * M) + (g + 1) / (2 * g) * math.log((g + 1) * M * M / (2 + (g - 1) * M * M))\n\ndef fanno_mach(fL, supersonic, g=1.4):\n    a, b = 1e-6, 100.0\n    fa = fanno_fL(a, g) - fL\n    for i in range(200):\n        m = 0.5 * (a + b)\n        fm = fanno_fL(m, g) - fL\n        if fa * fm <= 0:\n            b = m\n        else:\n            a, fa = m, fm\n    return 0.5 * (a + b)\n",
                                 "import math\n\ndef fanno_fL(M, g=1.4):\n    return (1 - M * M) / (g * M * M) + (g + 1) / (2 * g) * math.log10((g + 1) * M * M / (2 + (g - 1) * M * M))\n\ndef fanno_mach(fL, supersonic, g=1.4):\n    return 0.5\n"],
                          hints=["math.log is the natural log; math.log10 is base 10.", "4fL*/D falls to 0 at M = 1 from both sides, so each branch needs its own bracket."],
                          fn="fanno_mach")]),
        ]),
    concept(
        "c-fanno-choking", "Longer than L*: subsonic flow throttles itself; supersonic flow takes a shock", 1, C10,
        r"""
Make the duct longer than $L^*$ and the flow can't simply go past Mach 1.
- **Subsonic inflow**: the news travels upstream. The inlet Mach number and mass flow drop until the new length is exactly $L^*$: **frictional choking**, like adding a smaller throat.
- **Supersonic inflow**: the news can't travel upstream, so a **normal shock** forms in the duct (stable here, unlike in a diverging nozzle). The subsonic flow behind it takes a much longer distance to choke, so the shock positions itself so the exit is just sonic. More length pushes the shock upstream, eventually into the nozzle and to its throat.

Useful fact: $p^*$ is the same on both sides of a shock in a Fanno duct, so one sonic reference serves the whole problem. Solve by trying a regime, marching to the exit, and comparing the exit pressure with the back pressure.
""",
        deeper=["c-fanno-relations", "c-shock-in-nozzle"],
        math=[r"L > L^*\ \Rightarrow\ \begin{cases}\dot m\downarrow & \text{subsonic}\\ \text{shock in duct} & \text{supersonic}\end{cases}"],
        source="Notes, Sections 10.3–10.4",
        problems=[
            problem("c-fc-1", "Supersonic flow with friction (notes example 10.4.1)",
                    r"Air enters a 3.5 m duct (diameter 0.3 m, $f = 0.005$) from a nozzle at Mach 2.0 and 101.3 kPa, and exhausts into 350 kPa.",
                    [num("Length to choke the supersonic inflow, $L^*$?", _Lstar2, "m"), num("Sonic pressure $p^*$?", _pst, "kPa"),
                     num("Exit pressure if the flow stays supersonic throughout?", _pe_sup, "kPa"),
                     num("Exit pressure with a shock at the duct entrance?", _pe_entry, "kPa"),
                     num("With a shock at the exit plane?", _pe_exitshock, "kPa"),
                     num("So where is the shock, measured from the entrance (the notes interpolate to about 2.59 m)?", _xs, "m", tol=0.01),
                     num("Exit Mach number?", _Mex, tol=0.005)],
                    kind="notes"),
            problem("c-fc-2", "Subsonic: too long",
                    r"A subsonic duct already flowing at its choking length is extended by 20% with the reservoir and back pressure unchanged.",
                    [choice("What happens?", [opt("The inlet Mach number and mass flow drop so the new length is the choking length", True),
                                              opt("A shock forms near the exit", why="Shocks need supersonic flow; a subsonic flow simply throttles itself."),
                                              opt("The exit goes supersonic", why="Friction drives toward Mach 1 and can't take it past.")])]),
        ]),
    concept(
        "c-rayleigh-effects", "Heating drives a flow toward Mach 1 too, with a twist in temperature", 1, C11,
        r"""
Constant area, no friction, heat added ($dq>0$): **Rayleigh flow**. Heat goes straight into stagnation temperature, $dq = c_p\,dT_0$, so $T_0$ is no longer constant. Heating **accelerates** subsonic flow and **decelerates** supersonic flow: again toward Mach 1, like a converging duct. Cooling does the reverse (like a diverging duct).

The twist: static temperature peaks at $M = 1/\sqrt\gamma = 0.845$. Between 0.845 and 1, adding heat makes the gas **colder**: the heat goes into speeding it up faster than into warming it. Static pressure falls whenever velocity rises. $p_0$ falls with heating (and can rise with cooling, since cooling removes entropy).

In principle you could heat to Mach 1 and then *cool* to go supersonic in a straight pipe, but nobody has built one (extracting heat from supersonic flow is hard); "pathological detonations" do it naturally.
""",
        deeper=["c-area-velocity", "c-cv-energy"],
        math=[r"dq = c_p\,dT_0", r"T_{max}\ \text{at}\ M = 1/\sqrt{\gamma}"],
        widget={"type": "ts", "preset": "rayleigh"},
        exam="Know the three bands: M < 0.845 (heating warms and speeds), 0.845 < M < 1 (heating cools and speeds), M > 1 (heating warms and slows).",
        source="Notes, Section 11.1",
        problems=[
            problem("c-re-1", "Heat in, temperature down?",
                    r"Rayleigh flow of air.",
                    [num("Mach number of maximum static temperature?", 1 / math.sqrt(1.4), tol=0.002),
                     choice("At Mach 0.9, adding heat makes the static temperature:", [opt("Fall", True), opt("Rise", why="Between 0.845 and 1 the heat goes more into kinetic energy than into temperature.")]),
                     choice("At Mach 2, adding heat:", [opt("Slows the flow and raises T", True), opt("Speeds the flow", why="Supersonic flow decelerates toward Mach 1 when heated.")])]),
        ]),
    concept(
        "c-rayleigh-relations", "Rayleigh relations: T₀/T₀* sets the Mach number", 1, C11,
        r"""
From continuity and momentum ($p + \rho V^2$ constant, $\rho V^2 = \gamma pM^2$), referred to the sonic state:
$$\frac{p}{p^*} = \frac{1+\gamma}{1+\gamma M^2},\quad \frac{T}{T^*} = \left(\frac{M(1+\gamma)}{1+\gamma M^2}\right)^2,\quad \frac{T_0}{T_0^*} = \frac{2(\gamma+1)M^2}{(1+\gamma M^2)^2}\left(1+\frac{\gamma-1}{2}M^2\right).$$
**Method**: inlet $M_1$ gives $T_{01}$ and $T_0^*$; heat $q$ gives $T_{02} = T_{01} + q/c_p$; then $T_{02}/T_0^*$ gives $M_2$ (pick the branch of the inflow); then $p$, $T$, $p_0$ from the sonic state.
""",
        deeper=["c-rayleigh-effects", "c-reference-state-method"],
        math=[r"\frac{T_0}{T_0^*} = \frac{2(\gamma+1)M^2}{(1+\gamma M^2)^2}\left(1+\frac{\gamma-1}{2}M^2\right)", r"q = c_p(T_{02} - T_{01})"],
        widget={"type": "tables", "preset": "rayleigh"},
        source="Notes, Section 11.2",
        problems=[
            problem("c-rr-1", "Heating to sonic (notes example 11.2.1)",
                    r"Air enters a frictionless duct at Mach 0.7, 300 K, 1 atm. $c_p = 1004.5$ J/(kg·K).",
                    [num("Inlet $T_0$?", _T01, "K"), num("Sonic $T_0^*$?", _T0s, "K"), num("Heat to reach sonic?", _qs, "kJ/kg"),
                     num("Exit static temperature at sonic, $T^*$?", _Tstar, "K", explain="Barely above the inlet's 300 K: the temperature rose and then fell past Mach 0.845."),
                     num("If instead it leaves at Mach 0.5: heat transferred (negative means cooling)?", _qb, "kJ/kg"),
                     num("Exit temperature at Mach 0.5?", _T2b, "K")],
                    kind="notes"),
            problem("c-rr-2", "Code Rayleigh flow",
                    r"The heat-addition table in code.",
                    [code("Write `ray_T0(M, g)` ($T_0/T_0^*$) and `mach_after_heating(M1, q, T01, cp, g)` returning the subsonic exit Mach number (assume the inflow is subsonic and not choked).",
                          starter="def ray_T0(M, g=1.4):\n    pass\n\ndef mach_after_heating(M1, q, T01, cp=1004.5, g=1.4):\n    pass\n",
                          solution="def ray_T0(M, g=1.4):\n    return 2 * (g + 1) * M * M / (1 + g * M * M) ** 2 * (1 + (g - 1) / 2 * M * M)\n\ndef mach_after_heating(M1, q, T01, cp=1004.5, g=1.4):\n    T0s = T01 / ray_T0(M1, g)\n    target = (T01 + q / cp) / T0s\n    a, b = 1e-6, 1.0\n    for i in range(200):\n        m = 0.5 * (a + b)\n        if (ray_T0(a, g) - target) * (ray_T0(m, g) - target) <= 0:\n            b = m\n        else:\n            a = m\n    return 0.5 * (a + b)\n",
                          tests=f"check('T0/T0* at 0.7', ray_T0(0.7), {gas.ray_T0(0.7):.10f}, 1e-9)\ncheck('combustor', mach_after_heating(0.25, 600e3, {_T0c:.8f}), {_Mc2:.10f}, 1e-6)\n",
                          wrong=["def ray_T0(M, g=1.4):\n    return 2 * (g + 1) * M * M / (1 + g * M * M) ** 2\n\ndef mach_after_heating(M1, q, T01, cp=1004.5, g=1.4):\n    return M1\n",
                                 "def ray_T0(M, g=1.4):\n    return 2 * (g + 1) * M * M / (1 + g * M * M) ** 2 * (1 + (g - 1) / 2 * M * M)\n\ndef mach_after_heating(M1, q, T01, cp=1004.5, g=1.4):\n    T0s = T01 / ray_T0(M1, g)\n    target = (T01 + q) / T0s\n    a, b = 1e-6, 1.0\n    for i in range(200):\n        m = 0.5 * (a + b)\n        if (ray_T0(a, g) - target) * (ray_T0(m, g) - target) <= 0:\n            b = m\n        else:\n            a = m\n    return 0.5 * (a + b)\n"],
                          hints=["T0* comes from the inlet: T0* = T01 / ray_T0(M1).", "Heat raises the stagnation temperature by q/cp, not by q."],
                          fn="mach_after_heating")]),
        ]),
    concept(
        "c-thermal-choking", "Too much heat chokes the flow", 1, C11,
        r"""
Once enough heat is added to reach Mach 1 at the duct exit, adding more can't be absorbed at the same inflow.
- **Subsonic inflow**: the inlet Mach number and mass flow fall (**thermal choking**).
- **Supersonic inflow**: a normal shock forms **upstream of the heated section** (in the nozzle). Unlike Fanno flow it can't sit in the heated duct: the shock is adiabatic and doesn't change $T_0^*$, so the subsonic flow behind it would choke just the same. Only pushing the shock into the diverging nozzle lowers the duct's inlet Mach number enough.

This matters for ramjet and scramjet combustors: burn too much fuel and the inlet unstarts.
""",
        deeper=["c-rayleigh-relations", "c-fanno-choking"],
        math=[r"q_{max} = c_p\,(T_0^* - T_{01})"],
        source="Notes, Ch. 11",
        problems=[
            problem("c-tc-1", "A combustor (new numbers)",
                    r"Air enters a constant-area combustor at Mach 0.25 and 500 K; $c_p = 1004.5$ J/(kg·K).",
                    [num("Maximum heat before choking?", _qmax, "kJ/kg"),
                     num("Exit Mach number after adding 600 kJ/kg?", _Mc2, tol=0.003),
                     choice("Adding 2000 kJ/kg instead?", [opt("It exceeds the choking limit: the inlet Mach number and mass flow must drop", True),
                                                          opt("The exit goes supersonic", why="Heating can't push the flow past Mach 1 in a constant-area duct.")])]),
        ]),
]
assert 2000 > _qmax
