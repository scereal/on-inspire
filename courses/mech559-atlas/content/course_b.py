"""Layer 1, Lecture 4: data-based (surrogate) models."""
import math
import sympy as sp
from lib import *

L4 = "Lecture 4 · Data-based models"

# Least-squares example: points (0,1), (1,2), (2,2).
_Z = sp.Matrix([[1, 0], [1, 1], [1, 2]])
_y = sp.Matrix([1, 2, 2])
_w = (_Z.T * _Z).inv() * _Z.T * _y
assert _w == sp.Matrix([sp.Rational(7, 6), sp.Rational(1, 2)])
# RMSE / R^2 example.
_yt, _yh = [1, 2, 3], [1, 2, 4]
_rmse = math.sqrt(sum((a - b)**2 for a, b in zip(_yt, _yh)) / 3)
_r2 = 1 - sum((a - b)**2 for a, b in zip(_yt, _yh)) / sum((a - 2)**2 for a in _yt)
# RBF example: two centres 1 apart, Gaussian lambda = 1, data y = [1, 0].
_e = math.exp(-1)
_w1, _w2 = 1 / (1 - _e**2), -_e / (1 - _e**2)

CONCEPTS = [
    concept(
        "c-surrogates-why", "When the true function is expensive, black-box or noisy, fit a cheap model to a few samples", 1, L4,
        r"""
So far we've assumed $f(\mathbf{x})$ and the constraints are cheap and have derivatives. Often they don't:

- an evaluation is an **expensive simulation** (CFD, FEA) taking minutes to days;
- the model is a **black box** (legacy code, an experiment, a proprietary tool) with no derivatives;
- evaluations are **noisy** (measurements, stochastic simulations);
- and optimizers need **many** evaluations.

So we fit a cheap **data-based model** $\hat f(\mathbf{x})$ to a limited set of observations $\{(\mathbf{x}_i, y_i)\}_{i=1}^p$. It goes by many names: *metamodel*, *surrogate*, *emulator*, *response surface*. A physics-based model derives $f$ from governing equations; a data-based one assumes only a mathematical form (smoothness, polynomial degree, kernel). So it should **not be trusted outside the region where the data was sampled**: extrapolation is risky.
""",
        deeper=["c-models-and-classes"],
        math=[r"\hat f(\mathbf{x})\approx f(\mathbf{x})\ \text{ from }\ \{(\mathbf{x}_i, y_i)\}_{i=1}^p"],
        analogy=analogy("A weather forecaster can't run the atmosphere twice, so they learn patterns from past observations and predict from those.",
                        "forecasts degrade for unprecedented conditions, just as a surrogate degrades outside its sampled region. It has no physics to fall back on."),
        exam="Whenever a surrogate is used, state its training region and avoid quoting predictions outside it.",
        source="Lecture 4, slides 3–12",
        problems=[
            problem("c-sw-1", "Why a surrogate?",
                    r"Each evaluation of your objective runs a 6-hour CFD simulation.",
                    [choice("What's the main reason to build a surrogate?", [opt("An optimizer needs many evaluations, which would take far too long on the real model", True),
                                                                             opt("Surrogates are more accurate than the simulation", why="They approximate it; they can't beat the data they're trained on."),
                                                                             opt("Surrogates never need validation", why="They must be validated, ideally on held-out data."),
                                                                             opt("CFD can't be optimized at all", why="It can, just expensively.")]),
                     choice("Where should you trust its predictions least?", [opt("Outside the region where training samples were taken", True), opt("At the training points", why="Interpolating models reproduce the data exactly there."),
                                                                              opt("Near the centre of the sampled region", why="That's usually where it's most reliable."), opt("Everywhere equally", why="Reliability depends on distance from data.")])]),
        ]),

    concept(
        "c-doe", "Design of experiments: where to sample. Latin hypercubes beat grids in high dimensions", 1, L4,
        r"""
A good sampling plan is **space-filling** (no big unexplored gaps), **non-collapsing** (each variable's projection is well spread, no repeated values along an axis) and **economical**.

- **Full factorial (grid):** $k$ levels in each of $n$ variables needs $k^n$ runs. That explodes quickly: the *curse of dimensionality*.
- **Pure random:** cheap, but leaves gaps and clusters.
- **Latin hypercube (LHS):** split each variable's range into $p$ equal intervals and use each interval **exactly once per variable**. You get $p$ distinct levels in every 1-D projection, for only $p$ runs.

In SciPy: `scipy.stats.qmc.LatinHypercube(d=n, seed=...)`, then `qmc.scale` to your bounds ([[lib-qmc-lhs]]).
""",
        deeper=["c-surrogates-why"],
        math=[r"\text{grid runs} = k^n,\qquad \text{levels a grid of } p \text{ runs affords} = \lfloor p^{1/n}\rfloor"],
        analogy=analogy("Seating guests so every row and every column has exactly one person, like rooks on a chessboard that can't attack each other: everyone is spread out, and no row or column is wasted.",
                        "a Latin hypercube can still be poor (all points on a diagonal satisfies the rule). Good LHS designs also optimize spacing, e.g. maximin."),
        exam="Compare budgets numerically: '$k^n$ for a grid vs $p$ for LHS' is a one-line, high-value argument.",
        widget={"type": "doe"},
        source="Lecture 4, slides 13–15",
        problems=[
            problem("c-doe-1", "The curse, in numbers",
                    r"An LHS with $p = 100$ points in $n = 4$ dimensions has 100 distinct levels per variable.",
                    [num("How many runs would a full-factorial grid need for the same 100 levels per variable?", 100**4, "",
                         explain="$100^4 = 10^8$ runs, against 100 for the LHS."),
                     num("How many levels per variable can a grid of at most 100 runs afford?", math.floor(100 ** 0.25), "",
                         explain="$\\lfloor100^{1/4}\\rfloor = \\lfloor3.16\\rfloor = 3$ levels.")]),
            problem("c-doe-2", "What makes it Latin?",
                    r"Each variable's range is split into $p$ equal intervals.",
                    [choice("The defining LHS rule is…", [opt("each interval is used exactly once for each variable", True), opt("points lie on a regular grid", why="That's full factorial."),
                                                          opt("points are drawn independently at random", why="That's pure random sampling."),
                                                          opt("points cluster near the expected optimum", why="That's adaptive (infill) sampling, a later idea.")])]),
        ]),

    concept(
        "c-model-taxonomy", "Interpolation or regression, parametric or not, local or global", 1, L4,
        r"""
Three ways to classify a data-based model:

| Axis | One end | Other end |
|---|---|---|
| Fit | **interpolating**: passes through every data point; for deterministic, noise-free simulations | **regression**: minimizes a fitting error; for noisy data |
| Form | **parametric**: fixed form, finite coefficients (a quadratic polynomial) | **non-parametric**: complexity grows with data (Kriging, RBF) |
| Scope | **local**: refit near the current design (trust-region surrogates) | **global**: built once over the whole domain |

The lecture studies three global families: polynomial regression ([[c-least-squares]]), neural networks ([[c-ann]], [[c-rbf]]) and Kriging ([[c-kriging]]).
""",
        deeper=["c-surrogates-why"],
        math=[],
        analogy=analogy("Interpolation is a tailor who sews through every measurement exactly; regression is one who fits a pattern that ignores a measurement taken while you slouched.",
                        "with noise-free data, 'ignoring' a point throws away truth; with noisy data, honouring every point fits the noise."),
        exam="Justify interpolation vs regression from the data: deterministic simulation → interpolation is fine; noisy measurements → regression.",
        source="Lecture 4, slides 16–19",
        problems=[
            problem("c-tax-1", "Classify Kriging",
                    r"Ordinary Kriging without a nugget.",
                    [choice("Which description fits?", [opt("interpolating, non-parametric, global", True), opt("regression, parametric, global", why="It passes through the data, and its complexity grows with the data."),
                                                        opt("interpolating, parametric, local", why="Kriging isn't parametric, and the lecture builds it globally."),
                                                        opt("regression, non-parametric, local", why="Without a nugget it interpolates exactly.")]),
                     choice("Your data comes from noisy wind-tunnel measurements. Better choice?", [opt("a regression model", True), opt("an exactly interpolating model", why="It would faithfully fit the noise."),
                                                                                                    opt("no model: noise can't be modelled", why="Regression is designed for noisy data."), opt("a full-factorial design", why="That's a sampling plan, not a model.")])]),
        ]),

    concept(
        "c-model-assessment", "Judge a model on data it hasn't seen: hold-out sets and k-fold cross-validation", 1, L4,
        r"""
- **Underfitting**: too simple to capture the trend; large error on training *and* new data.
- **Overfitting**: so flexible it fits the noise; tiny training error, poor predictions elsewhere.

Training error can't detect overfitting, because it always falls as flexibility grows. So we judge on **unseen** data:
- a **train/test split**: fit on the training set, assess on the held-out test set; or, with little data,
- **k-fold cross-validation**: split into $k$ folds, train on $k-1$, test on the remaining one, rotate through all $k$, and average the errors.

Every family has a **complexity knob** (polynomial degree or ridge $\lambda$, RBF spread, network width, Kriging length-scale). Pick it by cross-validation error, never by training error ([[c-surrogate-choice]]).
""",
        deeper=["c-model-taxonomy"],
        math=[r"\text{CV error} = \frac1k\sum_{j=1}^k \text{error on fold } j"],
        analogy=analogy("A student who memorizes past exam answers aces the practice paper (training error) and fails the real exam (new data). Cross-validation is giving them unseen papers.",
                        "CV still uses the same overall dataset. If the whole dataset is unrepresentative (all from one corner of the design space), CV can't warn you."),
        exam="Always report which error (training, CV, test) a number is. 'RMSE = 0.01' alone is meaningless.",
        widget={"type": "fit"},
        source="Lecture 4, slides 20–22",
        problems=[
            problem("c-ma-1", "How many points train each model?",
                    r"5-fold cross-validation on $p = 50$ data points.",
                    [num("How many points train each of the 5 models?", 40, ""), num("How many models are fitted in total?", 5, "")]),
            problem("c-ma-2", "Picking the knob",
                    r"Polynomial degree 1 to 12, fitted to 30 points.",
                    [choice("Which degree should you choose?", [opt("the one with the lowest cross-validation error", True), opt("the one with the lowest training error", why="That's always the highest degree: it fits the noise."),
                                                                opt("the highest, to be safe", why="Higher degree overfits."), opt("degree 1, because simple is best", why="Too simple underfits; let CV decide.")])]),
        ]),

    concept(
        "c-error-metrics", "RMSE has the units of y; R² says what fraction of the variability the model explains", 1, L4,
        r"""
On $q$ test points with true values $y_i$ and predictions $\hat f(\mathbf{x}_i)$:
$$\text{RMSE} = \sqrt{\frac1q\sum_{i=1}^q\big(y_i - \hat f(\mathbf{x}_i)\big)^2},\qquad R^2 = 1 - \frac{\sum(y_i - \hat f(\mathbf{x}_i))^2}{\sum(y_i - \bar y)^2}.$$
RMSE has the same units as $y$, so it's easy to interpret physically. $R^2$ near 1 means the model explains most of the variability; $R^2$ can be *negative* on test data if the model is worse than just predicting the mean.
""",
        deeper=["c-model-assessment", "p-statistics"],
        math=[r"\text{RMSE} = \sqrt{\tfrac1q\textstyle\sum(y_i - \hat y_i)^2}", r"R^2 = 1 - \dfrac{\sum(y_i - \hat y_i)^2}{\sum(y_i - \bar y)^2}"],
        analogy=analogy("RMSE is 'how far off, typically, in real units'; $R^2$ is 'how much better than a lazy guess of the average'.",
                        "a high $R^2$ can hide a large RMSE when $y$ varies a lot, and vice versa. Report both."),
        exam="Compute both on the **test** set, and state which set you used.",
        source="Lecture 4, slides 23–25",
        problems=[
            problem("c-em-1", "Compute both",
                    r"True $y = [1, 2, 3]$, predicted $\hat y = [1, 2, 4]$.",
                    [num("RMSE?", _rmse, "", explain="$\\sqrt{(0 + 0 + 1)/3} = 0.577$."),
                     num("$R^2$?", _r2, "", explain="$1 - 1/2 = 0.5$, since $\\sum(y_i - \\bar y)^2 = 2$.")]),
            problem("c-em-2", "Negative R²",
                    r"A model scores $R^2 = -0.3$ on the test set.",
                    [choice("What does that mean?", [opt("It predicts worse than simply using the mean of the test data", True), opt("It's a calculation error: $R^2$ can't be negative", why="On test data it can, whenever the model's error exceeds the variance."),
                                                     opt("It's 30% accurate", why="$R^2$ isn't an accuracy percentage."), opt("It overfits a little", why="It could be badly overfit or badly underfit: it's worse than the mean.")])]),
        ]),

    concept(
        "c-least-squares", "Least squares: minimize the squared error, get the normal equations", 1, L4,
        r"""
A polynomial model is linear in its coefficients: $\hat{\mathbf{y}} = \mathbf{Z}\mathbf{w}$, where each row of the **design matrix** $\mathbf{Z}$ holds the basis terms at one data point, e.g. $[1,\ x_{1i},\ x_{2i},\ x_{1i}^2,\ x_{2i}^2,\ x_{1i}x_{2i}]$ for a 2-D quadratic. With more data than coefficients ($p > n$) the system is overdetermined, so minimize
$$\varepsilon = (\mathbf{Z}\mathbf{w} - \mathbf{y})^T(\mathbf{Z}\mathbf{w} - \mathbf{y}).$$
Setting $\partial\varepsilon/\partial\mathbf{w} = 2\mathbf{Z}^T\mathbf{Z}\mathbf{w} - 2\mathbf{Z}^T\mathbf{y} = \mathbf{0}$ ([[p-matrix-calculus]]) gives the **normal equations**
$$\mathbf{Z}^T\mathbf{Z}\,\mathbf{w} = \mathbf{Z}^T\mathbf{y}.$$
In NumPy: `w = np.linalg.solve(Z.T @ Z, Z.T @ y)`. (`np.linalg.lstsq(Z, y)` solves the same problem more stably, without ever forming $\mathbf{Z}^T\mathbf{Z}$.) If you have multiple outputs, fit one model per output.
""",
        deeper=["c-model-taxonomy", "p-matrix-calculus", "p-linear-systems", "p-numpy-shapes"],
        math=[r"\mathbf{Z}^T\mathbf{Z}\,\mathbf{w} = \mathbf{Z}^T\mathbf{y}"],
        analogy=analogy("Each data point pulls the fitted line toward itself with a spring; least squares finds where all the springs balance (spring energy ∝ distance squared).",
                        "squaring makes outliers pull very hard, so one bad point can drag the whole fit. Robust regression uses gentler 'springs'."),
        exam="Show the design matrix's first two rows explicitly. It proves you know which basis terms you're fitting.",
        source="Lecture 4, slides 28–42, 54–55",
        problems=[
            problem("c-ls-1", "Fit a line by hand",
                    r"Fit $\hat y = w_0 + w_1x$ to the points $(0, 1)$, $(1, 2)$, $(2, 2)$. Here $\mathbf{Z}^T\mathbf{Z} = \begin{bmatrix}3 & 3\\3 & 5\end{bmatrix}$ and $\mathbf{Z}^T\mathbf{y} = \begin{bmatrix}5\\6\end{bmatrix}$.",
                    [num(r"$w_0$?", float(_w[0]), ""), num(r"$w_1$?", float(_w[1]), "",
                         explain="Solve $\\begin{bmatrix}3&3\\\\3&5\\end{bmatrix}\\mathbf{w} = \\begin{bmatrix}5\\\\6\\end{bmatrix}$: $w_0 = 7/6$, $w_1 = 1/2$.")]),
            problem("c-ls-2", "In NumPy",
                    r"`Z` is the design matrix and `y` the data vector.",
                    [blank("Complete: `w = np.linalg.solve(Z.T @ Z, ____)`", ["Z.T @ y", "Z.T@y", "Z.T.dot(y)", "np.dot(Z.T, y)", "Z.T @ y.ravel()"], mode="code",
                           explain="The right-hand side of the normal equations is $\\mathbf{Z}^T\\mathbf{y}$."),
                     choice("Which shape must `y` have for `w` to come out as a 1-D vector?", [opt("`(p,)`", True), opt("`(1, p)`", why="`Z.T @ y` would fail: `(n, p) @ (1, p)` doesn't align."),
                                                                                              opt("`(p, p)`", why="That's a matrix, not a data vector."), opt("Any shape works", why="Shapes matter; `(p, 1)` gives a `(n, 1)` result instead.")])]),
        ]),

    concept(
        "c-conditioning-ridge", "Ill-conditioning makes the fit jittery; ridge regression trades a little bias for stability", 1, L4,
        r"""
The **condition number** $\kappa(\mathbf{A}) = |\lambda_{max}|/|\lambda_{min}|$ measures how much a small change in the data can change the solution. $\mathbf{Z}^T\mathbf{Z}$ becomes **ill-conditioned** when the columns of $\mathbf{Z}$ are nearly collinear or badly scaled (high-degree terms over a narrow range), not simply because there's a lot of data.

**Ridge regression** (Tikhonov regularization) penalizes large coefficients:
$$\varepsilon_{ridge} = (\mathbf{Z}\mathbf{w} - \mathbf{y})^T(\mathbf{Z}\mathbf{w} - \mathbf{y}) + \lambda\mathbf{w}^T\mathbf{w}\ \Rightarrow\ \mathbf{w}_{ridge} = (\mathbf{Z}^T\mathbf{Z} + \lambda\mathbf{I})^{-1}\mathbf{Z}^T\mathbf{y}.$$
Adding $\lambda\mathbf{I}$ raises every eigenvalue by $\lambda$, so $\kappa(\mathbf{Z}^T\mathbf{Z} + \lambda\mathbf{I}) = (\lambda_{max}+\lambda)/(\lambda_{min}+\lambda)$ falls, at the cost of biasing $\mathbf{w}$ toward 0 (the **bias–variance trade-off**). $\lambda$ is a hyperparameter: pick it by cross-validation. Replacing $\lambda\mathbf{w}^T\mathbf{w}$ by $\lambda\|\mathbf{w}\|_1$ gives **LASSO**, which also zeroes some coefficients.
""",
        deeper=["c-least-squares", "p-eigen-definiteness"],
        math=[r"\mathbf{w}_{ridge} = (\mathbf{Z}^T\mathbf{Z} + \lambda\mathbf{I})^{-1}\mathbf{Z}^T\mathbf{y}", r"\kappa(\mathbf{Z}^T\mathbf{Z}+\lambda\mathbf{I}) = \frac{\lambda_{max}+\lambda}{\lambda_{min}+\lambda}"],
        analogy=analogy("A wobbly table on an uneven floor: tiny shifts make it rock wildly (ill-conditioned). Ridge is a felt pad under the short leg: the table is a hair off level, but it stops rocking.",
                        "too thick a pad (huge λ) tilts the table badly: the model becomes too biased to fit anything."),
        exam="Quote κ before and after any fix (scaling or ridge). The improvement factor is the evidence.",
        source="Lecture 4, slides 42–53",
        problems=[
            problem("c-ridge-1", "κ from eigenvalues",
                    r"Lecture 4's example matrix has eigenvalues $-0.236$, $4.236$ and $5$.",
                    [num(r"$\kappa$?", 5 / 0.236, "", tol=0.01, explain="$|5|/|-0.236|\\approx21.2$."),
                     num(r"If $\mathbf{Z}^T\mathbf{Z}$ has $\lambda_{max} = 100$, $\lambda_{min} = 0.01$, what is $\kappa(\mathbf{Z}^T\mathbf{Z} + 1\cdot\mathbf{I})$?", 101 / 1.01, "",
                         explain="$(100+1)/(0.01+1) = 100$, down from $10^4$.")]),
            problem("c-ridge-2", "The trade-off",
                    r"You increase ridge's $\lambda$ from $10^{-4}$ to $100$.",
                    [choice("What happens?", [opt("Conditioning improves, but the coefficients are pulled toward zero (more bias)", True),
                                              opt("Training error always falls", why="Penalizing coefficients makes the training fit worse, not better."),
                                              opt("Nothing changes", why="$\\lambda$ directly changes the solution."),
                                              opt("Variance increases", why="Regularization reduces variance.")])]),
        ]),

    concept(
        "c-variable-scaling", "Scale inputs to [0, 1] before building matrices; use the training set's bounds for everything", 1, L4,
        r"""
Badly scaled inputs (one variable around $10^6$, another around $10^{-2}$) make $\mathbf{Z}^T\mathbf{Z}$ and Kriging's $\mathbf{R}$ ill-conditioned. **Min–max scaling** fixes this:
$$x^{scaled}_i = \frac{x_i - l_i}{u_i - l_i}\in[0, 1].$$
In Lecture 4's example, scaling cut $\kappa(\mathbf{Z}^T\mathbf{Z})$ from $2.14\times10^6$ to $2432$.

Two rules: compute $l$ and $u$ from the **training** data only, and apply the **same** $l, u$ to test points and to every future prediction. Fitting the scaler on all the data leaks test information into training ([[e-scale-leak]]). Variables spanning orders of magnitude (like Reynolds number) are often better transformed to $\log_{10}$ first.
""",
        deeper=["c-conditioning-ridge"],
        math=[r"x^{scaled} = \frac{x - l}{u - l}"],
        analogy=analogy("Converting all measurements to the same unit system before comparing them: nobody should win an argument because their number was written in millimetres.",
                        "scaling changes conditioning, not information. It won't rescue a model that's simply the wrong form."),
        exam="Report the scaling (bounds used, any log transforms) in the method section. Results can't be reproduced without it.",
        source="Lecture 4, slides 96–98",
        problems=[
            problem("c-scale-1", "Scale a value",
                    r"Training data for $x$ spans $l = 2$ to $u = 12$.",
                    [num(r"Scaled value of $x = 7$?", 0.5, ""), num(r"Scaled value of a test point $x = 14$?", (14 - 2) / 10, "",
                         explain="$1.2$: test points can fall outside $[0, 1]$. That's correct; don't rescale them with their own bounds.")]),
        ]),

    concept(
        "c-ann", "A neural network is a big sum of simple nonlinear pieces, trained by unconstrained optimization", 1, L4,
        r"""
Function approximation as a basis expansion, $f(\mathbf{x})\approx\sum_{i=1}^k w_i\phi_i(\mathbf{x})$: polynomials use monomials, Taylor series use derivatives at one point (accurate locally, wild far away), neural networks use neurons.

A **neuron** computes $n = \mathbf{W}\mathbf{p} + b$ and passes it through an activation $f$: logistic or tanh sigmoids, or **ReLU** $\max(0, n)$, the modern default because it avoids vanishing gradients. A **feedforward network** stacks layers; choosing the number of layers, the neurons per layer and the activation is a large, empirical design problem.

**Training is an unconstrained optimization problem:** minimize $\varepsilon(\mathbf{w}) = \sum_i(\hat y(\mathbf{x}_i;\mathbf{w}) - y_i)^2$. Unlike polynomial regression, $\hat y$ is nonlinear and non-convex in $\mathbf{w}$, so there are no normal equations. We use gradient methods ([[c-gradient-method]], [[c-quasi-newton]]), with gradients from **backpropagation** (the chain rule, layer by layer: [[p-chain-rule]]), and stochastic mini-batch methods (SGD, Adam) for large datasets.
""",
        deeper=["c-model-taxonomy", "p-chain-rule"],
        math=[r"n = \mathbf{W}\mathbf{p} + b,\quad a = f(n)", r"\min_{\mathbf{w}}\ \varepsilon(\mathbf{w}) = \sum_i\big(\hat y(\mathbf{x}_i;\mathbf{w}) - y_i\big)^2"],
        analogy=analogy("Building any shape from Lego: each brick (neuron) is trivial, but enough of them, arranged well, can approximate anything.",
                        "more bricks also means more ways to build the wrong thing: wide networks overfit unless width is chosen by cross-validation."),
        exam="If asked why ANN training can get stuck, the answer is non-convexity: local minima, plus saturating activations causing vanishing gradients.",
        source="Lecture 4, slides 57–70",
        problems=[
            problem("c-ann-1", "One ReLU neuron",
                    r"Weights $\mathbf{W} = [2, -1]$, input $\mathbf{p} = [1, 3]^T$, bias $b = 0.5$, ReLU activation.",
                    [num("Net input $n$?", 2 * 1 - 1 * 3 + 0.5, ""), num("Output?", 0, "", tol=0.001, explain="ReLU of $-0.5$ is 0: this neuron is 'off' for this input.")]),
            problem("c-ann-2", "Why iterate?",
                    r"Polynomial regression has a closed-form solution; network training doesn't.",
                    [choice("Why not?", [opt("The network output is nonlinear in its weights, so the loss is non-convex with no normal-equation solution", True),
                                         opt("Networks have too many data points", why="Data size isn't the reason; even small networks need iterative training."),
                                         opt("Backpropagation is too slow", why="Backpropagation computes gradients; it doesn't replace solving."),
                                         opt("The loss isn't differentiable", why="It is (with smooth activations), which is why gradient methods work.")])]),
        ]),

    concept(
        "c-rbf", "Radial basis functions: a bump at every data point, weights from one linear solve", 1, L4,
        r"""
An RBF network places one radial bump at each data point and sums them:
$$\hat y(\mathbf{x}) = \sum_{i=1}^p w_i\,\phi(\|\mathbf{x} - \mathbf{x}_i\|),\qquad \phi(r) = e^{-\lambda r^2}\ \text{(Gaussian)}.$$
Requiring $\hat y(\mathbf{x}_i) = y_i$ gives one linear system, $\boldsymbol\Phi\mathbf{w} = \mathbf{y}$ with $\Phi_{ij} = \phi(\|\mathbf{x}_i - \mathbf{x}_j\|)$, structurally the same as Kriging's.

The **spread** $\lambda$ is the complexity knob. Large $\lambda$ means narrow bumps: spikes at the data and nothing in between (poor generalization). Small $\lambda$ means wide, overlapping bumps: smooth, but $\boldsymbol\Phi$ becomes ill-conditioned. Pick $\lambda$ by cross-validation. In SciPy, `RBFInterpolator(..., kernel='gaussian', epsilon=np.sqrt(lam))`. Its default thin-plate kernel ignores `epsilon` entirely ([[e-rbf-epsilon]]).
""",
        deeper=["c-model-taxonomy", "p-linear-systems"],
        math=[r"\hat y(\mathbf{x}) = \sum_i w_i\,e^{-\lambda\|\mathbf{x}-\mathbf{x}_i\|^2}", r"\boldsymbol\Phi\mathbf{w} = \mathbf{y}"],
        analogy=analogy("Pitching a tent with a pole at every data point: thin poles (narrow bumps) give spikes, while wide, soft poles give a smooth canopy that may sag between them.",
                        "unlike tent poles, wide bumps overlap so much that the system to solve for their heights becomes nearly singular."),
        exam="Sweep $\\lambda$ across orders of magnitude (e.g. $10^{-4}$ to $10^3$) on a log axis; a linear sweep misses the interesting range.",
        widget={"type": "rbf"},
        source="Lecture 4, slides 71–76",
        problems=[
            problem("c-rbf-1", "Two bumps",
                    r"Two centres 1 apart, Gaussian $\phi$ with $\lambda = 1$, data $\mathbf{y} = [1, 0]$. So $\boldsymbol\Phi = \begin{bmatrix}1 & e^{-1}\\ e^{-1} & 1\end{bmatrix}$.",
                    [num(r"$w_1$?", _w1, ""), num(r"$w_2$?", _w2, "", explain="The second bump goes negative to cancel the first one's tail at $x_2$.")]),
            problem("c-rbf-2", "Spread extremes",
                    r"Cross-validation error is high both at $\lambda = 10^{3}$ and at $\lambda = 10^{-4}$.",
                    [choice(r"At $\lambda = 10^3$ (very narrow bumps) the model…", [opt("spikes at the data and falls to ~0 between points", True), opt("is too smooth", why="Narrow bumps can't reach between data points."),
                                                                                   opt("is ill-conditioned", why="Narrow bumps make $\\boldsymbol\\Phi\\approx\\mathbf{I}$, well-conditioned."), opt("is linear", why="It's a sum of narrow Gaussians.")])]),
        ]),

    concept(
        "c-kriging", "Kriging: treat the error as spatially correlated, so nearby points predict each other", 1, L4,
        r"""
Least squares and RBFs treat the error as independent between points. Danie Krige's insight: for a smooth function, values at nearby points are likely to be similar, so the error is **spatially correlated**. Kriging models it as a random process with a correlation function, typically $R(\mathbf{x}_i, \mathbf{x}_j) = e^{-\theta\|\mathbf{x}_i - \mathbf{x}_j\|^2}$.

**Ordinary Kriging** estimates a constant mean $\beta$ by generalized least squares and predicts
$$\hat y(\mathbf{x}_{new}) = \hat\beta + \mathbf{r}^T\mathbf{R}^{-1}(\mathbf{y} - \hat\beta\mathbf{1}),\qquad \hat\beta = \frac{\mathbf{1}^T\mathbf{R}^{-1}\mathbf{y}}{\mathbf{1}^T\mathbf{R}^{-1}\mathbf{1}},$$
where $\mathbf{R}$ holds the correlations among data points and $\mathbf{r}$ those between $\mathbf{x}_{new}$ and each data point. It interpolates the data exactly. Small $\theta$ (long correlation) makes all of $\mathbf{R}$'s entries close to 1, so $\mathbf{R}$ becomes nearly singular. A small **nugget** $\epsilon\mathbf{I}$ restores conditioning. In practice, $\theta$ is fit by maximum likelihood, not chosen by hand.
""",
        deeper=["c-rbf", "c-conditioning-ridge"],
        math=[r"\hat y(\mathbf{x}) = \hat\beta + \mathbf{r}^T\mathbf{R}^{-1}(\mathbf{y} - \hat\beta\mathbf{1})", r"R_{ij} = e^{-\theta\|\mathbf{x}_i - \mathbf{x}_j\|^2}"],
        analogy=analogy("Guessing house prices: a house next door to a known sale is probably priced similarly, one across town less so. Kriging weights neighbours by how correlated they are.",
                        "it assumes correlation depends only on distance (stationarity). If the function behaves very differently in different regions, that assumption strains."),
        exam="When a Kriging fit misbehaves, report κ(R). Huge values point to a θ that's too small or near-duplicate points; a nugget is the standard fix.",
        widget={"type": "kriging"},
        source="Lecture 4, slides 80–94",
        problems=[
            problem("c-kr-1", "A correlation entry",
                    r"$R = e^{-\theta d^2}$ with $\theta = 2$.",
                    [num(r"Correlation between two points $d = 0.5$ apart?", math.exp(-2 * 0.25), ""),
                     choice(r"As $\theta\to0$, what happens to $\mathbf{R}$?", [opt("All entries approach 1, so it becomes nearly singular", True),
                                                                               opt("It becomes the identity", why="That's $\\theta\\to\\infty$: everything uncorrelated."),
                                                                               opt("Its entries go to 0", why="$e^{0} = 1$."), opt("It's unaffected", why="Every entry depends on θ.")])]),
            problem("c-kr-2", "The nugget",
                    r"`np.linalg.cond(R)` returns $10^{17}$.",
                    [choice("Standard fix?", [opt("Add a small nugget: $\\mathbf{R} + \\epsilon\\mathbf{I}$ with $\\epsilon\\approx10^{-6}$", True),
                                              opt("Invert it anyway with `np.linalg.inv`", why="The result would be numerically meaningless."),
                                              opt("Remove the mean $\\hat\\beta$", why="The mean doesn't affect $\\mathbf{R}$."),
                                              opt("Increase the number of points near the bad ones", why="More near-duplicate points make conditioning worse.")])]),
        ]),

    concept(
        "c-gpr-uncertainty", "Kriging also says how unsure it is: zero at the data, growing in the gaps", 1, L4,
        r"""
Because Kriging models the error as a Gaussian random process, it gives a **predicted variance** at every new point:
$$s^2(\mathbf{x}_{new}) = \hat\sigma^2\left[1 - \mathbf{r}^T\mathbf{R}^{-1}\mathbf{r} + \frac{(1 - \mathbf{1}^T\mathbf{R}^{-1}\mathbf{r})^2}{\mathbf{1}^T\mathbf{R}^{-1}\mathbf{1}}\right].$$
$s^2\to0$ at sampled points and grows in unexplored regions. This is exactly what machine learning calls **Gaussian process regression (GPR)**. The uncertainty can guide *where to sample next* (infill criteria such as expected improvement), which is the idea behind Bayesian optimization.

In scikit-learn: `GaussianProcessRegressor(...).predict(X, return_std=True)` ([[lib-gpr]]).
""",
        deeper=["c-kriging", "p-statistics"],
        math=[r"s^2(\mathbf{x})\to0\ \text{at data points}"],
        analogy=analogy("A night-time map lit by streetlamps at each data point: bright and certain near the lamps, darker and less certain in between.",
                        "the 'darkness' reflects the model's assumptions (correlation length, Gaussianity). It isn't a guarantee about the true function."),
        exam="When asked about uncertainty, compare $s$ at the test point nearest to the training data and at the farthest: that contrast is the whole story.",
        source="Lecture 4, slide 91",
        problems=[
            problem("c-gpr-1", "Where is it unsure?",
                    r"A Kriging model trained on 20 points.",
                    [choice("Where is its predicted standard deviation smallest?", [opt("At (and very near) the training points", True), opt("Far from all training points", why="That's where it's largest."),
                                                                                    opt("Uniform everywhere", why="It depends on the distance to data."), opt("At the domain corners", why="Only if the training points are there.")]),
                     choice("Which family gives this uncertainty natively?", [opt("Kriging / GPR", True), opt("Polynomial least squares", why="It gives a point prediction only (without extra statistics)."),
                                                                             opt("RBF networks", why="Standard RBF interpolation gives no variance."), opt("A single neural network", why="Ensembles can approximate uncertainty; a single network doesn't give it natively.")])]),
        ]),

    concept(
        "c-surrogate-choice", "Every surrogate family has a complexity knob, and you choose it by cross-validation", 1, L4,
        r"""
| Family | Parametric? | Complexity knob | Native uncertainty? | Best suited for |
|---|---|---|---|---|
| Polynomial (least squares) | yes | degree, ridge $\lambda$ | no | smooth, low-dimensional, few data |
| RBF network | no | number of centres, spread $\lambda$ | no | scattered data, moderate dimension |
| Neural network | yes (large) | layers and neurons, weight decay | no | large datasets, high dimension |
| Kriging / GPR | no | correlation length $\theta$ | **yes**, $s^2$ | small or expensive data, sequential design |

The lecture's remark: every family's knob trades **bias for variance**, and regardless of family it's selected the same way, by cross-validation error, never training error.
""",
        deeper=["c-model-assessment", "c-least-squares", "c-rbf", "c-ann", "c-kriging"],
        math=[],
        analogy=analogy("Choosing a camera lens: each lens has a zoom ring (the knob), and you check the shot (cross-validation), not the viewfinder's flattering preview (training error).",
                        "the table gives tendencies, not rules. With modern tools, GPR scales further and networks can be uncertainty-aware."),
        exam="A comparison answer needs, for each family: its knob, the knob value chosen by CV, the test RMSE/$R^2$, and whether it gives uncertainty.",
        source="Lecture 4, slide 101",
        problems=[
            problem("c-sc-1", "Match the knob",
                    r"Each surrogate family has its own complexity knob.",
                    [choice("The complexity knob of an RBF network is…", [opt("the spread $\\lambda$ (and number of centres)", True), opt("the polynomial degree", why="That's polynomial regression."),
                                                                         opt("the number of hidden layers", why="That's a feedforward ANN."), opt("the correlation length θ", why="That's Kriging.")]),
                     choice("You have 30 expensive simulations and want to choose where to run the 31st. Best family?", [opt("Kriging / GPR, for its native uncertainty", True),
                                                                                                                          opt("A deep neural network", why="Too little data, and no native uncertainty."),
                                                                                                                          opt("A degree-10 polynomial", why="30 points can't support it safely, and there's no uncertainty to guide sampling."),
                                                                                                                          opt("Any: they're equivalent", why="Only Kriging gives the uncertainty that guides sequential sampling.")])]),
        ]),

    concept(
        "c-surrogate-optimization", "Surrogate-based optimization: sample, fit, optimize the cheap model, check, repeat", 1, L4,
        r"""
The loop:
1. Sample the design space (DOE: [[c-doe]]).
2. Evaluate the true, expensive function at those points.
3. Fit a surrogate $\hat f$.
4. Optimize $\hat f$, which is cheap, so you can afford many optimizer iterations.
5. Evaluate the true $f$ at the proposed optimum to validate it.
6. Add that point to the data, refit, and repeat until converged.

The true function is only re-evaluated to validate and refine the surrogate near the candidate optimum. Kriging's uncertainty can also add exploratory points where the model is unsure ([[c-gpr-uncertainty]]).
""",
        deeper=["c-surrogates-why", "c-doe", "c-surrogate-choice"],
        math=[],
        analogy=analogy("Planning a road trip with a cheap paper map, then confirming each leg by actually driving it, and correcting the map wherever it was wrong.",
                        "if the map is wrong in a region you never drive through, you'll never find out. Exploration points guard against that."),
        exam="When reporting a surrogate-based optimum, always give the *true* function value at the final point, not just the surrogate's prediction.",
        source="Lecture 4, slide 26",
        problems=[
            problem("c-sbo-1", "Order the loop",
                    r"Surrogate-based optimization.",
                    [order("Put the steps in order.", [
                        "Choose sample points with a design of experiments",
                        "Evaluate the true function at the samples",
                        "Fit the surrogate",
                        "Optimize the surrogate",
                        "Validate the proposed optimum with the true function",
                        "Add the new point to the data and refit",
                    ])]),
        ]),
]
