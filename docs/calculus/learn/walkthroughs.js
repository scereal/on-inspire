// Learn walkthroughs for the calculus explorer. Valid JSON after the "=" (tests/check_curriculum.py reads it).
// Spec: design/specs/2026-10-05-math-140-explorer-design.md section 4.
window.WALKTHROUGHS = [
  {
    "id": "learn-rate",
    "subtopic": "140.3.1.rate",
    "title": "How fast is the ball falling, right now?",
    "problem": "A ball is dropped from a tall building. After $t$ seconds it has fallen $s(t) = 4.9t^2$ metres. How fast is it falling at exactly $t = 2$ seconds?",
    "steps": [
      {
        "ask": {
          "prompt": "Start with what we can measure. How far does the ball fall between $t = 2$ and $t = 3$?",
          "format": "choice",
          "options": [
            {
              "label": "24.5 m",
              "correct": true
            },
            {
              "label": "44.1 m",
              "misconception": "value-not-change",
              "feedback": "That's $s(3)$, the total distance from the start. We want only what happens between $t = 2$ and $t = 3$: subtract $s(2) = 19.6$."
            },
            {
              "label": "4.9 m",
              "misconception": "coefficient",
              "feedback": "4.9 is the number in front of $t^2$, not a distance over this second. Work out $s(3) - s(2)$."
            }
          ]
        },
        "narration": "$s(3) - s(2) = 44.1 - 19.6 = 24.5$ m, covered in 1 second: an average of 24.5 m/s. That's an [[average-vs-instantaneous-rate|average rate]], the slope of the line through two points on the graph.\n\nBut the ball speeds up during that second, so 24.5 m/s is more than its speed at the very start, $t = 2$.",
        "builds_on": [
          "foundation:function"
        ]
      },
      {
        "ask": {
          "prompt": "Shrink the window to $[2, 2.1]$. What's the average speed now? ($s(2.1) = 21.609$)",
          "format": "choice",
          "options": [
            {
              "label": "20.09 m/s",
              "correct": true
            },
            {
              "label": "2.009 m/s",
              "misconception": "change-not-rate",
              "feedback": "2.009 m is the distance covered. It took only 0.1 s, so divide: 2.009 ÷ 0.1."
            },
            {
              "label": "24.5 m/s",
              "misconception": "same-average",
              "feedback": "That was the average over a full second. A shorter window gives a different (smaller) average."
            }
          ]
        },
        "narration": "$\\frac{21.609 - 19.6}{0.1} = 20.09$ m/s. Keep shrinking: over $[2, 2.01]$ it's 19.649 m/s, over $[2, 2.001]$ it's 19.6049 m/s. The averages are closing in on something."
      },
      {
        "ask": {
          "prompt": "What value are these averages settling toward? (in m/s)",
          "format": "number",
          "answer": 19.6,
          "tolerance": 0.01,
          "hint": "Look at the pattern: 20.09, 19.649, 19.6049, … Which number are they approaching?"
        },
        "narration": "They settle on 19.6 m/s. The value an expression approaches as the window shrinks is a [[limit]], and that limit is the ball's speed at exactly $t = 2$: the [[derivative]] of $s$ at 2.\n\nAlgebra confirms it. Over $[2, 2 + h]$ the average is $\\frac{4.9(2+h)^2 - 19.6}{h} = 19.6 + 4.9h$, and as $h \\to 0$ that becomes 19.6.",
        "math": [
          "\\lim_{h\\to 0}\\frac{s(2+h) - s(2)}{h} = \\lim_{h\\to 0}(19.6 + 4.9h) = 19.6"
        ],
        "widget": {
          "type": "secant",
          "f": "fall",
          "x0": 2,
          "prompt": "Shrink h: the secant's slope settles on the ball's speed at t = 2."
        },
        "builds_on": [
          "140.2.1"
        ]
      },
      {
        "ask": {
          "prompt": "What are the units of that answer?",
          "format": "choice",
          "options": [
            {
              "label": "metres per second",
              "correct": true
            },
            {
              "label": "metres",
              "misconception": "units-no-time",
              "feedback": "A rate always says per what: distance per unit of time."
            },
            {
              "label": "seconds per metre",
              "misconception": "units-flipped",
              "feedback": "Change in distance goes on top, time underneath."
            }
          ]
        },
        "narration": "A rate of change is always \"output units per input unit\": here metres per second, the units of speed. That's true of every derivative: it measures how much the output changes for each unit of input."
      }
    ],
    "summary": "Average rates come from two points; instantaneous rates come from shrinking the gap to nothing, which is a limit. The ball is falling at **19.6 m/s** at $t = 2$, and that number is the derivative of $s(t) = 4.9t^2$ at $t = 2$.",
    "claims": [
      {
        "sympy": "Rational(49, 10)*9 - Rational(49, 10)*4",
        "equals": "Rational(49, 2)"
      },
      {
        "sympy": "(Rational(49, 10)*Rational(21, 10)**2 - Rational(49, 10)*4)/Rational(1, 10)",
        "equals": "Rational(2009, 100)"
      },
      {
        "sympy": "limit((Rational(49, 10)*(2 + h)**2 - Rational(49, 10)*4)/h, h, 0)",
        "equals": "Rational(98, 5)"
      },
      {
        "sympy": "simplify((Rational(49, 10)*(2 + h)**2 - Rational(98, 5))/h - (Rational(98, 5) + Rational(49, 10)*h))",
        "equals": "0"
      }
    ]
  },
  {
    "id": "learn-definition",
    "subtopic": "140.3.1.definition",
    "title": "The exact slope of x² at x = 3",
    "problem": "Find the exact slope of $f(x) = x^2$ at $x = 3$, using only the definition of the derivative: $f'(3) = \\lim_{h\\to 0}\\frac{f(3+h) - f(3)}{h}$.",
    "steps": [
      {
        "ask": {
          "prompt": "First, what is $f(3 + h)$?",
          "format": "choice",
          "options": [
            {
              "label": "$9 + 6h + h^2$",
              "correct": true
            },
            {
              "label": "$9 + h^2$",
              "misconception": "dropped-cross-term",
              "feedback": "$(3+h)^2$ means $(3+h)(3+h)$: there are two cross terms, $3h + 3h = 6h$."
            },
            {
              "label": "$3 + h^2$",
              "misconception": "squared-only-h",
              "feedback": "Square the whole thing, $(3+h)^2$, not just the $h$."
            }
          ]
        },
        "narration": "$(3 + h)^2 = 9 + 6h + h^2$. Picture a 3-by-3 square grown by $h$ on two sides: two strips of area $3h$ and a tiny corner $h^2$.",
        "builds_on": [
          "140.3.1.rate"
        ]
      },
      {
        "ask": {
          "prompt": "Now simplify $\\frac{f(3+h) - f(3)}{h}$.",
          "format": "choice",
          "options": [
            {
              "label": "$6 + h$",
              "correct": true
            },
            {
              "label": "$6h + h^2$",
              "misconception": "forgot-to-divide",
              "feedback": "That's the top after subtracting 9. Now divide each term by $h$."
            },
            {
              "label": "$\\frac{0}{0}$",
              "misconception": "early-substitution",
              "feedback": "That's what you get by putting $h = 0$ in first. Simplify while $h$ is still not zero."
            }
          ]
        },
        "narration": "$\\frac{9 + 6h + h^2 - 9}{h} = \\frac{6h + h^2}{h} = 6 + h$. Dividing by $h$ is allowed because a [[limit]] only looks at $h$ near 0, never at $h = 0$ itself.",
        "math": [
          "\\frac{(3+h)^2 - 9}{h} = \\frac{6h + h^2}{h} = 6 + h"
        ]
      },
      {
        "ask": {
          "prompt": "Let $h \\to 0$. What is $f'(3)$?",
          "format": "number",
          "answer": 6,
          "tolerance": 0.001
        },
        "narration": "As $h$ shrinks, $6 + h$ heads to 6. So the slope of $x^2$ at $x = 3$ is exactly 6. That's the [[derivative]], found from nothing but its definition.",
        "widget": {
          "type": "secant",
          "f": "square",
          "x0": 3,
          "span": 2,
          "prompt": "Shrink h at x = 3. The slope reads 6 + h, closing in on 6."
        },
        "builds_on": [
          "foundation:limit",
          "140.2.2"
        ]
      },
      {
        "ask": {
          "prompt": "Do the same steps at any $x$. What is $f'(x)$?",
          "format": "choice",
          "options": [
            {
              "label": "$2x$",
              "correct": true
            },
            {
              "label": "$x^2$",
              "misconception": "same-as-f",
              "feedback": "That's $f(x)$ itself. Repeat the steps: $(x+h)^2 - x^2 = 2xh + h^2$."
            },
            {
              "label": "$6$",
              "misconception": "value-not-function",
              "feedback": "6 is the slope at $x = 3$ only. At other $x$ the slope is different."
            }
          ]
        },
        "narration": "$\\frac{(x+h)^2 - x^2}{h} = \\frac{2xh + h^2}{h} = 2x + h \\to 2x$. So the slope of $x^2$ at any point is $2x$: 6 at $x = 3$, 0 at the bottom of the parabola, negative on the left. The [[power-rule|power rule]] is the shortcut for exactly this calculation."
      }
    ],
    "summary": "The definition turns \"slope at a point\" into algebra: expand $f(a + h)$, subtract $f(a)$, divide by $h$, then let $h \\to 0$. For $x^2$ it gives $f'(3) = 6$ and, in general, $f'(x) = 2x$.",
    "claims": [
      {
        "sympy": "expand((3 + h)**2)",
        "equals": "9 + 6*h + h**2"
      },
      {
        "sympy": "cancel(((3 + h)**2 - 9)/h)",
        "equals": "6 + h"
      },
      {
        "sympy": "limit(((x + h)**2 - x**2)/h, h, 0)",
        "equals": "2*x"
      }
    ]
  },
  {
    "id": "learn-continuity",
    "subtopic": "140.3.1.continuity",
    "title": "Does |x| have a slope at 0?",
    "problem": "The graph of $f(x) = |x|$ is a V with its point at the origin. Is there a derivative at $x = 0$?",
    "steps": [
      {
        "ask": {
          "prompt": "First: is $|x|$ continuous at $x = 0$?",
          "format": "choice",
          "options": [
            {
              "label": "Yes",
              "correct": true
            },
            {
              "label": "No",
              "misconception": "corner-is-break",
              "feedback": "A corner isn't a break. Both sides approach 0, and $f(0) = 0$: you can draw it without lifting your pen."
            }
          ]
        },
        "narration": "Approaching 0 from either side, $|x|$ gets close to 0, and $f(0) = 0$. No jump, no gap: continuous.",
        "builds_on": [
          "140.2.4"
        ]
      },
      {
        "ask": {
          "prompt": "To the right of 0, $|x| = x$. What is the slope there?",
          "format": "choice",
          "options": [
            {
              "label": "$1$",
              "correct": true
            },
            {
              "label": "$-1$",
              "misconception": "slopes-swapped",
              "feedback": "For $x > 0$, $|x|$ is just $x$, the line going up at 45°."
            },
            {
              "label": "$0$",
              "misconception": "value-not-slope",
              "feedback": "0 is the value at the corner. The slope of $y = x$ is 1."
            }
          ]
        },
        "narration": "From the right, every secant from 0 to $h > 0$ has slope $\\frac{|h| - 0}{h} = \\frac{h}{h} = 1$."
      },
      {
        "ask": {
          "prompt": "To the left of 0, $|x| = -x$. What is the slope there?",
          "format": "choice",
          "options": [
            {
              "label": "$-1$",
              "correct": true
            },
            {
              "label": "$1$",
              "misconception": "slopes-swapped",
              "feedback": "For $x < 0$, $|x| = -x$, which goes down as you move right."
            },
            {
              "label": "$0$",
              "misconception": "value-not-slope",
              "feedback": "The slope of $y = -x$ is $-1$."
            }
          ]
        },
        "narration": "From the left, $h < 0$ and $|h| = -h$, so the secant slope is $\\frac{-h}{h} = -1$. The two sides never agree, however small $h$ gets.",
        "widget": {
          "type": "secant",
          "f": "abs",
          "x0": 0,
          "span": 2,
          "sides": "both",
          "prompt": "Shrink h. Left slope −1, right slope +1, always."
        }
      },
      {
        "ask": {
          "prompt": "So: is $|x|$ differentiable at $x = 0$?",
          "format": "choice",
          "options": [
            {
              "label": "No",
              "correct": true
            },
            {
              "label": "Yes",
              "misconception": "continuous-means-differentiable",
              "feedback": "It's continuous, but a derivative needs one slope, and the two sides give $-1$ and $+1$."
            }
          ]
        },
        "narration": "The one-sided slopes are $-1$ and $+1$, so the limit of the secant slopes doesn't exist: there's no derivative at the corner. Continuity isn't enough. The reverse does hold, though: [[differentiable-implies-continuous|if a function is differentiable, it must be continuous]]."
      }
    ],
    "summary": "$|x|$ is continuous at 0 but not differentiable there: its one-sided slopes are $-1$ and $+1$. Every differentiable function is continuous, but a corner shows that continuous functions don't have to be differentiable.",
    "claims": [
      {
        "sympy": "limit(Abs(h)/h, h, 0, '+')",
        "equals": "1"
      },
      {
        "sympy": "limit(Abs(h)/h, h, 0, '-')",
        "equals": "-1"
      },
      {
        "sympy": "limit(Abs(x), x, 0)",
        "equals": "0"
      }
    ]
  },
  {
    "id": "learn-sum",
    "subtopic": "140.3.2.sum",
    "title": "Why each term gets its own derivative",
    "problem": "Find the slope of $f(x) = 3x^2 + 5x$ at $x = 2$, and see why you can differentiate it one term at a time.",
    "steps": [
      {
        "ask": {
          "prompt": "Start with the plain $x^2$. What is its derivative?",
          "format": "choice",
          "options": [
            {
              "label": "$2x$",
              "correct": true
            },
            {
              "label": "$x$",
              "misconception": "dropped-coefficient",
              "feedback": "From the definition, $\\frac{(x+h)^2 - x^2}{h} = 2x + h \\to 2x$. The 2 comes down."
            },
            {
              "label": "$2$",
              "misconception": "value-not-function",
              "feedback": "The slope of $x^2$ changes from point to point, so its derivative is a function of $x$: $2x$."
            }
          ]
        },
        "narration": "From [[derivative|the definition]], $\\frac{(x+h)^2 - x^2}{h} = 2x + h$, which goes to $2x$.",
        "builds_on": [
          "140.3.1.definition"
        ]
      },
      {
        "ask": {
          "prompt": "Now $3x^2$ is $x^2$ stretched vertically by 3. How do its slopes compare with those of $x^2$?",
          "format": "choice",
          "options": [
            {
              "label": "3 times as steep everywhere",
              "correct": true
            },
            {
              "label": "The same",
              "misconception": "dropped-coefficient",
              "feedback": "Stretching a graph up by 3 makes every rise 3 times bigger over the same run."
            },
            {
              "label": "3 more",
              "misconception": "add-not-multiply",
              "feedback": "A vertical stretch multiplies every height, and so every slope, by 3. It doesn't add."
            }
          ]
        },
        "narration": "Every rise is tripled over the same run, so every slope is tripled: $(3x^2)' = 3\\cdot 2x = 6x$. That's the constant-multiple rule from [[sum-and-constant-rules|the sum and constant rules]]."
      },
      {
        "ask": {
          "prompt": "What is the derivative of $5x$?",
          "format": "choice",
          "options": [
            {
              "label": "$5$",
              "correct": true
            },
            {
              "label": "$5x$",
              "misconception": "same-as-f",
              "feedback": "That's the function itself. $5x$ is a straight line with slope 5."
            },
            {
              "label": "$0$",
              "misconception": "constant-confusion",
              "feedback": "Constants have derivative 0, but $5x$ isn't constant: it rises 5 for every step of 1."
            }
          ]
        },
        "narration": "$5x$ is a straight line rising 5 for every step of 1, so its slope is 5 everywhere."
      },
      {
        "ask": {
          "prompt": "Put it together: what is $f'(2)$ for $f(x) = 3x^2 + 5x$?",
          "format": "number",
          "answer": 17,
          "tolerance": 0.001,
          "hint": "Add the two derivatives, $6x$ and $5$, then put in $x = 2$."
        },
        "narration": "$f'(x) = 6x + 5$, so $f'(2) = 17$. Splitting is allowed because the difference quotient of a sum is the sum of the difference quotients, and the [[limit]] of a sum is the sum of the limits.",
        "math": [
          "\\frac{d}{dx}(3x^2 + 5x) = 6x + 5",
          "f'(2) = 17"
        ]
      }
    ],
    "summary": "Derivatives split over sums, and constants just multiply through: $(f + g)' = f' + g'$ and $(c f)' = c f'$. That's why polynomials can be differentiated one term at a time.",
    "claims": [
      {
        "sympy": "diff(3*x**2 + 5*x, x)",
        "equals": "6*x + 5"
      },
      {
        "sympy": "diff(3*x**2 + 5*x, x).subs(x, 2)",
        "equals": "17"
      }
    ]
  },
  {
    "id": "learn-power",
    "subtopic": "140.3.2.power",
    "title": "The power rule for roots and reciprocals",
    "problem": "Find the slopes of $\\sqrt{x}$ and $\\frac{1}{x}$ at $x = 4$.",
    "steps": [
      {
        "ask": {
          "prompt": "First rewrite $\\sqrt{x}$ as a power of $x$.",
          "format": "choice",
          "options": [
            {
              "label": "$x^{1/2}$",
              "correct": true
            },
            {
              "label": "$x^{2}$",
              "misconception": "root-is-square",
              "feedback": "A square root undoes squaring. It's the power that, doubled, gives 1: $x^{1/2}$."
            },
            {
              "label": "$x^{-1/2}$",
              "misconception": "root-is-reciprocal",
              "feedback": "That's $\\frac{1}{\\sqrt{x}}$. The square root itself is $x^{1/2}$."
            }
          ]
        },
        "narration": "$\\sqrt{x} = x^{1/2}$, because $x^{1/2}\\cdot x^{1/2} = x^{1} = x$.",
        "builds_on": [
          "140.1.3"
        ]
      },
      {
        "ask": {
          "prompt": "Apply $n x^{n-1}$ with $n = \\frac{1}{2}$:",
          "format": "choice",
          "options": [
            {
              "label": "$\\frac{1}{2}x^{-1/2}$",
              "correct": true
            },
            {
              "label": "$\\frac{1}{2}x^{1/2}$",
              "misconception": "exponent-unchanged",
              "feedback": "Bring the $\\frac{1}{2}$ down and also lower the exponent by 1: $\\frac{1}{2} - 1 = -\\frac{1}{2}$."
            },
            {
              "label": "$\\frac{1}{2}x^{3/2}$",
              "misconception": "power-up",
              "feedback": "The exponent goes down by one, not up."
            }
          ]
        },
        "narration": "$\\frac{1}{2}x^{-1/2} = \\frac{1}{2\\sqrt{x}}$. Why does a rule proved for whole-number powers work for $\\frac{1}{2}$? See [[negative-and-fractional-powers|roots and reciprocals]]: differentiating $\\sqrt{x}\\cdot\\sqrt{x} = x$ gives exactly this.",
        "math": [
          "\\frac{d}{dx}\\sqrt{x} = \\frac{1}{2\\sqrt{x}}"
        ]
      },
      {
        "ask": {
          "prompt": "So what is the slope of $\\sqrt{x}$ at $x = 4$?",
          "format": "number",
          "answer": 0.25,
          "tolerance": 0.001
        },
        "narration": "$\\frac{1}{2\\sqrt{4}} = \\frac{1}{4}$. The [[power-rule|power rule]] at work: the square root rises more and more slowly as $x$ grows.",
        "widget": {
          "type": "secant",
          "f": "sqrt",
          "x0": 4,
          "span": 3.5,
          "prompt": "Shrink h at x = 4: the slope settles on 0.25."
        }
      },
      {
        "ask": {
          "prompt": "Now $\\frac{1}{x} = x^{-1}$. Its derivative is:",
          "format": "choice",
          "options": [
            {
              "label": "$-\\frac{1}{x^2}$",
              "correct": true
            },
            {
              "label": "$\\frac{1}{x^2}$",
              "misconception": "dropped-sign",
              "feedback": "Bringing down $n = -1$ brings a minus sign with it: $-1\\cdot x^{-2}$."
            },
            {
              "label": "$-\\frac{1}{x}$",
              "misconception": "exponent-unchanged",
              "feedback": "Lower the exponent too: $-1 - 1 = -2$."
            }
          ]
        },
        "narration": "$-1\\cdot x^{-2} = -\\frac{1}{x^2}$: always negative, because $\\frac{1}{x}$ falls as $x$ grows. At $x = 4$ the slope is $-\\frac{1}{16}$."
      }
    ],
    "summary": "Rewrite roots and reciprocals as powers ($\\sqrt{x} = x^{1/2}$, $\\frac{1}{x} = x^{-1}$), then use $n x^{n-1}$. The slopes at $x = 4$ are $\\frac{1}{4}$ and $-\\frac{1}{16}$.",
    "claims": [
      {
        "sympy": "diff(sqrt(x), x).subs(x, 4)",
        "equals": "Rational(1, 4)"
      },
      {
        "sympy": "diff(1/x, x)",
        "equals": "-1/x**2"
      },
      {
        "sympy": "diff(1/x, x).subs(x, 4)",
        "equals": "-Rational(1, 16)"
      }
    ]
  },
  {
    "id": "learn-product",
    "subtopic": "140.3.2.product",
    "title": "A growing rectangle",
    "problem": "A rectangle's width is $w(t) = 2 + t$ cm and its height is $h(t) = 3 + 2t$ cm, with $t$ in seconds. How fast is its area growing at $t = 1$?",
    "steps": [
      {
        "ask": {
          "prompt": "A tempting guess: multiply the two rates, $w' \\cdot h' = 1 \\cdot 2 = 2$ cm²/s. Is that right?",
          "format": "choice",
          "options": [
            {
              "label": "No, it's too small",
              "correct": true
            },
            {
              "label": "Yes",
              "misconception": "product-of-derivatives",
              "feedback": "That only counts the tiny corner where both sides grow. Most of the new area comes from strips along the existing sides."
            }
          ]
        },
        "narration": "At $t = 1$ the rectangle is 3 cm by 5 cm. As it grows, new area appears as a strip along each side plus a tiny corner. Multiplying the rates only counts the corner. This is the picture behind the [[product-rule|product rule]].",
        "widget": {
          "type": "product-rectangle",
          "prompt": "Shrink the change: the two strips dominate and the corner vanishes."
        },
        "builds_on": [
          "foundation:area-shapes"
        ]
      },
      {
        "ask": {
          "prompt": "When the width grows by $\\Delta w$, the new strip along the side has area:",
          "format": "choice",
          "options": [
            {
              "label": "$h \\cdot \\Delta w$",
              "correct": true
            },
            {
              "label": "$\\Delta w \\cdot \\Delta h$",
              "misconception": "corner-only",
              "feedback": "That's the little corner. The strip runs the full height $h$ of the rectangle."
            },
            {
              "label": "$w \\cdot \\Delta w$",
              "misconception": "wrong-side",
              "feedback": "The strip added to the width runs along the height, so its long side is $h$."
            }
          ]
        },
        "narration": "So the area grows by $h\\,\\Delta w + w\\,\\Delta h + \\Delta w\\,\\Delta h$. Divide by $\\Delta t$ and shrink it: the corner term vanishes, leaving $A' = w'h + wh'$.",
        "math": [
          "A' = w'\\,h + w\\,h'"
        ]
      },
      {
        "ask": {
          "prompt": "So how fast is the area growing at $t = 1$? (in cm²/s)",
          "format": "number",
          "answer": 11,
          "tolerance": 0.001,
          "hint": "At $t = 1$: $w = 3$, $h = 5$, $w' = 1$, $h' = 2$. Use $w'h + wh'$."
        },
        "narration": "$1\\cdot 5 + 3\\cdot 2 = 11$ cm²/s. Check by expanding: $A = (2 + t)(3 + 2t) = 6 + 7t + 2t^2$, so $A' = 7 + 4t$, which is 11 at $t = 1$. ✓"
      }
    ],
    "summary": "The rate of change of a product has two parts, one for each factor's growth: $(wh)' = w'h + wh'$. The rectangle's area grows at **11 cm²/s** at $t = 1$, not $w'h' = 2$.",
    "claims": [
      {
        "sympy": "diff((2 + t)*(3 + 2*t), t).subs(t, 1)",
        "equals": "11"
      },
      {
        "sympy": "expand((2 + t)*(3 + 2*t))",
        "equals": "6 + 7*t + 2*t**2"
      }
    ]
  },
  {
    "id": "learn-quotient",
    "subtopic": "140.3.2.quotient",
    "title": "Cost per item",
    "problem": "Making $x$ items costs a fixed 100 dollars plus $x^2$ dollars in materials, so the cost per item is $c(x) = \\frac{x^2 + 100}{x}$. How fast is the cost per item changing at $x = 5$?",
    "steps": [
      {
        "ask": {
          "prompt": "Write the fraction as a product: $\\frac{x^2 + 100}{x} = (x^2 + 100)\\cdot x^{-1}$. What is the derivative of $x^{-1}$?",
          "format": "choice",
          "options": [
            {
              "label": "$-x^{-2}$",
              "correct": true
            },
            {
              "label": "$x^{-2}$",
              "misconception": "dropped-sign",
              "feedback": "Bringing down $n = -1$ brings its minus sign: $-1\\cdot x^{-2}$."
            },
            {
              "label": "$-x^{0}$",
              "misconception": "power-up",
              "feedback": "The exponent goes down by one: $-1 - 1 = -2$."
            }
          ]
        },
        "narration": "By the [[power-rule|power rule]], $(x^{-1})' = -x^{-2}$. Dividing is just multiplying by a reciprocal, so a fraction is a product in disguise.",
        "builds_on": [
          "140.3.2.power"
        ]
      },
      {
        "ask": {
          "prompt": "The product rule on $f \\cdot g^{-1}$, put over a common denominator, gives:",
          "format": "choice",
          "options": [
            {
              "label": "$\\frac{f'g - fg'}{g^2}$",
              "correct": true
            },
            {
              "label": "$\\frac{fg' - f'g}{g^2}$",
              "misconception": "quotient-order",
              "feedback": "The derivative of the top comes first: $f'g - fg'$. Swapping flips the sign."
            },
            {
              "label": "$\\frac{f'g - fg'}{g}$",
              "misconception": "forgot-square",
              "feedback": "The $g^{-2}$ from differentiating $g^{-1}$ makes the denominator $g^2$."
            }
          ]
        },
        "narration": "$f'g^{-1} + f\\cdot(-g^{-2}g') = \\frac{f'g - fg'}{g^2}$. The [[chain-rule|chain rule]] handles $(g^{-1})'$. That's the whole [[quotient-rule|quotient rule]], built from rules you already know.",
        "math": [
          "\\left(\\frac{f}{g}\\right)' = \\frac{f'g - fg'}{g^2}"
        ],
        "builds_on": [
          "140.3.2.product",
          "140.3.2.chain"
        ]
      },
      {
        "ask": {
          "prompt": "With $f = x^2 + 100$ and $g = x$, what is $c'(5)$? (dollars per item, per extra item)",
          "format": "number",
          "answer": -3,
          "tolerance": 0.001,
          "hint": "$c'(x) = \\frac{2x\\cdot x - (x^2 + 100)\\cdot 1}{x^2}$. Put in $x = 5$."
        },
        "narration": "$c'(5) = \\frac{50 - 125}{25} = -3$: making one more item lowers the cost per item by about 3 dollars, because the fixed 100 dollars is spread over more items. Check: $c(x) = x + \\frac{100}{x}$, so $c'(x) = 1 - \\frac{100}{x^2} = -3$ at $x = 5$. ✓"
      }
    ],
    "summary": "A quotient is a product with a reciprocal, so the quotient rule $\\frac{f'g - fg'}{g^2}$ comes from the product, chain and power rules. Here the cost per item is falling at **3 dollars per extra item** when $x = 5$.",
    "claims": [
      {
        "sympy": "diff((x**2 + 100)/x, x).subs(x, 5)",
        "equals": "-3"
      },
      {
        "sympy": "simplify(diff((x**2 + 100)/x, x) - (2*x*x - (x**2 + 100))/x**2)",
        "equals": "0"
      }
    ]
  },
  {
    "id": "learn-chain",
    "subtopic": "140.3.2.chain",
    "title": "An inflating balloon",
    "problem": "A spherical balloon is being inflated so its radius grows at 2 cm/s. How fast is its volume growing when the radius is 3 cm? (The volume of a sphere is $V = \\frac{4}{3}\\pi r^3$.)",
    "steps": [
      {
        "ask": {
          "prompt": "Which rate are we given?",
          "format": "choice",
          "options": [
            {
              "label": "$\\frac{dr}{dt} = 2$ cm/s",
              "correct": true
            },
            {
              "label": "$\\frac{dV}{dt}$",
              "misconception": "wanted-not-given",
              "feedback": "That's what we're asked to find."
            },
            {
              "label": "$\\frac{dV}{dr}$",
              "misconception": "computed-not-given",
              "feedback": "We can work that out from the formula, but it isn't given."
            }
          ]
        },
        "narration": "The radius changes in time, and the volume depends on the radius. Time feeds the radius, and the radius feeds the volume: a chain of two functions.",
        "builds_on": [
          "140.1.1"
        ]
      },
      {
        "ask": {
          "prompt": "How fast does the volume change per centimetre of radius? $\\frac{dV}{dr} = $",
          "format": "choice",
          "options": [
            {
              "label": "$4\\pi r^2$",
              "correct": true
            },
            {
              "label": "$\\frac{4}{3}\\pi r^2$",
              "misconception": "dropped-coefficient",
              "feedback": "Bring the 3 down: $3\\cdot\\frac{4}{3} = 4$."
            },
            {
              "label": "$4\\pi r^3$",
              "misconception": "exponent-unchanged",
              "feedback": "Lower the exponent by one: $r^3$ becomes $3r^2$."
            }
          ]
        },
        "narration": "By the [[power-rule|power rule]], $\\frac{dV}{dr} = 4\\pi r^2$, which is the sphere's surface area. Growing a sphere adds a thin shell, and the shell's area is $4\\pi r^2$.",
        "builds_on": [
          "140.3.2.power"
        ]
      },
      {
        "ask": {
          "prompt": "How do the two rates combine into $\\frac{dV}{dt}$?",
          "format": "choice",
          "options": [
            {
              "label": "$\\frac{dV}{dr}\\cdot\\frac{dr}{dt}$",
              "correct": true
            },
            {
              "label": "$\\frac{dV}{dr} + \\frac{dr}{dt}$",
              "misconception": "add-rates",
              "feedback": "Rates along a chain multiply: each cm/s of radius brings $4\\pi r^2$ cm³ of volume per cm."
            },
            {
              "label": "$\\frac{dV}{dr} \\div \\frac{dr}{dt}$",
              "misconception": "divide-rates",
              "feedback": "Check the units: (cm³ per cm) × (cm per s) gives cm³ per s. Division doesn't."
            }
          ]
        },
        "narration": "Rates along a chain multiply. That's the [[chain-rule|chain rule]]: $\\frac{dV}{dt} = \\frac{dV}{dr}\\cdot\\frac{dr}{dt}$. The units cancel like fractions: $\\frac{\\text{cm}^3}{\\text{cm}}\\cdot\\frac{\\text{cm}}{\\text{s}} = \\frac{\\text{cm}^3}{\\text{s}}$.",
        "math": [
          "\\frac{dV}{dt} = \\frac{dV}{dr}\\cdot\\frac{dr}{dt}"
        ]
      },
      {
        "ask": {
          "prompt": "So how fast is the volume growing at $r = 3$? (in cm³/s, to one decimal place)",
          "format": "number",
          "answer": 226.19,
          "tolerance": 0.1,
          "hint": "$4\\pi\\cdot 3^2\\cdot 2$."
        },
        "narration": "$4\\pi\\cdot 9\\cdot 2 = 72\\pi \\approx 226.2$ cm³/s. Notice that the radius grows steadily but the volume grows faster and faster: the shell being added gets bigger as the balloon grows.",
        "widget": {
          "type": "chain-stretch",
          "f": "sin",
          "a": 2,
          "prompt": "Squeezing a curve by a multiplies its slopes by a: the same idea as multiplying rates."
        }
      }
    ],
    "summary": "When one quantity depends on another that changes in time, the rates multiply: $\\frac{dV}{dt} = \\frac{dV}{dr}\\cdot\\frac{dr}{dt}$. The balloon's volume grows at $72\\pi \\approx$ **226.2 cm³/s** when $r = 3$ cm.",
    "claims": [
      {
        "sympy": "diff(Rational(4, 3)*pi*x**3, x)",
        "equals": "4*pi*x**2"
      },
      {
        "sympy": "4*pi*3**2*2",
        "equals": "72*pi"
      },
      {
        "sympy": "72*pi",
        "approx": 226.19,
        "tol": 0.01
      }
    ]
  },
  {
    "id": "learn-table",
    "subtopic": "140.2.1.table",
    "title": "What is sin x / x at 0?",
    "problem": "$f(x) = \\frac{\\sin x}{x}$ can't be evaluated at $x = 0$. What does it do near 0?",
    "steps": [
      {
        "ask": {
          "prompt": "Substitute $x = 0$. What do you get?",
          "format": "choice",
          "options": [
            {
              "label": "$\\frac{0}{0}$, which is undefined",
              "correct": true
            },
            {
              "label": "$0$",
              "misconception": "top-is-zero",
              "feedback": "The top is 0, but so is the bottom. $\\frac{0}{0}$ isn't 0; it isn't anything yet."
            },
            {
              "label": "$\\infty$",
              "misconception": "divide-by-zero-is-infinity",
              "feedback": "A number over 0 blows up only when the top isn't 0. Here the top is 0 too."
            }
          ]
        },
        "narration": "$\\frac{\\sin 0}{0} = \\frac{0}{0}$, which is undefined. That's not the end of the story. A [[limit]] asks where the values head as $x$ gets close to 0, not what happens at 0.",
        "builds_on": [
          "foundation:function"
        ]
      },
      {
        "ask": {
          "prompt": "Use a calculator in radians. What is $\\frac{\\sin(0.1)}{0.1}$, to 3 decimal places?",
          "format": "number",
          "answer": 0.998,
          "tolerance": 0.001,
          "hint": "$\\sin(0.1) \\approx 0.09983$. Divide that by $0.1$."
        },
        "narration": "$\\frac{\\sin(0.1)}{0.1} \\approx 0.99833$. Closer in, $\\frac{\\sin(0.01)}{0.01} \\approx 0.99998$ and $\\frac{\\sin(0.001)}{0.001} \\approx 0.9999998$. Negative inputs give exactly the same values, because $\\frac{\\sin(-x)}{-x} = \\frac{\\sin x}{x}$.",
        "math": [
          "\\begin{array}{c|c} x & \\frac{\\sin x}{x} \\\\ \\hline \\pm 0.1 & 0.99833 \\\\ \\pm 0.01 & 0.99998 \\\\ \\pm 0.001 & 0.9999998 \\end{array}"
        ]
      },
      {
        "ask": {
          "prompt": "What value are the outputs approaching?",
          "format": "number",
          "answer": 1,
          "tolerance": 0.001,
          "hint": "Look at the pattern: 0.99833, 0.99998, 0.9999998. Which number are they closing in on?"
        },
        "narration": "They settle on 1 from both sides, so $\\lim_{x\\to 0}\\frac{\\sin x}{x} = 1$. On the [[unit-circle|unit circle]], a small angle's height $\\sin x$ and its arc length $x$ are almost the same, so their ratio is almost 1.",
        "widget": {
          "type": "limit-zoom",
          "g": "sinh_over_h",
          "at": 0,
          "limit": 1,
          "prompt": "Zoom in toward 0: the outputs settle on 1, even though there's a hole at 0 itself."
        }
      },
      {
        "ask": {
          "prompt": "So does $\\frac{\\sin x}{x}$ have a limit at 0, even though it has no value there?",
          "format": "choice",
          "options": [
            {
              "label": "Yes: the limit is 1",
              "correct": true
            },
            {
              "label": "No: with no value at 0, there's no limit",
              "misconception": "limit-needs-value",
              "feedback": "A limit never uses the value at the point, only the values near it, and those clearly head to 1."
            },
            {
              "label": "Yes: the limit is $\\frac{0}{0}$",
              "misconception": "zero-over-zero-is-a-value",
              "feedback": "$\\frac{0}{0}$ isn't a number. The limit is where the values head, and the table shows that."
            }
          ]
        },
        "narration": "A limit doesn't need a value at the point. This one, $\\frac{\\sin x}{x} \\to 1$, is the key step in finding the derivative of $\\sin$ ([[sin-h-over-h|see why]])."
      }
    ],
    "summary": "A table of values closing in from both sides shows where a function is heading. $\\frac{\\sin x}{x}$ is undefined at 0, yet $\\lim_{x\\to 0}\\frac{\\sin x}{x} = 1$: a limit only cares about the values **near** the point.",
    "claims": [
      {
        "sympy": "limit(sin(x)/x, x, 0)",
        "equals": "1"
      },
      {
        "sympy": "sin(Rational(1, 10))/Rational(1, 10)",
        "approx": 0.998334,
        "tol": 1e-06
      },
      {
        "sympy": "sin(Rational(1, 100))/Rational(1, 100)",
        "approx": 0.9999833,
        "tol": 1e-07
      }
    ]
  },
  {
    "id": "learn-one-sided",
    "subtopic": "140.2.1.one-sided",
    "title": "The parking garage jump",
    "problem": "A garage charges 4 dollars for every hour or part of an hour. What happens to the cost $C(t)$ as the parking time $t$ approaches 2 hours?",
    "steps": [
      {
        "ask": {
          "prompt": "What do you pay for 1 hour 59 minutes?",
          "format": "choice",
          "options": [
            {
              "label": "8 dollars",
              "correct": true
            },
            {
              "label": "About 7.93 dollars",
              "misconception": "prorated",
              "feedback": "The garage charges whole hours. Any part of the second hour costs the full 4 dollars."
            },
            {
              "label": "4 dollars",
              "misconception": "rounded-down",
              "feedback": "1 h 59 min is into the second hour, so you pay for two hours."
            }
          ]
        },
        "narration": "Any time in the second hour costs $2 \\times 4 = 8$ dollars. As $t$ creeps up to 2 from below (1.9 h, 1.99 h, 1.999 h), the cost stays at 8. That's the [[one-sided-limit|left-hand limit]]: $\\lim_{t\\to 2^-} C(t) = 8$.",
        "builds_on": [
          "140.2.1.table"
        ]
      },
      {
        "ask": {
          "prompt": "And just after 2 hours, at 2 h 01 min?",
          "format": "choice",
          "options": [
            {
              "label": "12 dollars",
              "correct": true
            },
            {
              "label": "8 dollars",
              "misconception": "same-both-sides",
              "feedback": "One minute past 2 hours, you've started a third hour."
            },
            {
              "label": "10 dollars",
              "misconception": "average-of-sides",
              "feedback": "There's no in-between price: one minute past 2 hours starts a whole new hour."
            }
          ]
        },
        "narration": "Past 2 hours you've started a third hour, so the cost is 12 dollars. As $t$ approaches 2 from above, the cost stays at 12, so $\\lim_{t\\to 2^+} C(t) = 12$.",
        "widget": {
          "type": "limit-zoom",
          "g": "parking",
          "at": 2,
          "left": 8,
          "right": 12,
          "prompt": "Zoom in on t = 2: the left side stays at 8 and the right side at 12, however close you get."
        }
      },
      {
        "ask": {
          "prompt": "Does $\\lim_{t\\to 2} C(t)$ exist?",
          "format": "choice",
          "options": [
            {
              "label": "No: the left and right limits disagree",
              "correct": true
            },
            {
              "label": "Yes, it's 8, because $C(2) = 8$",
              "misconception": "limit-is-value",
              "feedback": "$C(2) = 8$ is the price at exactly 2 hours. The limit asks where the price is heading, and it heads to two different places."
            },
            {
              "label": "Yes, it's 10, halfway between",
              "misconception": "average-of-sides",
              "feedback": "Averaging doesn't rescue it. A two-sided limit exists only when both sides agree."
            }
          ]
        },
        "narration": "The two-sided [[limit]] exists only when both one-sided limits agree. Since $8 \\ne 12$, there's no limit at 2, even though the garage has a price at exactly 2 hours ($C(2) = 8$). A value and a limit answer different questions."
      }
    ],
    "summary": "Approaching from the left, the cost heads to **8 dollars**; from the right, to **12 dollars**. The one-sided limits disagree, so $\\lim_{t\\to 2} C(t)$ doesn't exist, even though $C(2) = 8$ does.",
    "claims": [
      {
        "sympy": "4*ceiling(Rational(199, 100))",
        "equals": "8"
      },
      {
        "sympy": "4*ceiling(Rational(201, 100))",
        "equals": "12"
      },
      {
        "sympy": "4*ceiling(2)",
        "equals": "8"
      }
    ]
  },
  {
    "id": "learn-factor",
    "subtopic": "140.2.2.factor",
    "title": "Cancelling the zero",
    "problem": "Find $\\lim_{x\\to 3}\\frac{x^2 - 9}{x - 3}$.",
    "steps": [
      {
        "ask": {
          "prompt": "Substitute $x = 3$. What do you get?",
          "format": "choice",
          "options": [
            {
              "label": "$\\frac{0}{0}$",
              "correct": true
            },
            {
              "label": "$0$",
              "misconception": "zero-over-zero-is-0",
              "feedback": "The top is 0, but so is the bottom. $\\frac{0}{0}$ isn't 0: it's a sign to simplify."
            },
            {
              "label": "No limit: you can't divide by zero",
              "misconception": "zero-over-zero-dne",
              "feedback": "$\\frac{0}{0}$ means the algebra isn't finished, not that there's no limit."
            }
          ]
        },
        "narration": "$\\frac{9 - 9}{3 - 3} = \\frac{0}{0}$. That's an [[indeterminate-form|indeterminate form]]: a signal to simplify, not an answer.",
        "builds_on": [
          "140.2.1.table"
        ]
      },
      {
        "ask": {
          "prompt": "Factor the top. What is $x^2 - 9$?",
          "format": "choice",
          "options": [
            {
              "label": "$(x - 3)(x + 3)$",
              "correct": true
            },
            {
              "label": "$(x - 3)^2$",
              "misconception": "square-of-difference",
              "feedback": "$(x - 3)^2 = x^2 - 6x + 9$. You want a difference of squares."
            },
            {
              "label": "$(x - 9)(x + 1)$",
              "misconception": "factor-slip",
              "feedback": "Multiply it out: $(x - 9)(x + 1) = x^2 - 8x - 9$, not $x^2 - 9$."
            }
          ]
        },
        "narration": "It's a difference of squares: $x^2 - 9 = (x - 3)(x + 3)$. Now the top and bottom share the factor $x - 3$."
      },
      {
        "ask": {
          "prompt": "Cancel the common factor. What's left?",
          "format": "choice",
          "options": [
            {
              "label": "$x + 3$",
              "correct": true
            },
            {
              "label": "$x - 3$",
              "misconception": "kept-cancelled-factor",
              "feedback": "$x - 3$ is the factor that cancels. What's left is the other one."
            },
            {
              "label": "$x^2 - 3$",
              "misconception": "cancelled-terms",
              "feedback": "You can only cancel factors, not pieces of a sum: $\\frac{x^2 - 9}{x - 3}$ isn't $x^2 - \\frac{9}{3}$."
            }
          ]
        },
        "narration": "For every $x \\ne 3$, $\\frac{(x - 3)(x + 3)}{x - 3} = x + 3$. Cancelling is allowed because a [[limit]] never looks at $x = 3$ itself, only near it."
      },
      {
        "ask": {
          "prompt": "Now substitute $x = 3$. What is the limit?",
          "format": "number",
          "answer": 6,
          "tolerance": 0.001
        },
        "narration": "$x + 3 \\to 6$. The original function is the line $y = x + 3$ with one point missing: a hole at $(3, 6)$.",
        "math": [
          "\\lim_{x\\to 3}\\frac{x^2 - 9}{x - 3} = \\lim_{x\\to 3}(x + 3) = 6"
        ],
        "widget": {
          "type": "limit-zoom",
          "g": "hole3",
          "at": 3,
          "limit": 6,
          "prompt": "Zoom in at x = 3: the outputs settle on 6, right at the hole."
        }
      }
    ],
    "summary": "Substituting gave $\\frac{0}{0}$, so we simplified. Factoring and cancelling $x - 3$ left $x + 3$, and $\\lim_{x\\to 3}\\frac{x^2 - 9}{x - 3} = $ **6**.",
    "claims": [
      {
        "sympy": "limit((x**2 - 9)/(x - 3), x, 3)",
        "equals": "6"
      },
      {
        "sympy": "factor(x**2 - 9)",
        "equals": "(x - 3)*(x + 3)"
      },
      {
        "sympy": "expand((x - 9)*(x + 1))",
        "equals": "x**2 - 8*x - 9"
      }
    ]
  },
  {
    "id": "learn-rationalize",
    "subtopic": "140.2.2.rationalize",
    "title": "A square root in the way",
    "problem": "Find $\\lim_{x\\to 0}\\frac{\\sqrt{x + 4} - 2}{x}$.",
    "steps": [
      {
        "ask": {
          "prompt": "Substituting gives $\\frac{0}{0}$. Can you factor and cancel as it stands?",
          "format": "choice",
          "options": [
            {
              "label": "No: there's no common factor while the square root is there",
              "correct": true
            },
            {
              "label": "Yes: cancel the $x$ on top with the $x$ below",
              "misconception": "cancelled-inside-root",
              "feedback": "The $x$ on top is inside the square root. You can only cancel a factor of the whole top."
            },
            {
              "label": "Yes: $\\sqrt{x + 4} - 2 = \\sqrt{x}$",
              "misconception": "split-root",
              "feedback": "Square roots don't split over sums. Check $x = 5$: $\\sqrt{9} - 2 = 1$, but $\\sqrt{5} \\approx 2.24$."
            }
          ]
        },
        "narration": "The top is a square root minus a number, with no visible factor of $x$. We need to get rid of the square root first.",
        "builds_on": [
          "140.2.2.factor"
        ]
      },
      {
        "ask": {
          "prompt": "Multiply top and bottom by which expression?",
          "format": "choice",
          "options": [
            {
              "label": "$\\sqrt{x + 4} + 2$",
              "correct": true
            },
            {
              "label": "$\\sqrt{x + 4} - 2$",
              "misconception": "same-not-conjugate",
              "feedback": "Multiplying by the same expression squares it and keeps the root. Flip the middle sign: $(A - B)(A + B) = A^2 - B^2$."
            },
            {
              "label": "$x$",
              "misconception": "wrong-factor",
              "feedback": "That doesn't touch the square root."
            }
          ]
        },
        "narration": "The [[conjugate-trick|conjugate]] $\\sqrt{x + 4} + 2$ turns the top into a difference of squares: $(\\sqrt{x + 4} - 2)(\\sqrt{x + 4} + 2) = (x + 4) - 4 = x$.",
        "math": [
          "\\frac{\\sqrt{x + 4} - 2}{x}\\cdot\\frac{\\sqrt{x + 4} + 2}{\\sqrt{x + 4} + 2} = \\frac{x}{x\\,(\\sqrt{x + 4} + 2)}"
        ]
      },
      {
        "ask": {
          "prompt": "Cancel the $x$. What's left?",
          "format": "choice",
          "options": [
            {
              "label": "$\\frac{1}{\\sqrt{x + 4} + 2}$",
              "correct": true
            },
            {
              "label": "$\\sqrt{x + 4} + 2$",
              "misconception": "flipped",
              "feedback": "The conjugate ended up on the bottom: you multiplied the bottom by it."
            },
            {
              "label": "$\\frac{1}{\\sqrt{x + 4} - 2}$",
              "misconception": "sign-slip",
              "feedback": "The factor you multiplied by has a plus sign, and that's the one that stays."
            }
          ]
        },
        "narration": "Once the $x$ cancels, nothing is $\\frac{0}{0}$ any more."
      },
      {
        "ask": {
          "prompt": "Substitute $x = 0$. What is the limit?",
          "format": "number",
          "answer": 0.25,
          "tolerance": 0.002,
          "hint": "$\\sqrt{4} = 2$, so the bottom is $2 + 2$."
        },
        "narration": "$\\frac{1}{\\sqrt{4} + 2} = \\frac{1}{4}$. Zooming in on the original function confirms it.",
        "widget": {
          "type": "limit-zoom",
          "g": "rootdiff",
          "at": 0,
          "limit": 0.25,
          "prompt": "Zoom in at 0: the original function settles on 1/4."
        }
      }
    ],
    "summary": "The square root hid the common factor. Multiplying by the conjugate $\\sqrt{x + 4} + 2$ exposed it, and the limit is **1/4**.",
    "claims": [
      {
        "sympy": "limit((sqrt(x + 4) - 2)/x, x, 0)",
        "equals": "1/4"
      },
      {
        "sympy": "simplify((sqrt(x + 4) - 2)/x - 1/(sqrt(x + 4) + 2))",
        "equals": "0"
      },
      {
        "sympy": "expand((sqrt(x + 4) - 2)*(sqrt(x + 4) + 2))",
        "equals": "x"
      }
    ]
  },
  {
    "id": "learn-squeeze",
    "subtopic": "140.2.2.squeeze",
    "title": "Trapping a wild function",
    "problem": "Find $\\lim_{x\\to 0} x^2 \\sin\\left(\\frac{1}{x}\\right)$.",
    "steps": [
      {
        "ask": {
          "prompt": "Can you use \"the limit of a product is the product of the limits\"?",
          "format": "choice",
          "options": [
            {
              "label": "No: $\\sin(1/x)$ has no limit at 0",
              "correct": true
            },
            {
              "label": "Yes: it's $0 \\cdot \\sin(\\infty) = 0$",
              "misconception": "infinity-as-number",
              "feedback": "$\\sin(\\infty)$ isn't a number. As $\\frac{1}{x}$ grows, $\\sin(1/x)$ keeps swinging between $-1$ and $1$."
            },
            {
              "label": "No: $x^2$ has no limit at 0",
              "misconception": "blamed-wrong-factor",
              "feedback": "$x^2$ behaves perfectly: it goes to 0. The problem is the other factor."
            }
          ]
        },
        "narration": "As $x \\to 0$, $\\frac{1}{x}$ races off and $\\sin(1/x)$ swings between $-1$ and $1$ faster and faster. It never settles, so the product law can't be used.",
        "builds_on": [
          "foundation:unit-circle"
        ]
      },
      {
        "ask": {
          "prompt": "Which pair of bounds traps $x^2 \\sin(1/x)$ and closes in on a single value?",
          "format": "choice",
          "options": [
            {
              "label": "$-x^2 \\le x^2\\sin(1/x) \\le x^2$",
              "correct": true
            },
            {
              "label": "$-1 \\le x^2\\sin(1/x) \\le 1$",
              "misconception": "bounds-dont-meet",
              "feedback": "True near 0, but these bounds stay 2 apart. They trap the function without squeezing it."
            },
            {
              "label": "$0 \\le x^2\\sin(1/x) \\le x^2$",
              "misconception": "lower-bound-too-high",
              "feedback": "$\\sin(1/x)$ is negative about half the time, so the function dips below 0."
            }
          ]
        },
        "narration": "Since $-1 \\le \\sin(1/x) \\le 1$, multiplying by $x^2 \\ge 0$ gives $-x^2 \\le x^2\\sin(1/x) \\le x^2$.",
        "widget": {
          "type": "limit-zoom",
          "g": "x2sin",
          "at": 0,
          "limit": 0,
          "bounds": [
            "square",
            "negsquare"
          ],
          "prompt": "Zoom in: the wiggles never escape the two parabolas, and the parabolas pinch to 0."
        }
      },
      {
        "ask": {
          "prompt": "Both bounds go to 0 as $x \\to 0$. What is the limit?",
          "format": "number",
          "answer": 0,
          "tolerance": 0.001
        },
        "narration": "Trapped between $-x^2$ and $x^2$, both heading to 0, the function has nowhere else to go: the limit is 0. That's the [[squeeze-theorem|squeeze theorem]]."
      }
    ],
    "summary": "$\\sin(1/x)$ has no limit, but it's bounded. Squeezed between $-x^2$ and $x^2$, the product $x^2\\sin(1/x)$ goes to **0**.",
    "claims": [
      {
        "sympy": "limit(x**2*sin(1/x), x, 0)",
        "equals": "0"
      },
      {
        "sympy": "limit(x**2, x, 0)",
        "equals": "0"
      }
    ]
  },
  {
    "id": "learn-infinity",
    "subtopic": "140.2.3.infinity",
    "title": "Where average cost settles",
    "problem": "A print shop pays 5000 dollars to set up a poster run, plus 3 dollars per poster. For $n$ posters the average cost per poster is $A(n) = \\frac{5000 + 3n}{n}$. What happens to $A(n)$ as $n$ grows?",
    "steps": [
      {
        "ask": {
          "prompt": "What is the average cost per poster for 1000 posters, in dollars?",
          "format": "number",
          "answer": 8,
          "tolerance": 0.01,
          "hint": "$\\frac{5000 + 3 \\cdot 1000}{1000}$"
        },
        "narration": "$A(1000) = \\frac{8000}{1000} = 8$ dollars a poster. For 10 000 posters it's 3.50 dollars, and for 100 000 it's 3.05 dollars."
      },
      {
        "ask": {
          "prompt": "Split the fraction. $A(n)$ equals:",
          "format": "choice",
          "options": [
            {
              "label": "$\\frac{5000}{n} + 3$",
              "correct": true
            },
            {
              "label": "$5000 + 3$",
              "misconception": "cancelled-n-wrongly",
              "feedback": "Divide each term on top by $n$: $\\frac{5000}{n} + \\frac{3n}{n}$."
            },
            {
              "label": "$\\frac{5000}{n} + 3n$",
              "misconception": "forgot-to-divide",
              "feedback": "The $3n$ term is divided by $n$ too: $\\frac{3n}{n} = 3$."
            }
          ]
        },
        "narration": "Divide each term by $n$ to get $\\frac{5000}{n} + 3$. The setup cost is being shared among more and more posters."
      },
      {
        "ask": {
          "prompt": "As $n \\to \\infty$, what does $A(n)$ approach, in dollars?",
          "format": "number",
          "answer": 3,
          "tolerance": 0.01
        },
        "narration": "$\\frac{5000}{n} \\to 0$, so $A(n) \\to 3$. That's a [[limit-at-infinity|limit at infinity]], and $y = 3$ is a horizontal asymptote. The average cost gets as close to the 3 dollar printing cost as you like, but never reaches it.",
        "widget": {
          "type": "far-out",
          "mode": "infinity",
          "f": "avgcost",
          "asymptote": 3,
          "prompt": "Push n further out: the average cost flattens toward 3 dollars."
        }
      },
      {
        "ask": {
          "prompt": "Which shortcut gives this answer for any fraction of polynomials whose top and bottom have the same degree?",
          "format": "choice",
          "options": [
            {
              "label": "Divide the leading coefficients: $\\frac{3n}{n} \\to 3$",
              "correct": true
            },
            {
              "label": "Divide the constant terms",
              "misconception": "constant-terms",
              "feedback": "Far out, the constants are negligible; the highest powers dominate."
            },
            {
              "label": "The answer is always $\\infty$, because the top grows",
              "misconception": "top-grows-so-infinity",
              "feedback": "The bottom grows too, and at the same rate when the degrees match."
            }
          ]
        },
        "narration": "Far out, only the highest powers matter. When the top and bottom have the same degree, the limit is the ratio of the leading coefficients. A smaller top degree gives 0, and a bigger one means no finite limit."
      }
    ],
    "summary": "Splitting the fraction showed $A(n) = \\frac{5000}{n} + 3$. As $n \\to \\infty$, the average cost approaches **3 dollars**: the horizontal asymptote $y = 3$.",
    "claims": [
      {
        "sympy": "limit((5000 + 3*x)/x, x, oo)",
        "equals": "3"
      },
      {
        "sympy": "Rational(5000 + 3*1000, 1000)",
        "equals": "8"
      },
      {
        "sympy": "Rational(5000 + 3*10000, 10000)",
        "equals": "7/2"
      },
      {
        "sympy": "Rational(5000 + 3*100000, 100000)",
        "equals": "61/20"
      }
    ]
  },
  {
    "id": "learn-asymptote",
    "subtopic": "140.2.3.asymptotes",
    "title": "When the bottom hits zero",
    "problem": "What does $f(x) = \\frac{x + 1}{x - 2}$ do near $x = 2$?",
    "steps": [
      {
        "ask": {
          "prompt": "Substitute $x = 2$. What do you get?",
          "format": "choice",
          "options": [
            {
              "label": "$\\frac{3}{0}$: a nonzero number over zero",
              "correct": true
            },
            {
              "label": "$\\frac{0}{0}$",
              "misconception": "assumed-zero-over-zero",
              "feedback": "The top is $2 + 1 = 3$, not 0."
            },
            {
              "label": "$0$",
              "misconception": "tiny-bottom-small-answer",
              "feedback": "Dividing by zero doesn't give zero. The top stays near 3 while the bottom shrinks."
            }
          ]
        },
        "narration": "$\\frac{3}{0}$ isn't $\\frac{0}{0}$, so there's nothing to cancel. A number near 3 divided by something closer and closer to 0 grows without bound: there's a vertical asymptote at $x = 2$.",
        "builds_on": [
          "140.2.1.one-sided"
        ]
      },
      {
        "ask": {
          "prompt": "Just right of 2, say at $x = 2.001$, what is $f(x)$ like?",
          "format": "choice",
          "options": [
            {
              "label": "Large and positive",
              "correct": true
            },
            {
              "label": "Large and negative",
              "misconception": "sign-slip",
              "feedback": "At 2.001 the bottom is $+0.001$ and the top is about 3, so the ratio is positive."
            },
            {
              "label": "Close to 0",
              "misconception": "tiny-bottom-small-answer",
              "feedback": "Dividing by a tiny number makes the result huge, not tiny."
            }
          ]
        },
        "narration": "$f(2.001) = \\frac{3.001}{0.001} = 3001$, and $f(2.0001) = 30\\,001$. So $\\lim_{x\\to 2^+} f(x) = +\\infty$."
      },
      {
        "ask": {
          "prompt": "And as $x \\to 2$ from the left?",
          "format": "choice",
          "options": [
            {
              "label": "$f(x) \\to -\\infty$",
              "correct": true
            },
            {
              "label": "$f(x) \\to +\\infty$",
              "misconception": "same-both-sides",
              "feedback": "Left of 2 the bottom $x - 2$ is negative, so the ratio is negative."
            },
            {
              "label": "$f(x) \\to 0$",
              "misconception": "tiny-bottom-small-answer",
              "feedback": "Dividing by a tiny number makes the result huge, not tiny."
            }
          ]
        },
        "narration": "$f(1.999) = \\frac{2.999}{-0.001} = -2999$. From the left the outputs plunge: $\\lim_{x\\to 2^-} f(x) = -\\infty$. The two [[one-sided-limit|one-sided limits]] head in opposite directions, the signature of a [[vertical-asymptote|vertical asymptote]].",
        "widget": {
          "type": "far-out",
          "mode": "asymptote",
          "f": "asym",
          "at": 2,
          "prompt": "Close in on x = 2 from both sides: one side shoots up, the other plunges."
        }
      }
    ],
    "summary": "At $x = 2$ the top is 3 and the bottom is 0, so the outputs blow up: **$+\\infty$ from the right and $-\\infty$ from the left**. The line $x = 2$ is a vertical asymptote.",
    "claims": [
      {
        "sympy": "limit((x + 1)/(x - 2), x, 2, '+')",
        "equals": "oo"
      },
      {
        "sympy": "limit((x + 1)/(x - 2), x, 2, '-')",
        "equals": "-oo"
      },
      {
        "sympy": "((x + 1)/(x - 2)).subs(x, Rational(2001, 1000))",
        "equals": "3001"
      },
      {
        "sympy": "((x + 1)/(x - 2)).subs(x, Rational(1999, 1000))",
        "equals": "-2999"
      }
    ]
  },
  {
    "id": "learn-continuous",
    "subtopic": "140.2.4.continuity",
    "title": "Gluing two pieces together",
    "problem": "For which $k$ is $f(x) = \\begin{cases} kx + 1 & x < 2 \\\\ x^2 & x \\ge 2 \\end{cases}$ continuous at $x = 2$?",
    "steps": [
      {
        "ask": {
          "prompt": "What does continuity at $x = 2$ require?",
          "format": "choice",
          "options": [
            {
              "label": "$\\lim_{x\\to 2} f(x)$ exists and equals $f(2)$",
              "correct": true
            },
            {
              "label": "The slopes on each side match",
              "misconception": "slopes-must-match",
              "feedback": "Matching slopes is the extra condition for a derivative. Continuity only needs the graph to meet itself with no gap."
            },
            {
              "label": "$f(2)$ is defined",
              "misconception": "defined-is-enough",
              "feedback": "Being defined isn't enough: $f(2)$ must equal the value the graph is heading toward."
            }
          ]
        },
        "narration": "Continuity means no gap: the [[limit]] from each side must equal the value. Here $f(2) = 2^2 = 4$, from the right piece. ([[continuity|More on continuity]].)",
        "builds_on": [
          "140.2.1.one-sided"
        ]
      },
      {
        "ask": {
          "prompt": "What does the right piece approach as $x \\to 2^+$?",
          "format": "number",
          "answer": 4,
          "tolerance": 0.001
        },
        "narration": "$x^2 \\to 4$, which equals $f(2)$. So the left piece must also approach 4."
      },
      {
        "ask": {
          "prompt": "What does the left piece approach as $x \\to 2^-$?",
          "format": "choice",
          "options": [
            {
              "label": "$2k + 1$",
              "correct": true
            },
            {
              "label": "$k + 1$",
              "misconception": "forgot-to-substitute",
              "feedback": "Substitute $x = 2$ into $kx + 1$: $k \\cdot 2 + 1$."
            },
            {
              "label": "$4$",
              "misconception": "assumed-the-goal",
              "feedback": "That's what it needs to approach. First work out what it does approach, in terms of $k$."
            }
          ]
        },
        "narration": "$kx + 1 \\to 2k + 1$ as $x \\to 2$."
      },
      {
        "ask": {
          "prompt": "Solve $2k + 1 = 4$. What is $k$?",
          "format": "number",
          "answer": 1.5,
          "tolerance": 0.001
        },
        "narration": "$k = \\frac{3}{2}$. With that slope, the line arrives exactly where the parabola starts, at $(2, 4)$, so the graph has no gap. The slopes don't match ($\\frac{3}{2}$ on the left, 4 on the right), so there's a corner, but a corner is still continuous."
      }
    ],
    "summary": "Continuity at 2 needs both sides to meet $f(2) = 4$. The left piece approaches $2k + 1$, so $k = $ **3/2**. The result has a corner, not a gap.",
    "claims": [
      {
        "sympy": "solve(2*a + 1 - 4, a)",
        "equals": "[Rational(3, 2)]"
      },
      {
        "sympy": "limit(x**2, x, 2)",
        "equals": "4"
      },
      {
        "sympy": "diff(x**2, x).subs(x, 2)",
        "equals": "4"
      }
    ]
  },
  {
    "id": "learn-ivt",
    "subtopic": "140.2.4.ivt",
    "title": "Is there a root between 0 and 1?",
    "problem": "Does $x^3 + x - 1 = 0$ have a solution between 0 and 1?",
    "steps": [
      {
        "ask": {
          "prompt": "Let $f(x) = x^3 + x - 1$. What is $f(0)$?",
          "format": "number",
          "answer": -1,
          "tolerance": 0.001
        },
        "narration": "$f(0) = -1$, which is below zero.",
        "builds_on": [
          "140.2.4.continuity"
        ]
      },
      {
        "ask": {
          "prompt": "And what is $f(1)$?",
          "format": "number",
          "answer": 1,
          "tolerance": 0.001
        },
        "narration": "$f(1) = 1 + 1 - 1 = 1$, which is above zero."
      },
      {
        "ask": {
          "prompt": "What can you conclude?",
          "format": "choice",
          "options": [
            {
              "label": "There's a root somewhere in $(0, 1)$",
              "correct": true
            },
            {
              "label": "The root is at $x = 0.5$, halfway",
              "misconception": "ivt-gives-location",
              "feedback": "$f(0.5) = -0.375$, not 0. The theorem says a root exists, not where it is."
            },
            {
              "label": "Nothing: the theorem needs $f(0)$ or $f(1)$ to be 0",
              "misconception": "misread-ivt",
              "feedback": "The theorem needs the target value, 0, to lie between $f(0)$ and $f(1)$. It does: $-1 < 0 < 1$."
            }
          ]
        },
        "narration": "$f$ is a polynomial, so it's [[continuity|continuous]]. It goes from $-1$ to $1$ without breaks, so it must cross 0 somewhere in between. That's the [[intermediate-value-theorem|Intermediate Value Theorem]]. (The root is about 0.682.)",
        "widget": {
          "type": "secant",
          "mode": "trace",
          "f": "ivtcubic",
          "x0": 0.5,
          "span": 1,
          "prompt": "Drag from x = 0 to x = 1: the output goes from −1 to 1, so it has to pass through 0."
        }
      },
      {
        "ask": {
          "prompt": "Now take $g(x) = (x - 0.5)^2 - 0.01$. Both $g(0)$ and $g(1)$ equal $0.24$. What does the theorem say about roots of $g$ in $[0, 1]$?",
          "format": "choice",
          "options": [
            {
              "label": "Nothing: it gives no guarantee either way",
              "correct": true
            },
            {
              "label": "$g$ has no roots in $[0, 1]$",
              "misconception": "ivt-converse",
              "feedback": "In fact $g$ has roots at 0.4 and 0.6. Ends with the same sign don't rule roots out."
            },
            {
              "label": "$g$ has exactly one root",
              "misconception": "ivt-counts",
              "feedback": "The theorem never counts roots, and here the end values don't even straddle 0."
            }
          ]
        },
        "narration": "The theorem only works one way. Ends on opposite sides of 0 guarantee a root; ends on the same side guarantee nothing. $g$ hides two roots, at 0.4 and 0.6, between ends of the same sign."
      }
    ],
    "summary": "$f(0) = -1$ and $f(1) = 1$, and polynomials are continuous, so $x^3 + x - 1 = 0$ **has a solution in $(0, 1)$**. The theorem can't tell you where, how many, or anything at all when the ends share a sign.",
    "claims": [
      {
        "sympy": "(x**3 + x - 1).subs(x, 0)",
        "equals": "-1"
      },
      {
        "sympy": "(x**3 + x - 1).subs(x, 1)",
        "equals": "1"
      },
      {
        "sympy": "(x**3 + x - 1).subs(x, Rational(1, 2))",
        "equals": "-3/8"
      },
      {
        "sympy": "nsolve(x**3 + x - 1, x, 0.5)",
        "approx": 0.6823,
        "tol": 0.0001
      },
      {
        "sympy": "((x - Rational(1, 2))**2 - Rational(1, 100)).subs(x, 0)",
        "equals": "6/25"
      },
      {
        "sympy": "solve((x - Rational(1, 2))**2 - Rational(1, 100), x)",
        "equals": "[Rational(2, 5), Rational(3, 5)]"
      }
    ]
  },
  {
    "id": "learn-epsilon-delta",
    "subtopic": "140.2.5.epsilon-delta",
    "title": "How close is close enough?",
    "problem": "Show that $\\lim_{x\\to 1}(2x + 1) = 3$ the precise way: for any tolerance $\\varepsilon > 0$, find how close $x$ must be to 1 to land within $\\varepsilon$ of 3.",
    "steps": [
      {
        "ask": {
          "prompt": "We want $|(2x + 1) - 3| < \\varepsilon$. Simplify $|(2x + 1) - 3|$.",
          "format": "choice",
          "options": [
            {
              "label": "$2|x - 1|$",
              "correct": true
            },
            {
              "label": "$|x - 1|$",
              "misconception": "forgot-slope",
              "feedback": "$(2x + 1) - 3 = 2x - 2 = 2(x - 1)$. The 2 stays."
            },
            {
              "label": "$|2x + 1|$",
              "misconception": "forgot-to-subtract-L",
              "feedback": "The gap is between $f(x)$ and the limit 3: start from $|f(x) - 3|$."
            }
          ]
        },
        "narration": "$|(2x + 1) - 3| = |2x - 2| = 2|x - 1|$. The output's distance from 3 is always twice the input's distance from 1.",
        "builds_on": [
          "140.2.1.table"
        ]
      },
      {
        "ask": {
          "prompt": "So $2|x - 1| < \\varepsilon$ exactly when:",
          "format": "choice",
          "options": [
            {
              "label": "$|x - 1| < \\frac{\\varepsilon}{2}$",
              "correct": true
            },
            {
              "label": "$|x - 1| < 2\\varepsilon$",
              "misconception": "multiplied-instead",
              "feedback": "Divide both sides by 2; don't multiply."
            },
            {
              "label": "$|x - 1| < \\varepsilon$",
              "misconception": "forgot-slope",
              "feedback": "That ignores the factor of 2: an input $\\varepsilon$ away from 1 lands $2\\varepsilon$ away from 3."
            }
          ]
        },
        "narration": "Dividing by 2 gives $|x - 1| < \\frac{\\varepsilon}{2}$. So $\\delta = \\frac{\\varepsilon}{2}$ works, for every $\\varepsilon$ at once."
      },
      {
        "ask": {
          "prompt": "For $\\varepsilon = 0.1$, what is the largest $\\delta$ that works?",
          "format": "number",
          "answer": 0.05,
          "tolerance": 0.0005
        },
        "narration": "$\\delta = 0.05$: every $x$ between 0.95 and 1.05 gives $2x + 1$ between 2.9 and 3.1. Shrink $\\varepsilon$ and $\\delta$ shrinks with it, but there's always a $\\delta$. That promise is exactly what a [[limit]] means ([[epsilon-delta|more on ε and δ]]).",
        "widget": {
          "type": "limit-zoom",
          "g": "line21",
          "at": 1,
          "limit": 3,
          "epsilon": true,
          "prompt": "Shrink ε: the δ-window (dashed lines) shrinks with it, always half as wide."
        }
      }
    ],
    "summary": "$|(2x + 1) - 3| = 2|x - 1|$, so choosing $\\delta = \\frac{\\varepsilon}{2}$ keeps every output within $\\varepsilon$ of 3. For $\\varepsilon = 0.1$, **δ = 0.05**.",
    "claims": [
      {
        "sympy": "expand((2*x + 1) - 3 - 2*(x - 1))",
        "equals": "0"
      },
      {
        "sympy": "2*Rational(95, 100) + 1",
        "equals": "29/10"
      },
      {
        "sympy": "2*Rational(105, 100) + 1",
        "equals": "31/10"
      }
    ]
  },
  {
    "id": "learn-trig-derivs",
    "subtopic": "140.4.1.trig",
    "title": "Why the derivative of sin is cos",
    "problem": "Show that $(\\sin x)' = \\cos x$ from the definition of the derivative, then differentiate $f(x) = \\sin(3x)$.",
    "steps": [
      {
        "ask": {
          "prompt": "$(\\sin x)' = \\lim_{h\\to 0}\\frac{\\sin(x + h) - \\sin x}{h}$. First, expand $\\sin(x + h)$:",
          "format": "choice",
          "options": [
            {
              "label": "$\\sin x\\cos h + \\cos x\\sin h$",
              "correct": true
            },
            {
              "label": "$\\sin x + \\sin h$",
              "misconception": "split-function",
              "feedback": "$\\sin$ doesn't split over sums: $\\sin(\\frac{\\pi}{2} + \\frac{\\pi}{2}) = 0$, but $1 + 1 = 2$."
            },
            {
              "label": "$\\sin x\\cos h - \\cos x\\sin h$",
              "misconception": "sign-slip",
              "feedback": "That's $\\sin(x - h)$. For $x + h$ both terms are added."
            }
          ]
        },
        "narration": "[[angle-addition|Angle addition]] gives $\\sin(x + h) = \\sin x\\cos h + \\cos x\\sin h$. Regrouping the difference quotient: $\\sin x\\cdot\\frac{\\cos h - 1}{h} + \\cos x\\cdot\\frac{\\sin h}{h}$.",
        "builds_on": [
          "foundation:unit-circle"
        ]
      },
      {
        "ask": {
          "prompt": "As $h \\to 0$, $\\frac{\\sin h}{h} \\to 1$ and $\\frac{\\cos h - 1}{h} \\to 0$. So $(\\sin x)'$ is:",
          "format": "choice",
          "options": [
            {
              "label": "$\\cos x$",
              "correct": true
            },
            {
              "label": "$-\\cos x$",
              "misconception": "sign-slip",
              "feedback": "Both limits are non-negative here: $\\sin x \\cdot 0 + \\cos x \\cdot 1$."
            },
            {
              "label": "$\\sin x$",
              "misconception": "unchanged",
              "feedback": "The $\\sin x$ term is multiplied by $\\frac{\\cos h - 1}{h}$, which goes to 0."
            }
          ]
        },
        "narration": "$\\sin x \\cdot 0 + \\cos x \\cdot 1 = \\cos x$. The two key limits are [[sin-h-over-h|sin h / h → 1]] and [[cos-h-minus-1-over-h|(cos h − 1)/h → 0]]. The same method gives $(\\cos x)' = -\\sin x$.",
        "widget": {
          "type": "secant",
          "f": "sin",
          "x0": 1,
          "prompt": "Shrink h at x = 1: the slope settles on cos 1 ≈ 0.540."
        }
      },
      {
        "ask": {
          "prompt": "Now $f(x) = \\sin(3x)$. What is $f'(x)$?",
          "format": "choice",
          "options": [
            {
              "label": "$3\\cos(3x)$",
              "correct": true
            },
            {
              "label": "$\\cos(3x)$",
              "misconception": "dropped-inner",
              "feedback": "The [[chain-rule|chain rule]] multiplies by the derivative of the inside, $3x$, which is 3."
            },
            {
              "label": "$3\\cos x$",
              "misconception": "chain-on-outside",
              "feedback": "The inside stays inside: $\\cos(3x)$, then times 3."
            }
          ]
        },
        "narration": "The [[chain-rule]] multiplies by the inside's derivative, 3: $f'(x) = 3\\cos(3x)$. Squeezing the sine wave 3 times horizontally makes it 3 times as steep.",
        "builds_on": [
          "140.3.2.chain"
        ]
      },
      {
        "ask": {
          "prompt": "What is $f'(0)$?",
          "format": "number",
          "answer": 3,
          "tolerance": 0.001
        },
        "narration": "$f'(0) = 3\\cos 0 = 3$: at the origin, $\\sin(3x)$ rises three times as steeply as $\\sin x$."
      }
    ],
    "summary": "Angle addition and two key limits give $(\\sin x)' = \\cos x$. With the chain rule, $(\\sin 3x)' = 3\\cos 3x$, so the slope at 0 is **3**.",
    "claims": [
      {
        "sympy": "diff(sin(x), x)",
        "equals": "cos(x)"
      },
      {
        "sympy": "diff(sin(3*x), x)",
        "equals": "3*cos(3*x)"
      },
      {
        "sympy": "expand(sin(x + h), trig=True)",
        "equals": "sin(x)*cos(h) + sin(h)*cos(x)"
      },
      {
        "sympy": "limit(sin(h)/h, h, 0)",
        "equals": "1"
      },
      {
        "sympy": "limit((cos(h) - 1)/h, h, 0)",
        "equals": "0"
      },
      {
        "sympy": "cos(1)",
        "approx": 0.5403,
        "tol": 0.0001
      }
    ]
  },
  {
    "id": "learn-exp-log",
    "subtopic": "140.4.1.exp-log",
    "title": "Growth in proportion to size",
    "problem": "A bacteria culture has $P(t) = 100e^{0.5t}$ cells after $t$ hours. How fast is it growing? And why is the derivative of $\\ln x$ equal to $\\frac{1}{x}$?",
    "steps": [
      {
        "ask": {
          "prompt": "What is $P'(t)$?",
          "format": "choice",
          "options": [
            {
              "label": "$50e^{0.5t}$",
              "correct": true
            },
            {
              "label": "$100e^{0.5t}$",
              "misconception": "exp-dropped-inner",
              "feedback": "$e^{0.5t}$ needs the chain rule: its derivative is $0.5e^{0.5t}$."
            },
            {
              "label": "$50t\\,e^{0.5t - 1}$",
              "misconception": "power-rule-on-exp",
              "feedback": "The power rule is for a fixed exponent. Here the exponent changes: $(e^{u})' = e^{u}u'$."
            }
          ]
        },
        "narration": "$(e^{0.5t})' = 0.5e^{0.5t}$, so $P'(t) = 50e^{0.5t} = 0.5\\,P(t)$. The culture grows at a rate proportional to its size, which is what exponential growth means ([[derivative-of-exp|why $e^x$ is its own derivative]]).",
        "builds_on": [
          "140.3.2.chain"
        ]
      },
      {
        "ask": {
          "prompt": "How fast is the culture growing at $t = 0$, in cells per hour?",
          "format": "number",
          "answer": 50,
          "tolerance": 0.01
        },
        "narration": "$P'(0) = 50$ cells per hour, half the population of 100. Two hours later there are $100e \\approx 272$ cells, growing at about 136 per hour."
      },
      {
        "ask": {
          "prompt": "Now $y = \\ln x$, which means $e^y = x$. Differentiate both sides with respect to $x$:",
          "format": "choice",
          "options": [
            {
              "label": "$e^y\\,y' = 1$",
              "correct": true
            },
            {
              "label": "$e^y = 1$",
              "misconception": "forgot-chain-on-y",
              "feedback": "$y$ depends on $x$, so $(e^y)' = e^y\\,y'$ by the chain rule."
            },
            {
              "label": "$y\\,e^{y - 1}\\,y' = 1$",
              "misconception": "power-rule-on-exp",
              "feedback": "$e^y$ isn't a power of $y$; its derivative is $e^y$ (times $y'$)."
            }
          ]
        },
        "narration": "$y$ depends on $x$, so the chain rule gives $e^y\\,y'$ on the left. The right side, $x$, has derivative 1."
      },
      {
        "ask": {
          "prompt": "Solve for $y'$:",
          "format": "choice",
          "options": [
            {
              "label": "$y' = \\frac{1}{x}$",
              "correct": true
            },
            {
              "label": "$y' = e^x$",
              "misconception": "confused-inverse",
              "feedback": "$y' = \\frac{1}{e^y}$, and $e^y$ is $x$, not $e^x$."
            },
            {
              "label": "$y' = \\ln x$",
              "misconception": "derivative-is-itself",
              "feedback": "Only $e^x$ is its own derivative. Solve $e^y\\,y' = 1$ for $y'$."
            }
          ]
        },
        "narration": "$y' = \\frac{1}{e^y} = \\frac{1}{x}$. That's the [[derivative-of-ln|derivative of ln]], and it comes from the [[inverse-function-derivative|inverse-function rule]]: $\\ln$ undoes $e^x$, so its slopes are reciprocals."
      }
    ],
    "summary": "$P'(t) = 50e^{0.5t} = 0.5P$: growth in proportion to size, **50 cells per hour** at the start. Differentiating $e^y = x$ gives $(\\ln x)' = \\frac{1}{x}$.",
    "claims": [
      {
        "sympy": "diff(100*exp(t/2), t)",
        "equals": "50*exp(t/2)"
      },
      {
        "sympy": "diff(100*exp(t/2), t).subs(t, 0)",
        "equals": "50"
      },
      {
        "sympy": "100*exp(1)",
        "approx": 271.83,
        "tol": 0.01
      },
      {
        "sympy": "diff(log(x), x)",
        "equals": "1/x"
      }
    ]
  },
  {
    "id": "learn-inverse",
    "subtopic": "140.4.2.inverse",
    "title": "The slope of an inverse",
    "problem": "$f(x) = x^3 + x$ is always increasing, so it has an inverse. Find $(f^{-1})'(2)$ without finding a formula for $f^{-1}$.",
    "steps": [
      {
        "ask": {
          "prompt": "Which input does $f$ send to 2?",
          "format": "choice",
          "options": [
            {
              "label": "$x = 1$",
              "correct": true
            },
            {
              "label": "$x = 2$",
              "misconception": "used-b",
              "feedback": "2 is the output. You need the input that $f$ sends to 2."
            },
            {
              "label": "$x = \\sqrt[3]{2}$",
              "misconception": "dropped-term",
              "feedback": "$\\sqrt[3]{2}$ solves $x^3 = 2$, but $f$ also has the $+x$: $f(\\sqrt[3]{2}) \\approx 3.26$."
            }
          ]
        },
        "narration": "$f(1) = 1 + 1 = 2$, so $f^{-1}(2) = 1$.",
        "builds_on": [
          "140.1.1"
        ]
      },
      {
        "ask": {
          "prompt": "What is $f'(1)$?",
          "format": "number",
          "answer": 4,
          "tolerance": 0.001
        },
        "narration": "$f'(x) = 3x^2 + 1$, so $f'(1) = 4$. Near $x = 1$, $f$ stretches small distances by a factor of 4."
      },
      {
        "ask": {
          "prompt": "So what is $(f^{-1})'(2)$?",
          "format": "choice",
          "options": [
            {
              "label": "$\\frac{1}{4}$",
              "correct": true
            },
            {
              "label": "$4$",
              "misconception": "forgot-to-flip",
              "feedback": "The inverse undoes the stretch, so its slope is the reciprocal: mirroring across $y = x$ swaps rise and run."
            },
            {
              "label": "$\\frac{1}{13}$",
              "misconception": "wrong-point",
              "feedback": "That's $\\frac{1}{f'(2)}$. Evaluate $f'$ at the input 1, not at the output 2."
            }
          ]
        },
        "narration": "The inverse shrinks distances back by 4: $(f^{-1})'(2) = \\frac{1}{f'(1)} = \\frac{1}{4}$. That's the [[inverse-function-derivative|inverse-function rule]], from differentiating $f(f^{-1}(x)) = x$ with the [[chain-rule]].",
        "widget": {
          "type": "secant",
          "f": "sqrt",
          "x0": 4,
          "prompt": "The same idea for √x, which undoes x²: at x = 4 its slope settles on 1/(2·2) = 1/4."
        },
        "builds_on": [
          "140.3.2.chain"
        ]
      }
    ],
    "summary": "$f(1) = 2$ and $f'(1) = 4$, so $(f^{-1})'(2) = \\frac{1}{f'(1)} = $ **1/4**. Evaluate $f'$ at the input, then flip.",
    "claims": [
      {
        "sympy": "(x**3 + x).subs(x, 1)",
        "equals": "2"
      },
      {
        "sympy": "1/diff(x**3 + x, x).subs(x, 1)",
        "equals": "1/4"
      },
      {
        "sympy": "1/diff(x**3 + x, x).subs(x, 2)",
        "equals": "1/13"
      },
      {
        "sympy": "(x**3 + x).subs(x, 2**Rational(1, 3))",
        "approx": 3.26,
        "tol": 0.01
      }
    ]
  },
  {
    "id": "learn-inverse-trig",
    "subtopic": "140.4.2.inverse-trig",
    "title": "The derivative of arctan",
    "problem": "Find $(\\arctan x)'$, and the slope of $\\arctan$ at $x = 1$.",
    "steps": [
      {
        "ask": {
          "prompt": "$y = \\arctan x$ means $\\tan y = x$. Differentiate both sides with respect to $x$:",
          "format": "choice",
          "options": [
            {
              "label": "$\\sec^2 y \\cdot y' = 1$",
              "correct": true
            },
            {
              "label": "$\\sec^2 y = 1$",
              "misconception": "forgot-chain-on-y",
              "feedback": "$y$ depends on $x$, so the chain rule adds a factor $y'$."
            },
            {
              "label": "$\\sec y \\cdot y' = 1$",
              "misconception": "sec-not-squared",
              "feedback": "$(\\tan y)' = \\sec^2 y$, from the quotient rule on $\\frac{\\sin y}{\\cos y}$."
            }
          ]
        },
        "narration": "[[implicit-differentiation|Differentiating implicitly]] gives $\\sec^2 y\\cdot y' = 1$, so $y' = \\frac{1}{\\sec^2 y}$.",
        "builds_on": [
          "140.4.2.inverse"
        ]
      },
      {
        "ask": {
          "prompt": "Use $1 + \\tan^2 y = \\sec^2 y$. In terms of $x$, $y'$ is:",
          "format": "choice",
          "options": [
            {
              "label": "$\\frac{1}{1 + x^2}$",
              "correct": true
            },
            {
              "label": "$\\frac{1}{1 - x^2}$",
              "misconception": "sign-slip",
              "feedback": "$\\sec^2 y = 1 + \\tan^2 y = 1 + x^2$: a plus sign."
            },
            {
              "label": "$\\frac{1}{\\sqrt{1 - x^2}}$",
              "misconception": "arcsin-confused",
              "feedback": "That's the derivative of arcsin. Here $\\sec^2 y = 1 + x^2$."
            }
          ]
        },
        "narration": "$\\sec^2 y = 1 + \\tan^2 y = 1 + x^2$, so $(\\arctan x)' = \\frac{1}{1 + x^2}$ ([[derivative-of-arctan|more on arctan]]).",
        "builds_on": [
          "foundation:unit-circle"
        ]
      },
      {
        "ask": {
          "prompt": "What is the slope of $\\arctan$ at $x = 1$?",
          "format": "number",
          "answer": 0.5,
          "tolerance": 0.002
        },
        "narration": "$\\frac{1}{1 + 1} = \\frac{1}{2}$. At the origin the slope is 1, and far out it flattens toward 0, as the graph levels off at $\\pm\\frac{\\pi}{2}$.",
        "widget": {
          "type": "secant",
          "f": "atan",
          "x0": 1,
          "prompt": "Shrink h at x = 1: the slope settles on 1/2."
        }
      }
    ],
    "summary": "From $\\tan y = x$: $\\sec^2 y \\cdot y' = 1$, and $\\sec^2 y = 1 + x^2$, so $(\\arctan x)' = \\frac{1}{1 + x^2}$, which is **1/2** at $x = 1$.",
    "claims": [
      {
        "sympy": "diff(atan(x), x)",
        "equals": "1/(x**2 + 1)"
      },
      {
        "sympy": "diff(atan(x), x).subs(x, 1)",
        "equals": "1/2"
      },
      {
        "sympy": "simplify(1 + tan(x)**2 - sec(x)**2)",
        "equals": "0"
      }
    ]
  },
  {
    "id": "learn-implicit",
    "subtopic": "140.4.3.implicit",
    "title": "The slope of a circle",
    "problem": "The circle $x^2 + y^2 = 25$ passes through $(3, 4)$. What is the slope of its tangent there?",
    "steps": [
      {
        "ask": {
          "prompt": "Differentiate both sides with respect to $x$. The left side becomes:",
          "format": "choice",
          "options": [
            {
              "label": "$2x + 2y\\,y'$",
              "correct": true
            },
            {
              "label": "$2x + 2y$",
              "misconception": "forgot-chain-on-y",
              "feedback": "$y$ depends on $x$, so $(y^2)' = 2y\\,y'$ by the chain rule."
            },
            {
              "label": "$2x + 2y'$",
              "misconception": "chain-dropped-outer",
              "feedback": "The chain rule keeps the outer derivative: $(y^2)' = 2y\\cdot y'$."
            }
          ]
        },
        "narration": "$y$ is a function of $x$, so $y^2$ needs the [[chain-rule]]: $2y\\,y'$. The right side, 25, is a constant, so its derivative is 0.",
        "builds_on": [
          "140.3.2.chain"
        ]
      },
      {
        "ask": {
          "prompt": "Solve $2x + 2y\\,y' = 0$ for $y'$:",
          "format": "choice",
          "options": [
            {
              "label": "$y' = -\\frac{x}{y}$",
              "correct": true
            },
            {
              "label": "$y' = \\frac{x}{y}$",
              "misconception": "implicit-sign-slip",
              "feedback": "Moving $2x$ to the other side makes it $-2x$."
            },
            {
              "label": "$y' = -\\frac{y}{x}$",
              "misconception": "implicit-swapped",
              "feedback": "Divide by $2y$, the coefficient of $y'$: $y' = \\frac{-2x}{2y}$."
            }
          ]
        },
        "narration": "$y' = -\\frac{x}{y}$. That's [[implicit-differentiation|implicit differentiation]]: no need to solve for $y$ first."
      },
      {
        "ask": {
          "prompt": "What is the slope at $(3, 4)$?",
          "format": "number",
          "answer": -0.75,
          "tolerance": 0.002
        },
        "narration": "$-\\frac{3}{4}$. The radius to $(3, 4)$ has slope $\\frac{4}{3}$, and $-\\frac{3}{4}\\cdot\\frac{4}{3} = -1$: the tangent is perpendicular to the radius, just as geometry says.",
        "widget": {
          "type": "circle-tangent",
          "r": 5,
          "deg": 53.13,
          "prompt": "Move the point around the circle: the tangent's slope is always −x/y."
        }
      }
    ],
    "summary": "Differentiating $x^2 + y^2 = 25$ gives $2x + 2y\\,y' = 0$, so $y' = -\\frac{x}{y}$, which is **−3/4** at $(3, 4)$.",
    "claims": [
      {
        "sympy": "idiff(x**2 + y**2 - 25, y, x)",
        "equals": "-x/y"
      },
      {
        "sympy": "(-x/y).subs({x: 3, y: 4})",
        "equals": "-3/4"
      },
      {
        "sympy": "Rational(-3, 4)*Rational(4, 3)",
        "equals": "-1"
      }
    ]
  },
  {
    "id": "learn-log-diff",
    "subtopic": "140.4.3.log-diff",
    "title": "Differentiating x to the x",
    "problem": "Find the derivative of $y = x^x$, and its value at $x = 1$.",
    "steps": [
      {
        "ask": {
          "prompt": "Which rule differentiates $x^x$ directly?",
          "format": "choice",
          "options": [
            {
              "label": "Neither: both the base and the exponent change",
              "correct": true
            },
            {
              "label": "The power rule: $x\\cdot x^{x - 1}$",
              "misconception": "power-rule-on-variable-exponent",
              "feedback": "The power rule needs a fixed exponent. Here the exponent is $x$ too."
            },
            {
              "label": "The exponential rule: $x^x \\ln x$",
              "misconception": "exp-rule-fixed-base",
              "feedback": "That rule needs a fixed base, like $2^x$. Here the base changes too."
            }
          ]
        },
        "narration": "The power rule needs a fixed exponent and the exponential rule needs a fixed base. $x^x$ has neither, so take logs.",
        "builds_on": [
          "140.4.1.exp-log"
        ]
      },
      {
        "ask": {
          "prompt": "Take the natural log of both sides. $\\ln y = $",
          "format": "choice",
          "options": [
            {
              "label": "$x\\ln x$",
              "correct": true
            },
            {
              "label": "$(\\ln x)^x$",
              "misconception": "exponent-not-down",
              "feedback": "The point of the log is that it brings the exponent down: $\\ln(x^x) = x\\ln x$."
            },
            {
              "label": "$2\\ln x$",
              "misconception": "logs-of-power-add",
              "feedback": "$x^x$ is $x$ multiplied by itself $x$ times, so $\\ln(x^x) = x\\ln x$, not $\\ln x + \\ln x$."
            }
          ]
        },
        "narration": "Logs bring exponents down: $\\ln y = x\\ln x$."
      },
      {
        "ask": {
          "prompt": "Differentiate both sides. The left side becomes $\\frac{y'}{y}$. The right side is:",
          "format": "choice",
          "options": [
            {
              "label": "$\\ln x + 1$",
              "correct": true
            },
            {
              "label": "$\\frac{1}{x}$",
              "misconception": "forgot-product-rule",
              "feedback": "$x\\ln x$ is a product: $1\\cdot\\ln x + x\\cdot\\frac{1}{x}$."
            },
            {
              "label": "$\\ln x$",
              "misconception": "dropped-term",
              "feedback": "The product rule has two terms; the second is $x\\cdot\\frac{1}{x} = 1$."
            }
          ]
        },
        "narration": "The product rule and the [[derivative-of-ln|derivative of ln]] give $(x\\ln x)' = \\ln x + 1$. On the left, $(\\ln y)' = \\frac{y'}{y}$ by [[implicit-differentiation|implicit differentiation]].",
        "builds_on": [
          "140.4.3.implicit"
        ]
      },
      {
        "ask": {
          "prompt": "Multiply back by $y = x^x$. What is $y'$ at $x = 1$?",
          "format": "number",
          "answer": 1,
          "tolerance": 0.001
        },
        "narration": "$y' = x^x(\\ln x + 1)$, and at $x = 1$ that's $1\\cdot(0 + 1) = 1$. The step people forget is multiplying back by $y$ ([[logarithmic-differentiation|more on logarithmic differentiation]]).",
        "widget": {
          "type": "secant",
          "f": "xpowx",
          "x0": 1,
          "span": 0.8,
          "prompt": "Shrink h at x = 1: the slope of xˣ settles on 1."
        }
      }
    ],
    "summary": "$\\ln y = x\\ln x$, so $\\frac{y'}{y} = \\ln x + 1$ and $y' = x^x(\\ln x + 1)$, which is **1** at $x = 1$.",
    "claims": [
      {
        "sympy": "diff(x**x, x).subs(x, 1)",
        "equals": "1"
      },
      {
        "sympy": "simplify(diff(x*log(x), x) - (log(x) + 1))",
        "equals": "0"
      },
      {
        "sympy": "simplify(diff(x**x, x) - x**x*(log(x) + 1))",
        "equals": "0"
      }
    ]
  },
  {
    "id": "learn-higher",
    "subtopic": "140.4.4.higher",
    "title": "A ball thrown upward",
    "problem": "A ball is thrown straight up at 20 m/s. Its height after $t$ seconds is $h(t) = 20t - 4.9t^2$ metres. Find its velocity, its acceleration, and the shape of its graph.",
    "steps": [
      {
        "ask": {
          "prompt": "What is the velocity $v(t) = h'(t)$?",
          "format": "choice",
          "options": [
            {
              "label": "$20 - 9.8t$",
              "correct": true
            },
            {
              "label": "$20 - 4.9t$",
              "misconception": "dropped-coefficient",
              "feedback": "The power rule brings the exponent down: $(4.9t^2)' = 9.8t$."
            },
            {
              "label": "$20t - 9.8t^2$",
              "misconception": "exponent-unchanged",
              "feedback": "The power rule also lowers each exponent by one."
            }
          ]
        },
        "narration": "$v(t) = 20 - 9.8t$: it starts at 20 m/s and drops by 9.8 m/s every second.",
        "builds_on": [
          "140.3.2.power"
        ]
      },
      {
        "ask": {
          "prompt": "What is the velocity at $t = 1$, in m/s?",
          "format": "number",
          "answer": 10.2,
          "tolerance": 0.01
        },
        "narration": "$v(1) = 20 - 9.8 = 10.2$ m/s: still rising, but more slowly than at the start."
      },
      {
        "ask": {
          "prompt": "What is the acceleration $a(t) = h''(t)$?",
          "format": "choice",
          "options": [
            {
              "label": "$-9.8$",
              "correct": true
            },
            {
              "label": "$20 - 9.8t$",
              "misconception": "acceleration-is-velocity",
              "feedback": "That's the velocity. Acceleration is the derivative of velocity: differentiate once more."
            },
            {
              "label": "$0$",
              "misconception": "constant-velocity",
              "feedback": "Differentiating $20 - 9.8t$: the 20 disappears, but $-9.8t$ leaves $-9.8$."
            }
          ]
        },
        "narration": "$a(t) = -9.8$ m/s² at every moment. That's gravity ([[second-derivative|the second derivative]])."
      },
      {
        "ask": {
          "prompt": "Is the graph of $h$ concave up or concave down?",
          "format": "choice",
          "options": [
            {
              "label": "Concave down",
              "correct": true
            },
            {
              "label": "Concave up",
              "misconception": "concavity-from-f-prime",
              "feedback": "$h'(1) = 10.2$ is positive, but concavity comes from $h''$, which is $-9.8$: negative."
            }
          ]
        },
        "narration": "$h'' < 0$ everywhere, so the graph bends downward everywhere: an upside-down parabola, with its peak where $v = 0$ at $t \\approx 2.04$ s."
      }
    ],
    "summary": "$v(t) = 20 - 9.8t$, so **v(1) = 10.2 m/s**. $a(t) = -9.8$ m/s² everywhere, so the graph is concave down.",
    "claims": [
      {
        "sympy": "diff(20*t - Rational(49, 10)*t**2, t)",
        "equals": "20 - 49*t/5"
      },
      {
        "sympy": "diff(20*t - Rational(49, 10)*t**2, t).subs(t, 1)",
        "equals": "51/5"
      },
      {
        "sympy": "diff(20*t - Rational(49, 10)*t**2, t, 2)",
        "equals": "-49/5"
      },
      {
        "sympy": "Rational(20, 1)/Rational(98, 10)",
        "approx": 2.041,
        "tol": 0.001
      }
    ]
  }
];
