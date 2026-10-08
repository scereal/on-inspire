// Compressible-flow relations for a calorically perfect gas. Mirrors content/gas.py exactly;
// the browser test compares the two at hundreds of points.
window.Gas = (function () {
  const G0 = 1.4, D = Math.PI / 180;
  const T0_T = (M, g = G0) => 1 + ((g - 1) / 2) * M * M;
  const p0_p = (M, g = G0) => Math.pow(T0_T(M, g), g / (g - 1));
  const r0_r = (M, g = G0) => Math.pow(T0_T(M, g), 1 / (g - 1));
  const A_Astar = (M, g = G0) => (1 / M) * Math.pow((2 / (g + 1)) * T0_T(M, g), (g + 1) / (2 * (g - 1)));
  const mass_flux = (M, g = G0) => Math.sqrt(g) * M * Math.pow(T0_T(M, g), -(g + 1) / (2 * (g - 1)));
  function bisect(f, a, b, tol = 1e-12, n = 300) {
    let fa = f(a);
    for (let i = 0; i < n; i++) {
      const m = 0.5 * (a + b), fm = f(m);
      if (fa * fm <= 0) b = m; else { a = m; fa = fm; }
      if (b - a < tol) break;
    }
    return 0.5 * (a + b);
  }
  const M_from_AR = (ar, sup, g = G0) => Math.abs(ar - 1) < 1e-12 ? 1 : sup ? bisect((M) => A_Astar(M, g) - ar, 1, 100) : bisect((M) => A_Astar(M, g) - ar, 1e-9, 1);
  const M_from_p0p = (r, g = G0) => Math.sqrt((2 / (g - 1)) * (Math.pow(r, (g - 1) / g) - 1));
  const sound = (T, g = G0, R = 287) => Math.sqrt(g * R * T);
  const mach_angle = (M) => Math.asin(1 / M) / D;
  // normal shock
  const ns_M2 = (M, g = G0) => Math.sqrt((1 + ((g - 1) / 2) * M * M) / (g * M * M - (g - 1) / 2));
  const ns_p2p1 = (M, g = G0) => 1 + ((2 * g) / (g + 1)) * (M * M - 1);
  const ns_r2r1 = (M, g = G0) => ((g + 1) * M * M) / ((g - 1) * M * M + 2);
  const ns_T2T1 = (M, g = G0) => ns_p2p1(M, g) / ns_r2r1(M, g);
  const ns_p02p01 = (M, g = G0) => (ns_p2p1(M, g) * p0_p(ns_M2(M, g), g)) / p0_p(M, g);
  const pitot_ratio = (M, g = G0) => ns_p02p01(M, g) * p0_p(M, g);
  const piston_shock_mach = (v, g = G0) => { const a = ((g + 1) / 4) * v; return a + Math.sqrt(a * a + 1); };
  const piston_speed = (Ms, g = G0) => (2 / (g + 1)) * (Ms - 1 / Ms);
  // Fanno
  const fanno_fL = (M, g = G0) => (1 - M * M) / (g * M * M) + ((g + 1) / (2 * g)) * Math.log(((g + 1) * M * M) / (2 + (g - 1) * M * M));
  const fanno_T = (M, g = G0) => (g + 1) / (2 + (g - 1) * M * M);
  const fanno_p = (M, g = G0) => (1 / M) * Math.sqrt(fanno_T(M, g));
  const fanno_p0 = (M, g = G0) => (1 / M) * Math.pow((2 + (g - 1) * M * M) / (g + 1), (g + 1) / (2 * (g - 1)));
  const fanno_M = (fl, sup, g = G0) => sup ? bisect((M) => fanno_fL(M, g) - fl, 1, 1e4) : bisect((M) => fanno_fL(M, g) - fl, 1e-6, 1);
  // Rayleigh
  const ray_p = (M, g = G0) => (1 + g) / (1 + g * M * M);
  const ray_T = (M, g = G0) => Math.pow(M * ray_p(M, g), 2);
  const ray_T0 = (M, g = G0) => ((2 * (g + 1) * M * M) / Math.pow(1 + g * M * M, 2)) * (1 + ((g - 1) / 2) * M * M);
  const ray_p0 = (M, g = G0) => ray_p(M, g) * Math.pow((2 + (g - 1) * M * M) / (g + 1), g / (g - 1));
  const ray_M = (t0, sup, g = G0) => sup ? bisect((M) => ray_T0(M, g) - t0, 1, 1e4) : bisect((M) => ray_T0(M, g) - t0, 1e-9, 1);
  // oblique shock and Prandtl-Meyer
  function ob_delta(M, s, g = G0) {
    const r = s * D, num = (2 / Math.tan(r)) * (M * M * Math.sin(r) ** 2 - 1), den = M * M * (g + Math.cos(2 * r)) + 2;
    return Math.atan(num / den) / D;
  }
  function ob_max(M, g = G0) {
    const phi = (Math.sqrt(5) - 1) / 2;
    let a = mach_angle(M), b = 90;
    for (let i = 0; i < 200; i++) { const c = b - phi * (b - a), d = a + phi * (b - a); if (ob_delta(M, c, g) > ob_delta(M, d, g)) b = d; else a = c; }
    const s = 0.5 * (a + b);
    return [ob_delta(M, s, g), s];
  }
  function ob_sigma(M, delta, strong = false, g = G0) {
    const [dmax, smax] = ob_max(M, g);
    if (delta > dmax + 1e-9) return NaN;
    return strong ? bisect((s) => ob_delta(M, s, g) - delta, smax, 90) : bisect((s) => ob_delta(M, s, g) - delta, mach_angle(M) + 1e-12, smax);
  }
  function ob_after(M, delta, strong = false, g = G0) {
    const s = ob_sigma(M, delta, strong, g);
    if (!isFinite(s)) return null;
    const Mn1 = M * Math.sin(s * D), Mn2 = ns_M2(Mn1, g);
    return { sigma: s, Mn1, M2: Mn2 / Math.sin((s - delta) * D), p2p1: ns_p2p1(Mn1, g), T2T1: ns_T2T1(Mn1, g), p02p01: ns_p02p01(Mn1, g) };
  }
  function pm_nu(M, g = G0) {
    const k = Math.sqrt((g + 1) / (g - 1));
    return (k * Math.atan(Math.sqrt((M * M - 1) / (k * k))) - Math.atan(Math.sqrt(M * M - 1))) / D;
  }
  const pm_M = (nu, g = G0) => bisect((M) => pm_nu(M, g) - nu, 1, 1e4);
  const nu_max = (g = G0) => 90 * (Math.sqrt((g + 1) / (g - 1)) - 1);
  // rockets
  const exit_velocity = (T0, pe_p0, g = G0, R = 287) => Math.sqrt(((2 * g) / (g - 1)) * R * T0 * (1 - Math.pow(pe_p0, (g - 1) / g)));
  const v_max = (T0, g = G0, R = 287) => Math.sqrt(((2 * g) / (g - 1)) * R * T0);
  // converging-diverging nozzle with back pressure (mirrors gas.nozzle)
  function nozzle(AeAt, pb, g = G0) {
    const Msub = M_from_AR(AeAt, false, g), Msup = M_from_AR(AeAt, true, g);
    const p3 = 1 / p0_p(Msub, g), pd = 1 / p0_p(Msup, g), p4 = pd * ns_p2p1(Msup, g);
    const out = { p3, p4, pd, Me_sub: Msub, Me_sup: Msup };
    if (pb >= p3) {
      const Me = pb < 1 ? M_from_p0p(1 / pb, g) : 0;
      return Object.assign(out, { regime: "subsonic", Me, pe: pb, mdot: Me > 0 ? (mass_flux(Me, g) * AeAt) / mass_flux(1, g) : 0 });
    }
    out.mdot = 1;
    if (pb > p4 + 1e-15) {
      const peFor = (As) => { const M1 = M_from_AR(As, true, g), r = ns_p02p01(M1, g), Me = M_from_AR(AeAt * r, false, g); return [r / p0_p(Me, g), Me, M1, r]; };
      const As = bisect((a) => peFor(a)[0] - pb, 1 + 1e-9, AeAt);
      const [pe, Me, M1, r] = peFor(As);
      return Object.assign(out, { regime: "shock", As, Ms: M1, Me, pe, p0r: r });
    }
    if (pb > pd * (1 + 1e-9)) return Object.assign(out, { regime: "overexpanded", Me: Msup, pe: pd });
    if (pb >= pd * (1 - 1e-9)) return Object.assign(out, { regime: "design", Me: Msup, pe: pd });
    return Object.assign(out, { regime: "underexpanded", Me: Msup, pe: pd });
  }
  const inlet_start_ratio = (M, g = G0) => 1 / A_Astar(ns_M2(M, g), g);
  const inlet_isentropic_ratio = (M, g = G0) => 1 / A_Astar(M, g);
  return {
    G0, T0_T, p0_p, r0_r, A_Astar, mass_flux, bisect, M_from_AR, M_from_p0p, sound, mach_angle,
    ns_M2, ns_p2p1, ns_r2r1, ns_T2T1, ns_p02p01, pitot_ratio, piston_shock_mach, piston_speed,
    fanno_fL, fanno_T, fanno_p, fanno_p0, fanno_M, ray_p, ray_T, ray_T0, ray_p0, ray_M,
    ob_delta, ob_max, ob_sigma, ob_after, pm_nu, pm_M, nu_max, exit_velocity, v_max, nozzle,
    inlet_start_ratio, inlet_isentropic_ratio,
  };
})();
