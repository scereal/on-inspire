"""Layer 3: the course's practice exercises (Exercises 1-4), each question broken into pencil-free steps.

These are the ungraded practice sets, so the walkthroughs do reach the answers. Every number is solved
here with SymPy as the module imports; a wrong value fails the build.
"""
import sympy as sp
from lib import *

E1, E2, E3, E4 = ("Exercise 1 · Optimality and first iterations", "Exercise 2 · Monotonicity, convexity, line search, BFGS",
                  "Exercise 3 · KKT and reduced gradients", "Exercise 4 · Regularity, reduced gradients, KKT")
pos = sp.symbols("p1 p2 p3", positive=True)
P1, P2, P3 = pos
bb, hh, ph = sp.symbols("b h phi", positive=True)
al = sp.Symbol("alpha", positive=True)


def grad(f, v):
    return sp.Matrix([sp.diff(f, s) for s in v])


# ---- Exercise 1 ------------------------------------------------------------------------------
# Q1: f = x1^2 + x1 x2 + x2^2 - ln x1 - ln x2 on x > 0.
_f11 = P1**2 + P1 * P2 + P2**2 - sp.log(P1) - sp.log(P2)
_s11 = sp.solve(list(grad(_f11, (P1, P2))), [P1, P2], dict=True)
assert _s11 == [{P1: 1 / sp.sqrt(3), P2: 1 / sp.sqrt(3)}], _s11
_H11 = sp.hessian(_f11, (P1, P2)).subs(_s11[0])
assert _H11 == sp.Matrix([[5, 1], [1, 5]])

# Q3: f = x^2 + 3y^2 - 3xy from (1, 3).
_f13 = x**2 + 3 * y**2 - 3 * x * y
_g13 = grad(_f13, (x, y)).subs({x: 1, y: 3})
assert list(_g13) == [-7, 15]
_gd13 = sp.Matrix([1, 3]) - sp.Rational(1, 100) * _g13
_H13 = sp.hessian(_f13, (x, y))
_nt13 = sp.Matrix([1, 3]) - _H13.inv() * _g13
assert list(_gd13) == [sp.Rational(107, 100), sp.Rational(57, 20)] and list(_nt13) == [0, 0]

# ---- Exercise 2 ------------------------------------------------------------------------------
# Q1: max x1 s.t. e^x1 <= x2, e^x2 <= x3, x3 <= 10: every constraint ends up active.
_x3 = 10
_x2 = sp.log(_x3)
_x1 = sp.log(_x2)

# Q3 (and Exercise 4 Q3): closest point to (-1, 0, 1) on x1 + 2x2 + 3x3 = 1.
_f23 = (x1 + 1)**2 + x2**2 + (x3 - 1)**2
_h23 = x1 + 2 * x2 + 3 * x3 - 1
_s23 = sp.solve(list(grad(_f23 + lam1 * _h23, (x1, x2, x3))) + [_h23], [x1, x2, x3, lam1], dict=True)[0]
assert (_s23[x1], _s23[x2], _s23[x3], _s23[lam1]) == (sp.Rational(-15, 14), sp.Rational(-1, 7), sp.Rational(11, 14), sp.Rational(1, 7))
_dist23 = sp.sqrt(_f23.subs(_s23))
assert sp.simplify(_dist23 - 1 / sp.sqrt(14)) == 0
# reduced gradient with x1 as the state variable: dz f = grad_d f - grad_s f (dh/ds)^-1 grad_d h, decisions (x2, x3)
_red23 = sp.Matrix([sp.diff(_f23, d) - sp.diff(_f23, x1) * sp.diff(_h23, d) / sp.diff(_h23, x1) for d in (x2, x3)])
assert sp.expand(_red23[0] - (2 * x2 - 4 * (x1 + 1))) == 0

# Q4: f = x1^2 + 2 x2^2 at (2, 1), Armijo-Goldstein with eps1 = 0.2, eps2 = 0.8.
_f24 = x1**2 + 2 * x2**2
_g24 = grad(_f24, (x1, x2)).subs({x1: 2, x2: 1})
_phi24 = sp.expand(_f24.subs({x1: 2 - al * _g24[0], x2: 1 - al * _g24[1]}))
assert _phi24 == 48 * al**2 - 32 * al + 6
_dphi0_24 = sp.diff(_phi24, al).subs(al, 0)
_hi24 = [s for s in sp.solve(sp.Eq(_phi24, 6 + sp.Rational(1, 5) * _dphi0_24 * al), al) if s != 0][0]
_lo24 = [s for s in sp.solve(sp.Eq(_phi24, 6 + sp.Rational(4, 5) * _dphi0_24 * al), al) if s != 0][0]
_ex24 = sp.solve(sp.diff(_phi24, al), al)[0]
assert (_lo24, _hi24, _ex24) == (sp.Rational(2, 15), sp.Rational(8, 15), sp.Rational(1, 3))
_xn24 = (2 - _ex24 * _g24[0], 1 - _ex24 * _g24[1])
_fn24 = _f24.subs({x1: _xn24[0], x2: _xn24[1]})
assert _xn24 == (sp.Rational(2, 3), sp.Rational(-1, 3)) and _fn24 == sp.Rational(2, 3)

# Q5: f = x1^2 + 4 x2^2 at (2, 1), Armijo's two-sided test with eps = 0.2, backtracking from 1 with beta = 0.5.
_f25 = x1**2 + 4 * x2**2
_g25 = grad(_f25, (x1, x2)).subs({x1: 2, x2: 1})
_phi25 = sp.expand(_f25.subs({x1: 2 - al * _g25[0], x2: 1 - al * _g25[1]}))
assert _phi25 == 272 * al**2 - 80 * al + 8
_d25 = sp.diff(_phi25, al).subs(al, 0)
_hi25 = [s for s in sp.solve(sp.Eq(_phi25, 8 + sp.Rational(1, 5) * _d25 * al), al) if s != 0][0]
_lo25 = [s for s in sp.solve(sp.Eq(_phi25.subs(al, 2 * al), 8 + 2 * sp.Rational(1, 5) * _d25 * al), al) if s != 0][0]
assert (_lo25, _hi25) == (sp.Rational(2, 17), sp.Rational(4, 17))
_trials25, _a = [], sp.Integer(1)
while True:
    ok = _phi25.subs(al, _a) <= 8 + sp.Rational(1, 5) * _d25 * _a
    _trials25.append((_a, _phi25.subs(al, _a), 8 + sp.Rational(1, 5) * _d25 * _a, ok))
    if ok:
        break
    _a /= 2
