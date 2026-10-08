"""Reference compressible-flow relations for a calorically perfect gas (pure Python, no dependencies).

Every answer in the atlas is computed from these functions, and the module checks itself on import
against the worked numerical examples in the MECH 430 notes (Higgins). If a relation is wrong, the
build fails before anything is published. src/gas.js mirrors these functions for the widgets; the
browser test compares the two at hundreds of points.
"""
import math

RU = 8314.0          # universal gas constant [J/(kmol K)], as used in the notes
G = 1.4


def R_of(MW):
    return RU / MW


def sound(T, g=G, R=287.0):
    return math.sqrt(g * R * T)


def mach_angle(M):
    return math.degrees(math.asin(1 / M))


# ---- isentropic ----------------------------------------------------------------------------
def T0_T(M, g=G):
    return 1 + (g - 1) / 2 * M * M


def p0_p(M, g=G):
    return T0_T(M, g) ** (g / (g - 1))


def r0_r(M, g=G):
    return T0_T(M, g) ** (1 / (g - 1))


def A_Astar(M, g=G):
    return (1 / M) * ((2 / (g + 1)) * T0_T(M, g)) ** ((g + 1) / (2 * (g - 1)))


def mass_flux(M, g=G):
    """mdot sqrt(R T0) / (A p0): the dimensionless mass flow per unit area."""
    return math.sqrt(g) * M * T0_T(M, g) ** (-(g + 1) / (2 * (g - 1)))


def bisect(f, a, b, tol=1e-12, n=300):
    fa, fb = f(a), f(b)
    assert fa * fb <= 0, (a, b, fa, fb)
    for _ in range(n):
        m = 0.5 * (a + b)
        fm = f(m)
        if fa * fm <= 0:
            b, fb = m, fm
        else:
            a, fa = m, fm
        if b - a < tol:
            break
    return 0.5 * (a + b)


def M_from_AR(ar, supersonic, g=G):
    if abs(ar - 1) < 1e-12:
        return 1.0
    if supersonic:
        return bisect(lambda M: A_Astar(M, g) - ar, 1.0, 100.0)
    return bisect(lambda M: A_Astar(M, g) - ar, 1e-9, 1.0)


def M_from_p0p(r, g=G):
    return math.sqrt(2 / (g - 1) * (r ** ((g - 1) / g) - 1))


def M_from_T0T(r, g=G):
    return math.sqrt(2 / (g - 1) * (r - 1))


# ---- normal shock --------------------------------------------------------------------------
def ns_M2(M1, g=G):
    return math.sqrt((1 + (g - 1) / 2 * M1 * M1) / (g * M1 * M1 - (g - 1) / 2))


def ns_p2p1(M1, g=G):
    return 1 + 2 * g / (g + 1) * (M1 * M1 - 1)


def ns_r2r1(M1, g=G):
    return (g + 1) * M1 * M1 / ((g - 1) * M1 * M1 + 2)


def ns_T2T1(M1, g=G):
    return ns_p2p1(M1, g) / ns_r2r1(M1, g)


def ns_p02p01(M1, g=G):
    M2 = ns_M2(M1, g)
    return ns_p2p1(M1, g) * p0_p(M2, g) / p0_p(M1, g)


def ns_ds_R(M1, g=G):
    """Entropy rise across the shock divided by R."""
    return -math.log(ns_p02p01(M1, g))


def ns_M1_from_p02p01(r, g=G):
    return bisect(lambda M: ns_p02p01(M, g) - r, 1.0, 50.0)


def pitot_ratio(M1, g=G):
    """p02/p1 for a pitot tube in supersonic flow (Rayleigh pitot formula)."""
    return ns_p02p01(M1, g) * p0_p(M1, g)


def piston_shock_mach(vp_over_c, g=G):
    """Shock Mach number driven into quiescent gas by a piston moving at vp (relative to the gas ahead)."""
    a = (g + 1) / 4 * vp_over_c
    return a + math.sqrt(a * a + 1)


def piston_speed(Ms, g=G):
    """Particle velocity behind a shock of Mach Ms, divided by the sound speed ahead."""
    return 2 / (g + 1) * (Ms - 1 / Ms)


