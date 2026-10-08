"""Layer 2: questions that join several ideas, the way exam questions do."""
import math
from lib import *
import gas

Q = "Questions that join the ideas"

_n = gas.nozzle(2.0, 0.5)
assert _n["regime"] == "overexpanded"

CONCEPTS = [
    concept(
        "q-three-chokes", "Three ways to choke a flow: area, friction, heat", 2, Q,
        r"""
A converging area, wall friction and heat addition all push a flow **toward Mach 1**, and each can choke it. Their differences are in what they cost and how the flow escapes when you overdo them:

| driver | toward M = 1 by | $T_0$ | $p_0$ | overdone, subsonic | overdone, supersonic |
|---|---|---|---|---|---|
| area (isentropic) | converging | const | const | mass flow drops | shock / unstart |
| friction (Fanno) | length | const | falls | mass flow drops | shock in the duct |
| heat (Rayleigh) | heating | rises | falls | mass flow drops | shock upstream of heater |

The reverse drivers (diverging area, cooling) push away from Mach 1. Friction has no reverse.
""",
        deeper=["c-choking", "c-fanno-choking", "c-thermal-choking"],
        problems=[
            problem("q-tc-1", "Match the driver",
                    r"A subsonic flow is choked in each case and you overdo it.",
                    [choice("You lengthen a pipe already at its choking length. The flow:", [opt("Lowers its inlet Mach number and mass flow", True), opt("Forms a shock", why="Subsonic flows adjust upstream instead.")]),
                     choice("Which driver can take a flow *through* Mach 1 in a constant-area duct, in principle?", [opt("Heating then cooling", True), opt("Friction", why="Friction always drives toward Mach 1 and has no reverse."),
                                                                                                                   opt("Neither", why="Heating to Mach 1 then cooling would continue to supersonic, in theory.")]),
                     choice("Supersonic inflow, too much heat. Where does the shock go?", [opt("Upstream of the heated section", True), opt("Inside the heated duct", why="A shock doesn't change T0*, so the subsonic flow behind it would still choke; only a lower inlet Mach number helps."),
                                                                                       opt("Nowhere: the flow just slows", why="Supersonic flow can't adjust smoothly to downstream news.")])]),
        ]),
    concept(
        "q-what-survives", "Which reference states survive a shock, friction or heating?", 2, Q,
        r"""
The reference-state method works only if you know which references stay constant:

| process | $T_0$ | $p_0$ | $A^*$ | sonic reference |
|---|---|---|---|---|
| isentropic area change | const | const | const | $p^*$, $T^*$ const |
| normal shock | const | falls | grows ($\times p_{0x}/p_{0y}$) | Fanno $p^*$ unchanged in a duct |
| friction | const | falls | grows | $L^*$ shrinks along the duct |
| heating | rises | falls | — | $T_0^*$ const for given inflow |
""",
        deeper=["c-shock-in-nozzle", "c-fanno-relations", "c-rayleigh-relations"],
        problems=[
            problem("q-ws-1", "Sort them",
                    r"Mark what stays constant.",
                    [choice("Across a normal shock, which is constant?", [opt("$T_0$ only", True), opt("$T_0$ and $p_0$", why="p0 falls across every real shock."), opt("$A^*$", why="A* grows by p0x/p0y.")]),
                     choice("In Rayleigh heating, which is constant along the duct?", [opt("$T_0^*$, the sonic stagnation temperature for this inflow", True), opt("$T_0$", why="Heat raises T0 directly: q = cp ΔT0.")]),
                     num("A shock with $p_{0y}/p_{0x} = 0.72$: by what factor does $A^*$ grow?", 1 / 0.72, tol=0.002)]),
        ]),
    concept(
        "q-frames", "Reference frames: static stays, stagnation and Mach number change", 2, Q,
        r"""
Three places the frame decides the answer: the speed of sound (ride the wave), moving shocks (ride the shock), and stagnation properties (whose "rest"?). Static $p$, $T$, $\rho$ are frame-independent; velocity, Mach number and stagnation properties are not. Behind a moving shock the gas can even be supersonic in the lab while subsonic relative to the shock.
""",
        deeper=["c-moving-shocks", "c-stagnation", "c-sound-derivation"],
        problems=[
            problem("q-fr-1", "Same gas, three observers",
                    r"Gas behind a Mach 3 shock moving into still air at 300 K.",
                    [choice("Is the gas behind the shock subsonic or supersonic?", [opt("Subsonic relative to the shock, supersonic relative to the lab", True), opt("Subsonic in every frame", why="The 'downstream is subsonic' rule is for the shock's frame only.")]),
                     choice("Its static temperature (804 K) in the lab frame versus the shock frame:", [opt("The same", True), opt("Higher in the lab frame", why="Static temperature doesn't depend on the observer.")]),
                     choice("Its stagnation temperature:", [opt("Depends on the frame", True), opt("Is the same in both frames", why="T0 includes V²/2cp, and V depends on the frame.")])]),
        ]),
    concept(
        "q-whole-nozzle", "The whole nozzle story, from no flow to underexpanded", 2, Q,
        r"""
Lower the back pressure on a converging–diverging nozzle step by step and you meet every tool of the course: subsonic Venturi flow, choking at $p_3$, a normal shock walking down the diverging section, the shock at the exit at $p_4$, oblique shocks outside, design at $p_d$, and expansion fans below it. Mass flow rises until $p_3$ and then never again.
""",
        deeper=["c-back-pressure-regimes", "c-over-under-expanded"],
        widget={"type": "nozzle"},
        problems=[
            problem("q-wn-1", "Put the regimes in order",
                    r"$A_e/A_t = 2$; back pressure decreasing from $p_0$.",
                    [order("Order the regimes as $p_b$ falls:",
                           ["Subsonic everywhere, mass flow rising", "Sonic throat, subsonic exit ($p_3$)", "Normal shock in the diverging section",
                            "Normal shock at the exit plane ($p_4$)", "Oblique shocks outside (overexpanded)", "Design ($p_d$)", "Expansion fans outside (underexpanded)"]),
                     num("$p_3/p_0$ for this nozzle?", _n["p3"], tol=0.003), num("$p_4/p_0$?", _n["p4"], tol=0.003), num("$p_d/p_0$?", _n["pd"], tol=0.003),
                     choice("Which regime is $p_b/p_0 = 0.5$?", [opt("Overexpanded: oblique shocks outside", True),
                                                               opt("Normal shock in the diverging section", why="That needs p_b above p4 = 0.513 p0."),
                                                               opt("Underexpanded", why="That needs p_b < pd.")])]),
        ]),
    concept(
        "q-p0-entropy", "Stagnation-pressure loss is entropy you can measure", 2, Q,
        r"""
For an adiabatic process, $\Delta s/R = -\ln(p_{02}/p_{01})$. Shocks, friction and (in a sense) heating all lower $p_0$; a pitot probe measures it. That's why inlet designers chase "pressure recovery", why oblique-shock inlets beat a single normal shock, and why a supersonic tunnel needs a compressor at all.
""",
        deeper=["c-shock-entropy", "c-pitot", "c-supersonic-inlet"],
        problems=[
            problem("q-pe-1", "One strong or two weak?",
                    r"Decelerate Mach 3 air to subsonic.",
                    [num("Stagnation-pressure recovery through a single normal shock at Mach 3?", gas.ns_p02p01(3.0), tol=0.003),
                     num("Through a 10° oblique shock, then a normal shock at the new Mach number?", gas.ob_after(3.0, 10.0)["p02p01"] * gas.ns_p02p01(gas.ob_after(3.0, 10.0)["M2"]), tol=0.003),
                     choice("Conclusion?", [opt("Breaking the compression into weaker shocks recovers much more stagnation pressure", True), opt("They're about the same", why="Compare your two numbers.")])]),
        ]),
    concept(
        "q-information", "Can the flow hear downstream? Subsonic adjusts, supersonic gets surprised", 2, Q,
        r"""
Sound carries news at $c$ relative to the gas. In subsonic flow news travels upstream, so the flow adjusts smoothly: exit pressure matches back pressure, an over-long Fanno duct throttles the mass flow. In supersonic flow it can't, so mismatches resolve abruptly: shocks appear, inlets disgorge their shock and unstart, the steady equations change type (elliptic to hyperbolic). Choking is the boundary: once the throat is sonic, lowering the back pressure further can't be heard upstream.
""",
        deeper=["c-choking", "c-supersonic-inlet", "c-fanno-choking", "c-pde-types"],
        problems=[
            problem("q-in-1", "Who adjusts?",
                    r"Predict the response.",
                    [choice("A converging nozzle exits subsonically and the back pressure drops slightly:", [opt("Exit pressure drops to match and mass flow rises", True), opt("Nothing changes", why="Subsonic exit flow hears the back pressure and adjusts.")]),
                     choice("The same nozzle is choked and the back pressure drops further:", [opt("Mass flow stays the same; the jet expands outside the nozzle", True), opt("Mass flow rises", why="Sonic flow at the exit means the news can't travel upstream.")]),
                     choice("A started supersonic inlet slows slightly below its design Mach number:", [opt("It unstarts: a normal shock is disgorged in front", True), opt("The shock moves smoothly downstream", why="Supersonic flow ahead of the throat can't adjust; the throat is suddenly too small.")])]),
        ]),
    concept(
        "q-hysteresis", "Hysteresis twice: inlet starting and Mach reflection", 2, Q,
        r"""
Two places in the course where the same conditions allow two flows, and history picks: a supersonic inlet between its design and starting Mach numbers can be started or unstarted; an oblique shock reflection between the von Neumann and detachment criteria can be regular or Mach. In both, a quasi-steady analysis gives two valid answers and only the path decides.
""",
        deeper=["c-supersonic-inlet", "c-mach-reflection"],
        problems=[
            problem("q-hy-1", "Two answers",
                    r"Compare the two hysteresis loops.",
                    [choice("What do they have in common?", [opt("Two steady solutions exist between two critical conditions; the flow's history selects one", True),
                                                             opt("Both are caused by viscosity", why="Both appear in inviscid analysis.")]),
                     choice("An inlet at a Mach number between design and start, which was just accelerated from Mach 1.2:", [opt("Unstarted", True), opt("Started", why="Coming from below, it hasn't reached the starting Mach number yet.")])]),
        ]),
]
