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
    "body": "Area counts how many unit squares fit inside a shape. A rectangle $w$ wide and $h$ tall holds $w \\times h$ of them; that's the starting point.\n\nCut a rectangle along its diagonal and you get two identical right triangles, so each has half the area: $\\frac{1}{2} w h$. Any triangle can be split into two right triangles, so every triangle's area is $\\frac{1}{2} \\times \\text{base} \\times \\text{height}$. A region under a curve isn't made of rectangles or triangles, but it can be approximated by them as closely as we like, which is exactly what integrals do.",
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
    "body": "Add water and the concentrate stays the same while the total grows. Double the volume with an equal amount of water and the same concentrate is spread through twice as much drink, so the [[strength]] is multiplied by $\\frac{1}{2}$, not reduced by a fixed amount.\n\nMore generally, going from volume $m$ to volume $M$ multiplies strength by $\\frac{m}{M}$: you're taking [[fraction-of-a-fraction|a fraction of a fraction]]. That's why diluting a $\\frac{1}{4}$ drink with equal water gives $\\frac{1}{8}$, not $\\frac{1}{4} - \\frac{1}{8}$ or some other subtraction.",
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
    "related": [],
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
  }
];