assert [t[0] for t in _trials25] == [1, sp.Rational(1, 2), sp.Rational(1, 4), sp.Rational(1, 8)]
assert _trials25[2][1:3] == (5, 4) and _trials25[3][1:3] == (sp.Rational(9, 4), 6)
_ex25 = sp.solve(sp.diff(_phi25, al), al)[0]
assert _ex25 == sp.Rational(5, 34) and _lo25 <= sp.Rational(1, 8) <= _hi25

# Q6: one BFGS update on f = x1^2 + x1 x2 + 2 x2^2 from (1, 0), H0 = I, alpha0 = 0.5.
_f26 = x1**2 + x1 * x2 + 2 * x2**2
_gf26 = lambda p: grad(_f26, (x1, x2)).subs({x1: p[0], x2: p[1]})
_x0 = sp.Matrix([1, 0])
_s0 = -sp.Rational(1, 2) * _gf26(_x0)
_x1v = _x0 + _s0
_y0 = _gf26(_x1v) - _gf26(_x0)
_ys = (_y0.T * _s0)[0]
_Hh1 = sp.eye(2) - (_s0 * _s0.T) / (_s0.T * _s0)[0] + (_y0 * _y0.T) / _ys
assert list(_s0) == [-1, sp.Rational(-1, 2)] and list(_x1v) == [0, sp.Rational(-1, 2)] and list(_y0) == [sp.Rational(-5, 2), -3] and _ys == 4
assert _Hh1 == sp.Matrix([[sp.Rational(141, 80), sp.Rational(59, 40)], [sp.Rational(59, 40), sp.Rational(61, 20)]])
assert _Hh1 * _s0 == _y0
_d1 = -_Hh1.inv() * _gf26(_x1v)
assert (_d1.T * _gf26(_x1v))[0] < 0
_nt26 = _x1v - sp.hessian(_f26, (x1, x2)).inv() * _gf26(_x1v)
assert list(_nt26) == [0, 0]

# Q7: canal. Side walls at angle phi to the horizontal; area h(b + h cot phi) = 100; perimeter b + 2h/sin(phi).
_bsub = 100 / hh - hh * sp.cot(ph)
_P27 = _bsub + 2 * hh / sp.sin(ph)
_phi_star = sp.pi / 3
assert sp.simplify(sp.diff(_P27, ph).subs(ph, _phi_star)) == 0
_h27 = [s for s in sp.solve(sp.diff(_P27.subs(ph, _phi_star), hh), hh) if s.is_positive][0]
_b27 = sp.simplify(_bsub.subs({ph: _phi_star, hh: _h27}))
_Pmin27 = sp.simplify(_P27.subs({ph: _phi_star, hh: _h27}))
assert abs(float(_h27) - 7.598) < 1e-3 and abs(float(_b27) - 8.774) < 1e-3 and abs(float(_Pmin27) - 3 * float(_b27)) < 1e-9
_H27 = sp.hessian(_P27, (hh, ph)).subs({ph: _phi_star, hh: _h27})
assert all(float(v) > 0 for v in _H27.eigenvals())

# ---- Exercise 3 ------------------------------------------------------------------------------
# Q1: maximize 3x1 - x2 + x3^2 s.t. x1 + x2 + x3 <= 0, -x1 + 2x2 + x3^2 = 0. Written as min -f.
_f31 = -(3 * x1 - x2 + x3**2)
_g31 = x1 + x2 + x3
_h31 = -x1 + 2 * x2 + x3**2
_s31 = sp.solve(list(grad(_f31 + mu * _g31 + lam1 * _h31, (x1, x2, x3))) + [_g31, _h31], [x1, x2, x3, mu, lam1], dict=True)
assert len(_s31) == 1
_s31 = _s31[0]
assert (_s31[x3], _s31[mu], _s31[lam1]) == (sp.Rational(5, 14), sp.Rational(5, 3), sp.Rational(-4, 3))
assert (_s31[x1], _s31[x2]) == (sp.Rational(-115, 588), sp.Rational(-95, 588))
# along the active boundary, f reduces to (7/3) x3^2 - (5/3) x3: unbounded above, so the KKT point is not a maximizer
_fred31 = sp.expand((3 * x1 - x2 + x3**2).subs(x1, 2 * x2 + x3**2).subs(x2, -(x3**2 + x3) / 3))
assert _fred31 == sp.Rational(7, 3) * x3**2 - sp.Rational(5, 3) * x3

# Q2: min -2x1 - b x2 s.t. x1^2 + x2^2 = 5; with x1 decision, x2 state: dz f = -2 + b x1/x2.
_f32 = -2 * x1 - b * x2
_h32 = x1**2 + x2**2 - 5
_red32 = sp.diff(_f32, x1) - sp.diff(_f32, x2) * sp.diff(_h32, x1) / sp.diff(_h32, x2)
assert sp.simplify(_red32 - (-2 + b * x1 / x2)) == 0
_b32 = sp.solve(_red32.subs({x1: 1, x2: 2}), b)[0]
assert _b32 == 4
_x1b = 2 * sp.sqrt(5) / sp.sqrt(4 + b**2)
assert sp.simplify(_x1b.subs(b, 4) - 1) == 0