# ---- Fanno (adiabatic, frictional, constant area) ----------------------------------------------
def fanno_fL(M, g=G):
    """4 f L*/D, with f the Fanning friction factor used in the notes."""
    return (1 - M * M) / (g * M * M) + (g + 1) / (2 * g) * math.log((g + 1) * M * M / (2 + (g - 1) * M * M))


def fanno_T(M, g=G):
    return (g + 1) / (2 + (g - 1) * M * M)


def fanno_p(M, g=G):
    return (1 / M) * math.sqrt(fanno_T(M, g))


def fanno_p0(M, g=G):
    return (1 / M) * ((2 + (g - 1) * M * M) / (g + 1)) ** ((g + 1) / (2 * (g - 1)))


def fanno_V(M, g=G):
    return M * math.sqrt(fanno_T(M, g))


def fanno_M(fl, supersonic, g=G):
    if supersonic:
        return bisect(lambda M: fanno_fL(M, g) - fl, 1.0, 1e4)
    return bisect(lambda M: fanno_fL(M, g) - fl, 1e-6, 1.0)


# ---- Rayleigh (frictionless, heat transfer, constant area) -------------------------------------
def ray_p(M, g=G):
    return (1 + g) / (1 + g * M * M)


def ray_T(M, g=G):
    return (M * ray_p(M, g)) ** 2


def ray_T0(M, g=G):
    return 2 * (g + 1) * M * M / (1 + g * M * M) ** 2 * (1 + (g - 1) / 2 * M * M)


def ray_p0(M, g=G):
    return ray_p(M, g) * ((2 + (g - 1) * M * M) / (g + 1)) ** (g / (g - 1))


def ray_M(t0, supersonic, g=G):
    if supersonic:
        return bisect(lambda M: ray_T0(M, g) - t0, 1.0, 1e4)
    return bisect(lambda M: ray_T0(M, g) - t0, 1e-9, 1.0)


# ---- oblique shocks and Prandtl-Meyer -----------------------------------------------------------
def ob_delta(M, sigma_deg, g=G):
    s = math.radians(sigma_deg)
    num = 2 / math.tan(s) * (M * M * math.sin(s) ** 2 - 1)
    den = M * M * (g + math.cos(2 * s)) + 2
    return math.degrees(math.atan(num / den))


def ob_max(M, g=G):
    """(delta_max, sigma at delta_max) by golden-section search."""
    lo, hi = mach_angle(M), 90.0
    phi = (math.sqrt(5) - 1) / 2
    a, b = lo, hi
    for _ in range(200):
        c, d = b - phi * (b - a), a + phi * (b - a)
        if ob_delta(M, c, g) > ob_delta(M, d, g):
            b = d
        else:
            a = c
    s = 0.5 * (a + b)
    return ob_delta(M, s, g), s


def ob_sigma(M, delta_deg, strong=False, g=G):
    dmax, smax = ob_max(M, g)
    assert delta_deg <= dmax + 1e-9, "detached: delta exceeds delta_max"
    if strong:
        return bisect(lambda s: ob_delta(M, s, g) - delta_deg, smax, 90.0)
    return bisect(lambda s: ob_delta(M, s, g) - delta_deg, mach_angle(M) + 1e-12, smax)


def ob_after(M, delta_deg, strong=False, g=G):
    s = ob_sigma(M, delta_deg, strong, g)
    Mn1 = M * math.sin(math.radians(s))
    Mn2 = ns_M2(Mn1, g)
    M2 = Mn2 / math.sin(math.radians(s - delta_deg))
    return {"sigma": s, "Mn1": Mn1, "M2": M2, "p2p1": ns_p2p1(Mn1, g), "T2T1": ns_T2T1(Mn1, g), "p02p01": ns_p02p01(Mn1, g)}


def pm_nu(M, g=G):
    k = math.sqrt((g + 1) / (g - 1))
    return math.degrees(k * math.atan(math.sqrt((M * M - 1) / (k * k))) - math.atan(math.sqrt(M * M - 1)))


