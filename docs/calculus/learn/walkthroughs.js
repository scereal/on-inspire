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
  }
];
