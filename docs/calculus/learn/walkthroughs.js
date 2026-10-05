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
          "f": "square",
          "x0": 2,
          "prompt": "Shrink h: the secant's slope settles on the tangent's slope."
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
  }
];