def pm_M(nu_deg, g=G):
    return bisect(lambda M: pm_nu(M, g) - nu_deg, 1.0, 1e4)


def nu_max(g=G):
    return 90 * (math.sqrt((g + 1) / (g - 1)) - 1)


# ---- rockets ----------------------------------------------------------------------------------
def exit_velocity(T0, pe_p0, g=G, R=287.0):
    return math.sqrt(2 * g / (g - 1) * R * T0 * (1 - pe_p0 ** ((g - 1) / g)))


def v_max(T0, g=G, R=287.0):
    return math.sqrt(2 * g / (g - 1) * R * T0)


def thrust_per_mdot(T0, p0, pe, pamb, Ae_over_mdot, g=G, R=287.0):
    return exit_velocity(T0, pe / p0, g, R) + Ae_over_mdot * (pe - pamb)


def mdot_choked(p0, T0, At, g=G, R=287.0):
    return At * p0 / math.sqrt(R * T0) * mass_flux(1.0, g)


# ---- converging-diverging nozzle with variable back pressure ---------------------------------------
def nozzle(AeAt, pb_p0, g=G):
    """Solve the quasi-1D nozzle for a back pressure. Returns a dict with the regime and key numbers.

    Regimes: 'subsonic' (not choked), 'shock' (normal shock inside, at area As/At), 'overexpanded'
    (oblique shocks outside), 'design', 'underexpanded'. p3/p4/pd are the critical back pressures.
    """
    Msub = M_from_AR(AeAt, False, g)
    Msup = M_from_AR(AeAt, True, g)
    p3 = 1 / p0_p(Msub, g)
    pd = 1 / p0_p(Msup, g)
    p4 = pd * ns_p2p1(Msup, g)
    out = {"p3": p3, "p4": p4, "pd": pd, "Me_sub": Msub, "Me_sup": Msup}
    if pb_p0 >= p3:
        Me = M_from_p0p(1 / pb_p0, g) if pb_p0 < 1 else 0.0
        out.update(regime="subsonic", Me=Me, pe=pb_p0, mdot=mass_flux(Me, g) * AeAt / mass_flux(1.0, g) if Me > 0 else 0.0)
        return out
    out["mdot"] = 1.0
    if pb_p0 > p4 + 1e-15:
        def pe_for(As):
            M1 = M_from_AR(As, True, g)
            p0r = ns_p02p01(M1, g)
            Me = M_from_AR(AeAt * p0r, False, g)  # A*_2 = At / p0r, so Ae/A*_2 = (Ae/At) p0r
            return p0r / p0_p(Me, g), Me, M1, p0r
        As = bisect(lambda a: pe_for(a)[0] - pb_p0, 1.0 + 1e-9, AeAt)
        pe, Me, M1, p0r = pe_for(As)
        out.update(regime="shock", As=As, Ms=M1, Me=Me, pe=pe, p0r=p0r)
    elif pb_p0 > pd * (1 + 1e-9):
        out.update(regime="overexpanded", Me=Msup, pe=pd)
    elif pb_p0 >= pd * (1 - 1e-9):
        out.update(regime="design", Me=Msup, pe=pd)
    else:
        out.update(regime="underexpanded", Me=Msup, pe=pd)
    return out


# ---- supersonic inlet (Kantrowitz) -------------------------------------------------------------
def inlet_start_ratio(M, g=G):
    """Throat-to-inlet area that just swallows the normal shock at flight Mach M."""
    return 1 / A_Astar(ns_M2(M, g), g) * 1  # A_t/A_i = A*_y/A_i = (A*_y/A_y)(A_y/A_i), A_y = A_i


def inlet_isentropic_ratio(M, g=G):
    return 1 / A_Astar(M, g)


# ---- method of characteristics -------------------------------------------------------------------
def moc_interior(CI, CII, g=G):
    nu = (CI + CII) / 2
    theta = (CI - CII) / 2
    return nu, theta, pm_M(nu, g)


def close(a, b, tol):
    return abs(a - b) <= tol * max(1.0, abs(b)) if tol < 1 else abs(a - b) <= tol


