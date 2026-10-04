// The "Why?" concept network. Valid JSON after the "=" so tests/check_concepts.py can read it.
// Spec: design/specs/2026-10-04-why-network-design.md. [[id]] or [[id|label]] in a body becomes a button.
window.CONCEPTS = [
  {
    "id": "function",
    "title": "A function turns each input into one output",
    "body": "A function is a rule: give it an input, and it gives back exactly one output. Write it as $f(x)$, read \"f of x\". The rule $f(x) = x^2$ turns 3 into 9 and −3 into 9 as well. Two inputs can share an output, but one input can never have two.\n\nA graph draws every input–output pair at once: the input runs along the horizontal axis and the output is the height above it. Everything in calculus is about how a function's outputs change as its input moves.",
    "math": [
      "f(x) = x^2"
    ],
    "widget": {
      "type": "secant",
      "mode": "trace",
      "f": "square",
      "x0": 1.5,
      "prompt": "Drag the point along the curve and read the output for each input."
    },
    "deeper": [],
    "related": [
      "limit"
    ],
    "foundation": true,
    "claims": [
      {
        "sympy": "(x**2).subs(x, 3) - (x**2).subs(x, -3)",
        "equals": "0"
      }
    ]
  },
  {
    "id": "limit",
    "title": "A limit is the value something settles toward",
    "body": "Sometimes a formula breaks at one exact point but behaves perfectly near it. $\\frac{x^2-1}{x-1}$ is $\\frac{0}{0}$ at $x = 1$, which means nothing. But at $x = 1.1$ it's 2.1, at $1.01$ it's 2.01, at $1.001$ it's 2.001. The outputs settle toward 2. We say the limit as $x$ approaches 1 is 2.\n\nThe precise version: for any tolerance $\\varepsilon$ you choose, however tiny, there is a distance $\\delta$ so that every $x$ within $\\delta$ of 1 (other than 1 itself) gives an output within $\\varepsilon$ of 2. A limit never needs the value at the point itself, only the values arbitrarily close to it. That idea is what lets calculus talk about \"instantaneous\" speed and exact areas.",
    "math": [
      "\\lim_{x\\to 1} \\frac{x^2-1}{x-1} = 2"
    ],
    "widget": {
      "type": "limit-zoom",
      "g": "hole",
      "at": 1,
      "limit": 2,
      "epsilon": true,
      "prompt": "Shrink ε. There's always a window around x = 1 where every output stays inside the band."
    },
    "deeper": [],
    "related": [
      "function"
    ],
    "foundation": true,
    "claims": [
      {
        "sympy": "limit((x**2 - 1)/(x - 1), x, 1)",
        "equals": "2"
      }
    ]
  },
  {
    "id": "unit-circle",
    "title": "Sine and cosine are coordinates on a circle",
    "body": "Draw a circle of radius 1 centred at the origin. Start at the point $(1, 0)$ and walk counterclockwise around the circle through an angle $\\theta$. The point you land on has coordinates $(\\cos\\theta, \\sin\\theta)$. That is the definition: cosine is how far right, sine is how far up.\n\nEverything else follows. Since the point is 1 away from the centre, Pythagoras gives $\\cos^2\\theta + \\sin^2\\theta = 1$. After a full turn ($2\\pi$ radians) you're back where you started, so both repeat every $2\\pi$. Angles here are measured in radians: the length of arc you walked. That's why the circle has radius 1.",
    "math": [
      "(\\cos\\theta, \\sin\\theta)",
      "\\cos^2\\theta + \\sin^2\\theta = 1"
    ],
    "widget": {
      "type": "unit-circle",
      "mode": "basic",
      "prompt": "Drag the point around the circle and watch sin θ and cos θ change."
    },
    "deeper": [],
    "related": [
      "area-shapes"
    ],
    "foundation": true,
    "claims": [
      {
        "sympy": "sin(t)**2 + cos(t)**2",
        "equals": "1"
      }
    ]
  },
  {
    "id": "area-shapes",
    "title": "Area of rectangles and triangles",
    "body": "Area counts how many unit squares fit inside a shape. A rectangle $w$ wide and $h$ tall holds $w \\times h$ of them; that's the starting point.\n\nCut a rectangle along its diagonal and you get two identical right triangles, so each has half the area: $\\frac{1}{2} w h$. Drop a perpendicular from a triangle's top corner to its base (extended if needed) and any triangle becomes the sum or difference of two right triangles, so every triangle's area is $\\frac{1}{2} \\times \\text{base} \\times \\text{height}$. A region under a curve isn't made of rectangles or triangles, but it can be approximated by them as closely as we like, which is exactly what integrals do.",
    "math": [
      "A_{\\text{rectangle}} = w h",
      "A_{\\text{triangle}} = \\tfrac{1}{2} b h"
    ],
    "widget": {
      "type": "riemann",
      "mode": "shapes",
      "prompt": "Change the width and height; the triangle is always exactly half the rectangle."
    },
    "deeper": [],
    "related": [
      "unit-circle"
    ],
    "foundation": true,
    "claims": [
      {
        "sympy": "integrate(a*x/b, (x, 0, b))",
        "equals": "a*b/2"
      }
    ]
  },
  {
    "id": "fraction-as-parts",
    "title": "A fraction is some of a whole cut into equal parts",
    "body": "$\\frac{3}{4}$ means: cut a whole into 4 equal parts and take 3 of them. The bottom number (the denominator) says how many equal parts the whole has; the top number (the numerator) says how many you have.\n\nThe parts must be equal, or the fraction means nothing. $\\frac{4}{4}$ is the whole thing, and $\\frac{0}{4}$ is none of it. A fraction is also a division: $\\frac{3}{4}$ is $3 \\div 4 = 0.75$, the size of one share when 3 things are split among 4.",
    "math": [
      "\\frac{3}{4} = 3 \\div 4 = 0.75"
    ],
    "widget": {
      "type": "fraction-bar",
      "mode": "parts",
      "parts": 4,
      "filled": 3,
      "prompt": "Change how many parts the bar is cut into and how many are filled."
    },
    "deeper": [],
    "related": [
      "conservation"
    ],
    "foundation": true,
    "claims": [
      {
        "sympy": "Rational(3, 4)",
        "equals": "0.75"
      }
    ]
  },
  {
    "id": "conservation",
    "title": "Pouring moves stuff around; it never creates or destroys it",
    "body": "If a cup holds 2 marks of liquid and 1 mark of it is concentrate, then pouring, splitting or combining can move that concentrate between cups, but the total amount of concentrate stays exactly the same. Water works the same way.\n\nThis is a conservation law: some quantity stays the same through every change. It lets you track a mixture by bookkeeping alone. Add up the concentrate before and after, and the totals must match.",
    "math": [
      "\\text{concentrate}_{\\text{before}} = \\text{concentrate}_{\\text{after}}"
    ],
    "widget": {
      "type": "fraction-bar",
      "mode": "pour",
      "prompt": "Pour between the cups. The total concentrate counter never changes."
    },
    "deeper": [],
    "related": [
      "fraction-as-parts"
    ],
    "foundation": true,
    "claims": [
      {
        "sympy": "Rational(1, 2)*2 + Rational(1, 4)*2",
        "equals": "Rational(3, 2)"
      }
    ]
  },
  {
    "id": "ratio-vs-fraction",
    "title": "A ratio compares parts; a fraction compares a part with the whole",
    "body": "\"1 to 3\" is a ratio: for every 1 part of tea there are 3 parts of water. It compares the parts with each other. A fraction compares one part with the whole: here the whole drink is $1 + 3 = 4$ parts, so tea is $\\frac{1}{4}$ of it.\n\nThe classic slip is reading $1:3$ as $\\frac{1}{3}$. That would be 1 part tea in 3 parts total, which is the same as 1 to 2. Always add the parts first to find the whole, then use [[fraction-as-parts|the fraction rule]]: the part over the whole. That fraction is the drink's [[strength]].",
    "math": [
      "a : b \\quad\\Rightarrow\\quad \\frac{a}{a+b}",
      "1 : 3 \\quad\\Rightarrow\\quad \\frac{1}{4}"
    ],
    "widget": {
      "type": "fraction-bar",
      "mode": "ratio",
      "a": 1,
      "b": 3,
      "prompt": "Change the parts of each. The concentrate's share is always its parts over all the parts."
    },
    "deeper": [
      "fraction-as-parts"
    ],
    "related": [
      "strength"
    ],
    "foundation": false,
    "claims": [
      {
        "sympy": "Rational(1, 1 + 3)",
        "equals": "Rational(1, 4)"
      }
    ]
  },
  {
    "id": "strength",
    "title": "Strength is concentrate divided by the whole drink",
    "body": "The strength of a drink is the fraction of it that is concentrate: $\\text{strength} = \\frac{\\text{concentrate}}{\\text{total}}$. 1 mark of tea in a 4-mark drink is $\\frac{1}{4}$ strength, no matter how big the marks are.\n\nIt's just [[fraction-as-parts|a fraction]] where the whole is the drink. And because [[conservation|concentrate is never created or destroyed]], you can always find a strength by counting how much concentrate went in and how much liquid there is in total.",
    "math": [
      "\\text{strength} = \\frac{\\text{concentrate}}{\\text{total volume}}"
    ],
    "widget": {
      "type": "fraction-bar",
      "mode": "cup",
      "marks": 4,
      "conc": 1,
      "prompt": "Change the total and the concentrate. Strength is always concentrate over total."
    },
    "deeper": [
      "fraction-as-parts",
      "conservation"
    ],
    "related": [
      "ratio-vs-fraction"
    ],
    "foundation": false,
    "claims": [
      {
        "sympy": "Rational(1, 4)",
        "equals": "0.25"
      }
    ]
  },
  {
    "id": "pouring-keeps-strength",
    "title": "Pouring some of a drink doesn't change its strength",
    "body": "A well-mixed drink is the same all the way through: every mark of it has the same share of concentrate. So when you pour 1 mark out of a $\\frac{1}{2}$-strength drink, that mark is $\\frac{1}{2}$ concentrate, and what stays behind is still $\\frac{1}{2}$ strength.\n\nCheck it by bookkeeping: 2 marks at $\\frac{1}{2}$ hold 1 mark of concentrate. Pour out 1 mark carrying $\\frac{1}{2}$ mark of concentrate: 1 mark with $\\frac{1}{2}$ mark of concentrate remains, still [[strength|strength]] $\\frac{1}{2}$, and [[conservation|nothing went missing]]. This is what lets you make a drink, then use part of it as an ingredient.",
    "math": [
      "\\frac{c - c\\,\\frac{k}{m}}{m - k} = \\frac{c}{m}"
    ],
    "widget": {
      "type": "fraction-bar",
      "mode": "pour",
      "prompt": "Pour back and forth. Each cup's strength only changes when liquids of different strengths meet."
    },
    "deeper": [
      "strength",
      "conservation"
    ],
    "related": [
      "diluting-multiplies"
    ],
    "foundation": false,
    "claims": [
      {
        "sympy": "simplify((a - a*u/b)/(b - u) - a/b)",
        "equals": "0"
      }
    ]
  },
  {
    "id": "fraction-of-a-fraction",
    "title": "A fraction of a fraction is a product",
    "body": "Half of a quarter: cut a whole into 4 columns and take one, then cut that column into 2 rows and take one. You now hold 1 of the $4 \\times 2 = 8$ small pieces, so $\\frac{1}{2}$ of $\\frac{1}{4}$ is $\\frac{1}{8}$.\n\nIn general, \"$\\frac{a}{b}$ of $\\frac{c}{d}$\" means $\\frac{a}{b} \\times \\frac{c}{d} = \\frac{ac}{bd}$: the pieces get smaller in both directions, so the denominators multiply. This rests on [[fraction-as-parts|what a fraction is]], and the same picture shows why [[equivalent-fractions|different-looking fractions can be equal]].",
    "math": [
      "\\frac{1}{2} \\times \\frac{1}{4} = \\frac{1}{8}",
      "\\frac{a}{b} \\times \\frac{c}{d} = \\frac{ac}{bd}"
    ],
    "widget": {
      "type": "fraction-bar",
      "mode": "grid",
      "kind": "of",
      "p": 2,
      "q": 4,
      "prompt": "Take 1 row of 1 column. Count how many small pieces the whole has."
    },
    "deeper": [
      "fraction-as-parts"
    ],
    "related": [
      "equivalent-fractions"
    ],
    "foundation": false,
    "claims": [
      {
        "sympy": "Rational(1, 2) * Rational(1, 4)",
        "equals": "Rational(1, 8)"
      }
    ]
  },
  {
    "id": "diluting-multiplies",
    "title": "Diluting multiplies the strength",
    "body": "Add water and the concentrate stays the same while the total grows. Double the volume with an equal amount of water and the same concentrate is spread through twice as much drink, so the [[strength]] is multiplied by $\\frac{1}{2}$, not reduced by a fixed amount.\n\nMore generally, going from volume $m$ to volume $M$ multiplies strength by $\\frac{m}{M}$: you're taking [[fraction-of-a-fraction|a fraction of a fraction]]. That's why diluting a $\\frac{1}{4}$ drink with equal water gives $\\frac{1}{8}$: half of what it was, not $\\frac{1}{4}$ minus some fixed amount.",
    "math": [
      "s_{\\text{new}} = s \\times \\frac{m}{M}",
      "\\frac{1}{4} \\times \\frac{1}{2} = \\frac{1}{8}"
    ],
    "widget": {
      "type": "fraction-bar",
      "mode": "dilute",
      "marks": 2,
      "conc": 1,
      "prompt": "Add an equal amount of water, again and again. Watch the strength halve each time."
    },
    "deeper": [
      "strength",
      "fraction-of-a-fraction"
    ],
    "related": [
      "weighted-average"
    ],
    "foundation": false,
    "claims": [
      {
        "sympy": "Rational(1, 4) * Rational(2, 4)",
        "equals": "Rational(1, 8)"
      }
    ]
  },
  {
    "id": "serial-dilution",
    "title": "Serial dilution: dilute something already diluted",
    "body": "A 4-mark cup can't hold 8 equal parts, so you can't measure out $\\frac{1}{8}$ directly. But you can dilute twice. Make a drink, take some of it ([[pouring-keeps-strength|which keeps its strength]]), and add an equal amount of water: that [[diluting-multiplies|halves the strength]]. Repeat, and each round multiplies by $\\frac{1}{2}$ again.\n\nStarting from pure concentrate: $\\frac{1}{2}, \\frac{1}{4}, \\frac{1}{8}, \\frac{1}{16}, \\dots$: that is $\\left(\\frac{1}{2}\\right)^n$ after $n$ rounds. Chemists and biologists use exactly this to reach tiny concentrations with ordinary glassware. Every result is also an [[equivalent-fractions|ordinary fraction]] of the original.",
    "math": [
      "s_n = \\left(\\tfrac{1}{2}\\right)^n"
    ],
    "widget": {
      "type": "fraction-bar",
      "mode": "serial",
      "rounds": 3,
      "prompt": "Add rounds of 'keep a mark, add a mark of water'. Each one halves the strength."
    },
    "deeper": [
      "diluting-multiplies",
      "pouring-keeps-strength"
    ],
    "related": [
      "equivalent-fractions"
    ],
    "foundation": false,
    "claims": [
      {
        "sympy": "Rational(1, 2)**3",
        "equals": "Rational(1, 8)"
      }
    ]
  },
  {
    "id": "weighted-average",
    "title": "Mixing two drinks gives a weighted average",
    "body": "Pour two drinks together and count: the total concentrate is the sum of each drink's concentrate ([[conservation|nothing is lost]]), and the total volume is the sum of the volumes. So the mix's [[strength]] is $\\frac{m_1 s_1 + m_2 s_2}{m_1 + m_2}$.\n\nThat's a weighted average: each strength counts in proportion to how much of that drink there is. With equal amounts it becomes the plain average, which is why 1 mark at $\\frac{1}{2}$ plus 1 mark at $\\frac{1}{4}$ gives $\\frac{3}{8}$, halfway between. The result always lands between the two strengths: never above the stronger, never below the weaker.",
    "math": [
      "s = \\frac{m_1 s_1 + m_2 s_2}{m_1 + m_2}"
    ],
    "widget": {
      "type": "fraction-bar",
      "mode": "combine",
      "m1": 1,
      "s1": 0.5,
      "m2": 1,
      "s2": 0.25,
      "prompt": "Change how much of each drink goes in. The mix slides toward whichever there's more of."
    },
    "deeper": [
      "strength",
      "conservation"
    ],
    "related": [
      "average-of-function"
    ],
    "foundation": false,
    "claims": [
      {
        "sympy": "(1*Rational(1, 2) + 1*Rational(1, 4)) / 2",
        "equals": "Rational(3, 8)"
      },
      {
        "sympy": "(1*Rational(1, 2) + 3*Rational(1, 4)) / 4",
        "equals": "Rational(5, 16)"
      }
    ]
  },
  {
    "id": "equivalent-fractions",
    "title": "Equivalent fractions: same amount, smaller pieces",
    "body": "Cut every piece of $\\frac{1}{2}$ into 2 and you hold 2 of 4 pieces: $\\frac{2}{4}$. Cut into 3 and it's $\\frac{3}{6}$. The shaded amount never changed; only the size of the pieces did. Multiplying the top and bottom by the same number gives an equal fraction.\n\nThat's why \"1 mark of tea in 2 marks\" and \"2 marks of tea in 4 marks\" are the same strength, and why [[fraction-as-parts|a fraction]] has a simplest form: divide top and bottom by everything they share. It's the same picture as [[fraction-of-a-fraction|a fraction of a fraction]], with the cuts made evenly through the whole.",
    "math": [
      "\\frac{a}{b} = \\frac{a k}{b k}",
      "\\frac{1}{2} = \\frac{2}{4} = \\frac{3}{6}"
    ],
    "widget": {
      "type": "fraction-bar",
      "mode": "grid",
      "kind": "equivalent",
      "num": 1,
      "q": 2,
      "prompt": "Cut each part into more pieces. The fraction's numbers change; the amount doesn't."
    },
    "deeper": [
      "fraction-as-parts"
    ],
    "related": [
      "fraction-of-a-fraction"
    ],
    "foundation": false,
    "claims": [
      {
        "sympy": "Rational(2, 4) - Rational(1, 2)",
        "equals": "0"
      }
    ]
  },
  {
    "id": "tc-half",
    "entry": true,
    "title": "Why does equal tea and water make half?",
    "body": "With 1 mark of tea and 1 mark of water, the cup holds 2 marks and 1 of them is tea. [[strength|Strength is tea over total]]: $\\frac{1}{2}$.\n\n2 marks of each works just as well: $\\frac{2}{4}$ is [[equivalent-fractions|the same fraction]] as $\\frac{1}{2}$. What matters is the share of the whole, not the amounts.",
    "widget": {
      "type": "fraction-bar",
      "mode": "cup",
      "marks": 2,
      "conc": 1,
      "prompt": "Try 2 of 4, or 3 of 6. Every equal split is still 1/2."
    },
    "deeper": [
      "strength",
      "equivalent-fractions"
    ],
    "related": [],
    "foundation": false
  },
  {
    "id": "tc-one-to-three",
    "entry": true,
    "title": "Why is \"1 to 3\" a quarter, not a third?",
    "body": "\"1 to 3\" is a [[ratio-vs-fraction|ratio]]: 1 part tea for every 3 parts water. The whole drink is $1 + 3 = 4$ parts, so tea is $\\frac{1}{4}$ of it. That fraction is the drink's [[strength]].\n\nThat's why 1 mark of tea and 3 marks of water fill a 4-mark cup exactly.",
    "widget": {
      "type": "fraction-bar",
      "mode": "ratio",
      "a": 1,
      "b": 3,
      "prompt": "Compare 1:3 with 1:2. Which one is really 1/3?"
    },
    "deeper": [
      "ratio-vs-fraction",
      "strength"
    ],
    "related": [],
    "foundation": false
  },
  {
    "id": "tc-one-eighth",
    "entry": true,
    "title": "Why can 4-mark cups make 1/8?",
    "body": "A cup with 4 marks can't measure 1 part in 8 directly. So make $\\frac{1}{4}$ first (1 tea, 3 water). Pour 1 mark of it into the other cup; [[pouring-keeps-strength|that mark is still 1/4 strength]]. Add 1 mark of water: the volume doubles, so [[diluting-multiplies|the strength halves]]: $\\frac{1}{4} \\times \\frac{1}{2} = \\frac{1}{8}$.\n\nDiluting a drink that's already diluted is [[serial-dilution|serial dilution]]: each round multiplies by $\\frac{1}{2}$, so a small cup can reach very small strengths.",
    "widget": {
      "type": "fraction-bar",
      "mode": "serial",
      "rounds": 3,
      "prompt": "How many rounds of halving does it take to reach 1/8? To reach 1/16?"
    },
    "deeper": [
      "serial-dilution",
      "diluting-multiplies"
    ],
    "related": [
      "pouring-keeps-strength"
    ],
    "foundation": false
  },
  {
    "id": "tc-three-eighths",
    "entry": true,
    "title": "Why do 1/2 and 1/4 mix to 3/8?",
    "body": "Count the tea. 1 mark at $\\frac{1}{2}$ holds $\\frac{1}{2}$ mark of tea ([[pouring-keeps-strength|each poured mark carries its cup's strength]]). 1 mark at $\\frac{1}{4}$ holds $\\frac{1}{4}$ mark. Together: $\\frac{3}{4}$ mark of tea in 2 marks of drink, so the strength is $\\frac{3}{4} \\div 2 = \\frac{3}{8}$.\n\nThat's a [[weighted-average|weighted average]]. With equal amounts it lands exactly halfway between $\\frac{2}{8}$ and $\\frac{4}{8}$.",
    "widget": {
      "type": "fraction-bar",
      "mode": "combine",
      "m1": 1,
      "s1": 0.5,
      "m2": 1,
      "s2": 0.25,
      "prompt": "Now try 1 mark of 1/2 with 3 marks of 1/4. Does it still land halfway?"
    },
    "deeper": [
      "weighted-average",
      "pouring-keeps-strength"
    ],
    "related": [],
    "foundation": false
  },
  {
    "id": "derivative",
    "title": "The derivative is the limit of slopes",
    "body": "The slope of a straight line is rise over run. A curve has no single slope, but you can draw a line through two of its points, $x$ and $x + h$, and take that line's slope: $\\frac{f(x+h) - f(x)}{h}$. That line is a secant.\n\nNow slide the second point toward the first. As $h$ shrinks, the secant swings into the tangent, the line that just touches the curve at $x$. The derivative is the [[limit]] of those slopes. It tells you how fast the [[function]]'s output is changing at that exact input. It's the reverse of finding [[integral-as-area|area]].",
    "math": [
      "f'(x) = \\lim_{h\\to 0} \\frac{f(x+h) - f(x)}{h}"
    ],
    "widget": {
      "type": "secant",
      "f": "square",
      "x0": 1,
      "prompt": "Shrink h. The secant's slope settles on 2, the slope of x² at x = 1."
    },
    "deeper": [
      "limit",
      "function"
    ],
    "related": [
      "integral-as-area"
    ],
    "foundation": false,
    "claims": [
      {
        "sympy": "limit(((1 + h)**2 - 1)/h, h, 0)",
        "equals": "2"
      }
    ]
  },
  {
    "id": "integral-as-area",
    "title": "The integral is area, built from thin rectangles",
    "body": "To find the area under a curve, cut it into thin vertical strips. Each strip is almost a rectangle, and [[area-shapes|a rectangle's area is width times height]], so add up $f(x_i)\\,\\Delta x$ for all of them. That sum is close but not exact, because the curve's top isn't flat.\n\nUse more, thinner strips and the error shrinks. The integral is the [[limit]] of that sum as the strips get infinitely thin: $\\int_a^b f(x)\\,dx$. The $\\int$ is a stretched S for \"sum\", and $dx$ stands for the vanishing width. Area below the axis counts as negative. It's the reverse of the [[derivative]].",
    "math": [
      "\\int_a^b f(x)\\,dx = \\lim_{n\\to\\infty} \\sum_{i=1}^{n} f(x_i)\\,\\Delta x"
    ],
    "widget": {
      "type": "riemann",
      "f": "square",
      "a": 0,
      "b": 1,
      "n": 4,
      "prompt": "Add rectangles. The total closes in on the exact area under x² from 0 to 1, which is 1/3."
    },
    "deeper": [
      "limit",
      "area-shapes"
    ],
    "related": [
      "derivative",
      "average-of-function"
    ],
    "foundation": false,
    "claims": [
      {
        "sympy": "integrate(x**2, (x, 0, 1))",
        "equals": "Rational(1, 3)"
      },
      {
        "sympy": "limit(Sum(((k + Rational(1, 2))/n)**2/n, (k, 0, n - 1)).doit(), n, oo)",
        "equals": "Rational(1, 3)"
      }
    ]
  },
  {
    "id": "ftc",
    "title": "The fundamental theorem: area grows at the rate of the height",
    "body": "Let $A(x)$ be the area under $f$ from a fixed start up to $x$. Move $x$ a tiny step $h$ to the right and you add one thin strip, about $f(x)$ tall and $h$ wide. So $\\frac{A(x+h) - A(x)}{h} \\approx f(x)$, and in the limit the [[derivative]] of the area function is the height: $A'(x) = f(x)$.\n\nThat links the two halves of calculus. To find an [[integral-as-area|area]], find any function whose derivative is $f$ (an antiderivative $F$), then subtract: $\\int_a^b f = F(b) - F(a)$. Differentiating and integrating undo each other, up to [[antiderivative-plus-c|a constant]].",
    "math": [
      "\\frac{d}{dx}\\int_a^x f(t)\\,dt = f(x)",
      "\\int_a^b f(x)\\,dx = F(b) - F(a)"
    ],
    "widget": {
      "type": "accumulator",
      "f": "cos",
      "prompt": "Sweep x. The slope of the area graph always matches the height of cos x."
    },
    "deeper": [
      "derivative",
      "integral-as-area"
    ],
    "related": [
      "antiderivative-plus-c"
    ],
    "foundation": false,
    "claims": [
      {
        "sympy": "diff(integrate(cos(t), (t, 0, x)), x)",
        "equals": "cos(x)"
      }
    ]
  },
  {
    "id": "antiderivative-plus-c",
    "title": "Antiderivatives come with a + C",
    "body": "An antiderivative of $f$ is any function whose [[derivative]] is $f$. But adding a constant doesn't change slopes: $\\sin x$, $\\sin x + 5$ and $\\sin x - 2$ all have derivative $\\cos x$. Shifting a graph up or down leaves every slope the same.\n\nIs that the only freedom? Yes. If two functions have the same derivative everywhere, their difference has derivative 0, and a function whose slope is zero everywhere can't rise or fall, so it's a constant. That's why every indefinite integral ends with $+ C$, and why [[ftc|the fundamental theorem]] can use any antiderivative: the constant cancels in $F(b) - F(a)$.",
    "math": [
      "\\int \\cos x\\,dx = \\sin x + C"
    ],
    "widget": {
      "type": "accumulator",
      "f": "cos",
      "mode": "shift",
      "prompt": "Shift the antiderivative up and down. The slope at x never changes."
    },
    "deeper": [
      "derivative",
      "ftc"
    ],
    "related": [
      "check-by-differentiating"
    ],
    "foundation": false,
    "claims": [
      {
        "sympy": "diff(sin(x) + 5, x)",
        "equals": "cos(x)"
      }
    ]
  },
  {
    "id": "sin-h-over-h",
    "title": "Why sin h / h → 1 as h → 0",
    "body": "Plug in $h = 0$ and you get $\\frac{0}{0}$, so we need a [[limit]]. On the [[unit-circle|unit circle]], take a small angle $h$ and compare three shapes that share a corner at the centre. A triangle inside the circular wedge has area $\\frac{1}{2}\\sin h$. The wedge (sector) itself has area $\\frac{1}{2}h$, because a full circle of area $\\pi$ spans $2\\pi$ radians. A triangle reaching out to the tangent line has area $\\frac{1}{2}\\tan h$. They're nested, so their [[area-shapes|areas]] are in order: $\\sin h \\le h \\le \\tan h$.\n\nDivide through by $\\sin h$ and flip: $\\cos h \\le \\frac{\\sin h}{h} \\le 1$. As $h \\to 0$, $\\cos h \\to 1$, so $\\frac{\\sin h}{h}$ is squeezed between two things heading to 1. It has nowhere else to go. Its cousin [[cos-h-minus-1-over-h|(cos h − 1)/h → 0]] follows from this one.",
    "math": [
      "\\sin h \\le h \\le \\tan h",
      "\\cos h \\le \\frac{\\sin h}{h} \\le 1"
    ],
    "widget": {
      "type": "unit-circle",
      "mode": "squeeze",
      "prompt": "Shrink h. The three areas pinch together, and sin h / h is squeezed toward 1."
    },
    "deeper": [
      "limit",
      "unit-circle",
      "area-shapes"
    ],
    "related": [
      "cos-h-minus-1-over-h"
    ],
    "foundation": false,
    "claims": [
      {
        "sympy": "limit(sin(h)/h, h, 0)",
        "equals": "1"
      }
    ]
  },
  {
    "id": "cos-h-minus-1-over-h",
    "title": "Why (cos h − 1) / h → 0",
    "body": "Also $\\frac{0}{0}$ at $h = 0$. Multiply top and bottom by $\\cos h + 1$ and use $\\cos^2 h - 1 = -\\sin^2 h$: $\\frac{\\cos h - 1}{h} = -\\frac{\\sin h}{h}\\cdot\\frac{\\sin h}{\\cos h + 1}$.\n\nNow take the [[limit]] piece by piece. [[sin-h-over-h|sin h / h goes to 1]], and $\\frac{\\sin h}{\\cos h + 1}$ goes to $\\frac{0}{2} = 0$. So the whole thing goes to $-1 \\times 0 = 0$. Geometrically: at angle 0 the point sits at $(1, 0)$, the right-hand end of the circle, where cos is at its maximum. Near a maximum a curve is flat, so cos's rate of change at 0 is zero.",
    "math": [
      "\\frac{\\cos h - 1}{h} = -\\frac{\\sin h}{h}\\cdot\\frac{\\sin h}{\\cos h + 1} \\to -1 \\cdot 0 = 0"
    ],
    "widget": {
      "type": "limit-zoom",
      "g": "cosh_minus_1_over_h",
      "at": 0,
      "limit": 0,
      "prompt": "Zoom in toward h = 0. The values flatten out at 0."
    },
    "deeper": [
      "sin-h-over-h",
      "limit"
    ],
    "related": [],
    "foundation": false,
    "claims": [
      {
        "sympy": "limit((cos(h) - 1)/h, h, 0)",
        "equals": "0"
      },
      {
        "sympy": "simplify((cos(h) - 1)/h + sin(h)/h*sin(h)/(cos(h) + 1))",
        "equals": "0"
      }
    ]
  },
  {
    "id": "angle-addition",
    "title": "The angle-addition formulas",
    "body": "On the [[unit-circle|unit circle]], turning by $a$ and then by $b$ is the same as turning by $a + b$. Work out where the point lands in two ways. Directly, it's at $(\\cos(a+b), \\sin(a+b))$. Or start from the point at angle $a$ and rotate it by $b$. Rotating by $b$ sends the arrow to $(1, 0)$ to $(\\cos b, \\sin b)$ and the arrow to $(0, 1)$ to $(-\\sin b, \\cos b)$ (it's the first arrow turned a quarter turn further). Rotation keeps sums and stretches of arrows, and $(x, y)$ is $x$ copies of $(1, 0)$ plus $y$ copies of $(0, 1)$, so it lands at $(x\\cos b - y\\sin b,\\ x\\sin b + y\\cos b)$.\n\nSet the two equal and you get the formulas below. They're the engine behind the derivative of sine and cosine, and behind the product-to-sum identities used in Fourier series.",
    "math": [
      "\\sin(a+b) = \\sin a\\cos b + \\cos a \\sin b",
      "\\cos(a+b) = \\cos a\\cos b - \\sin a \\sin b"
    ],
    "widget": {
      "type": "unit-circle",
      "mode": "two-angle",
      "prompt": "Change a and b. The point at a + b always matches the formula."
    },
    "deeper": [
      "unit-circle"
    ],
    "related": [
      "product-to-sum"
    ],
    "foundation": false,
    "claims": [
      {
        "sympy": "simplify(sin(a + b) - (sin(a)*cos(b) + cos(a)*sin(b)))",
        "equals": "0"
      },
      {
        "sympy": "simplify(cos(a + b) - (cos(a)*cos(b) - sin(a)*sin(b)))",
        "equals": "0"
      }
    ]
  },
  {
    "id": "derivative-of-sin-cos",
    "title": "Why the derivative of sin is cos (and of cos is −sin)",
    "body": "Use the [[derivative|definition]]: $\\frac{\\sin(x+h) - \\sin x}{h}$. Expand with [[angle-addition|angle addition]]: $\\sin(x+h) = \\sin x\\cos h + \\cos x\\sin h$. Regroup to get $\\sin x\\cdot\\frac{\\cos h - 1}{h} + \\cos x\\cdot\\frac{\\sin h}{h}$.\n\nAs $h \\to 0$, [[cos-h-minus-1-over-h|the first fraction goes to 0]] and [[sin-h-over-h|the second goes to 1]]. What's left is $\\cos x$. The same steps with $\\cos(x+h) = \\cos x\\cos h - \\sin x\\sin h$ give $-\\sin x$. So differentiating cycles: sin → cos → −sin → −cos → sin.",
    "math": [
      "\\frac{d}{dx}\\sin x = \\cos x",
      "\\frac{d}{dx}\\cos x = -\\sin x"
    ],
    "widget": {
      "type": "secant",
      "f": "sin",
      "x0": 0.8,
      "prompt": "Shrink h at x = 0.8. The slope heads to cos(0.8) ≈ 0.697."
    },
    "deeper": [
      "derivative",
      "angle-addition",
      "sin-h-over-h",
      "cos-h-minus-1-over-h"
    ],
    "related": [
      "sine-waves"
    ],
    "foundation": false,
    "claims": [
      {
        "sympy": "diff(sin(x), x)",
        "equals": "cos(x)"
      },
      {
        "sympy": "diff(cos(x), x)",
        "equals": "-sin(x)"
      }
    ]
  },
  {
    "id": "product-rule",
    "title": "The product rule",
    "body": "Think of $u(x)\\,v(x)$ as the area of a rectangle with sides $u$ and $v$. Nudge $x$ and both sides grow a little, by $du$ and $dv$. The new area is the old one plus a strip $u\\,dv$ along one side, a strip $v\\,du$ along the other, and a tiny corner $du\\,dv$.\n\nDivide by the step and take the [[limit]]: the strips give $u v' + v u'$, while the corner is a product of two small things, so it shrinks faster than the step and drops out. That's the [[derivative]] of a product. Run it backwards and you get integration by parts. It sits alongside the [[chain-rule|chain rule]], the other way of combining functions.",
    "math": [
      "(uv)' = u'v + uv'"
    ],
    "widget": {
      "type": "product-rectangle",
      "prompt": "Shrink the change. The two strips dominate and the corner vanishes."
    },
    "deeper": [
      "derivative",
      "limit"
    ],
    "related": [
      "chain-rule"
    ],
    "foundation": false,
    "claims": [
      {
        "sympy": "diff(x*exp(x), x)",
        "equals": "exp(x) + x*exp(x)"
      }
    ]
  },
  {
    "id": "chain-rule",
    "title": "The chain rule: squeezing a curve multiplies its slopes",
    "body": "Compare $g(x)$ with $g(ax)$. The second runs through the same values $a$ times faster: it's the same curve squeezed horizontally by a factor of $a$. Squeezing a hill makes it $a$ times steeper, so the slope of $g(ax)$ at $x$ is $a$ times the slope of $g$ at $ax$: $\\frac{d}{dx}g(ax) = a\\,g'(ax)$.\n\nIn general, if $x$ feeds into an inside function and its output feeds into $f$, the rates multiply: $\\frac{d}{dx}f(g(x)) = f'(g(x))\\,g'(x)$. It's a [[derivative]] fact. Together with the [[product-rule|product rule]] it handles almost every combination of functions.",
    "math": [
      "\\frac{d}{dx}\\,g(ax) = a\\,g'(ax)",
      "\\frac{d}{dx}\\,f(g(x)) = f'(g(x))\\,g'(x)"
    ],
    "widget": {
      "type": "chain-stretch",
      "f": "sin",
      "a": 2,
      "prompt": "Change the squeeze factor a. The slope at x₀ is a times the original slope."
    },
    "deeper": [
      "derivative"
    ],
    "related": [
      "product-rule"
    ],
    "foundation": false,
    "claims": [
      {
        "sympy": "diff(sin(3*x), x)",
        "equals": "3*cos(3*x)"
      }
    ]
  },
  {
    "id": "power-rule",
    "title": "The power rule: the derivative of xⁿ is n xⁿ⁻¹",
    "body": "Expand $(x+h)^n$: it's $x^n + n x^{n-1}h$ plus terms that contain $h^2$ or higher powers. For $n = 3$: $(x+h)^3 = x^3 + 3x^2 h + 3x h^2 + h^3$.\n\nSo the secant slope $\\frac{(x+h)^n - x^n}{h} = n x^{n-1} + (\\text{terms with } h)$, and as $h \\to 0$ only $n x^{n-1}$ survives: that's the [[derivative]]. Each differentiation lowers the power by one, so after enough steps a polynomial becomes a constant and then 0. That's exactly why [[polynomial-as-u|the polynomial should be u]] in integration by parts.",
    "math": [
      "\\frac{d}{dx}x^n = n x^{n-1}",
      "(x+h)^3 = x^3 + 3x^2h + 3xh^2 + h^3"
    ],
    "widget": {
      "type": "secant",
      "f": "cube",
      "x0": 1,
      "prompt": "Shrink h at x = 1. The slope of x³ heads to 3·1² = 3."
    },
    "deeper": [
      "derivative"
    ],
    "related": [
      "polynomial-as-u"
    ],
    "foundation": false,
    "claims": [
      {
        "sympy": "diff(x**3, x)",
        "equals": "3*x**2"
      },
      {
        "sympy": "expand((x + h)**3)",
        "equals": "x**3 + 3*x**2*h + 3*x*h**2 + h**3"
      }
    ]
  },
  {
    "id": "derivative-of-exp",
    "title": "Why eˣ is its own derivative",
    "body": "For any base $b$, $\\frac{b^{x+h} - b^x}{h} = b^x\\cdot\\frac{b^h - 1}{h}$, so the slope of $b^x$ is $b^x$ times a constant, the [[limit]] of $\\frac{b^h - 1}{h}$. For $b = 2$ that constant is about 0.69; for $b = 3$ it's about 1.10.\n\nSomewhere between 2 and 3 there's a base where the constant is exactly 1. That number is $e \\approx 2.718$, and for it the [[derivative]] of $e^x$ is $e^x$ itself: the function's slope always equals its height. Combined with the chain rule, $\\frac{d}{dx}e^{ax} = a\\,e^{ax}$.",
    "math": [
      "\\lim_{h\\to 0}\\frac{e^h - 1}{h} = 1",
      "\\frac{d}{dx}e^x = e^x"
    ],
    "widget": {
      "type": "limit-zoom",
      "g": "exph_minus_1_over_h",
      "at": 0,
      "limit": 1,
      "prompt": "Zoom in toward h = 0. (eʰ − 1)/h settles at exactly 1."
    },
    "deeper": [
      "derivative",
      "limit"
    ],
    "related": [],
    "foundation": false,
    "claims": [
      {
        "sympy": "diff(exp(x), x)",
        "equals": "exp(x)"
      },
      {
        "sympy": "limit((exp(h) - 1)/h, h, 0)",
        "equals": "1"
      }
    ]
  },
  {
    "id": "parts-is-product-rule-backwards",
    "title": "Integration by parts is the product rule run backwards",
    "body": "The [[product-rule|product rule]] says $(uv)' = u'v + uv'$. Integrate both sides. The left side is the integral of a derivative, so by [[ftc|the fundamental theorem]] it's just $uv$. The right side splits in two: $uv = \\int v\\,du + \\int u\\,dv$.\n\nRearranged, that's $\\int u\\,dv = uv - \\int v\\,du$. Geometrically, the two integrals are two regions that together fill the rectangle $uv$. You trade the integral you can't do for one you can, which is why choosing $u$ well matters. The minus sign comes from moving one region to the other side; see [[minus-sign-in-parts|where the minus comes from]].",
    "math": [
      "\\int u\\,dv = uv - \\int v\\,du"
    ],
    "widget": {
      "type": "product-rectangle",
      "mode": "parts",
      "prompt": "Move the end point. The two regions always add up to the rectangle uv."
    },
    "deeper": [
      "product-rule",
      "ftc"
    ],
    "related": [
      "minus-sign-in-parts"
    ],
    "foundation": false,
    "claims": [
      {
        "sympy": "simplify(integrate(x*cos(x), x) - (x*sin(x) - integrate(sin(x), x)))",
        "equals": "0"
      }
    ]
  },
  {
    "id": "minus-sign-in-parts",
    "title": "Where the minus sign in uv − ∫v du comes from",
    "body": "Start from [[parts-is-product-rule-backwards|uv = ∫u dv + ∫v du]]. The two integrals are pieces of one rectangle, and together they make the whole. To isolate the piece you want, subtract the other piece from the whole: $\\int u\\,dv = uv - \\int v\\,du$.\n\nSo the minus isn't a convention to memorize; it's \"whole minus the other part\". Writing a plus there double-counts the second region, which is why a flipped sign always gives an answer that fails the differentiation check.",
    "math": [
      "uv = \\int u\\,dv + \\int v\\,du \\;\\Longrightarrow\\; \\int u\\,dv = uv - \\int v\\,du"
    ],
    "widget": {
      "type": "product-rectangle",
      "mode": "parts",
      "prompt": "Read the gold region as 'whole rectangle minus teal'. That's the minus sign."
    },
    "deeper": [
      "parts-is-product-rule-backwards"
    ],
    "related": [],
    "foundation": false,
    "claims": [
      {
        "sympy": "simplify(integrate(log(x), x) - (x*log(x) - integrate(1, x)))",
        "equals": "0"
      }
    ]
  },
  {
    "id": "polynomial-as-u",
    "title": "Why the polynomial should be u",
    "body": "Integration by parts swaps $\\int u\\,dv$ for $\\int v\\,du$. It only helps if the new integral is simpler. Differentiating a polynomial lowers its power by one ([[power-rule|the power rule]]), so with $u = x^n$ the new integral has $x^{n-1}$, then $x^{n-2}$, until the power reaches 0 and the integral is easy. That takes exactly $n$ rounds.\n\nMeanwhile $e^{ax}$, $\\sin$ and $\\cos$ never get simpler when integrated: they just stay exponentials or cycle between sin and cos. So they belong in $dv$, where they're integrated without harm. Choose the other way round and the power of $x$ goes up instead. Each round is one application of [[parts-is-product-rule-backwards|uv − ∫v du]].",
    "math": [
      "x^3 \\to 3x^2 \\to 6x \\to 6 \\to 0"
    ],
    "widget": {
      "type": "derivative-ladder",
      "prompt": "Differentiate repeatedly. Only the polynomial ever reaches 0."
    },
    "deeper": [
      "power-rule",
      "parts-is-product-rule-backwards"
    ],
    "related": [],
    "foundation": false,
    "claims": [
      {
        "sympy": "diff(x**3, x, 4)",
        "equals": "0"
      }
    ]
  },
  {
    "id": "one-over-a",
    "title": "Why integrating g(ax) brings out 1/a",
    "body": "The [[chain-rule|chain rule]] says differentiating $G(ax)$ gives $a\\,G'(ax)$: an extra factor of $a$. So if $G$ is an antiderivative of $g$, then $\\frac{1}{a}G(ax)$ differentiates to exactly $g(ax)$. That's the [[antiderivative-plus-c|antiderivative]]: $\\int g(ax)\\,dx = \\frac{1}{a}G(ax) + C$.\n\nIn pictures: $g(ax)$ is $g$ squeezed $a$ times narrower, so every area under it is $a$ times smaller. That's why $\\int e^{3x}dx = \\frac{1}{3}e^{3x}$ and $\\int \\cos 2x\\,dx = \\frac{1}{2}\\sin 2x$. Forgetting the $\\frac{1}{a}$ is the most common slip in integration, along with [[integral-of-sin|sign errors on sin and cos]].",
    "math": [
      "\\int g(ax)\\,dx = \\frac{1}{a}\\,G(ax) + C"
    ],
    "widget": {
      "type": "chain-stretch",
      "f": "sin",
      "a": 2,
      "mode": "area",
      "prompt": "Change a. One hump's area is always 2 ÷ a."
    },
    "deeper": [
      "chain-rule",
      "antiderivative-plus-c"
    ],
    "related": [
      "integral-of-sin"
    ],
    "foundation": false,
    "claims": [
      {
        "sympy": "integrate(exp(3*x), x)",
        "equals": "exp(3*x)/3"
      },
      {
        "sympy": "integrate(cos(2*x), x)",
        "equals": "sin(2*x)/2"
      }
    ]
  },
  {
    "id": "integral-of-sin",
    "title": "Why ∫ sin x dx = −cos x",
    "body": "We need a function whose derivative is $\\sin x$. From [[derivative-of-sin-cos|the derivatives of sin and cos]], $\\frac{d}{dx}\\cos x = -\\sin x$, so $\\frac{d}{dx}(-\\cos x) = \\sin x$. That makes $-\\cos x$ an [[antiderivative-plus-c|antiderivative]]: $\\int \\sin x\\,dx = -\\cos x + C$.\n\nThe minus sign is easy to drop. Check the picture: from 0 to $\\pi$, $\\sin x$ is positive, so the area must be positive. $-\\cos\\pi - (-\\cos 0) = 1 + 1 = 2$. A plus sign would give $-2$, a negative area for a positive curve. With [[one-over-a|a squeezed sine]], also remember the 1/a.",
    "math": [
      "\\int \\sin x\\,dx = -\\cos x + C",
      "\\int_0^{\\pi}\\sin x\\,dx = 2"
    ],
    "widget": {
      "type": "accumulator",
      "f": "sin",
      "prompt": "Sweep x from 0 to π. The area climbs to 2, the shape of −cos x shifted up by 1."
    },
    "deeper": [
      "derivative-of-sin-cos",
      "antiderivative-plus-c"
    ],
    "related": [
      "one-over-a"
    ],
    "foundation": false,
    "claims": [
      {
        "sympy": "integrate(sin(x), x)",
        "equals": "-cos(x)"
      },
      {
        "sympy": "integrate(sin(x), (x, 0, pi))",
        "equals": "2"
      }
    ]
  },
  {
    "id": "check-by-differentiating",
    "title": "Check any integral by differentiating it",
    "body": "Integrating can be hard; differentiating is mechanical. And by [[ftc|the fundamental theorem]], they undo each other: if $F$ is right, then $F' = f$ exactly. So after any integration, differentiate your answer and compare with the integrand.\n\nIt catches every common slip: a wrong sign (like [[integral-of-sin|∫ sin = +cos]]), a missing $\\frac{1}{a}$, a dropped term from parts. It can't catch a wrong constant, but [[antiderivative-plus-c|every antiderivative differs by a constant]] anyway, so the $+ C$ covers that. Example: $\\frac{d}{dx}(x\\sin x + \\cos x) = \\sin x + x\\cos x - \\sin x = x\\cos x$. ✓",
    "math": [
      "\\frac{d}{dx}\\left(x\\sin x + \\cos x\\right) = x\\cos x"
    ],
    "widget": {
      "type": "accumulator",
      "f": "cos",
      "prompt": "Sweep x. Differentiating the area gives back the curve you started with."
    },
    "deeper": [
      "ftc",
      "antiderivative-plus-c"
    ],
    "related": [
      "integral-of-sin"
    ],
    "foundation": false,
    "claims": [
      {
        "sympy": "diff(x*sin(x) + cos(x), x)",
        "equals": "x*cos(x)"
      }
    ]
  },
  {
    "id": "ibp-pick-u",
    "entry": true,
    "title": "Why u = x for ∫ x e²ˣ dx?",
    "body": "Differentiating $x$ gives 1, the simplest possible thing ([[polynomial-as-u|the polynomial should be u]]), and $e^{2x}$ is easy to integrate: $v = \\frac{1}{2}e^{2x}$. Then [[parts-is-product-rule-backwards|uv − ∫v du]] leaves $\\int \\frac{1}{2}e^{2x}\\,dx$, which you can do on sight.\n\nWith $u = e^{2x}$ instead, $v = \\frac{x^2}{2}$ and the new integral has $x^2$: harder than where you started.",
    "widget": {
      "type": "derivative-ladder",
      "poly": [
        0,
        1
      ],
      "prompt": "Differentiate once. x becomes 1, and the integral that's left is easy."
    },
    "deeper": [
      "polynomial-as-u",
      "parts-is-product-rule-backwards"
    ],
    "related": [],
    "foundation": false
  },
  {
    "id": "ibp-sign",
    "entry": true,
    "title": "Why is it + cos x, not − cos x?",
    "body": "The last step subtracts $\\int \\sin x\\,dx$. [[integral-of-sin|That integral is −cos x]], and subtracting a negative gives a plus: $x\\sin x - (-\\cos x) = x\\sin x + \\cos x$.\n\n[[check-by-differentiating|Check by differentiating]]: $\\frac{d}{dx}(x\\sin x + \\cos x) = \\sin x + x\\cos x - \\sin x = x\\cos x$. With $-\\cos x$ you'd get $x\\cos x + 2\\sin x$ instead.",
    "widget": {
      "type": "accumulator",
      "f": "sin",
      "prompt": "Watch the area under sin x. It follows −cos x, not +cos x."
    },
    "deeper": [
      "integral-of-sin",
      "check-by-differentiating"
    ],
    "related": [],
    "foundation": false
  },
  {
    "id": "ibp-v",
    "entry": true,
    "title": "Why v = ⅓e³ˣ, not 3e³ˣ?",
    "body": "$v$ has to be a function whose derivative is $e^{3x}$. But [[derivative-of-exp|differentiating e³ˣ]] gives $3e^{3x}$: the inner 3 comes out. To undo that, divide by 3: [[one-over-a|integrating g(ax) brings out 1/a]], so $v = \\frac{1}{3}e^{3x}$.\n\n$3e^{3x}$ is what you'd get by differentiating, the opposite of what $v$ needs.",
    "widget": {
      "type": "chain-stretch",
      "f": "exp",
      "a": 3,
      "prompt": "Squeeze eˣ into e³ˣ. Slopes triple, so the antiderivative needs a 1/3."
    },
    "deeper": [
      "one-over-a",
      "derivative-of-exp"
    ],
    "related": [],
    "foundation": false
  },
  {
    "id": "ibp-blank",
    "entry": true,
    "title": "Why does 2x eˣ go in the box?",
    "body": "In [[parts-is-product-rule-backwards|uv − ∫v du]] the new integral is $\\int v\\,du$. With $u = x^2$ and $dv = e^x dx$: $v = e^x$ and $du = 2x\\,dx$, so the box holds $e^x\\cdot 2x$.\n\nThe power of $x$ dropped from 2 to 1. One more round brings it to 0 ([[polynomial-as-u|that's why the polynomial is u]]).",
    "widget": {
      "type": "derivative-ladder",
      "poly": [
        0,
        0,
        1
      ],
      "prompt": "Differentiate x² twice. Each round of parts uses one of these steps."
    },
    "deeper": [
      "parts-is-product-rule-backwards",
      "polynomial-as-u"
    ],
    "related": [],
    "foundation": false
  },
  {
    "id": "ibp-chain",
    "entry": true,
    "title": "Why ½ sin 2x, not sin 2x?",
    "body": "[[chain-rule|Differentiating sin 2x]] gives $2\\cos 2x$: the inner 2 comes out. So $\\int \\cos 2x\\,dx$ must undo that factor: $\\frac{1}{2}\\sin 2x$. [[one-over-a|Integrating g(ax) always brings out 1/a.]]\n\nThat makes the last term $\\frac{1}{2}\\cdot\\frac{1}{2}\\sin 2x = \\frac{1}{4}\\sin 2x$.",
    "widget": {
      "type": "chain-stretch",
      "f": "cos",
      "a": 2,
      "prompt": "Squeeze cos x into cos 2x. Its slopes double, so its antiderivative needs a ½."
    },
    "deeper": [
      "one-over-a",
      "chain-rule"
    ],
    "related": [],
    "foundation": false
  },
  {
    "id": "ibp-minus",
    "entry": true,
    "title": "Why minus ∫ v du?",
    "body": "Because $uv$ is a whole made of two parts, $\\int u\\,dv$ and $\\int v\\,du$, [[minus-sign-in-parts|the part you want is the whole minus the other part]]. A plus sign double-counts. Here that turns the correct $x\\ln x - x + C$ into the wrong $x\\ln x + x + C$.",
    "widget": {
      "type": "product-rectangle",
      "mode": "parts",
      "prompt": "The gold region is the rectangle minus the teal one. That's the minus sign."
    },
    "deeper": [
      "minus-sign-in-parts"
    ],
    "related": [],
    "foundation": false
  },
  {
    "id": "ibp-check",
    "entry": true,
    "title": "Why is ½x² ln x − ¼x² the right one?",
    "body": "[[check-by-differentiating|Differentiate each candidate.]] Using the [[product-rule|product rule]] on $\\frac{1}{2}x^2\\ln x$: $x\\ln x + \\frac{1}{2}x^2\\cdot\\frac{1}{x} = x\\ln x + \\frac{1}{2}x$. Then $-\\frac{1}{4}x^2$ contributes $-\\frac{1}{2}x$. Total: $x\\ln x$. ✓\n\nThe others leave something extra behind, which is how you know they're wrong without redoing the integral.",
    "widget": {
      "type": "product-rectangle",
      "prompt": "The product rule as area: two strips for the two terms of the derivative."
    },
    "deeper": [
      "check-by-differentiating",
      "product-rule"
    ],
    "related": [],
    "foundation": false
  },
  {
    "id": "sine-waves",
    "title": "Sine waves: height and frequency",
    "body": "Walk around the [[unit-circle|unit circle]] at a steady pace and track your height: it rises, falls and repeats. Plot that height against time and you get $\\sin t$, a smooth wave that repeats every $2\\pi$.\n\nTwo dials change it. Multiplying by $A$ stretches it vertically: $A\\sin t$ swings between $-A$ and $A$ (the amplitude). Putting $n$ inside, $\\sin(nt)$, makes you walk the circle $n$ times as fast, so the wave fits $n$ full wiggles into each $2\\pi$. Every term in a Fourier series is a [[function]] of exactly this shape.",
    "math": [
      "A\\sin(nt)",
      "\\sin\\!\\left(n\\left(t + \\tfrac{2\\pi}{n}\\right)\\right) = \\sin(nt)"
    ],
    "widget": {
      "type": "wave-mixer",
      "mode": "single",
      "prompt": "Change the height and the wiggles per period."
    },
    "deeper": [
      "unit-circle",
      "function"
    ],
    "related": [],
    "foundation": false,
    "claims": [
      {
        "sympy": "simplify(sin(3*(t + 2*pi/3)) - sin(3*t))",
        "equals": "0"
      }
    ]
  },
  {
    "id": "average-of-function",
    "title": "The average of a function",
    "body": "To average a list of numbers, add them and divide by how many there are. A function has infinitely many values, so instead you add them continuously, which is the [[integral-as-area|integral]], and divide by the length of the interval: $\\bar f = \\frac{1}{b-a}\\int_a^b f(x)\\,dx$.\n\nPicture it as levelling sand: the average is the height of the flat rectangle with the same area and width as the region under the curve. It's the continuous cousin of a [[weighted-average|weighted average]], and it's how the square-wave page measures the [[why-square-the-gap|gap]].",
    "math": [
      "\\bar f = \\frac{1}{b-a}\\int_a^b f(x)\\,dx",
      "\\text{average of } \\sin \\text{ on } [0,\\pi] = \\frac{2}{\\pi}"
    ],
    "widget": {
      "type": "riemann",
      "mode": "average",
      "f": "sin",
      "a": 0,
      "b": 3.14159,
      "n": 12,
      "prompt": "The dashed line is the average height. Its rectangle has the same area as the region under the curve."
    },
    "deeper": [
      "integral-as-area"
    ],
    "related": [
      "why-square-the-gap",
      "weighted-average"
    ],
    "foundation": false,
    "claims": [
      {
        "sympy": "integrate(sin(x), (x, 0, pi))/pi",
        "equals": "2/pi"
      }
    ]
  },
  {
    "id": "why-square-the-gap",
    "title": "Why we square the gap",
    "body": "To score how well a curve fits a target, look at the gap $d(t)$ between them at every point. You can't just [[average-of-function|average]] $d(t)$: where the curve is too high the gap is positive, where it's too low it's negative, and they cancel. A terrible fit could average to zero.\n\nSquaring fixes that. $d^2$ is never negative, so nothing cancels, and big misses cost much more than small ones. The page's \"gap\" is the root-mean-square: $\\sqrt{\\text{average of } d^2}$. There's a bonus: the average squared gap turns out to be a [[best-fit-parabola|parabola]] in the height you're choosing, and parabolas have one clear lowest point.",
    "math": [
      "\\text{gap} = \\sqrt{\\frac{1}{2\\pi}\\int_0^{2\\pi} \\big(a\\sin t - \\text{sq}(t)\\big)^2\\,dt}"
    ],
    "widget": {
      "type": "wave-mixer",
      "mode": "gap",
      "prompt": "Change the height. The plain average gap barely moves; the squared gap shows the real fit."
    },
    "deeper": [
      "average-of-function"
    ],
    "related": [
      "best-fit-parabola"
    ],
    "foundation": false,
    "claims": [
      {
        "sympy": "integrate((sin(t) - 1)**2, (t, 0, pi)) + integrate((sin(t) + 1)**2, (t, pi, 2*pi))",
        "equals": "3*pi - 8"
      }
    ]
  },
  {
    "id": "best-fit-parabola",
    "title": "The best fit is the bottom of a parabola",
    "body": "Write the average squared gap for height $a$ and expand the square: $E(a) = a^2\\,\\overline{\\sin^2} - 2a\\,\\overline{\\text{sq}\\cdot\\sin} + \\overline{\\text{sq}^2}$. For the square wave those averages are $\\frac{1}{2}$, $\\frac{2}{\\pi}$ and 1, so $E(a) = \\frac{a^2}{2} - \\frac{4a}{\\pi} + 1$.\n\nThat's a parabola opening upward. Its lowest point is where its slope is zero, which you find with the [[derivative]]: $E'(a) = a - \\frac{4}{\\pi} = 0$, so $a = \\frac{4}{\\pi} \\approx 1.27$. Squaring the gap ([[why-square-the-gap|why we do that]]) is what made the error a parabola. The general version of this answer is the [[projection]] formula.",
    "math": [
      "E(a) = \\frac{a^2}{2} - \\frac{4a}{\\pi} + 1",
      "E'(a) = a - \\frac{4}{\\pi} = 0 \\;\\Rightarrow\\; a = \\frac{4}{\\pi}"
    ],
    "widget": {
      "type": "parabola-min",
      "prompt": "Drag a. The tangent is flat exactly at 4/π."
    },
    "deeper": [
      "derivative",
      "why-square-the-gap"
    ],
    "related": [
      "projection"
    ],
    "foundation": false,
    "claims": [
      {
        "sympy": "diff(a**2/2 - 4*a/pi + 1, a).subs(a, 4/pi)",
        "equals": "0"
      },
      {
        "sympy": "(integrate((a*sin(t) - 1)**2, (t, 0, pi)) + integrate((a*sin(t) + 1)**2, (t, pi, 2*pi)))/(2*pi) - (a**2/2 - 4*a/pi + 1)",
        "equals": "0"
      }
    ]
  },
  {
    "id": "projection",
    "title": "The projection formula",
    "body": "The [[best-fit-parabola|parabola argument]] works for any target $f$ and any building block $g$: the best height is $a = \\frac{\\int f\\,g}{\\int g^2}$, where both are [[integral-as-area|integrals]] over one period. It's the same as projecting one arrow onto another: how much of $f$ points in the direction of $g$, divided by the length of $g$ squared.\n\nFor the square wave and $\\sin t$: $\\int_0^{2\\pi}\\text{sq}\\cdot\\sin = 4$ and $\\int_0^{2\\pi}\\sin^2 = \\pi$, so $a = \\frac{4}{\\pi}$. Because different sines are [[orthogonality|orthogonal]], you can project onto each sine separately.",
    "math": [
      "a = \\frac{\\int f\\,g}{\\int g^2}",
      "\\frac{4}{\\pi} = \\frac{\\int_0^{2\\pi} \\text{sq}(t)\\sin t\\,dt}{\\int_0^{2\\pi}\\sin^2 t\\,dt}"
    ],
    "widget": {
      "type": "parabola-min",
      "mode": "projection",
      "prompt": "Move a away from 4/π in either direction. The error only goes up."
    },
    "deeper": [
      "best-fit-parabola",
      "integral-as-area"
    ],
    "related": [
      "orthogonality"
    ],
    "foundation": false,
    "claims": [
      {
        "sympy": "(integrate(sin(t), (t, 0, pi)) - integrate(sin(t), (t, pi, 2*pi)))/integrate(sin(t)**2, (t, 0, 2*pi))",
        "equals": "4/pi"
      }
    ]
  },
  {
    "id": "integral-sin-half-period",
    "title": "Why the area under one hump of sin is exactly 2",
    "body": "By [[ftc|the fundamental theorem]], $\\int_0^\\pi \\sin t\\,dt = F(\\pi) - F(0)$ for any antiderivative $F$. Since [[derivative-of-sin-cos|the derivative of −cos is sin]], take $F = -\\cos$: $-\\cos\\pi - (-\\cos 0) = 1 + 1 = 2$.\n\nA curved hump with height 1 and width $\\pi \\approx 3.14$ has area exactly 2, a little less than two-thirds of the rectangle around it. The square wave is $+1$ on this half and $-1$ on the other, while $\\sin t$ is negative there too, so both halves contribute $+2$, giving the 4 in $\\frac{4}{\\pi}$. Compare it with [[average-of-sin-squared|the average of sin²]].",
    "math": [
      "\\int_0^{\\pi}\\sin t\\,dt = \\big[-\\cos t\\big]_0^{\\pi} = 2"
    ],
    "widget": {
      "type": "riemann",
      "f": "sin",
      "a": 0,
      "b": 3.14159,
      "n": 6,
      "prompt": "Add rectangles. The area under one hump closes in on exactly 2."
    },
    "deeper": [
      "ftc",
      "derivative-of-sin-cos"
    ],
    "related": [
      "average-of-sin-squared"
    ],
    "foundation": false,
    "claims": [
      {
        "sympy": "integrate(sin(t), (t, 0, pi))",
        "equals": "2"
      }
    ]
  },
  {
    "id": "average-of-sin-squared",
    "title": "Why sin² averages to ½",
    "body": "On the [[unit-circle|unit circle]], $\\sin^2 t + \\cos^2 t = 1$ at every angle. Over a full period, $\\cos$ is just $\\sin$ shifted by a quarter turn, so $\\sin^2$ and $\\cos^2$ take the same values and have the same [[average-of-function|average]].\n\nTwo equal averages that add up to 1 must each be $\\frac{1}{2}$. So $\\int_0^{2\\pi}\\sin^2 t\\,dt = \\frac{1}{2}\\cdot 2\\pi = \\pi$. That $\\pi$ is the denominator in $\\frac{4}{\\pi}$, and $\\sin^2(nt)$ averages to $\\frac{1}{2}$ for every $n$. Compare [[integral-sin-half-period|the area of one hump of sin]].",
    "math": [
      "\\sin^2 t + \\cos^2 t = 1",
      "\\frac{1}{2\\pi}\\int_0^{2\\pi}\\sin^2 t\\,dt = \\frac{1}{2}"
    ],
    "widget": {
      "type": "riemann",
      "mode": "average",
      "f": "sin2",
      "a": 0,
      "b": 6.28318,
      "n": 24,
      "prompt": "The dashed average line sits at exactly 1/2."
    },
    "deeper": [
      "average-of-function",
      "unit-circle"
    ],
    "related": [
      "integral-sin-half-period"
    ],
    "foundation": false,
    "claims": [
      {
        "sympy": "integrate(sin(t)**2, (t, 0, 2*pi))/(2*pi)",
        "equals": "Rational(1, 2)"
      }
    ]
  },
  {
    "id": "product-to-sum",
    "title": "Turning a product of sines into a sum",
    "body": "Write [[angle-addition|the cosine addition formula]] twice: $\\cos(A-B) = \\cos A\\cos B + \\sin A\\sin B$ and $\\cos(A+B) = \\cos A\\cos B - \\sin A\\sin B$. Subtract the second from the first and the $\\cos A\\cos B$ terms cancel, leaving $2\\sin A\\sin B$.\n\nSo a product of two sines is half the difference of two cosines. Products are hard to integrate; sums of cosines are easy. That's the key step in showing [[orthogonality|different sines are orthogonal]].",
    "math": [
      "\\sin A\\sin B = \\tfrac{1}{2}\\big[\\cos(A-B) - \\cos(A+B)\\big]"
    ],
    "widget": {
      "type": "wave-mixer",
      "mode": "product",
      "m": 2,
      "n": 3,
      "prompt": "The product sin 2t · sin 3t wiggles like ½[cos t − cos 5t]."
    },
    "deeper": [
      "angle-addition"
    ],
    "related": [
      "orthogonality"
    ],
    "foundation": false,
    "claims": [
      {
        "sympy": "simplify(sin(a)*sin(b) - (cos(a - b) - cos(a + b))/2)",
        "equals": "0"
      }
    ]
  },
  {
    "id": "orthogonality",
    "title": "Different sines are orthogonal",
    "body": "For whole numbers $m \\ne n$, $\\int_0^{2\\pi}\\sin(mt)\\sin(nt)\\,dt = 0$. [[product-to-sum|Turn the product into a sum]]: $\\frac{1}{2}[\\cos((m-n)t) - \\cos((m+n)t)]$. Each cosine completes a whole number of periods over $[0, 2\\pi]$, so its positive and negative [[integral-as-area|area]] cancel exactly.\n\nThat's what \"orthogonal\" means here, the function version of perpendicular arrows. It's why you can find each sine's best height on its own with [[projection|the projection formula]], without the others interfering. With $m = n$ you get $\\pi$ instead. It also explains [[half-wave-symmetry|why even sines don't help]] from another angle.",
    "math": [
      "\\int_0^{2\\pi}\\sin(mt)\\sin(nt)\\,dt = \\begin{cases}0 & m\\ne n\\\\ \\pi & m = n\\end{cases}"
    ],
    "widget": {
      "type": "wave-mixer",
      "mode": "product",
      "m": 2,
      "n": 3,
      "prompt": "Pick two different frequencies, then two equal ones. Watch the total area."
    },
    "deeper": [
      "product-to-sum",
      "integral-as-area"
    ],
    "related": [
      "projection",
      "half-wave-symmetry"
    ],
    "foundation": false,
    "claims": [
      {
        "sympy": "integrate(sin(2*t)*sin(3*t), (t, 0, 2*pi))",
        "equals": "0"
      },
      {
        "sympy": "integrate(sin(3*t)**2, (t, 0, 2*pi))",
        "equals": "pi"
      }
    ]
  },
  {
    "id": "half-wave-symmetry",
    "title": "Why even sines can't help build a square wave",
    "body": "The square wave's second half is an upside-down copy of its first: $\\text{sq}(t + \\pi) = -\\text{sq}(t)$. Now compare the [[sine-waves|sines]]. An odd one like $\\sin 3t$ also flips: $\\sin(3(t + \\pi)) = -\\sin 3t$. An even one like $\\sin 2t$ doesn't: $\\sin(2(t+\\pi)) = \\sin 2t$, because $2\\pi$ is a full period.\n\nThe best height is $\\frac{\\int \\text{sq}\\cdot\\sin(nt)}{\\int\\sin^2(nt)}$. Split that top [[integral-as-area|integral]] into the two halves. For odd $n$ both factors flip, so the second half matches the first and they add. For even $n$ only the square wave flips, so the second half is the negative of the first and they cancel. The best height for every even sine is exactly 0. See also [[orthogonality]].",
    "math": [
      "\\text{sq}(t+\\pi) = -\\text{sq}(t)",
      "\\sin(2(t+\\pi)) = \\sin 2t, \\quad \\sin(3(t+\\pi)) = -\\sin 3t"
    ],
    "widget": {
      "type": "wave-mixer",
      "mode": "shift",
      "prompt": "Try n = 2, 3, 4, 5. Even n: the halves cancel. Odd n: they add."
    },
    "deeper": [
      "integral-as-area",
      "sine-waves"
    ],
    "related": [
      "orthogonality"
    ],
    "foundation": false,
    "claims": [
      {
        "sympy": "simplify(sin(2*(t + pi)) - sin(2*t))",
        "equals": "0"
      },
      {
        "sympy": "simplify(sin(3*(t + pi)) + sin(3*t))",
        "equals": "0"
      }
    ]
  },
  {
    "id": "coefficients-4-over-n-pi",
    "title": "Why the heights are 4/(nπ)",
    "body": "Apply [[projection|the projection formula]] to $\\sin(nt)$. The bottom is $\\int_0^{2\\pi}\\sin^2(nt) = \\pi$ ([[average-of-sin-squared|sin² averages ½]]). For the top, both halves contribute equally when $n$ is odd, so it's $2\\int_0^\\pi \\sin(nt)\\,dt$.\n\nThat integral is like [[integral-sin-half-period|the area of one hump]], but $\\sin(nt)$ is squeezed $n$ times, so by the [[chain-rule|chain rule]] its antiderivative is $-\\frac{1}{n}\\cos(nt)$: $\\int_0^\\pi\\sin(nt)\\,dt = \\frac{1 - \\cos n\\pi}{n} = \\frac{2}{n}$ for odd $n$. Top $= \\frac{4}{n}$, so the height is $\\frac{4}{n\\pi}$: 1.27, 0.42, 0.25, … falling like $\\frac{1}{n}$. Adding these up gives the [[partial-sums|partial sums]].",
    "math": [
      "b_n = \\frac{1}{\\pi}\\int_0^{2\\pi}\\text{sq}(t)\\sin(nt)\\,dt = \\begin{cases}\\frac{4}{n\\pi} & n \\text{ odd}\\\\ 0 & n \\text{ even}\\end{cases}"
    ],
    "widget": {
      "type": "wave-mixer",
      "mode": "partials",
      "prompt": "Each extra sine uses the next odd n with height 4/(nπ)."
    },
    "deeper": [
      "projection",
      "integral-sin-half-period",
      "chain-rule",
      "average-of-sin-squared"
    ],
    "related": [
      "partial-sums"
    ],
    "foundation": false,
    "claims": [
      {
        "sympy": "(integrate(sin(3*t), (t, 0, pi)) - integrate(sin(3*t), (t, pi, 2*pi)))/pi",
        "equals": "4/(3*pi)"
      },
      {
        "sympy": "(integrate(sin(5*t), (t, 0, pi)) - integrate(sin(5*t), (t, pi, 2*pi)))/pi",
        "equals": "4/(5*pi)"
      },
      {
        "sympy": "(integrate(sin(2*t), (t, 0, pi)) - integrate(sin(2*t), (t, pi, 2*pi)))/pi",
        "equals": "0"
      }
    ]
  },
  {
    "id": "partial-sums",
    "title": "Partial sums and what \"converges\" means",
    "body": "A partial sum adds the first few terms: $S_N(t) = \\sum \\frac{4}{n\\pi}\\sin(nt)$ over the first $N$ odd $n$. Each $S_N$ is a smooth [[sine-waves|sum of sine waves]]. As $N$ grows, the sums get closer to the square wave.\n\n\"Converges\" is a [[limit]] statement: at each fixed $t$ away from a jump, $S_N(t)$ settles on the square wave's value. At $t = \\frac{\\pi}{2}$ it becomes $\\frac{4}{\\pi}(1 - \\frac{1}{3} + \\frac{1}{5} - \\dots) = 1$. At the jumps themselves the sums sit at 0, halfway. Next to the jumps there's a stubborn surprise: the [[gibbs|Gibbs overshoot]].",
    "math": [
      "S_N(t) = \\frac{4}{\\pi}\\sum_{k=0}^{N-1}\\frac{\\sin((2k+1)t)}{2k+1}",
      "\\frac{4}{\\pi}\\left(1 - \\tfrac{1}{3} + \\tfrac{1}{5} - \\cdots\\right) = 1"
    ],
    "widget": {
      "type": "wave-mixer",
      "mode": "partials",
      "prompt": "Add sines one at a time and watch the sum close in."
    },
    "deeper": [
      "limit",
      "sine-waves"
    ],
    "related": [
      "gibbs"
    ],
    "foundation": false,
    "claims": [
      {
        "sympy": "4/pi*Sum((-1)**k/(2*k + 1), (k, 0, oo)).doit()",
        "equals": "1"
      }
    ]
  },
  {
    "id": "gibbs",
    "title": "The Gibbs phenomenon: the overshoot that won't go away",
    "body": "Next to each jump, every [[partial-sums|partial sum]] overshoots the square wave. Add more sines and the horn gets narrower and moves closer to the jump, but its height doesn't shrink: it settles at about 1.179, an overshoot of roughly 9% of the jump (from −1 to 1). The exact limit is $\\frac{2}{\\pi}\\int_0^\\pi\\frac{\\sin u}{u}\\,du$, an [[integral-as-area|area]] under $\\frac{\\sin u}{u}$.\n\nHow can the sums converge if the overshoot never shrinks? Because the horn gets narrower: at any fixed point the sums do settle, and the [[why-square-the-gap|average squared gap]] goes to zero. They just never fit the jump uniformly well. A sum of smooth waves can't make a sharp corner without ringing.",
    "math": [
      "\\lim_{N\\to\\infty}\\max S_N = \\frac{2}{\\pi}\\int_0^{\\pi}\\frac{\\sin u}{u}\\,du \\approx 1.179"
    ],
    "widget": {
      "type": "wave-mixer",
      "mode": "zoom",
      "prompt": "Zoomed in at the jump: add sines and watch the horn narrow while its peak stays near 1.179."
    },
    "deeper": [
      "partial-sums",
      "integral-as-area"
    ],
    "related": [
      "why-square-the-gap"
    ],
    "foundation": false,
    "claims": [
      {
        "sympy": "2/pi*Si(pi)",
        "approx": 1.179,
        "tol": 0.001
      }
    ]
  },
  {
    "id": "sw-best-height",
    "entry": true,
    "title": "Why is the best height 4/π, not 1?",
    "body": "The best height is the one that makes the [[why-square-the-gap|average squared gap]] as small as possible. That error is a [[best-fit-parabola|parabola in the height a]], and its lowest point is given by the [[projection|projection formula]]: $a = \\frac{\\int\\text{sq}\\cdot\\sin}{\\int\\sin^2}$.\n\nThe top is 4: each half of the period contributes [[integral-sin-half-period|the area of one hump, 2]]. The bottom is $\\pi$, because [[average-of-sin-squared|sin² averages ½]] over $2\\pi$. So $a = \\frac{4}{\\pi} \\approx$ {{A1}}. Height 1 matches the flat top at a single point, while 4/π trades a small bulge in the middle for a much closer fit everywhere else.",
    "widget": {
      "type": "parabola-min",
      "prompt": "Find the lowest point of the error parabola, then compare it with a = 1."
    },
    "deeper": [
      "projection",
      "best-fit-parabola",
      "integral-sin-half-period",
      "average-of-sin-squared"
    ],
    "related": [
      "why-square-the-gap"
    ],
    "foundation": false
  },
  {
    "id": "sw-why-sin3t",
    "entry": true,
    "title": "Why sin 3t, and why not sin 2t?",
    "body": "Even sines can't help: the square wave flips sign every half period, and an even sine repeats instead of flipping, so the two halves of its projection cancel. That's [[half-wave-symmetry|half-wave symmetry]], and it makes the best height for sin 2t exactly 0.\n\nFor sin 3t, both halves add. Because different sines are [[orthogonality|orthogonal]], its best height doesn't depend on the sin t already there: it's $\\frac{\\int\\text{sq}\\cdot\\sin 3t}{\\int\\sin^2 3t} = \\frac{4}{3\\pi} \\approx$ {{A3}}.",
    "widget": {
      "type": "wave-mixer",
      "mode": "shift",
      "prompt": "Compare n = 2 with n = 3: one cancels, one adds."
    },
    "deeper": [
      "half-wave-symmetry",
      "orthogonality"
    ],
    "related": [],
    "foundation": false
  },
  {
    "id": "sw-pattern",
    "entry": true,
    "title": "Why do the heights fall like 1/n?",
    "body": "Every height comes from the same projection, and [[coefficients-4-over-n-pi|working it out for sin(nt) gives 4/(nπ)]]. The area under one squeezed hump of $\\sin(nt)$ is $\\frac{2}{n}$, so the heights are $\\frac{4}{\\pi}\\cdot\\frac{1}{n}$: 1.27, then ÷3, then ÷5, and so on.",
    "widget": {
      "type": "wave-mixer",
      "mode": "partials",
      "prompt": "Add sines one by one: each uses height 4/(nπ) for the next odd n."
    },
    "deeper": [
      "coefficients-4-over-n-pi"
    ],
    "related": [],
    "foundation": false
  },
  {
    "id": "sw-gibbs",
    "entry": true,
    "title": "Why doesn't the overshoot go away?",
    "body": "The [[partial-sums|partial sums]] do converge: at every point away from a jump they settle on the square wave. But right next to the jump each sum overshoots, and as you add sines the horn only gets narrower, not lower. Its peak settles near {{peak}}, overshooting by about 9% of the jump. That's the [[gibbs|Gibbs phenomenon]]: smooth waves can't make a sharp corner without ringing.",
    "widget": {
      "type": "wave-mixer",
      "mode": "zoom",
      "prompt": "Add sines while zoomed in on the jump. The peak readout barely moves."
    },
    "deeper": [
      "gibbs",
      "partial-sums"
    ],
    "related": [],
    "foundation": false
  }
];
