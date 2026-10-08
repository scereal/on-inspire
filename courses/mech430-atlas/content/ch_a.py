"""Layer 1, Chapters 1-4: conservation laws for a control volume, 1-D steady flow, speed of sound, Mach number."""
import math
import sympy as sp
from lib import *
import gas

C2, C3, C4 = "Ch. 1–2 · Conservation laws", "Ch. 3 · One-dimensional steady flow", "Ch. 4 · Speed of sound"
ATM = 101325.0

# PS1-style steady device, new numbers: air (MW 29, gamma 1.4) through a diffuser-like device, no work or heat.
_R29 = gas.R_of(29.0)
_cp29 = 1.4 * _R29 / 0.4
_V1, _p1, _T1, _A1, _A2, _T2 = 20.0, 10.0, 700.0, 0.04, 0.12, 520.0
_V2 = math.sqrt(_V1 ** 2 + 2 * _cp29 * (_T1 - _T2))
_p2 = _p1 * (_T2 / _T1) * (_V1 * _A1) / (_V2 * _A2)

# PS1-style engine thrust, new numbers.
_Vf = 800 / 3.6            # flight speed (m/s)
_pa, _Ta = 25e3, 273.15 - 45
_ma, _mf = 30.0, 2.5
_pe, _Ae, _Ve = 50e3, 0.25, 1600 / 3.6
_me = _ma + _mf
_rho_e = _me / (_Ve * _Ae)
_Te = _pe / (_rho_e * gas.R_of(28.0))
_F_mom = _me * _Ve - _ma * _Vf
_F_p = (_pe - _pa) * _Ae
_F = _F_mom + _F_p

# Sound speeds at 20 C for gases not used in the problem set.
_GASES = [("neon", 20.18, 5 / 3), ("krypton", 83.8, 5 / 3), ("hydrogen", 2.016, 1.41), ("methane", 16.04, 1.31)]
_c = {n: gas.sound(293.15, gm, gas.R_of(mw)) for n, mw, gm in _GASES}

# Mach cone: a jet at Mach 2.2 passes 9 km overhead.
_mu22 = gas.mach_angle(2.2)
_delay = 9000 / math.tan(math.radians(_mu22)) / (2.2 * 295.0)  # time after overhead until the cone arrives (c = 295 m/s)