def _check(name, got, want, rtol):
    assert abs(got - want) <= rtol * abs(want), f"{name}: got {got:.6g}, notes give {want:.6g}"


# ---- self-checks against the worked examples in the notes ------------------------------------------
# Sonic reference ratios (Section 5.3)
_check("T*/T0", 1 / T0_T(1), 0.8333, 1e-3)
_check("p*/p0", 1 / p0_p(1), 0.5283, 1e-3)
_check("rho*/rho0", 1 / r0_r(1), 0.6339, 1e-3)
# 5.2.1: reservoir 5 atm, 500 K; Mach 0.75 and Mach 2
_check("5.2.1 p at M=0.75", 5 / p0_p(0.75), 3.44, 2e-3)
_check("5.2.1 p at M=2", 5 / p0_p(2.0), 0.639, 2e-3)
_check("5.2.1 T at M=2", 500 / T0_T(2.0), 278, 2e-3)
# 5.5.1: A* = 0.746 m^2, p0 = 1 atm; M = 0.8 -> 0.656 atm; A = 1.5 m^2 -> M = 0.304 or 2.202
_check("5.5.1 p2", 1 / p0_p(0.8), 0.656, 2e-3)
_check("5.5.1 M3 sub", M_from_AR(1.5 / 0.746, False), 0.304, 3e-3)
_check("5.5.1 M3 sup", M_from_AR(1.5 / 0.746, True), 2.202, 2e-3)
_check("5.5.1 p3 sub", 1 / p0_p(M_from_AR(1.5 / 0.746, False)), 0.938, 2e-3)
_check("5.5.1 p3 sup", 1 / p0_p(M_from_AR(1.5 / 0.746, True)), 0.0932, 3e-3)
# Fliegner's formula for air: mdot = 0.0404 p0 A* / sqrt(T0)  (SI)
_check("Fliegner", mass_flux(1.0) / math.sqrt(287.0), 0.0404, 2e-3)
# 5.6: at Mach 0.3, Bernoulli underestimates p0 - p by about 2%
_q = 0.5 * G * 0.3 ** 2
_check("5.6 compressibility at M=0.3", (p0_p(0.3) - 1) / _q - 1, 0.0226, 0.02)
# 6.3.4: nuclear thermal rocket (H2 modelled with gamma = 1.4), 3000 K, 30 atm: optimal at sea level gives M_exit = 2.87
_check("6.3.4 M_exit", M_from_p0p(30.0), 2.87, 2e-3)
_check("6.3.4 M for ratio 500 (notes read 9.83 from a table)", M_from_AR(500.0, True), 9.83, 3e-3)
_check("6.3.4 p_exit at ratio 500", 30 / p0_p(M_from_AR(500.0, True)), 7.9e-4, 0.02)
# 7.2: normal shock tables at M = 2
_check("NS M2(2)", ns_M2(2.0), 0.5774, 1e-3)
_check("NS p2/p1(2)", ns_p2p1(2.0), 4.5, 1e-6)
_check("NS p02/p01(2)", ns_p02p01(2.0), 0.7209, 1e-3)
# 7.3: strong-shock limits
_check("strong M2 limit", ns_M2(1e4), math.sqrt((G - 1) / (2 * G)), 1e-6)
_check("strong density limit", ns_r2r1(1e4), (G + 1) / (G - 1), 1e-6)
# 8.1.1: shock at M = 2.20 in a nozzle fed at 1 atm: p0y = 0.628 atm
_check("8.1.1 p0y", ns_p02p01(2.20), 0.628, 2e-3)
# 8.2.1: At = 1, Ae = 3, pb = 0.7 atm -> supersonic exit Mach 2.64, shock near A = 1.67 m^2
_n = nozzle(3.0, 0.7)
_check("8.2.1 Me design", _n["Me_sup"], 2.64, 2e-3)
assert _n["regime"] == "shock"
_check("8.2.1 shock area (notes interpolate to about 1.67)", _n["As"], 1.67, 0.03)
# 8.1.1 / 8.2.1: shock at A = 2.0 m^2 (Mach 2.20) gives an exit pressure of 0.58 atm for Ae = 3 m^2
_M1 = M_from_AR(2.0, True)
_check("8.1.1 exit pressure", ns_p02p01(_M1) / p0_p(M_from_AR(3.0 * ns_p02p01(_M1), False)), 0.58, 0.01)
# 8.4.1: Mach 3 shock into 1 atm, 300 K air (MW 28.8): p = 10.33 atm, T = 804 K, Vs = 1044 m/s
_check("8.4.1 py", ns_p2p1(3.0), 10.33, 2e-3)
_check("8.4.1 Ty", 300 * ns_T2T1(3.0), 804, 2e-3)
_check("8.4.1 Vs", 3 * sound(300, R=R_of(28.8)), 1044, 2e-3)
# 9.4 Shinkansen: train at 83.3 m/s, c = 348 m/s -> Ms = 1.154 and a 39% pressure rise; 3 psi limit -> Ms = 1.082 and vp = 0.1315 c
_c = sound(300, R=R_of(28.8))
_check("9.4 Ms", piston_shock_mach(83.3 / _c), 1.154, 2e-3)
_check("9.4 overpressure", ns_p2p1(piston_shock_mach(83.3 / _c)) - 1, 0.39, 0.02)
_check("9.4 vp at Ms 1.082", piston_speed(1.082), 0.1315, 5e-3)
_check("9.4 tunnel area ratio", 1 / (1 - 1 / A_Astar(83.3 / _c)), 1.66, 0.01)
# 9.2: diffuser designed for Mach 1.5 has At/Ai = 0.850 and must be overspeeded to Mach 1.83 to start; Kantrowitz limit near Mach 2
_check("9.2 At/Ai", inlet_isentropic_ratio(1.5), 0.850, 2e-3)
_check("9.2 M start", bisect(lambda M: inlet_start_ratio(M) - inlet_isentropic_ratio(1.5), 1.0001, 10), 1.83, 3e-3)
_check("9.2 variable throat", inlet_start_ratio(1.5), 0.91, 0.01)
# 10.2.1: Fanno, M = 0.5: 4fL*/D = 1.0691, p* = 0.468 atm from 1 atm
_check("Fanno 4fL*/D(0.5)", fanno_fL(0.5), 1.0691, 1e-3)
_check("10.2.1 p*", 1 / fanno_p(0.5), 0.468, 2e-3)
# 10.4.1: M = 2: 4fL*/D = 0.30499, with f = 0.005, D = 0.3 m -> L* = 4.575 m; p* = 248.1 kPa from 101.3 kPa
_check("Fanno 4fL*/D(2)", fanno_fL(2.0), 0.30499, 1e-3)
_check("10.4.1 L*", fanno_fL(2.0) * 0.3 / (4 * 0.005), 4.575, 2e-3)
_check("10.4.1 p*", 101.3 / fanno_p(2.0), 248.1, 2e-3)
# 11.2.1: Rayleigh, M = 0.7, 300 K: T0 = 329.4 K, T0* = 362.6 K, q* = 33.3 kJ/kg; M = 0.5 -> T0 = 250.7 K, q = -79.0 kJ/kg
_T0 = 300 * T0_T(0.7)
_check("11.2.1 T0", _T0, 329.4, 2e-3)
_check("11.2.1 T0*", _T0 / ray_T0(0.7), 362.6, 2e-3)
_cp = G * 287.0 / (G - 1)
_check("11.2.1 q*", _cp * (_T0 / ray_T0(0.7) - _T0) / 1000, 33.3, 0.01)
_check("11.2.1 T0 at M 0.5", _T0 / ray_T0(0.7) * ray_T0(0.5), 250.7, 2e-3)
_check("11.2.1 T*", 300 / ray_T(0.7), 302, 3e-3)
_check("max-T Mach", 1 / math.sqrt(G), 0.845, 1e-3)
# 12.2.1: Mach 3, 10 degree wedge: sigma = 27.4 deg, M2 = 2.50, p2 = 2.055 atm; reflection: sigma2 = 31.86, M3 = 2.08, p3 = 3.825 atm
_o = ob_after(3.0, 10.0)
_check("12.2.1 sigma", _o["sigma"], 27.38, 3e-3)
_check("12.2.1 M2", _o["M2"], 2.50, 3e-3)
_check("12.2.1 p2", _o["p2p1"], 2.055, 3e-3)
_r = ob_after(_o["M2"], 10.0)
_check("12.3.1 sigma2", _r["sigma"], 31.86, 3e-3)
_check("12.3.1 M3 (notes carry rounded values)", _r["M2"], 2.08, 6e-3)
_check("12.3.1 p3", _o["p2p1"] * _r["p2p1"], 3.825, 3e-3)
# 12.2: delta_max = 34.1 deg at sigma = 65.2 deg for Mach 3; hypersonic limit 45.37 deg
_dm, _sm = ob_max(3.0)
_check("delta_max(3)", _dm, 34.07, 2e-3)
_check("sigma at delta_max(3)", _sm, 65.24, 2e-3)
# The notes quote 45.37 deg for the hypersonic limit; the exact limit is asin(1/gamma) = 45.58 deg for gamma = 1.4.
DELTA_MAX_LIMIT_NOTES = 45.37
_check("delta_max limit", ob_max(1e4)[0], math.degrees(math.asin(1 / G)), 1e-5)
# 12.3.2: Mach 3 with a 30 degree wedge: sigma ~ 52 deg and Mach 1.41 behind; delta_max(1.41) = 9.7 deg -> Mach reflection
_o30 = ob_after(3.0, 30.0)
_check("12.3.2 sigma", _o30["sigma"], 52.0, 0.01)
_check("12.3.2 M behind", _o30["M2"], 1.41, 0.01)
_check("12.3.2 delta_max(1.41)", ob_max(_o30["M2"])[0], 9.7, 0.02)
# 13.1: nu(2) = 26.38 deg, nu_max = 130.45 deg; Mach 2 turned 10 more degrees -> Mach 2.38
_check("nu(2)", pm_nu(2.0), 26.38, 1e-3)
_check("nu_max", nu_max(), 130.45, 1e-4)
_check("13.1 M after 10 deg", pm_M(pm_nu(2.0) + 10), 2.38, 3e-3)
# 15: MOC example: point 1 (M 2, 20 deg), point 2 (M 2.1, 5 deg) -> point 3: theta 11.15, M 2.34, alpha 25.30
_CI = pm_nu(2.0) + 20
_CII = pm_nu(2.1) - 5
_nu3, _th3, _M3 = moc_interior(_CI, _CII)
_check("15 CI", _CI, 46.38, 1e-3)
_check("15 CII", _CII, 24.07, 2e-3)
_check("15 theta3", _th3, 11.15, 3e-3)
_check("15 M3", _M3, 2.34, 3e-3)
_check("15 alpha3", mach_angle(_M3), 25.30, 3e-3)
# 15 channel table: Mach 3 -> nu = 49.757; points 4 (nu 44.757) -> M 2.753 and 6 (nu 39.757) -> M 2.527
_check("nu(3)", pm_nu(3.0), 49.757, 1e-4)
_check("MOC pt 4", pm_M(44.757), 2.753, 1e-3)
_check("MOC pt 6", pm_M(39.757), 2.527, 1e-3)
# 6.3.4 Isp values: H2 (MW 2) at 3000 K, 30 atm. Same nozzle in space: 8006 m/s; ratio-500 nozzle: 9111 m/s from momentum
_RH2 = R_of(2.0)
_ATM = 101325.0
_Me = M_from_p0p(30.0)
_Ae_mdot = A_Astar(_Me) * math.sqrt(_RH2 * 3000) / (30 * _ATM * mass_flux(1.0))
_check("6.3.4 Isp space, sea-level nozzle", exit_velocity(3000, 1 / 30, R=_RH2) + _Ae_mdot * _ATM, 8006, 2e-3)
_check("6.3.4 Ve ratio 500", exit_velocity(3000, (30 / p0_p(M_from_AR(500.0, True))) / 30, R=_RH2), 9111, 2e-3)
