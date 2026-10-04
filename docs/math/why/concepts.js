// The "Why?" concept network. Valid JSON after the "=" so tests/check_concepts.py can read it.
// Spec: design/specs/2026-10-04-why-network-design.md. [[id]] or [[id|label]] in a body becomes a button.
window.CONCEPTS = [
  {
    "id": "function",
    "title": "A function turns each input into one output",
    "body": "A function is a rule: give it an input, and it gives back exactly one output. Write it as $f(x)$, read \"f of x\". The rule $f(x) = x^2$ turns 3 into 9 and −3 into 9 as well. Two inputs can share an output, but one input can never have two.\n\nA graph draws every input–output pair at once: the input runs along the horizontal axis and the output is the height above it. Everything in calculus is about how a function's outputs change as its input moves.",
    "math": ["f(x) = x^2"],
    "widget": {"type": "secant", "mode": "trace", "f": "square", "x0": 1.5, "prompt": "Drag the point along the curve and read the output for each input."},
    "deeper": [],
    "related": ["limit"],
    "foundation": true,
    "claims": [{"sympy": "(x**2).subs(x, 3) - (x**2).subs(x, -3)", "equals": "0"}]
  },
  {
    "id": "limit",
    "title": "A limit is the value something settles toward",
    "body": "Sometimes a formula breaks at one exact point but behaves perfectly near it. $\\frac{x^2-1}{x-1}$ is $\\frac{0}{0}$ at $x = 1$, which means nothing. But at $x = 1.1$ it's 2.1, at $1.01$ it's 2.01, at $1.001$ it's 2.001. The outputs settle toward 2. We say the limit as $x$ approaches 1 is 2.\n\nThe precise version: for any tolerance $\\varepsilon$ you choose, however tiny, there is a distance $\\delta$ so that every $x$ within $\\delta$ of 1 (other than 1 itself) gives an output within $\\varepsilon$ of 2. A limit never needs the value at the point itself, only the values arbitrarily close to it. That idea is what lets calculus talk about \"instantaneous\" speed and exact areas.",
    "math": ["\\lim_{x\\to 1} \\frac{x^2-1}{x-1} = 2"],
    "widget": {"type": "limit-zoom", "g": "hole", "at": 1, "limit": 2, "epsilon": true, "prompt": "Shrink ε. There's always a window around x = 1 where every output stays inside the band."},
    "deeper": [],
    "related": ["function"],
    "foundation": true,
    "claims": [{"sympy": "limit((x**2 - 1)/(x - 1), x, 1)", "equals": "2"}]
  },
  {
    "id": "unit-circle",
    "title": "Sine and cosine are coordinates on a circle",
    "body": "Draw a circle of radius 1 centred at the origin. Start at the point $(1, 0)$ and walk counterclockwise around the circle through an angle $\\theta$. The point you land on has coordinates $(\\cos\\theta, \\sin\\theta)$. That is the definition: cosine is how far right, sine is how far up.\n\nEverything else follows. Since the point is 1 away from the centre, Pythagoras gives $\\cos^2\\theta + \\sin^2\\theta = 1$. After a full turn ($2\\pi$ radians) you're back where you started, so both repeat every $2\\pi$. Angles here are measured in radians: the length of arc you walked. That's why the circle has radius 1.",
    "math": ["(\\cos\\theta, \\sin\\theta)", "\\cos^2\\theta + \\sin^2\\theta = 1"],
    "widget": {"type": "unit-circle", "mode": "basic", "prompt": "Drag the point around the circle and watch sin θ and cos θ change."},
    "deeper": [],
    "related": ["area-shapes"],
    "foundation": true,
    "claims": [{"sympy": "sin(t)**2 + cos(t)**2", "equals": "1"}]
  },
  {
    "id": "area-shapes",
    "title": "Area of rectangles and triangles",
    "body": "Area counts how many unit squares fit inside a shape. A rectangle $w$ wide and $h$ tall holds $w \\times h$ of them; that's the starting point.\n\nCut a rectangle along its diagonal and you get two identical right triangles, so each has half the area: $\\frac{1}{2} w h$. Any triangle can be split into two right triangles, so every triangle's area is $\\frac{1}{2} \\times \\text{base} \\times \\text{height}$. A region under a curve isn't made of rectangles or triangles, but it can be approximated by them as closely as we like, which is exactly what integrals do.",
    "math": ["A_{\\text{rectangle}} = w h", "A_{\\text{triangle}} = \\tfrac{1}{2} b h"],
    "widget": {"type": "riemann", "mode": "shapes", "prompt": "Change the width and height; the triangle is always exactly half the rectangle."},
    "deeper": [],
    "related": ["unit-circle"],
    "foundation": true,
    "claims": [{"sympy": "integrate(a*x/b, (x, 0, b))", "equals": "a*b/2"}]
  },
  {
    "id": "fraction-as-parts",
    "title": "A fraction is some of a whole cut into equal parts",
    "body": "$\\frac{3}{4}$ means: cut a whole into 4 equal parts and take 3 of them. The bottom number (the denominator) says how many equal parts the whole has; the top number (the numerator) says how many you have.\n\nThe parts must be equal, or the fraction means nothing. $\\frac{4}{4}$ is the whole thing, and $\\frac{0}{4}$ is none of it. A fraction is also a division: $\\frac{3}{4}$ is $3 \\div 4 = 0.75$, the size of one share when 3 things are split among 4.",
    "math": ["\\frac{3}{4} = 3 \\div 4 = 0.75"],
    "widget": {"type": "fraction-bar", "mode": "parts", "parts": 4, "filled": 3, "prompt": "Change how many parts the bar is cut into and how many are filled."},
    "deeper": [],
    "related": ["conservation"],
    "foundation": true,
    "claims": [{"sympy": "Rational(3, 4)", "equals": "0.75"}]
  },
  {
    "id": "conservation",
    "title": "Pouring moves stuff around; it never creates or destroys it",
    "body": "If a cup holds 2 marks of liquid and 1 mark of it is concentrate, then pouring, splitting or combining can move that concentrate between cups, but the total amount of concentrate stays exactly the same. Water works the same way.\n\nThis is a conservation law: some quantity stays the same through every change. It lets you track a mixture by bookkeeping alone. Add up the concentrate before and after, and the totals must match.",
    "math": ["\\text{concentrate}_{\\text{before}} = \\text{concentrate}_{\\text{after}}"],
    "widget": {"type": "fraction-bar", "mode": "pour", "prompt": "Pour between the cups. The total concentrate counter never changes."},
    "deeper": [],
    "related": ["fraction-as-parts"],
    "foundation": true,
    "claims": [{"sympy": "Rational(1, 2)*2 + Rational(1, 4)*2", "equals": "Rational(3, 2)"}]
  }
]
