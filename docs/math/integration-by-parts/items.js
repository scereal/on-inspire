// Problem data. Keep this file valid JSON after the "=" so tests/check_math.py can parse it.
// "verify" holds SymPy expressions: the integrand, the correct antiderivative, and any wrong answers shown.
window.IBP_ITEMS = [
  {
    "why": "ibp-pick-u",
    "type": "choose",
    "title": "Pick u",
    "integral": "∫ x e<sup>2x</sup> dx",
    "prompt": "Which split makes this integral easier?",
    "options": [
      { "label": "u = x, &nbsp; dv = e<sup>2x</sup> dx", "right": true, "feedback": "<strong>Yes.</strong> Differentiating x turns it into 1, and e<sup>2x</sup> is easy to integrate. What's left is just ∫ ½e<sup>2x</sup> dx." },
      { "label": "u = e<sup>2x</sup>, &nbsp; dv = x dx", "feedback": "Then v = x²/2, and the new integral ∫ x² e<sup>2x</sup> dx is harder than the one you started with. Choose the u that gets simpler when you differentiate it." },
      { "label": "u = x e<sup>2x</sup>, &nbsp; dv = dx", "feedback": "Then du needs the product rule, and the new integral ∫ x(1 + 2x)e<sup>2x</sup> dx is messier. Split the two factors instead." }
    ],
    "verify": { "integrand": "x*exp(2*x)", "answer": "x*exp(2*x)/2 - exp(2*x)/4" }
  },
  {
    "why": "ibp-sign",
    "type": "error",
    "title": "Find the error",
    "integral": "∫ x cos x dx",
    "lines": [
      "u = x, &nbsp; dv = cos x dx",
      "du = dx, &nbsp; v = sin x",
      "= x sin x − ∫ sin x dx",
      "= x sin x − cos x + C"
    ],
    "wrong": 3,
    "feedback": "<strong>Found it.</strong> The integral of sin x is −cos x, so subtracting it gives x sin x <em>+</em> cos x + C. Check by differentiating: you get x cos x back.",
    "verify": { "integrand": "x*cos(x)", "answer": "x*sin(x) + cos(x)", "shown": "x*sin(x) - cos(x)" }
  },
  {
    "why": "ibp-v",
    "type": "error",
    "title": "Find the error",
    "integral": "∫ x e<sup>3x</sup> dx",
    "lines": [
      "u = x, &nbsp; dv = e<sup>3x</sup> dx",
      "du = dx, &nbsp; v = 3e<sup>3x</sup>",
      "= 3x e<sup>3x</sup> − ∫ 3e<sup>3x</sup> dx",
      "= 3x e<sup>3x</sup> − e<sup>3x</sup> + C"
    ],
    "wrong": 1,
    "feedback": "<strong>Found it.</strong> v has to be an antiderivative of e<sup>3x</sup>, so v = ⅓e<sup>3x</sup>. Multiplying by 3 is what <em>differentiating</em> does. Every line after this inherits the mistake.",
    "verify": { "integrand": "x*exp(3*x)", "answer": "x*exp(3*x)/3 - exp(3*x)/9", "shown": "3*x*exp(3*x) - exp(3*x)" }
  },
  {
    "why": "ibp-blank",
    "type": "choose",
    "title": "Fill the blank",
    "integral": "∫ x² e<sup>x</sup> dx = x² e<sup>x</sup> − ∫ ▢ dx",
    "prompt": "With u = x² and dv = e<sup>x</sup> dx, what goes in the box?",
    "options": [
      { "label": "x² e<sup>x</sup>", "feedback": "That's uv again. The new integral is ∫ v du: v = e<sup>x</sup> times du = 2x dx." },
      { "label": "2x", "feedback": "That's du, but v is missing. The new integral is ∫ v du = ∫ e<sup>x</sup> · 2x dx." },
      { "label": "2x e<sup>x</sup>", "right": true, "feedback": "<strong>Right.</strong> v du = e<sup>x</sup> · 2x dx. Notice the power of x went down by one. One more round of parts finishes it." },
      { "label": "e<sup>x</sup>", "feedback": "du isn't dx here. Differentiate u = x² to get du = 2x dx." }
    ],
    "verify": { "integrand": "x**2*exp(x)", "answer": "x**2*exp(x) - 2*x*exp(x) + 2*exp(x)", "blank": "2*x*exp(x)", "uv": "x**2*exp(x)" }
  },
  {
    "why": "ibp-chain",
    "type": "error",
    "title": "Find the error",
    "integral": "∫ x sin 2x dx",
    "lines": [
      "u = x, &nbsp; dv = sin 2x dx",
      "du = dx, &nbsp; v = −½ cos 2x",
      "= −½ x cos 2x + ½ ∫ cos 2x dx",
      "= −½ x cos 2x + ½ sin 2x + C"
    ],
    "wrong": 3,
    "feedback": "<strong>Found it.</strong> ∫ cos 2x dx is ½ sin 2x, not sin 2x. Integrating has to undo the chain rule's factor of 2. The last term should be ¼ sin 2x.",
    "verify": { "integrand": "x*sin(2*x)", "answer": "-x*cos(2*x)/2 + sin(2*x)/4", "shown": "-x*cos(2*x)/2 + sin(2*x)/2" }
  },
  {
    "why": "ibp-minus",
    "type": "error",
    "title": "Find the error",
    "integral": "∫ ln x dx",
    "lines": [
      "u = ln x, &nbsp; dv = dx",
      "du = (1/x) dx, &nbsp; v = x",
      "= x ln x + ∫ x · (1/x) dx",
      "= x ln x + x + C"
    ],
    "wrong": 2,
    "feedback": "<strong>Found it.</strong> The formula is uv <em>minus</em> ∫ v du. With the minus sign, the answer is x ln x − x + C.",
    "verify": { "integrand": "log(x)", "answer": "x*log(x) - x", "shown": "x*log(x) + x" }
  },
  {
    "why": "ibp-check",
    "type": "choose",
    "title": "Check by differentiating",
    "integral": "∫ x ln x dx",
    "prompt": "Three students got three answers. Differentiate each one: which is right?",
    "options": [
      { "label": "½x² ln x − ½x² + C", "feedback": "Differentiate: x ln x + ½x − x = x ln x − ½x. Too much was subtracted, because ∫ ½x dx is ¼x², not ½x²." },
      { "label": "x ln x − x + C", "feedback": "That's ∫ ln x dx. Differentiating it gives ln x, not x ln x." },
      { "label": "½x² ln x − ¼x² + C", "right": true, "feedback": "<strong>Right.</strong> Differentiate: x ln x + ½x − ½x = x ln x. Differentiating is the quickest way to check any integral." }
    ],
    "verify": { "integrand": "x*log(x)", "answer": "x**2*log(x)/2 - x**2/4", "wrongs": ["x**2*log(x)/2 - x**2/2", "x*log(x) - x"] }
  }
];