# ---- Exercise 4 ------------------------------------------------------------------------------
# Q1: min -x1 s.t. x2 - (1 - x1)^3 <= 0, -x2 <= 0. Optimum at the cusp (1, 0), where KKT fails.
_g41 = x2 - (1 - x1)**3
_J41 = sp.Matrix([list(grad(_g41, (x1, x2)).subs({x1: 1, x2: 0})), [0, -1]])
assert _J41.rank() == 1
_kkt41 = sp.solve([-1 + mu1 * _J41[0, 0] + mu2 * _J41[1, 0], 0 + mu1 * _J41[0, 1] + mu2 * _J41[1, 1]], [mu1, mu2], dict=True)
assert _kkt41 == []

# Q2: min |x|^2 on the ellipsoid x1^2/4 + x2^2/5 + x3^2/25 = 1 with x1 + x2 - x3 <= 0.
_axes = {(2, 0, 0): 4, (0, sp.sqrt(5), 0): 5, (0, 0, 5): 25}
_cands = [tuple(s * v for v in p) for p in _axes for s in (1, -1)]
_feas42 = [p for p in _cands if p[0] + p[1] - p[2] <= 0]
_best42 = min(_feas42, key=lambda p: sum(v**2 for v in p))
assert _best42 == (-2, 0, 0) and (2, 0, 0) not in _feas42

STEPWISE = "Each step asks for one choice, one number, one expression or one click; the hard algebra is done for you only after you've made the decision that matters."

