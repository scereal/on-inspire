// MATH 140 curriculum: units, outcomes and subtopics. Valid JSON after the "=" (tests/check_curriculum.py reads it).
// Spec: design/specs/2026-10-05-math-140-explorer-design.md. The outcome breakdown is ours; "official" quotes McGill.
window.CURRICULUM = {
  "course": "math-140",
  "code": "MATH 140",
  "title": "Calculus 1",
  "credits": 3,
  "official": "Review of functions and graphs. Limits, continuity, derivative. Differentiation of elementary functions. Antidifferentiation. Applications.",
  "source": "https://coursecatalogue.mcgill.ca/courses/math-140/",
  "units": [
    {
      "id": "140.1",
      "title": "Functions and graphs",
      "outcomes": [
        {
          "id": "140.1.1",
          "title": "Work with domain, range, composition and inverse functions",
          "summary": "Read what a function accepts and returns, chain functions together, and undo them.",
          "subtopics": []
        },
        {
          "id": "140.1.2",
          "title": "Transform graphs by shifting, stretching and reflecting",
          "summary": "Predict how a graph moves when you change its formula.",
          "subtopics": []
        },
        {
          "id": "140.1.3",
          "title": "Recognize and use the elementary functions",
          "summary": "Polynomials, rational functions, powers and roots, exponentials, logarithms, trig and inverse trig.",
          "subtopics": []
        }
      ]
    },
    {
      "id": "140.2",
      "title": "Limits and continuity",
      "outcomes": [
        {
          "id": "140.2.1",
          "title": "Find limits from graphs and tables, including one-sided limits",
          "summary": "See what value a function settles toward, from each side.",
          "subtopics": [
            {
              "id": "140.2.1.table",
              "title": "Limits from a table of values",
              "learn": "learn-table",
              "practice": {
                "framework": "limits",
                "level": 1
              },
              "builds_on": [
                "foundation:limit",
                "foundation:function"
              ]
            },
            {
              "id": "140.2.1.one-sided",
              "title": "One-sided limits",
              "learn": "learn-one-sided",
              "practice": {
                "framework": "limits",
                "level": 2
              },
              "builds_on": [
                "140.2.1.table"
              ]
            }
          ]
        },
        {
          "id": "140.2.2",
          "title": "Compute limits with limit laws, algebra and the squeeze theorem",
          "summary": "Turn 0/0 into an answer by factoring, rationalizing or squeezing.",
          "subtopics": [
            {
              "id": "140.2.2.factor",
              "title": "Factor and cancel",
              "learn": "learn-factor",
              "practice": {
                "framework": "limits",
                "level": 3
              },
              "builds_on": [
                "140.2.1.table"
              ]
            },
            {
              "id": "140.2.2.rationalize",
              "title": "Rationalize with the conjugate",
              "learn": "learn-rationalize",
              "practice": {
                "framework": "limits",
                "level": 4
              },
              "builds_on": [
                "140.2.2.factor",
                "foundation:conjugate-trick"
              ]
            },
            {
              "id": "140.2.2.squeeze",
              "title": "The squeeze theorem",
              "learn": "learn-squeeze",
              "practice": {
                "framework": "limits",
                "level": 5
              },
              "builds_on": [
                "140.2.2.factor",
                "foundation:unit-circle"
              ]
            }
          ]
        },
        {
          "id": "140.2.3",
          "title": "Find limits at infinity and asymptotes",
          "summary": "Describe what a function does far out and near its blow-ups.",
          "subtopics": [
            {
              "id": "140.2.3.infinity",
              "title": "Limits at infinity and horizontal asymptotes",
              "learn": "learn-infinity",
              "practice": {
                "framework": "limits",
                "level": 6
              },
              "builds_on": [
                "140.2.2.factor"
              ]
            },
            {
              "id": "140.2.3.asymptotes",
              "title": "Vertical asymptotes",
              "learn": "learn-asymptote",
              "practice": {
                "framework": "limits",
                "level": 7
              },
              "builds_on": [
                "140.2.1.one-sided",
                "140.2.3.infinity"
              ]
            }
          ]
        },
        {
          "id": "140.2.4",
          "title": "Decide continuity and use the Intermediate Value Theorem",
          "summary": "Know when a graph has no breaks, and what that guarantees.",
          "subtopics": [
            {
              "id": "140.2.4.continuity",
              "title": "What continuity means",
              "learn": "learn-continuous",
              "practice": {
                "framework": "continuity",
                "level": 1
              },
              "builds_on": [
                "140.2.1.one-sided"
              ]
            },
            {
              "id": "140.2.4.ivt",
              "title": "The Intermediate Value Theorem",
              "learn": "learn-ivt",
              "practice": {
                "framework": "continuity",
                "level": 2
              },
              "builds_on": [
                "140.2.4.continuity"
              ]
            }
          ]
        },
        {
          "id": "140.2.5",
          "title": "Use the epsilon–delta definition of a limit",
          "summary": "Say exactly what \"approaches\" means, and prove simple limits.",
          "subtopics": [
            {
              "id": "140.2.5.epsilon-delta",
              "title": "Finding δ for a given ε",
              "learn": "learn-epsilon-delta",
              "practice": {
                "framework": "continuity",
                "level": 3
              },
              "builds_on": [
                "140.2.1.table",
                "foundation:limit"
              ]
            }
          ]
        }
      ]
    },
    {
      "id": "140.3",
      "title": "The derivative",
      "outcomes": [
        {
          "id": "140.3.1",
          "title": "Understand the derivative as an instantaneous rate and compute it from the definition",
          "summary": "From average speed to speed at an instant, and from secant lines to the tangent.",
          "subtopics": [
            {
              "id": "140.3.1.rate",
              "title": "Slope as a rate of change",
              "learn": "learn-rate",
              "practice": {
                "framework": "derivative-definition",
                "level": 1
              },
              "builds_on": [
                "foundation:function",
                "140.2.1"
              ]
            },
            {
              "id": "140.3.1.definition",
              "title": "The limit definition of the derivative",
              "learn": "learn-definition",
              "practice": {
                "framework": "derivative-definition",
                "level": 2
              },
              "builds_on": [
                "140.3.1.rate",
                "foundation:limit",
                "140.2.2"
              ]
            },
            {
              "id": "140.3.1.continuity",
              "title": "Differentiable versus continuous",
              "learn": "learn-continuity",
              "practice": {
                "framework": "derivative-definition",
                "level": 3
              },
              "builds_on": [
                "140.3.1.definition",
                "140.2.4"
              ]
            }
          ]
        },
        {
          "id": "140.3.2",
          "title": "Differentiate using the sum, constant-multiple, power, product, quotient and chain rules",
          "summary": "Take derivatives without going back to the limit every time, and know which rule comes first.",
          "subtopics": [
            {
              "id": "140.3.2.sum",
              "title": "Sum and constant-multiple rules",
              "learn": "learn-sum",
              "practice": {
                "framework": "derivative-rules",
                "level": 1
              },
              "builds_on": [
                "140.3.1.definition"
              ]
            },
            {
              "id": "140.3.2.power",
              "title": "The power rule, including roots and reciprocals",
              "learn": "learn-power",
              "practice": {
                "framework": "derivative-rules",
                "level": 2
              },
              "builds_on": [
                "140.3.1.definition",
                "140.1.3"
              ]
            },
            {
              "id": "140.3.2.product",
              "title": "The product rule",
              "learn": "learn-product",
              "practice": {
                "framework": "derivative-rules",
                "level": 3
              },
              "builds_on": [
                "140.3.1.definition",
                "foundation:area-shapes"
              ]
            },
            {
              "id": "140.3.2.quotient",
              "title": "The quotient rule",
              "learn": "learn-quotient",
              "practice": {
                "framework": "derivative-rules",
                "level": 4
              },
              "builds_on": [
                "140.3.2.product",
                "140.3.2.chain",
                "140.3.2.power"
              ]
            },
            {
              "id": "140.3.2.chain",
              "title": "The chain rule",
              "learn": "learn-chain",
              "practice": {
                "framework": "derivative-rules",
                "level": 5
              },
              "builds_on": [
                "140.3.2.power",
                "140.1.1"
              ]
            }
          ],
          "practice": {
            "framework": "derivative-rules",
            "level": 6
          }
        }
      ]
    },
    {
      "id": "140.4",
      "title": "Differentiating elementary functions",
      "outcomes": [
        {
          "id": "140.4.1",
          "title": "Differentiate trig, exponential and logarithmic functions",
          "summary": "Why sin′ = cos, (eˣ)′ = eˣ and (ln x)′ = 1/x.",
          "subtopics": []
        },
        {
          "id": "140.4.2",
          "title": "Differentiate inverse functions and inverse trig",
          "summary": "Flip the graph, flip the slope.",
          "subtopics": []
        },
        {
          "id": "140.4.3",
          "title": "Use implicit and logarithmic differentiation",
          "summary": "Differentiate curves that aren't written as y = f(x), and tame products of powers.",
          "subtopics": []
        },
        {
          "id": "140.4.4",
          "title": "Find and interpret higher derivatives",
          "summary": "Acceleration, concavity and beyond.",
          "subtopics": []
        }
      ]
    },
    {
      "id": "140.5",
      "title": "Applications",
      "outcomes": [
        {
          "id": "140.5.1",
          "title": "Solve related-rates problems",
          "summary": "Connect how fast linked quantities change.",
          "subtopics": []
        },
        {
          "id": "140.5.2",
          "title": "Use linear approximation and differentials",
          "summary": "Estimate values with the tangent line, and judge the error.",
          "subtopics": []
        },
        {
          "id": "140.5.3",
          "title": "Apply the Mean Value Theorem",
          "summary": "Somewhere, the instantaneous rate equals the average rate.",
          "subtopics": []
        },
        {
          "id": "140.5.4",
          "title": "Find extrema and sketch curves",
          "summary": "Use the first and second derivatives to read a graph's shape.",
          "subtopics": []
        },
        {
          "id": "140.5.5",
          "title": "Solve optimization problems",
          "summary": "Build the function, then find its best value.",
          "subtopics": []
        },
        {
          "id": "140.5.6",
          "title": "Evaluate indeterminate limits with L'Hôpital's rule",
          "summary": "When 0/0 or ∞/∞ appears, compare rates instead.",
          "subtopics": []
        }
      ]
    },
    {
      "id": "140.6",
      "title": "Antidifferentiation",
      "outcomes": [
        {
          "id": "140.6.1",
          "title": "Find antiderivatives, with the + C",
          "summary": "Run differentiation backwards, and see why the constant is always there.",
          "subtopics": []
        },
        {
          "id": "140.6.2",
          "title": "Solve initial-value problems",
          "summary": "Pin down the constant from one known value, e.g. position from velocity.",
          "subtopics": []
        }
      ]
    }
  ]
};