CONCEPTS = [
    concept(
        "c-compressible-what", "Compressible flow: when the motion squeezes and stretches the fluid", 1, C2,
        r"""
In Fluids 1, density was a constant. Once the flow speed is comparable to the speed of sound, the motion itself compresses and expands each fluid element, like a tiny piston and cylinder. Work is done on the element by its neighbours, so the **energy equation** (the first law) joins mass and momentum, and the three must be solved together. The notes call compressible flow "the marriage between fluid dynamics and thermodynamics."

The same conservation laws hold for liquids and gases; only the equation of state differs. The course leans on gases (aerodynamics, propulsion), with surprising cousins: traffic jams and shallow-water waves obey mathematically identical equations.
""",
        deeper=["p-ideal-gas", "p-first-law"],
        math=[r"\text{mass} + \text{momentum} + \text{energy} + p = \rho R T"],
        analogy=analogy("A crowd walking slowly through a corridor keeps its spacing; a crowd running hard into a narrowing door bunches up and spreads out. Once the motion changes the spacing, you can't track the crowd without tracking how packed it is.",
                        "people choose to slow down; gas molecules don't. The 'information' that a door is ahead travels only at the speed of sound."),
        exam="If a problem mentions Mach numbers above about 0.3, density changes and Bernoulli's equation is out.",
        source="Notes, Ch. 1",
        problems=[
            problem("c-cw-1", "Which flows are compressible?",
                    r"Classify each flow.",
                    [choice("Air leaving a bicycle tyre valve (tyre at 3–4 atm, ambient 1 atm):",
                            [opt("Compressible: the flow chokes and reaches the speed of sound at the valve", True),
                             opt("Incompressible: the speeds are small", why="The notes point out this jet really does choke and go sonic.")]),
                     choice("Water in a garden hose at 5 m/s:",
                            [opt("Incompressible: 5 m/s is tiny compared with water's ~1500 m/s sound speed", True),
                             opt("Compressible: water is a fluid", why="Compressibility is about speed relative to the sound speed, not the phase.")])]),
        ]),
    concept(
        "c-control-volume", "Conservation of mass for a control volume", 1, C2,
        r"""
A system of fixed mass is awkward for a stream of air. A **control volume** (a fixed region of space, with mass free to cross its surface) is the **Eulerian** view. Bookkeeping the mass in and out over $\Delta t$ and letting $\Delta t\to0$:
$$\frac{\partial}{\partial t}\int_{CV}\rho\,dV = -\int_{CS}\rho\,\mathbf{V}\cdot d\mathbf{A}.$$
The notes take $d\mathbf{A}$ pointing **into** the volume, so the sign rule is simple: inflow counts positive automatically. The mass crossing an area element in $\Delta t$ is the mass in a slanted cylinder of base $dA$ and *height* $V_n\Delta t$ (not its side length).
""",
        deeper=["p-ideal-gas"],
        math=[r"\frac{\partial m_{cv}}{\partial t} = \sum\dot m_{in} - \sum\dot m_{out}", r"\dot m = \rho V A"],
        analogy=analogy("A room with open, screened windows during a weather front: cold dense air blowing in raises the mass in the room even though the room's volume never changes.",
                        "a room's air can also be compressed or heated in place; the equation only counts what crosses the boundary plus what's stored inside."),
        exam="State steady or unsteady first; in steady flow the storage term vanishes and inflow equals outflow.",
        source="Notes, Section 2.1",
        terms=["control volume", "steady"],
        problems=[
            problem("c-cv-1", "Mass balance",
                    r"A tank receives 3 kg/s through one pipe and loses 1.2 kg/s through another.",
                    [num("Rate of change of mass in the tank?", 1.8, "kg/s")]),
            problem("c-cv-2", "Slanted crossing",
                    r"Flow at 10 m/s crosses a 0.2 m² opening at 60° from the opening's normal, with ρ = 1.2 kg/m³.",
                    [num("Mass flow through the opening?", 1.2 * 10 * math.cos(math.radians(60)) * 0.2, "kg/s",
                         explain="Only the normal component counts: $\\dot m = \\rho V\\cos60°\\,A$.")]),
        ]),
    concept(
        "c-cv-momentum", "Momentum for a control volume: forces, momentum flux, thrust", 1, C2,
        r"""
Newton's second law for a control volume:
$$\sum\mathbf{F} = \frac{\partial}{\partial t}\int_{CV}\rho\mathbf{V}\,dV - \int_{CS}\mathbf{V}\,(\rho\mathbf{V}\cdot d\mathbf{A}).$$
"Forces equal the rate of change of momentum inside, minus the rate momentum is carried in." It's a **vector** equation: write one component at a time. Forces include pressure on the control surface (use **gauge** pressure if the atmosphere acts all round) and whatever holds the device in place.

Applied to a jet engine in its own frame (steady): air enters at the flight speed, exhaust leaves at $V_e$, and
$$F = \dot m_e V_e - \dot m_a V_\infty + (p_e - p_\infty)A_e.$$
The first two terms are momentum flux; the last is the pressure term ([[c-rocket-thrust]] does the same for rockets).
""",
        deeper=["p-momentum", "c-control-volume"],
        math=[r"\sum F_x = \dot m(V_{x,out} - V_{x,in})\ \text{(steady, one in, one out)}", r"F = \dot m_e V_e - \dot m_a V_\infty + (p_e - p_\infty)A_e"],
        analogy=analogy("A free-body diagram of a box that things fly through: every kilogram entering brings its momentum, every kilogram leaving takes its momentum away, and the walls must supply the difference.",
                        "unlike a rigid body, the 'box' can hold momentum that changes with time (unsteady flow), and pressure acts on the open faces as well as the walls."),
        exam="Draw the CV, mark every force and every momentum flux with its sign, and use gauge pressure if ambient acts everywhere else.",
        source="Notes, Section 2.2; Problem Set 1 (thrust and pipe forces)",
        problems=[
            problem("c-cvm-1", "Engine thrust, step by step",
                    rf"An engine flies at 800 km/h where $p_\infty = 25$ kPa, $T_\infty = -45$°C. It swallows 30 kg/s of air and adds 2.5 kg/s of fuel (injected at negligible velocity). At the exit, $p_e = 50$ kPa, $A_e = 0.25$ m², and the exhaust leaves at 1600 km/h relative to the engine. (Same skills as Problem Set 1, new numbers.)",
                    [num(r"Exhaust density $\rho_e = \dot m_e/(V_eA_e)$?", _rho_e, "kg/m³"),
                     num("Exhaust temperature, taking MW = 28 for the products?", _Te - 273.15, "°C", explain="$T_e = p_e/(\\rho_e R)$, then subtract 273.15."),
                     num("Momentum-flux part of the thrust, $\\dot m_eV_e - \\dot m_aV_\\infty$?", _F_mom / 1000, "kN"),
                     num("Pressure part, $(p_e - p_\\infty)A_e$?", _F_p / 1000, "kN"),
                     choice("Which dominates?", [opt("The momentum flux" if _F_mom > _F_p else "The pressure term", True),
                                                  opt("The pressure term" if _F_mom > _F_p else "The momentum flux", why="Compare the two numbers you just found.")])],
                    kind="variant"),
            problem("c-cvm-2", "Sign of the inflow term",
                    r"For the engine above, a student writes $F = \dot m_eV_e + \dot m_aV_\infty + (p_e - p_\infty)A_e$.",
                    [spot("Which piece is wrong?",
                          [("$\\dot m_eV_e$: momentum leaving with the exhaust", False, ""),
                           ("$+\\dot m_aV_\\infty$: momentum of the incoming air", True, "Incoming momentum is subtracted: the engine only gets credit for the momentum it *adds* to the air."),
                           ("$(p_e - p_\\infty)A_e$: pressure difference over the exit plane", False, "")])]),
        ]),
    concept(
        "c-cv-energy", "Energy for a control volume: h + V²/2 is what flows", 1, C2,
        r"""
The first law for a control volume, after splitting work into shaft work and **flow work** $p/\rho$ (the work of pushing mass across the boundary):
$$\frac{dE_{cv}}{dt} = \dot W_{cv} + \dot Q + \sum\dot m_{in}\left(h + \tfrac{V^2}{2}\right)_{in} - \sum\dot m_{out}\left(h + \tfrac{V^2}{2}\right)_{out}.$$
Steady, one inlet and one outlet, per unit mass: $q + w = \left(h_2 + \tfrac{V_2^2}{2}\right) - \left(h_1 + \tfrac{V_1^2}{2}\right)$. No friction assumption was needed: this holds through shocks and through viscous flow. With $h = c_pT$, kinetic energy and temperature trade directly.
""",
        deeper=["p-first-law", "c-control-volume"],
        math=[r"h_1 + \tfrac{V_1^2}{2} + q + w = h_2 + \tfrac{V_2^2}{2}"],
        analogy=analogy("A bank account in two currencies, thermal (c_pT) and kinetic (V²/2), with a fixed exchange rate: an adiabatic flow can convert between them but can't change the total.",
                        "the exchange is free in the energy equation, but the second law decides which conversions happen without losses (that's what stagnation pressure tracks)."),
        exam="The energy equation needs no inviscid assumption. Use it freely across shocks and friction.",
        source="Notes, Section 2.3; Problem Set 1, Problem 2 skills",
        problems=[
            problem("c-cve-1", "A steady-flow device (new numbers)",
                    rf"Air (MW 29, γ = 1.4) enters a device at {_V1:g} m/s, {_p1:g} atm, {_T1:g} K through {_A1} m². It leaves through {_A2} m² at {_T2:g} K. No work, no heat transfer.",
                    [num("$c_p$ for this air?", _cp29, "J/(kg·K)"),
                     num("Exit velocity, from the energy equation?", _V2, "m/s", explain="$V_2 = \\sqrt{V_1^2 + 2c_p(T_1 - T_2)}$."),
                     num("Exit pressure, from continuity with $\\rho = p/RT$?", _p2, "atm",
                         explain="$p_2 = p_1\\,\\dfrac{T_2}{T_1}\\,\\dfrac{V_1A_1}{V_2A_2}$.")],
                    kind="variant"),
            problem("c-cve-2", "Where did the energy go?",
                    r"In the device above the temperature fell by 180 K with no heat or work.",
                    [choice("What happened to that energy?", [opt("It became kinetic energy: the flow sped up", True),
                                                              opt("It was lost to friction", why="Friction converts kinetic energy back to thermal; it can't make total enthalpy disappear."),
                                                              opt("It went into flow work", why="Flow work is already inside h.")])]),
        ]),
    concept(
        "c-1d-terms", "The vocabulary: steady, uniform, one-dimensional, streamline, stream tube", 1, C3,
        r"""
Precise words prevent most mistakes in this course:
- **Steady**: nothing changes in time at a fixed point.
- **Uniform**: nothing changes in space (here, across a cross-section).
- **One-dimensional**: properties vary along one coordinate only and are uniform across each section. Good for slow area changes and turbulent profiles.
- **Inviscid**: no viscous stresses. **Compressible**: density changes matter.
- **Streamline**: a line everywhere tangent to the velocity. In steady flow, particles follow streamlines.
- **Stream tube**: a tube whose walls are streamlines, so no mass crosses the walls. An infinitesimally thin stream tube is exactly one-dimensional.

The notes ask you not to say a flow "is constant": say *steady* or *uniform*.
""",
        deeper=["c-control-volume"],
        math=[],
        source="Notes, Ch. 3; Problem Sets 1–2, Problem 1 (terminology)",
        terms=["steady", "uniform", "one-dimensional", "streamline", "stream tube", "inviscid"],
        problems=[
            problem("c-1t-1", "Steady or uniform?",
                    r"Classify each statement.",
                    [choice("Flow out of a garden hose held still, with the tap fixed:", [opt("Steady", True), opt("Uniform", why="The jet's velocity varies across the section (it's slower near the edges).")]),
                     choice("Air in a sealed room after the fan is switched off, at one instant:", [opt("Neither steady nor necessarily uniform: the air is still coming to rest", True),
                                                                                                 opt("Steady, because the fan is off", why="Steady means unchanging in time; decaying motion is unsteady.")]),
                     blank("A tube whose walls are made of streamlines is called a ____.", ["stream tube", "streamtube"], placeholder="two words")]),
        ]),
    concept(
        "c-1d-integral", "The steady 1-D toolbox in integral form", 1, C3,
        r"""
For a steady stream tube from station 1 to 2:
$$\rho_1V_1A_1 = \rho_2V_2A_2$$
$$F_{x,\text{wall}} + p_1A_1 - p_2A_2 = \dot m(V_2 - V_1)$$
$$h_1 + \tfrac{V_1^2}{2} + q = h_2 + \tfrac{V_2^2}{2}$$
For constant area and no wall force, momentum becomes $p_1 + \rho_1V_1^2 = p_2 + \rho_2V_2^2$. **This is not Bernoulli**: it's exact even across a shock. Integral (control-volume) forms are valid across discontinuities; differential forms are not ([[c-1d-differential]]).
""",
        deeper=["c-cv-momentum", "c-cv-energy", "c-1d-terms"],
        math=[r"\rho VA = \text{const}", r"p + \rho V^2 = \text{const (constant } A\text{, no wall force)}", r"h + \tfrac{V^2}{2} = h_0"],
        exam="Across a shock, use these integral forms, never the differential ones.",
        source="Notes, Sections 3.1–3.3",
        problems=[
            problem("c-1i-1", "Which equation is valid?",
                    r"Across a normal shock in a constant-area duct.",
                    [choice("Which momentum statement holds?", [opt("$p_1 + \\rho_1V_1^2 = p_2 + \\rho_2V_2^2$", True),
                                                               opt("$p_1 + \\tfrac12\\rho_1V_1^2 = p_2 + \\tfrac12\\rho_2V_2^2$", why="That's Bernoulli: it assumes isentropic incompressible flow, false across a shock."),
                                                               opt("$dp + \\rho V\\,dV = 0$", why="Differentials don't exist at a discontinuity.")])]),
        ]),
    concept(
        "c-1d-differential", "The differential forms: dρ/ρ + dV/V + dA/A = 0, dp + ρV dV = 0, dh + V dV = dq", 1, C3,
        r"""
Logarithmic differentiation of $\rho VA = $ const, and a thin slice of stream tube for momentum (inviscid) and energy, give
$$\frac{d\rho}{\rho} + \frac{dV}{V} + \frac{dA}{A} = 0,\qquad dp + \rho V\,dV = 0,\qquad dh + V\,dV = dq.$$
These answer "which way does each property go?" for area change, friction and heating ([[c-area-velocity]], [[c-fanno-effects]], [[c-rayleigh-effects]]). The momentum form says **pressure and velocity always change in opposite directions** in inviscid flow. They apply only where properties are smooth.
""",
        deeper=["c-1d-integral", "p-log-differentiation"],
        math=[r"\frac{d\rho}{\rho} + \frac{dV}{V} + \frac{dA}{A} = 0", r"dp + \rho V\,dV = 0"],
        source="Notes, Sections 3.1–3.3",
        problems=[
            problem("c-1d-1", "Read a sign",
                    r"Inviscid flow speeds up: $dV > 0$.",
                    [choice("Then the pressure:", [opt("Falls", True), opt("Rises", why="dp = −ρV dV: opposite signs, always, for inviscid flow."),
                                                   opt("It depends on whether the flow is supersonic", why="This relation has no Mach number in it; the Mach number decides how *area* relates to dV.")])]),
            problem("c-1d-2", "Derive the slice",
                    r"Put the steps for the inviscid momentum slice in order.",
                    [order("Order the derivation of $dp + \\rho V\\,dV = 0$:",
                           ["Draw a slice from $(p, V, A)$ to $(p+dp, V+dV, A+dA)$",
                            "Take the side-wall pressure as the average $p + dp/2$, acting on the projected area $dA$",
                            "Write net force $= \\dot m\\,dV$",
                            "Expand and drop products of differentials such as $dp\\,dA$",
                            "Divide by $A$ and use $\\dot m = \\rho VA$"])]),
        ]),
    concept(
        "c-sound-derivation", "The speed of sound from a control volume around the wave", 1, C4,
        r"""
A wall nudged at $dV$ sends a weak wave into still gas. The wave moves at $c$, so the flow is unsteady. **Ride along with the wave** ([[p-galilean]]): now gas approaches at $c$ and leaves at $c - dV$, and the picture is steady. Continuity and momentum on a thin control volume give
$$c\,d\rho = \rho\,dV,\qquad dp = \rho c\,dV\ \Rightarrow\ c^2 = \frac{dp}{d\rho}.$$
Since $\rho$, $c$, $dV$ are positive, a wave that pushes gas along ($dV$ in the direction of travel) **raises** density and pressure: a compression. Pull the wall back and the same algebra gives a rarefaction travelling at the same speed, with the gas set moving *opposite* to the wave.

The wave is weak, fast and of long wavelength, so it's adiabatic and reversible: **isentropic**. Hence $c^2 = (\partial p/\partial\rho)_s$. Newton (1687) assumed isothermal and got 15–20% too low; Laplace (1816) fixed it.
""",
        deeper=["p-galilean", "c-1d-integral", "p-entropy-isentropic"],
        math=[r"c^2 = \left(\frac{\partial p}{\partial \rho}\right)_s"],
        widget={"type": "soundframe"},
        analogy=analogy("A line of commuters on a moving walkway: from the station floor the bunching travels forward; step onto a platform moving with the bunching and you see commuters flowing steadily through it.",
                        "people don't push back on each other like pressure does; the analogy shows the frame change, not why the bunching moves at exactly c."),
        exam="Draw the wave-fixed control volume first: approach at c, leave at c − dV. Then continuity and momentum in two lines each.",
        source="Notes, Section 4.1; Problem Set 1, Problem 5 skills",
        problems=[
            problem("c-sd-1", "Which way does the gas move?",
                    r"A compression wave ($dp > 0$) travels to the **left** into still gas.",
                    [choice("The gas behind it moves:", [opt("To the left, in the direction the wave travels", True),
                                                        opt("To the right", why="That's a rarefaction moving left. A compression pushes gas along with it."),
                                                        opt("Not at all", why="dp = ρc dV: a pressure jump needs a velocity jump.")]),
                     choice("A rarefaction ($dp < 0$) travelling left sets the gas moving:", [opt("To the right", True), opt("To the left", why="Flip the sign of dp and dV flips too.")]),
                     choice("Do compression and rarefaction waves of infinitesimal strength travel at different speeds?",
                            [opt("No: both travel at $c = \\sqrt{(\\partial p/\\partial\\rho)_s}$", True),
                             opt("Yes, compressions are faster", why="For infinitesimal waves the speed is the same; only finite trains of compressions steepen (that's how shocks form).")])]),
            problem("c-sd-2", "The two equations",
                    r"In the wave frame, gas enters at speed $c$ with density $\rho$ and leaves at $c - dV$ with $\rho + d\rho$.",
                    [expr(r"Continuity gives $d\rho$ in terms of `rho`, `dV`, `c` (drop second-order terms). Type $d\rho$.", rho * dV / c, ["rho", "dV", "c"],
                          ranges={"rho": [0.5, 2], "dV": [0.1, 1], "c": [200, 400]}),
                     expr(r"Momentum ($p + \rho V^2$ conserved) gives $dp$. Type it.", rho * c * dV, ["rho", "dV", "c"], ranges={"rho": [0.5, 2], "dV": [0.1, 1], "c": [200, 400]})]),
        ]),
    concept(
        "c-sound-ideal-gas", "For an ideal gas, c = √(γRT): temperature alone sets the speed", 1, C4,
        r"""
With $p/\rho^\gamma$ constant along the isentrope, $c^2 = \gamma p/\rho = \gamma RT$:
$$c = \sqrt{\gamma R T}.$$
At fixed temperature, squeezing the gas doesn't change $c$: molecules collide more often but move at the same speed, and sound is carried by molecular motion. Light gases are fast (helium ~1000 m/s at room temperature), heavy ones slow (SF₆ ~135 m/s), which is why helium raises the pitch of your voice. For liquids and solids, $c = 1/\sqrt{\rho K_s}$ with $K_s$ the isentropic compressibility: stiff materials carry sound fast.
""",
        deeper=["c-sound-derivation", "p-ideal-gas", "p-python"],
        math=[r"c = \sqrt{\gamma R T}"],
        exam="Air at room temperature: about 343–347 m/s. Use it to sanity-check every answer.",
        source="Notes, Section 4.1; Problem Set 1, Problems 6–7 skills",
        problems=[
            problem("c-sg-1", "Sound speeds of other gases (20 °C)",
                    r"Use $c = \sqrt{\gamma R_uT/\mathrm{MW}}$, $T = 293.15$ K. (Problem Set 1 asks the same for five different gases.)",
                    [num("Neon (MW 20.18, γ = 5/3)?", _c["neon"], "m/s"),
                     num("Krypton (MW 83.8, γ = 5/3)?", _c["krypton"], "m/s"),
                     num("Hydrogen (MW 2.016, γ = 1.41)?", _c["hydrogen"], "m/s"),
                     choice("Breathing which one would lower the pitch of your voice?", [opt("Krypton", True), opt("Hydrogen", why="Hydrogen is the fastest of the three: it raises pitch, like helium."),
                                                                                       opt("Neon", why="Neon is faster than air (about 450 m/s), so it raises pitch.")])],
                    kind="variant"),
            problem("c-sg-2", "Same Mach, different speed",
                    r"Aircraft A reaches Mach 1 at 11 km where $T = 216.65$ K; car B reaches Mach 1 at sea level where $T = 303$ K. Air: $R = 287$, γ = 1.4.",
                    [num("Speed of A?", gas.sound(216.65), "m/s"), num("Speed of B?", gas.sound(303.0), "m/s"),
                     choice("Who was faster in m/s?", [opt("B, because the air was warmer", True), opt("A, because it was higher", why="Altitude matters only through temperature; colder air means slower sound.")])],
                    kind="variant"),
            problem("c-sg-3", "Code it for any gas",
                    r"Write a function you'll reuse.",
                    [code("`sound_speed_gas(T, MW, gamma)` returns $c$ in m/s from the molecular weight (use $R_u = 8314$).",
                          starter="import math\n\nRU = 8314.0\n\ndef sound_speed_gas(T, MW, gamma):\n    pass\n",
                          solution="import math\n\nRU = 8314.0\n\ndef sound_speed_gas(T, MW, gamma):\n    return math.sqrt(gamma * RU / MW * T)\n",
                          tests=f"check('neon', sound_speed_gas(293.15, 20.18, 5/3), {_c['neon']:.6f}, 1e-6)\ncheck('krypton', sound_speed_gas(293.15, 83.8, 5/3), {_c['krypton']:.6f}, 1e-6)\n",
                          wrong=["import math\n\nRU = 8314.0\n\ndef sound_speed_gas(T, MW, gamma):\n    return math.sqrt(gamma * RU * MW * T)\n",
                                 "import math\n\nRU = 8.314\n\ndef sound_speed_gas(T, MW, gamma):\n    return math.sqrt(gamma * RU / MW * T)\n"],
                          hints=["R = RU / MW, in J/(kg·K).", "RU is 8314 J/(kmol·K) when MW is in kg/kmol."], fn="sound_speed_gas")]),
        ]),
    concept(
        "c-mach-number", "The Mach number is local, and it belongs to a reference frame", 1, C4,
        r"""
$$M = \frac{V}{c},$$
with $V$ and $c$ taken **at the same point**. "The Concorde flies at Mach 2" really means: in the aircraft's frame, the air approaches at twice *its own* local sound speed. Mach number is the single most important parameter in compressible flow: subsonic ($M<1$) and supersonic ($M>1$) flows respond to everything (area change, friction, heat) in opposite ways.
""",
        deeper=["c-sound-ideal-gas"],
        math=[r"M = V/c"],
        source="Notes, Section 4.2; Problem Set 2, Problem 1",
        terms=["Mach number"],
        problems=[
            problem("c-mn-1", "Local means local",
                    r"Air leaves a nozzle at 600 m/s with static temperature 200 K. The reservoir was at 380 K.",
                    [num("Mach number at the exit?", 600 / gas.sound(200), explain="Use the local temperature, 200 K, not the reservoir's."),
                     choice("A student uses $c$ at 380 K instead. Their Mach number is:", [opt("Too small", True), opt("Too large", why="A hotter temperature gives a larger c, so V/c is smaller.")])]),
        ]),
    concept(
        "c-mach-cone", "Waves from a moving source: the Mach cone and the zone of silence", 1, C4,
        r"""
A source beeping every $\tau$ while moving at $V$: each beep spreads as a sphere of radius $ct$ centred where it was emitted. Below Mach 1 the spheres nest (crowded ahead: the Doppler shift). At Mach 1 they pile up into a plane front. Above Mach 1 they're confined to a cone of half-angle
$$\mu = \sin^{-1}\frac{1}{M},$$
the **Mach angle**. Outside the cone is the **zone of silence**. A meteor at Mach 100 has a needle-thin cone: you see it long before you could ever hear it. A real supersonic body drives a **shock**, stronger than sound, which decays to a Mach wave far away.
""",
        deeper=["c-mach-number"],
        math=[r"\sin\mu = \frac{1}{M}"],
        widget={"type": "machcone"},
        analogy=analogy("Stones dropped every second from a boat: on a still pond the rings overlap ahead of a fast boat and form a V.",
                        "a ship's bow wave stays near 19.5° whatever its speed (Kelvin's wake, because water waves are dispersive); a Mach cone narrows as speed grows."),
        exam="μ = sin⁻¹(1/M) needs M > 1. For M ≤ 1 there is no cone.",
        source="Notes, Section 4.3",
        problems=[
            problem("c-mc-1", "The cone",
                    r"A jet flies level at Mach 2.2, 9 km above you. Take $c = 295$ m/s at its altitude and treat the cone as straight.",
                    [num("Mach angle?", _mu22, "°"),
                     num("How many seconds after it passes directly overhead do you hear it?", _delay, "s",
                         explain="The cone trails the jet by a horizontal distance $h/\\tan\\mu$; divide by the jet's speed."),
                     dial("Set the Mach number that gives a 30° Mach angle.", "mach_angle", 30.0, 1.05, 4.0, 0.001, 2.0, var="M", tol=0.002)]),
        ]),
]