CONCEPTS = [
    concept(
        "x-e1-stationary", "Exercise 1.1: stationary points of x₁² + x₁x₂ + x₂² − ln x₁ − ln x₂", 3, E1,
        r"""
**The question.** Find the stationary points of $f(x_1,x_2) = x_1^2 + x_1x_2 + x_2^2 - \ln x_1 - \ln x_2$ where $f$ is defined, and classify them.

**Strategy.** The domain is $x_1, x_2 > 0$ (the logs). Set $\nabla f = \mathbf{0}$, use the symmetry of the two equations to cut the work, then check the Hessian ([[c-fonc]], [[c-sosc]]). {S}
""".replace("{S}", STEPWISE),
        deeper=["c-fonc", "c-sosc", "p-eigen-definiteness"],
        source="Exercise 1, question 1",
        problems=[
            problem("x-e11-a", "Set the gradient to zero",
                    r"$\nabla f = \left(2x_1 + x_2 - \tfrac{1}{x_1},\ x_1 + 2x_2 - \tfrac{1}{x_2}\right)$.",
                    [choice("Multiply the first equation by $x_1$ and the second by $x_2$, then subtract. What do you learn?",
                            [opt("$x_1^2 = x_2^2$, so $x_1 = x_2$ on the domain", True),
                             opt("$x_1 = -x_2$", why="That root is real algebra, but it leaves the domain $x > 0$."),
                             opt("Nothing: the equations are independent", why="Subtracting $2x_1^2 + x_1x_2 = 1$ and $x_1x_2 + 2x_2^2 = 1$ cancels the cross term.")]),
                     num(r"With $x_1 = x_2 = t$, the first equation is $3t = 1/t$. What is $t$?", 1 / sp.sqrt(3), tol=0.002,
                         explain="$t = 1/\\sqrt3\\approx0.577$. One stationary point: $(1/\\sqrt3, 1/\\sqrt3)$.")]),
            problem("x-e11-b", "Classify it",
                    r"$\nabla^2 f = \begin{bmatrix}2 + 1/x_1^2 & 1\\ 1 & 2 + 1/x_2^2\end{bmatrix}$.",
                    [num(r"$H_{11}$ at the stationary point?", _H11[0, 0]),
                     choice("With $\\mathbf{H} = \\begin{bmatrix}5 & 1\\\\1 & 5\\end{bmatrix}$ there, the point is:",
                            [opt("A strict local minimizer, and the global one on the domain", True),
                             opt("A saddle point", why="$\\det\\mathbf{H} = 24 > 0$ and the trace is positive: both eigenvalues (4 and 6) are positive."),
                             opt("A maximizer", why="A maximizer needs a negative definite Hessian.")],
                            explain="Better still, $\\nabla^2 f$ is positive definite **everywhere** on $x > 0$ (diagonal $> 2$, off-diagonal 1), so $f$ is convex there and this is the global minimizer ([[c-convexity]]).")]),
        ]),
    concept(
        "x-e1-existence", "Exercise 1.2: does a polynomial have a maximum or a minimum?", 3, E1,
        r"""
**The question.** For $f(x) = x^{10} + 9x^9 + 3x^2 + 14x + 7$: (a) does $f$ have a maximum on $[-1, 1]$? (b) a minimum on $(-\infty, \infty)$?

**Strategy.** Don't compute anything. Use existence results: Weierstrass on a compact set ([[p-sets-compactness]]), and coercivity (what happens as $|x|\to\infty$) on an unbounded one ([[c-boundedness]]).
""",
        deeper=["p-sets-compactness", "c-boundedness"],
        source="Exercise 1, question 2",
        problems=[
            problem("x-e12-a", "On the closed interval",
                    r"$f$ is a polynomial on $[-1, 1]$.",
                    [choice("Does $f$ attain a maximum on $[-1, 1]$?",
                            [opt("Yes: $f$ is continuous and $[-1, 1]$ is closed and bounded (Weierstrass)", True),
                             opt("Only if $f'(x) = 0$ somewhere inside", why="The maximum can sit at an endpoint; existence doesn't need a stationary point."),
                             opt("No: a degree-10 polynomial is unbounded", why="Unbounded on the real line, yes, but $[-1, 1]$ is compact.")])]),
            problem("x-e12-b", "On the whole line",
                    r"Now $x\in(-\infty,\infty)$.",
                    [choice("Does $f$ have a minimum on the real line?",
                            [opt("Yes: the leading term $x^{10}$ (even degree, positive) makes $f\\to+\\infty$ as $|x|\\to\\infty$, so $f$ is coercive", True),
                             opt("No: the set isn't compact, so Weierstrass fails", why="Weierstrass failing doesn't mean no minimum; coercivity rescues it."),
                             opt("No: the $9x^9$ term sends $f$ to $-\\infty$", why="For large $|x|$, $x^{10}$ dominates $9x^9$ in both directions.")],
                            explain="Coercive and continuous: restrict to a large closed interval where $f$ exceeds $f(0)$ outside, then apply Weierstrass.")]),
        ]),
    concept(
        "x-e1-iterations", "Exercise 1.3: one gradient step and one Newton step on x² + 3y² − 3xy", 3, E1,
        r"""
**The question.** For $f(x, y) = x^2 + 3y^2 - 3xy$ from $(x_0, y_0) = (1, 3)$: one iteration of gradient descent with fixed $\alpha = 0.01$, and one iteration of Newton's method.

**Strategy.** Both need $\nabla f$ at the start. Newton also needs $\mathbf{H}$, which is constant for a quadratic ([[c-gradient-method]], [[c-newton]]).
""",
        deeper=["c-gradient-method", "c-newton", "c-quadratic-functions"],
        source="Exercise 1, question 3",
        problems=[
            problem("x-e13-a", "The gradient",
                    r"$f = x^2 + 3y^2 - 3xy$.",
                    [expr(r"Type $\partial f/\partial x$.", 2 * x - 3 * y, ["x", "y"]),
                     num(r"$\partial f/\partial x$ at $(1, 3)$?", _g13[0]),
                     num(r"$\partial f/\partial y$ at $(1, 3)$?", _g13[1], explain="$\\nabla f(1,3) = (-7, 15)$.")]),
            problem("x-e13-b", "Gradient step",
                    r"$\mathbf{x}_1 = \mathbf{x}_0 - 0.01\,\nabla f(\mathbf{x}_0)$ with $\nabla f = (-7, 15)$.",
                    [num("$x_1$?", _gd13[0]), num("$y_1$?", _gd13[1], explain="$(1.07, 2.85)$: a small step, as $\\alpha = 0.01$ promises.")]),
            problem("x-e13-c", "Newton step",
                    r"$\mathbf{H} = \begin{bmatrix}2 & -3\\-3 & 6\end{bmatrix}$, $\det\mathbf{H} = 3$.",
                    [choice("Before computing: where will one Newton step from any start land?",
                            [opt("Exactly on the stationary point, because $f$ is quadratic", True),
                             opt("Closer, but more steps are needed", why="Newton minimizes the quadratic model; for a quadratic $f$ the model **is** $f$."),
                             opt("It depends on $\\alpha$", why="Pure Newton uses $\\alpha = 1$.")]),
                     num(r"$x_1$ after the Newton step?", _nt13[0]), num(r"$y_1$?", _nt13[1],
                         explain="$\\mathbf{H}$ is positive definite (trace 8, det 3), so $(0, 0)$ is the minimizer.")]),
        ]),

    concept(
        "x-e2-monotonicity", "Exercise 2.1: a chain of active constraints by monotonicity", 3, E2,
        r"""
**The question.** Maximize $f = x_1$ subject to $e^{x_1}\le x_2$, $e^{x_2}\le x_3$, $x_3\le10$, using monotonicity principles.

**Strategy.** Follow the first monotonicity principle ([[c-monotonicity]]): a variable the objective wants to push must be bounded by an active constraint. Then follow the chain.
""",
        deeper=["c-monotonicity", "c-constraint-activity"],
        source="Exercise 2, question 1 (Papalambros & Wilde 3.9)",
        problems=[
            problem("x-e21-a", "Who bounds whom",
                    r"$f = x_1$ increases with $x_1$.",
                    [order("Put the reasoning in order.",
                           ["$f$ increases in $x_1$, and only $e^{x_1}\\le x_2$ bounds $x_1$ above, so it's active: $x_1 = \\ln x_2$",
                            "A larger $x_2$ allows a larger $x_1$; only $e^{x_2}\\le x_3$ bounds $x_2$ above, so it's active: $x_2 = \\ln x_3$",
                            "A larger $x_3$ allows a larger $x_2$; only $x_3\\le10$ bounds it, so it's active: $x_3 = 10$",
                            "Back-substitute: $x_2 = \\ln 10$, $x_1 = \\ln\\ln10$"]),
                     num("$x_2^*$?", _x2, tol=0.002), num("$x_1^*$?", _x1, tol=0.002,
                         explain="$x^* = (\\ln\\ln10,\\ \\ln10,\\ 10)\\approx(0.834, 2.303, 10)$, with all three constraints active.")]),
        ]),
    concept(
        "x-e2-hyperplane", "Exercise 2.2: a hyperplane is a convex set", 3, E2,
        r"""
**The question.** Show that $\{\mathbf{x} : \mathbf{a}^T\mathbf{x} = c\}$ is convex.

**Strategy.** Use the definition ([[c-convexity]]): take two points in the set and show every convex combination is also in it.
""",
        deeper=["c-convexity"],
        source="Exercise 2, question 2 (Papalambros & Wilde 4.17)",
        problems=[
            problem("x-e22-a", "Find the broken proof line",
                    r"A student's proof that the hyperplane is convex.",
                    [spot("Which line is wrong?",
                          [("Take $\\mathbf{x}, \\mathbf{y}$ with $\\mathbf{a}^T\\mathbf{x} = c$ and $\\mathbf{a}^T\\mathbf{y} = c$, and $\\lambda\\in[0,1]$.", False, ""),
                           ("Let $\\mathbf{z} = \\lambda\\mathbf{x} + (1-\\lambda)\\mathbf{y}$.", False, ""),
                           ("$\\mathbf{a}^T\\mathbf{z} = \\lambda\\mathbf{a}^T\\mathbf{x} + (1-\\lambda)\\mathbf{a}^T\\mathbf{y} = \\lambda c + (1-\\lambda)c\\le c$.", True,
                            "It's an equality, $= c$, not just $\\le c$. With only $\\le$ you'd have shown $\\mathbf{z}$ is in the half-space, not on the hyperplane."),
                           ("So $\\mathbf{z}$ lies on the hyperplane, which is therefore convex.", False, "")])]),
        ]),
    concept(
        "x-e2-closest-point", "Exercise 2.3 and 4.3: the closest point on a plane, by reduced gradients and by KKT", 3, E2,
        r"""
**The question.** Find the point on $x_1 + 2x_2 + 3x_3 = 1$ closest to $(-1, 0, 1)$ and verify its nature. Exercise 4, question 3 asks for the same problem twice: by reduced gradients, then by the KKT conditions.

**Strategy.** Minimize the *squared* distance $f = (x_1+1)^2 + x_2^2 + (x_3-1)^2$ (same minimizer, no square root). With one equality: either eliminate one variable ([[c-reduced-gradient]]) or use a Lagrange multiplier ([[c-lagrangian-equality]]).
""",
        deeper=["c-reduced-gradient", "c-lagrangian-equality", "c-convexity"],
        source="Exercise 2, question 3 (Papalambros & Wilde 4.12); Exercise 4, question 3",
        problems=[
            problem("x-e23-a", "Reduced gradient",
                    r"Take $x_1$ as the state variable ($\partial h/\partial x_1 = 1$) and $(x_2, x_3)$ as decisions.",
                    [expr(r"Type the reduced gradient component $\partial z/\partial x_2 = \partial f/\partial x_2 - \dfrac{\partial f}{\partial x_1}\dfrac{\partial h/\partial x_2}{\partial h/\partial x_1}$.",
                          _red23[0], ["x1", "x2"], explain="$2x_2 - 2(x_1+1)\\cdot2$."),
                     num(r"Solving both reduced components with $h = 0$: $x_1^*$?", _s23[x1], tol=0.002),
                     num(r"$x_2^*$?", _s23[x2], tol=0.002), num(r"$x_3^*$?", _s23[x3], tol=0.002,
                         explain="$\\mathbf{x}^* = (-15/14,\\ -1/7,\\ 11/14)$.")]),
            problem("x-e23-b", "The same answer by KKT",
                    r"$\nabla f + \lambda\nabla h = \mathbf{0}$ with $\nabla h = (1, 2, 3)$.",
                    [num(r"From the first component, $2(x_1 + 1) + \lambda = 0$. What is $\lambda$?", _s23[lam1], tol=0.002),
                     num("The distance itself, $\\sqrt{f^*}$?", _dist23, tol=0.002, explain="$1/\\sqrt{14}$: the textbook point-to-plane formula $|\\mathbf{a}^T\\mathbf{p} - c|/\\|\\mathbf{a}\\|$ agrees."),
                     choice("Nature of the point?",
                            [opt("Global minimizer: $f$ is strictly convex and the constraint is linear", True),
                             opt("Need the bordered Hessian to know", why="That works, but convexity settles it immediately."),
                             opt("A saddle, because $\\lambda > 0$", why="An equality multiplier's sign carries no meaning about optimality.")])]),
        ]),
    concept(
        "x-e2-armijo-goldstein", "Exercise 2.4: the Armijo–Goldstein interval for x₁² + 2x₂²", 3, E2,
        r"""
**The question.** At $\mathbf{x}_k = (2, 1)$ with steepest descent on $f = x_1^2 + 2x_2^2$: build $\phi(\alpha)$, find the Armijo–Goldstein interval with $\epsilon_1 = 0.2$, $\epsilon_2 = 0.8$, and compare with the exact step.

**Strategy.** $\phi$ is a quadratic in $\alpha$. Each condition is a quadratic inequality whose nonzero root is one end of the interval ([[c-armijo]], [[c-exact-line-search]]).
""",
        deeper=["c-armijo", "c-exact-line-search"],
        source="Exercise 2, question 4",
        problems=[
            problem("x-e24-a", "The line function",
                    r"$\nabla f(2, 1) = (4, 4)$, $\mathbf{d} = (-4, -4)$.",
                    [expr(r"Type $\phi(\alpha) = f(\mathbf{x}_k + \alpha\mathbf{d})$, expanded or not.", _phi24.subs(al, alpha), ["alpha"], ranges={"alpha": [0, 1]}),
                     num(r"$\phi'(0)$?", _dphi0_24, explain="$\\phi'(0) = \\nabla f^T\\mathbf{d} = -32$.")]),
            problem("x-e24-b", "The interval",
                    r"$\phi(\alpha) = 48\alpha^2 - 32\alpha + 6$.",
                    [num(r"Upper end $\alpha_b$ (from $\phi(\alpha)\le\phi(0) + 0.2\,\phi'(0)\alpha$)?", _hi24, tol=0.002),
                     num(r"Lower end $\alpha_c$ (from $\phi(\alpha)\ge\phi(0) + 0.8\,\phi'(0)\alpha$)?", _lo24, tol=0.002,
                         explain="$[\\alpha_c, \\alpha_b] = [2/15, 8/15]$.")]),
            problem("x-e24-c", "The exact step",
                    r"Minimize $\phi$.",
                    [num(r"$\alpha^*$?", _ex24, tol=0.002),
                     choice("Is $\\alpha^* = 1/3$ acceptable to both conditions?",
                            [opt("Yes: $2/15\\le1/3\\le8/15$", True), opt("No, the Goldstein condition rejects it", why="$1/3 > 2/15$.")]),
                     num(r"$f(\mathbf{x}_{k+1})$?", _fn24, tol=0.002, explain="$\\mathbf{x}_{k+1} = (2/3, -1/3)$, $f = 2/3$, down from 6.")]),
        ]),
    concept(
        "x-e2-backtracking", "Exercise 2.5: backtracking on x₁² + 4x₂², trial by trial", 3, E2,
        r"""
**The question.** At $(2, 1)$ with steepest descent on $f = x_1^2 + 4x_2^2$: the interval from Armijo's two-sided test ($\epsilon = 0.2$), then backtracking from $\alpha_0 = 1$ with $\beta = 0.5$.

**Strategy.** The second test, $\phi(2\alpha)\ge\phi(0) + 2\epsilon\phi'(0)\alpha$, rules out steps that are too short. Backtracking only uses the first test ([[c-armijo]]).
""",
        deeper=["c-armijo", "c-exact-line-search"],
        source="Exercise 2, question 5",
        problems=[
            problem("x-e25-a", "Set up",
                    r"$\nabla f(2,1) = (4, 8)$.",
                    [expr(r"Type $\phi(\alpha)$.", _phi25.subs(al, alpha), ["alpha"], ranges={"alpha": [0, 1]}),
                     num(r"$\phi'(0)$?", _d25)]),
            problem("x-e25-b", "The two-sided interval",
                    r"$\phi(\alpha) = 272\alpha^2 - 80\alpha + 8$, $\epsilon = 0.2$.",
                    [num("Upper end (first test)?", _hi25, tol=0.002), num("Lower end (second test)?", _lo25, tol=0.002,
                                                                              explain="$[2/17, 4/17]\\approx[0.118, 0.235]$.")]),
            problem("x-e25-c", "Backtrack",
                    r"Right-hand side $\phi(0) + 0.2\,\phi'(0)\,\alpha = 8 - 16\alpha$.",
                    [choice("$\\alpha = 1$: $\\phi(1) = 200$ against $-8$. Pass or fail?", [opt("Fail: halve", True), opt("Pass", why="200 is far above $-8$.")]),
                     num(r"$\alpha = 0.25$: what is $\phi(0.25)$?", _trials25[2][1], explain="5 against a right-hand side of 4: still fails."),
                     num(r"The accepted step?", _trials25[-1][0], tol=0.002, explain="$\\alpha = 1/8$: $\\phi = 2.25\\le6$. Four trials."),
                     choice("Does $\\alpha = 0.125$ also pass the second test, and how does it compare with the exact step $5/34\\approx0.147$?",
                            [opt("Yes, it's inside $[0.118, 0.235]$ and a little shorter than exact", True),
                             opt("No, it's too short", why="$0.125 > 2/17\\approx0.118$.")])]),
        ]),
    concept(
        "x-e2-bfgs", "Exercise 2.6: one BFGS update by hand", 3, E2,
        r"""
**The question.** On $f = x_1^2 + x_1x_2 + 2x_2^2$ from $\mathbf{x}_0 = (1, 0)$ with $\hat{\mathbf{H}}_0 = \mathbf{I}$ and $\alpha_0 = 0.5$: compute $\mathbf{s}_0$, $\mathbf{y}_0$, the BFGS update $\hat{\mathbf{H}}_1$, check the secant condition, and compare the next direction with Newton's.

**Strategy.** Keep the bookkeeping straight: $\mathbf{s} = \mathbf{x}_1 - \mathbf{x}_0$, $\mathbf{y} = \nabla f_1 - \nabla f_0$ ([[c-quasi-newton]]).
""",
        deeper=["c-quasi-newton", "c-newton"],
        source="Exercise 2, question 6",
        problems=[
            problem("x-e26-a", "Step and gradient change",
                    r"$\nabla f = (2x_1 + x_2,\ x_1 + 4x_2)$, so $\nabla f(\mathbf{x}_0) = (2, 1)$.",
                    [num(r"$s_{0,1}$ (first component of $\mathbf{s}_0 = -0.5\,\nabla f_0$)?", _s0[0]),
                     num(r"$y_{0,2}$ (second component of $\mathbf{y}_0$, with $\mathbf{x}_1 = (0, -0.5)$)?", _y0[1]),
                     num(r"$\mathbf{y}_0^T\mathbf{s}_0$?", _ys, explain="Positive, so the update keeps $\\hat{\\mathbf{H}}$ positive definite. That's the curvature condition.")]),
            problem("x-e26-b", "The update",
                    r"$\hat{\mathbf{H}}_1 = \mathbf{I} - \dfrac{\mathbf{s}\mathbf{s}^T}{\mathbf{s}^T\mathbf{s}} + \dfrac{\mathbf{y}\mathbf{y}^T}{\mathbf{y}^T\mathbf{s}}$ with $\mathbf{s} = (-1, -0.5)$, $\mathbf{y} = (-2.5, -3)$.",
                    [num(r"$(\hat{H}_1)_{11}$?", _Hh1[0, 0], tol=0.002), num(r"$(\hat{H}_1)_{12}$?", _Hh1[0, 1], tol=0.002),
                     choice("The true Hessian is $\\begin{bmatrix}2 & 1\\\\1 & 4\\end{bmatrix}$. What does $\\hat{\\mathbf{H}}_1$ get exactly right?",
                            [opt("Its action along $\\mathbf{s}_0$: $\\hat{\\mathbf{H}}_1\\mathbf{s}_0 = \\mathbf{y}_0$ (the secant condition)", True),
                             opt("Every entry", why="$1.7625\\ne2$; one update only learns one direction of curvature."),
                             opt("Nothing yet", why="The secant condition holds exactly by construction.")])]),
            problem("x-e26-c", "Next direction",
                    r"At $\mathbf{x}_1 = (0, -0.5)$, $\nabla f_1 = (-0.5, -2)$.",
                    [choice("Is $\\mathbf{d}_1 = -\\hat{\\mathbf{H}}_1^{-1}\\nabla f_1$ a descent direction?",
                            [opt("Yes: $\\hat{\\mathbf{H}}_1$ is positive definite, so $\\nabla f_1^T\\mathbf{d}_1 < 0$", True), opt("Can't tell without a line search", why="Descent only needs the sign of $\\nabla f^T\\mathbf{d}$.")]),
                     num(r"A full Newton step from $\mathbf{x}_1$ lands at $x_1 = $?", _nt26[0]),
                     num(r"and $x_2 = $?", _nt26[1], explain="The minimizer $(0, 0)$ in one step, since $f$ is quadratic.")]),
        ]),
    concept(
        "x-e2-canal", "Exercise 2.7: the best canal cross-section", 3, E2,
        r"""
**The question.** A symmetric trapezoidal canal: height $h$, base $b$, wall angle $\phi$. Maximize flow (minimize the wetted perimeter) with the area fixed at 100 ft². Formulate in negative null form, then solve with unconstrained optimality conditions.

**Convention used here:** $\phi$ is the angle each wall makes with the horizontal, so the area is $h(b + h\cot\phi)$ and the perimeter is $b + 2h/\sin\phi$. (If your figure measures $\phi$ differently, the optimal *shape* is the same; only the number you report for the angle changes.)

**Strategy.** The equality constraint lets you eliminate $b$, which makes the problem unconstrained in $(h, \phi)$ ([[c-negative-null-form]], [[c-fonc]]).
""",
        deeper=["c-negative-null-form", "c-fonc", "c-sosc"],
        source="Exercise 2, question 7 (Papalambros & Wilde 4.16)",
        problems=[
            problem("x-e27-a", "Formulate",
                    r"Area $A = h(b + h\cot\phi)$, perimeter $P = b + 2h/\sin\phi$.",
                    [choice("Which is the negative null form?",
                            [opt("$\\min P$ s.t. $h(b + h\\cot\\phi) - 100 = 0$", True),
                             opt("$\\max 1/P$ s.t. $h(b + h\\cot\\phi)\\ge100$", why="Negative null form minimizes, and writes constraints as $g\\le0$ or $h = 0$."),
                             opt("$\\min P$ s.t. $100 - h(b + h\\cot\\phi)\\le0$", why="The area must **equal** 100; an inequality is a relaxation you'd have to justify.")]),
                     expr(r"Solve the constraint for $b$ and type it (use `phi`; write $\cot\phi$ as `cos(phi)/sin(phi)`).", _bsub, ["h", "phi"],
                          ranges={"h": [2, 10], "phi": [0.4, 1.4]})]),
            problem("x-e27-b", "Solve",
                    r"$P(h, \phi) = \dfrac{100}{h} - h\cot\phi + \dfrac{2h}{\sin\phi}$.",
                    [choice("$\\partial P/\\partial\\phi = h\\,\\dfrac{1 - 2\\cos\\phi}{\\sin^2\\phi}$. Setting it to zero gives:",
                            [opt("$\\cos\\phi = 1/2$, so $\\phi = 60°$", True), opt("$\\phi = 45°$", why="$\\cos45° = 0.707\\ne1/2$.")]),
                     num("Then $h^*$ (ft)?", _h27, tol=0.002), num("and $b^*$ (ft)?", _b27, tol=0.002,
                         explain="$b^* = 8.774$ ft, and each wall is $2h/\\sqrt3 = 8.774$ ft too: half a regular hexagon."),
                     choice("Nature?", [opt("A minimizer: the Hessian of $P$ is positive definite there", True), opt("A saddle", why="Both eigenvalues of $\\nabla^2P$ at the point are positive.")])]),
        ]),

    concept(
        "x-e3-kkt-unbounded", "Exercise 3.1: a KKT point that isn't the answer", 3, E3,
        r"""
**The question.** Maximize $f = 3x_1 - x_2 + x_3^2$ subject to $g_1 = x_1 + x_2 + x_3\le0$ and $h_1 = -x_1 + 2x_2 + x_3^2 = 0$, using the KKT conditions.

**Strategy.** Convert to $\min -f$. Guess $g_1$ active, solve, check $\mu\ge0$ ([[c-kkt]]). Then, as always, ask whether the KKT point is really the optimum ([[c-constrained-sosc]]).
""",
        deeper=["c-kkt", "c-constrained-sosc", "c-boundedness"],
        source="Exercise 3, question 1 (Papalambros & Wilde 5.8)",
        problems=[
            problem("x-e31-a", "The KKT system",
                    r"$\nabla(-f) + \mu\nabla g_1 + \lambda\nabla h_1 = \mathbf{0}$: $\ -3 + \mu - \lambda = 0$, $\ 1 + \mu + 2\lambda = 0$, $\ -2x_3 + \mu + 2\lambda x_3 = 0$.",
                    [num(r"From the first two equations, $\lambda$?", _s31[lam1], tol=0.002),
                     num(r"and $\mu$?", _s31[mu], tol=0.002, explain="$\\mu = 5/3\\ge0$: sign condition OK."),
                     num(r"Third equation: $x_3$?", _s31[x3], tol=0.002, explain="$x_3 = 5/14$; then $x_1 = -115/588$, $x_2 = -95/588$ from the two constraints.")]),
            problem("x-e31-b", "Is it the maximum?",
                    r"On the active set, eliminate $x_1$ and $x_2$: $f$ becomes $\tfrac73x_3^2 - \tfrac53x_3$.",
                    [choice("What does that tell you?",
                            [opt("$f\\to\\infty$ as $|x_3|\\to\\infty$ along feasible points: the problem has no maximum, and the KKT point is a minimum along that curve", True),
                             opt("The KKT point is the maximizer, since $\\mu\\ge0$", why="KKT is necessary, not sufficient. Here the second-order check fails badly."),
                             opt("The problem is infeasible", why="Every $x_3$ gives a feasible point on the boundary.")],
                            explain="The lesson of the exercise: always check boundedness and second-order conditions after finding a KKT point.")]),
        ]),
    concept(
        "x-e3-reduced-b", "Exercise 3.2: reduced gradient on a circle, for every b", 3, E3,
        r"""
**The question.** $\min -2x_1 - bx_2$ s.t. $x_1^2 + x_2^2 = 5$. The solution is $(1, 2)$ for one value of $b$. Use reduced gradients to solve it for every $b$.

**Strategy.** Take $x_1$ as the decision and $x_2$ as the state; set the reduced gradient to zero ([[c-reduced-gradient]]).
""",
        deeper=["c-reduced-gradient", "c-tangent-normal"],
        source="Exercise 3, question 2 (Papalambros & Wilde 5.18)",
        problems=[
            problem("x-e32-a", "The reduced gradient",
                    r"$\dfrac{dz}{dx_1} = \dfrac{\partial f}{\partial x_1} - \dfrac{\partial f}{\partial x_2}\dfrac{\partial h/\partial x_1}{\partial h/\partial x_2}$.",
                    [expr(r"Type $dz/dx_1$ in terms of $x_1, x_2, b$.", _red32, ["x1", "x2", "b"], ranges={"x1": [0.5, 2], "x2": [0.5, 2], "b": [1, 5]}),
                     num(r"For which $b$ is $(1, 2)$ stationary?", _b32)]),
            problem("x-e32-b", "Every b",
                    r"$dz/dx_1 = 0$ gives $x_2/x_1 = b/2$; the point lies on the circle of radius $\sqrt5$.",
                    [expr(r"Type $x_1^*(b)$ for the minimizer (the root with $x_1 > 0$).", _x1b, ["b"], ranges={"b": [0.5, 5]}),
                     choice("The other root, $-\\mathbf{x}^*$, is:",
                            [opt("The maximizer of $f$ on the circle", True), opt("Another minimizer", why="$f$ is linear: opposite points give opposite values of $f$.")])]),
        ]),

    concept(
        "x-e4-cusp", "Exercise 4.1: Kuhn and Tucker's cusp, where KKT fails at the optimum", 3, E4,
        r"""
**The question.** $\min f = -x_1$ s.t. $g_1 = x_2 - (1 - x_1)^3\le0$ and $x_2\ge0$. Solve graphically, then apply the optimality conditions and monotonicity.

**Strategy.** The feasible region is a horn that pinches to a point at $(1, 0)$. Check regularity there before trusting KKT ([[c-dof-regularity]], [[c-kkt]]).
""",
        deeper=["c-kkt", "c-dof-regularity", "c-monotonicity"],
        source="Exercise 4, question 1 (Papalambros & Wilde 5.4; Kuhn & Tucker 1951)",
        problems=[
            problem("x-e41-a", "Graphically",
                    r"$x_2\ge0$ and $x_2\le(1 - x_1)^3$ need $(1 - x_1)^3\ge0$.",
                    [num(r"The largest feasible $x_1$, so $x_1^*$?", 1, explain="The optimum is the cusp $(1, 0)$, with both constraints active.")]),
            problem("x-e41-b", "KKT at the cusp",
                    r"At $(1, 0)$: $\nabla f = (-1, 0)$, $\nabla g_1 = (0, 1)$, $\nabla g_2 = (0, -1)$ for $g_2 = -x_2$.",
                    [choice("Can $-\\nabla f = \\mu_1\\nabla g_1 + \\mu_2\\nabla g_2$ hold?",
                            [opt("No: both constraint gradients are vertical, $-\\nabla f$ is horizontal", True),
                             opt("Yes, with $\\mu_1 = \\mu_2 = 1$", why="That gives $(0, 0)$, not $(1, 0)$.")]),
                     choice("Why doesn't that contradict the KKT theorem?",
                            [opt("The active gradients are linearly dependent, so $(1, 0)$ isn't a regular point and KKT needn't hold", True),
                             opt("Because $(1, 0)$ isn't really the optimum", why="It is: the graph shows no feasible point has a larger $x_1$."),
                             opt("Because $f$ is linear", why="Linear objectives are fine; the trouble is the constraints' geometry.")],
                            explain="Monotonicity still works: $f$ decreases in $x_1$, so something must bound $x_1$, and only the pair of constraints together does.")]),
        ]),
    concept(
        "x-e4-ellipsoid", "Exercise 4.2: nearest point on an ellipsoid with an extra inequality", 3, E4,
        r"""
**The question.** $\min x_1^2 + x_2^2 + x_3^2$ s.t. $\tfrac{x_1^2}{4} + \tfrac{x_2^2}{5} + \tfrac{x_3^2}{25} = 1$ and $x_1 + x_2 - x_3\le0$, by reduced gradients.

**Strategy.** Reduced gradients handle equalities, so treat the inequality by cases: inactive (ignore it, then check it) or active (add it as a second equality) ([[c-reduced-gradient]], [[c-active-set]]).
""",
        deeper=["c-reduced-gradient", "c-active-set"],
        source="Exercise 4, question 2",
        problems=[
            problem("x-e42-a", "Inequality inactive first",
                    r"On the ellipsoid alone, the stationary points of $\|\mathbf{x}\|^2$ are the ends of the axes: $(\pm2,0,0)$, $(0,\pm\sqrt5,0)$, $(0,0,\pm5)$.",
                    [num(r"The smallest $f$ among them?", 4),
                     choice("Of $(2, 0, 0)$ and $(-2, 0, 0)$, which satisfy $x_1 + x_2 - x_3\le0$?",
                            [opt("Only $(-2, 0, 0)$", True), opt("Both", why="At $(2,0,0)$, $x_1 + x_2 - x_3 = 2 > 0$."), opt("Neither", why="At $(-2,0,0)$ it's $-2\\le0$.")]),
                     choice("So the minimizer is:",
                            [opt("$(-2, 0, 0)$ with $f^* = 4$, and the inequality is inactive there", True),
                             opt("Somewhere on $x_1 + x_2 = x_3$", why="The unconstrained-by-$h_2$ minimum is already feasible, and nothing feasible can beat the minimum over the larger set.")],
                            explain="The active case (both constraints as equalities) still has stationary points, which the full exercise asks you to find, but none of them can beat $f = 4$.")]),
        ]),
]
