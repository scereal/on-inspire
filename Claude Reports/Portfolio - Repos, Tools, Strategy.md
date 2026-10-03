# Building a Brilliant.org Application Portfolio: Repos, Tools, Strategy, and a 3-Week Plan

**Bottom line: build two or three polished, browser-native interactive problems first (in about two weeks). Make them with web-math libraries such as Mafs, JSXGraph, or manim-web, not diffusion video. Then apply through Lever and send short, low-ask LinkedIn notes that link to the finished work.** The role you linked is **Math Learning Designer** (NYC, SF, or Remote; US$110,000–180,000 plus stock options). The posting says outright that "to be considered for this role, please include your best example(s) of how you've taught mathematical concepts interactively online."\[1\] So your portfolio is not a nice extra. It is the application.

## TL;DR

- **Lead with interactive problems, not videos or a platform.** Brilliant has no videos ("there are no videos, and everything is interactive").\[2\] Its blog says AI handles implementation while designers own "the learning objective, the progression, and the 'aha moment'".\[3\] Your strongest evidence is 2–3 self-contained, playable problem sequences: Fourier square-wave knobs, the two-cup iced-tea problem, and an integration-by-parts "find the error" set.
- **Use deterministic code for the math. Use diffusion video, if at all, only for decoration.** Manim (ManimCE or ManimGL), manim-web, Mafs, JSXGraph, and Three.js render exactly what the math says. Diffusion models like Wan 2.2, or platforms like Higgsfield, routinely break physical and logical constraints. One 2026 benchmark found that 83.3% of exocentric and 93.5% of egocentric generated videos contained at least one human-identifiable physics violation.\[4\]
- **Build first, then reach out, and apply the same week.** Brilliant explicitly asks for samples. A LinkedIn Talent Blog analysis found the shortest InMails (under 400 characters) get response rates 22% above average. Greenhouse data cited by LinkedIn puts referred candidates' hire odds at 1 in 25 versus 1 in 200.\[5\] Send a short note that asks for feedback and links to finished work. It beats a cold "can we chat?" and it beats a half-built repo.

## Key Findings

### 1. What the job actually is

The posting is for a **Math Learning Designer** on Brilliant's Content team. It is not an engineering role. Responsibilities:

- Develop interactive courses in algebra, geometry, probability, calculus, and beyond.\[1\]
- Design "visual, puzzle-driven learning experiences that guide learners along problem-solving journeys."\[1\]
- "Decompose complex mathematical ideas into approachable, well-sequenced steps that empower learners to reason from first principles."\[1\]
- Create clear, creative, intuitive content using "visuals, interactivity, and problem sequencing."\[1\]
- Collaborate with product, design, and engineering on new interactive features for computers and phones.\[1\]

Qualifications:

- A STEM undergraduate degree, plus grounding "through research or teaching that extends beyond traditional math curricula."\[1\]
- "A knack for teaching complex topics using a progression of clear, simple, hands-on steps."\[1\]
- Experience building or using interactivity to engage learners.\[1\]
- Top-notch English writing.\[1\]
- Context-switching ability, openness to experimenting with formats, and willingness to "jump into any aspect of a project."\[1\]

The Lever form has fields for LinkedIn, GitHub, and Portfolio URLs. It allows two file uploads and two "website link" samples ("interactive learning experiences, blog posts, lesson or problem set PDFs, jupyter notebooks etc.") and a required "Why are you interested in Brilliant?" note.\[6\]

**What this means for you:** your TA experience and mechanical-engineering degree clear the formal bar. The deciding factor will be **taste in sequencing and interaction design**, shown through samples. Brilliant says it hires "very selectively and intentionally" and makes "First and Best offers" with no negotiation. Core hours are 9:30am–2:30pm Pacific,\[1\] which is workable from Montreal (Eastern time). Note the job is listed as NYC, SF, or Remote. A Canadian applicant should confirm early whether "Remote" includes Canada or would need US work authorization. That is an open question I could not verify.

### 2. How Brilliant thinks, and where your ideas fit

Brilliant's public statements describe a **problem-first, interactive, game-like** method:

- Its About page says it "pretest[s] on the material, letting the learner try to find a solution before learning the procedure." It builds intuition "with visual explanations, hands-on manipulation, and concrete computation." Each problem "gives instant, custom feedback."\[7\]
- The January 2025 blog post "Hand-crafted, machine-made" uses Super Mario as the model: "You don't get a text box saying 'You pressed the jump button too early.' You fall into the pit and die." Brilliant "decided to stay on the sidelines" of AI tutoring chatbots. In its words, "an AI at Brilliant needs to speak to the learner in rich, interactive games – not text."\[3\]
- On scale, the same post says a pre-algebra course has "50+ core concepts," needs "20+ problems per concept," and therefore "1,000+ individual problems." Brilliant already uses LLM pipelines to generate puzzles and practice-set variants. It went "from a 0% to 93% success rate" on gear-train puzzles by making game representations more LLM-friendly. "Every generated problem also goes through multiple rounds of human review."\[3\]
- The company reports serving "hundreds of thousands of paid subscribers."\[1\] Its careers page describes a team of "~60 people."\[8\]

**Mapping your ideas against Brilliant's existing approach (to avoid overclaiming):**

| Your idea | Brilliant already does… | How to position it |
|---|---|---|
| Mass-generated single-step problems | Has internal LLM tools for puzzle generation and variants with human review | Don't pitch "mass generation" as novel. Pitch your *taxonomy* of single-step formats (find the error, fill the blank, choose the equation, fit the curve, solve another way) and show 5–10 hand-curated examples. |
| Instant brief/in-depth feedback | "Instant, custom feedback" is core | Show *misconception-specific* feedback: each wrong answer maps to a named confusion. |
| Prerequisite network / stuck-detection tutor | Says it "tracks the concepts you've mastered and designs practice sets based on your progress"\[9\] | Frame it as a design exploration, a visual map of what a learner must know to derive one result. Don't frame it as a product. |
| Duolingo-like feel, project/goal-based | Streaks and leaderboards, plus a ten-week "Game Feel" North Star project with the agency ustwo | Note the alignment. Don't claim it as differentiation. |
| Learner-type options (hands-on vs. "auditory") | Brilliant is hands-on-first | Be careful: Pashler, McDaniel, Rohrer & Bjork's 2008 review in *Psychological Science in the Public Interest* found "no adequate evidence base to justify incorporating learning-styles assessments into general educational practice." Reframe as *multiple representations* (manipulative, verbal-precise, symbolic) that every learner moves through. This shows research literacy. |
| 5-levels-of-expertise explanation | Not a Brilliant format (it's text-heavy) | Good as a *writing* sample. Keep it secondary to interactive pieces. |
| Subscription CAD-like simulator product | Out of scope for this role | Leave it off the application. Mention it only as a long-term interest. |

### 3. Programmatic animation and interactive-math tools

The key distinction for Brilliant is **interactive (the learner manipulates it) versus rendered video (the learner watches it)**. Brilliant's product is the former, so weight your stack toward browser-interactive libraries. Use Manim-style video only for short "reveal" moments.

**Comparison table: key repos and tools**

| Tool / repo | What it is | License / status (as checked) | Learning curve | Best fit for your artifacts |
|---|---|---|---|---|
| **3b1b/manim (ManimGL)** | Grant Sanderson's original engine, OpenGL renderer; `pip install manimgl`\[10\] | MIT; actively used by 3Blue1Brown, less documented and less stable across versions | Medium–high | Only if you want to copy 3b1b scene code. Not recommended as your primary tool. |
| **ManimCommunity/manim (ManimCE)** | Community fork; `pip install manim`; docs at v0.21.0\[11\] | MIT; the community recommends it "for its continued development, improved features, enhanced documentation"\[12\] | Medium (Python + LaTeX + FFmpeg setup) | Integration-by-parts step animation, Fourier partial-sum video, short reveal clips |
| **maloyan/manim-web** | TypeScript port of Manim running in-browser via Three.js/WebGL, with React/Vue components and a `py2ts` converter\[13\]\[14\] | Open source; newer and less battle-tested (HN users reported text flicker in some demos)\[15\] | Low–medium if you know JS | Manim-style animation that is *also* clickable/draggable and embeddable in your site |
| **stevenpetryk/mafs** | "Opinionated React components for creating math visualizations": movable points, plots, vector fields\[16\] | MIT; ~3.4k stars; v0.21.0\[16\]\[17\] | Low (React) | Fourier knobs, curve-fitting, tangent/derivative problems, optimization in 2D |
| **JSXGraph** | Cross-browser JS library for interactive geometry, function plotting, charting\[18\] | Open source (verify current license terms on its site) | Low–medium | Geometry constructions, sliders, drag-to-answer problems; widely used in Moodle/STACK-style exercises |
| **motion-canvas/motion-canvas** | TypeScript library + real-time editor for programmatic vector animations synced to voice-over\[19\] | MIT; ~19k stars\[19\] | Medium | Polished explainer clips if you want a JS alternative to Manim |
| **Remotion** | Make videos programmatically in React | Source-available; companies above a size threshold need a paid licence (check its terms) | Medium | Turning React visuals into MP4 for social posts. Low priority for this application. |
| **Three.js / React Three Fiber** | WebGL 3D with orbit/pan/zoom controls | MIT | Medium | Optimization surfaces (z = f(x, y)) with gradient-descent path, CAD-like orbit views |
| **Plotly.js** | Interactive charts including 3D surfaces with built-in rotate/zoom | MIT | Low | Fastest way to get an orbitable surface plot for the optimization artifact |
| **p5.js** | Creative-coding canvas library | Open source (LGPL) | Low | Quick sketches, mixing/pouring simulations (iced-tea problem) |
| **D3 / Observable** | Data-driven SVG; notebook platform | Open source | Medium–high | Prerequisite-graph visualization (force-directed layout) |
| **GeoGebra / Desmos API** | Mature hosted math apps with embeddable applets and APIs | Free for non-commercial use with terms; Desmos API requires a key (verify current terms) | Low | Rapid prototyping. But a portfolio built on custom code shows more design control. |
| **Jupyter + ipywidgets** | Notebook sliders and widgets | BSD | Low | Brilliant's form explicitly accepts "jupyter notebooks".\[6\] Good for a derivation-heavy sample. |

**The LLM-to-Manim ecosystem (useful, but treat it as scaffolding):**

- **marcelo-earth/generative-manim:** "a suite of tools that allows you to create videos with Manim using LLMs." Updated September 2026. Its README makes the key point: "Manim is a deterministic verifier: code either renders or crashes."\[20\]\[21\] Note that *rendering* is not the same as *mathematically correct*.
- **HarleyCoops/Math-To-Manim** (~2.7k stars): multi-agent pipeline that turns a question into a math dossier, a shot list, and a Manim scene.\[22\]
- **Wing900/ManimCat, ashishjha-96/manim-gpt, VirajAnand-02/manimate_uni:** text-to-Manim web apps with automatic error-correction loops and TTS narration.\[21\]\[23\]\[24\]
- **SuienS/manim-trainer:** research toolkit for fine-tuning LLMs (SFT + GRPO) to write Manim code.\[25\]
- **MCP servers:** **abhiemj/manim-mcp-server** (~644 stars, MIT, listed in Awesome MCP Servers) lets Claude Desktop execute Manim scripts and return the rendered video.\[26\] **paulnegz/manim-mcp** uses ManimGL with 3,140 3b1b scene examples as retrieval context.\[27\]
- **Academic:** *Manimator* (arXiv 2507.14306) uses a two-stage pipeline in which an LLM writes a scene description and a code LLM writes Manim.\[28\]

**Recommendation:** you don't need these pipelines. Claude (in chat or Claude Code) writes Manim and Mafs code directly. The MCP server is worth installing only if you want Claude to render and look at its own output in a loop. In every case *you* check the math frame by frame. That checking is the "learning designer" skill Brilliant hires for.

### 4. Diffusion and generative video: an honest assessment

**Open models:**

- **Wan 2.2** (Wan-Video/Wan2.2) is the clearest fully open option. It is Apache 2.0, released July 28, 2025, with A14B mixture-of-experts text-to-video and image-to-video models and a 5B hybrid model that runs on a single 24 GB GPU.\[29\] It has native ComfyUI support.\[30\]
- Other open-weight families (HunyuanVideo, CogVideoX, LTX-Video, Stable Video Diffusion, AnimateDiff) run through **ComfyUI**, but their licences vary. Read each model card before any public use.

**Commercial:** **Higgsfield** is an aggregator ("15+" or "30+" models depending on the page, including Veo 3.1, Kling 3.0, Seedance 2.0, and Wan 2.6) with credit-based plans.\[31\]\[32\] Its own blog lists Starter at US$15/mo, Plus at US$49/mo, and Ultra at US$129/mo.\[33\]\[34\] Third-party reviews give conflicting tier prices,\[35\] so check the live pricing page. Reviewers estimate several dollars per *usable* premium clip after 3–5 retries.\[32\]\[36\]\[37\]\[38\]

**Can diffusion produce mathematically accurate animations? Not reliably. Evidence:**

- **Physion-Eval (arXiv 2603.19607, 2026):** "83.3% of exocentric and 93.5% of egocentric videos generated by leading video generation models contain at least one human-identifiable violation of contact, force, timing, or causality."\[4\]\[39\]
- **V-ReasonBench (arXiv 2511.16668):** documents "temporal hallucination." Models produce a correct final frame "while following an incorrect reasoning process," with physically inconsistent intermediate frames.\[40\]\[41\] That is fatal for a step-by-step derivation like integration by parts.
- **MMGR benchmark (arXiv 2512.14691):** on maze tasks Wan-2.2 scored 0.83%–5.00% and treated walls "as visual suggestions rather than impermeable boundaries." Even Veo-3 "cheats" by clipping through walls.\[42\]
- **VideoScience-Bench (arXiv 2512.02942):** current models "still struggle with following instructions and adhering to physical laws" on undergraduate-level science.\[43\]

**Verdict and hybrid workflow:** never let a diffusion model draw an axis, an equation, a waveform, or a quantity you're asking the learner to reason about. Acceptable uses:

1. A 3-second stylized intro or illustration (a kitchen scene for the iced-tea problem).
2. Background texture.
3. Mood boards.

All math-bearing visuals should come from code: Manim, Mafs, Three.js. For a Brilliant application in particular, a Higgsfield clip could backfire. It signals "watch" rather than "do," and reviewers will be alert to AI visuals that only look plausible. Brilliant itself stresses that "a single wrong problem can shake a learner's confidence."\[3\] **Drop Higgsfield from the core workflow.** Use Claude to write code, and verify that code yourself.

### 5. Learning, tutoring, and problem-generation repos

| Repo / tool | What it does | Relevance to your ideas |
|---|---|---|
| **Khan/perseus** | Khan Academy's exercise editor and renderer (TypeScript, MIT, ~1.6k stars, releases as recent as Oct 1, 2026)\[44\]\[45\]\[46\]\[47\] | Best reference for *exercise widget types* and grading schemas: sorters, number lines, interactive graphs. Study it; don't embed it. It's heavy. |
| **CAHLR/pyBKT** | Bayesian Knowledge Tracing in Python (MIT; Badrinath, Wang & Pardos, EDM 2021); `pip install pyBKT`\[48\]\[49\] | The "detect where the learner is stuck" engine. It estimates per-skill mastery from correct/incorrect sequences.\[48\] |
| **pyKT** | Toolkit bundling deep KT models (DKT, DKVMN, SAKT, AKT…)\[50\] | Research benchmarking. Overkill for a portfolio. |
| **cortex-js/compute-engine + arnog/mathlive** | MIT. MathLive is a math-input web component ("over 800 built-in LaTeX commands," virtual keyboards). Compute Engine parses LaTeX to MathJSON and simplifies/evaluates\[51\]\[52\] | Free-response answer checking in the browser: test whether a learner's expression is *equivalent* to the target, not just string-identical. |
| **SymPy / Math.js** | Python CAS; JS math library | Generate problem variants and verify answers (e.g., check that the integration-by-parts result differentiates back to the integrand). |
| **PreTeXt, Runestone, Open edX** | Interactive textbook and course platforms | Not needed for a portfolio. Mention them only if you discuss scaling. |
| **Mathigon (open-source TS libraries)** | Libraries for interactive courses and virtual manipulatives\[18\] | Good design inspiration for "explorable" sequencing. |

**For "mass-generate problems that isolate one step":** write a small Python/SymPy generator. Take a template such as ∫x·e^{ax}dx, pick parameters, compute each intermediate step symbolically, then emit one item per step and format: "which u?", "fill in du", "find the error in line 3". Output JSON that your front end renders. This mirrors Brilliant's described variant pipeline, and you can show 10 generated items next to the generator. Be explicit that you hand-reviewed them.

**For the prereq network:** a hand-authored JSON graph (≈15–25 nodes for one Calculus I derivation, e.g. "derivative of sin x from first principles") rendered with D3 force layout or React Flow. Clicking a node opens a 30-second check question. Optionally drive node colouring with a toy BKT update rule written in JS. The pyBKT parameters (prior, learn, guess, slip) are easy to hand-code.\[49\] Keep the claims modest: "a design sketch of prerequisite-aware remediation."

### 6. Tech stack, repo structure, and Claude Code workflow

**Recommended stack:**

- **Vite + React + TypeScript** for the site. Each artifact is a route or standalone page.
- **Mafs** for 2D interactives, **Plotly or React Three Fiber** for 3D surfaces, **KaTeX** for typesetting, and **MathLive + Compute Engine** for free-response input.
- **ManimCE** (Python, local) for 1–2 short MP4/WebM reveals. Embed them with `<video>` tags.
- Host on **GitHub Pages**: free, and it ties your GitHub URL to the portfolio. Vercel, Netlify, and Cloudflare Pages are equally good. Pick one and don't over-engineer.

**Repo structure (one monorepo):**

```
oninspire/
  site/                 # Vite+React app (landing page + artifact routes)
    src/artifacts/fourier-square-wave/
    src/artifacts/iced-tea-cups/
    src/artifacts/ibp-find-the-error/
    src/artifacts/optimization-surface/
    src/artifacts/prereq-graph/
  generators/           # Python/SymPy problem-variant generators -> JSON
  manim/                # ManimCE scenes -> rendered webm into site/public/
  DESIGN_NOTES.md       # learning objective, misconceptions, sequencing rationale per artifact
  AI_USAGE.md           # what Claude wrote, what you designed and verified
```

**Claude Code workflow:**

- **Cloud sessions.** Anthropic launched Claude Code on the web as a research preview on October 20, 2025. It lets you "connect your GitHub repositories, describe what you need, and Claude handles the implementation," with automatic PR creation.\[53\]\[54\] The service is now called "cloud sessions." It is listed as generally available for Pro, Max, and Team plans.\[55\] There is "no separate compute charge," but usage shares your plan's rate limits.\[56\] You can start sessions at claude.ai/code, from mobile, or with `claude --cloud`, and pull one down locally with `claude --teleport`.\[56\]\[57\]
- **Spec first.** For each artifact, write a short spec in `DESIGN_NOTES.md` covering the learning objective, the 3–6 screen sequence, the misconceptions targeted, and the feedback text for each wrong answer. Then ask Claude Code to implement against it. This mirrors how Brilliant describes its own split between design and implementation.\[3\]
- **Parallel sessions.** Run one cloud session per artifact on separate branches. Review PRs locally.
- **Verification step.** Ask Claude to write unit tests that check the math. Examples: the Fourier partial sum at given points, the iced-tea concentration arithmetic, SymPy differentiation of each integration-by-parts answer. Add a `CLAUDE.md` rule: "never hard-code a numeric answer without a test."

### 7. Domain: OnInspire.life vs. username.github.io

- **Cost.** Porkbun currently lists **.life at US$29.35/yr regular (renewal) price, with a first-year sale of US$2.57**.\[58\] Budget roughly US$30 per year after year one. Cloudflare Registrar sells supported TLDs at cost (wholesale plus ICANN fee) with renewal equal to registration.\[59\]\[60\] Check whether .life is supported and compare in-cart. I did not verify whether "oninspire.life" is currently available.
- **Connecting to GitHub Pages.**
  1. Add the custom domain in the repo's Pages settings *before* changing DNS. GitHub warns that the reverse order risks domain takeover.\[61\]\[62\]
  2. Create four A records for the apex pointing to 185.199.108.153, .109.153, .110.153, and .111.153 (or an ALIAS/ANAME record pointing to username.github.io).\[63\]\[64\]
  3. Create a CNAME record for `www` pointing to `username.github.io`.\[65\]\[66\]
  4. Verify the domain and enable "Enforce HTTPS."\[63\]
- **What to prioritize.** The domain matters far less than the artifacts. A reviewer clicking a Lever link will spend about two minutes. Use **username.github.io immediately** so you're never blocked, and point OnInspire.life at it once it's live. One consideration: "OnInspire" reads as a personal brand or startup. On a Brilliant application, label the site plainly, e.g. "[Your Name] — Interactive Math Learning Designs." This keeps the reviewer from wondering whether you're pitching a competing product.

### 8. Outreach strategy: build first, then reach out (and apply at the same time)

**Why build first:** Brilliant's posting makes samples the gate, and its careers page says it "often hire[s] for roles that aren't formally listed and meet people early."\[8\] A message with a link to a finished, playable artifact lets a Brilliant employee judge your taste in 60 seconds and forward you easily. A "can I pick your brain about what to build?" message costs them time and gives them nothing to forward.

**Evidence and best practice:**

- LinkedIn's Talent Blog reports that the shortest InMails (under 400 characters) get response rates 22% above average, yet only 10% of InMails are that short. Response rates fall below average from 800 characters (−6%) and are worst above 1,200 characters (−11%). Personalized messages see up to 40% higher acceptance. Most replies come within a week (90%). Caveat: this is recruiter-to-candidate data.
- Referrals matter. Greenhouse data cited by LinkedIn News gives referred candidates a 1-in-25 hire chance versus 1-in-200 for external applicants.\[5\] Peer-reviewed work (Brown, Setren & Topa, "Do Informal Referrals Lead to Better Matches?", *Journal of Labor Economics* 34(1), 2016) finds referred candidates "are more likely to be hired" and "have longer tenure in the firm."
- Career offices (UC Berkeley, UC Davis) consistently advise: ask for information or advice, not a job.\[67\]\[68\]

**Glassdoor signals on Brilliant's content hiring.** These are anonymous, small-sample, and indicative only. Reports for Producer-titled content roles (an earlier name for learning-design work) describe a ~30-minute intro call, then a **take-home task**, then a hiring-manager round. The process takes about 2 weeks. One report says the take-home "was also compensated."\[69\]\[70\] Expect to design a lesson or problem on short notice. Your portfolio is your rehearsal.

**Recommended sequencing (timed to graduation, presumably spring 2027):**

1. **Weeks 1–2:** ship 2–3 artifacts plus the landing page.
2. **Week 3:** submit the Lever application. Use both "website link" slots for your two best artifacts and the PDF slot for a one-page design-rationale doc. In the same week, send 3–5 LinkedIn notes, prioritizing current or former **learning designers / content** people over recruiters.
3. **Follow up once** after 7–10 days, with something *new*: a revised artifact based on their feedback, or a fresh one.
4. **Then go quiet** until you have a meaningful update. One more artifact every 3–4 weeks gives you a natural reason to re-engage. Apply now even though you graduate later. Content-role processes are short, and you can state your availability date plainly. If the role closes, the careers page invites "future interest" applications.\[8\]

**Sample messages (each under ~400 characters):**

*A. Learning designer, feedback ask:*
> Hi [Name] — I'm a McGill mech-eng grad (TA for 3 terms) applying for Math Learning Designer. I built a Brilliant-style problem where you build a square wave from 3 sine knobs: [link]. If you have 2 minutes, I'd love one note on what you'd change in the sequencing. No worries if not — thanks for the Mario post, it reframed how I design feedback.

*B. Someone whose course you admire:*
> Hi [Name] — your Visual Algebra lessons shaped how I approached a "two cups, four 250 mL marks" mixing problem I prototyped: [link]. I'm applying for the Math Learning Designer role and would value one blunt reaction: does the first screen ask the right question?

*C. Follow-up (7–10 days later, only with something new):*
> Hi [Name] — quick follow-up: I reworked the square-wave problem based on what I learned from playtesting with 5 students (wrong-answer feedback now targets the "more terms = taller" misconception): [link]. Applied via Lever last week. Thanks either way!

**Risks and how to manage them:**

- **Overbuilding.** A platform, tutor, or subscription product reads as unfocused. Three sharp problems beat ten half-done ideas.
- **Seeming generic.** Every artifact should have a one-paragraph rationale naming the misconception it targets. That is the learning-designer signal.
- **AI transparency.** Brilliant openly uses AI for implementation and is hiring for exactly that workflow; the CS Learning Designer posting even asks for candidates who have "used AI agents extensively."\[71\] So be *proud and precise*. Each artifact page should say: "Design, sequencing, misconceptions, feedback wording, and math verification: me. Implementation: written with Claude Code; all math checked by unit tests." Never present an unverified AI visual as your work.
- **Overclaiming your scores.** Mention the 144/150 Waterloo result in passing, or not at all. Three semesters of TA work and evidence of student playtesting are far more relevant.

## Recommendations: Prioritized, Time-Boxed Action Plan (ranked by impact for a Brilliant application)

**Week 1: core artifacts (highest impact)**

1. **Fourier square-wave builder (Mafs + KaTeX).** Learners drag amplitude and frequency knobs for 3 sinusoids to match a target square wave. Sequence:
   - Match a single sine.
   - Discover that only odd harmonics help.
   - Discover the 1/n amplitude pattern.
   - Predict what a 4th term does.
   Add misconception feedback (e.g., "adding even harmonics breaks the symmetry; look at t = 0"). Optional: a 10-second ManimCE reveal of the partial sums converging, including the Gibbs overshoot. This is the most "Brilliant-like" piece and shows calculus/analysis depth.
2. **Two-cup iced-tea problem (React + p5.js or SVG).** Two cups, each with four 250 mL markings. Learners pour powder and water by dragging to hit a target concentration. Escalate from "make it half as strong" to "you only have these cups — can you make 1:3?" This shows foundational, everyday-context design, which is most of Brilliant's catalogue, and it's quick to build.
3. **Landing page.** One sentence of positioning, three artifact cards (GIF thumbnail, one-line learning objective), a "How I design" paragraph, and the AI-usage note. Suggested headline: *"Interactive problems that make you discover the idea before you're told it."* Sub-line: *"I'm [Name], a McGill mechanical engineering grad and three-term TA. Each piece below targets one misconception, in a few screens, with feedback for every wrong answer."*

**Week 2: depth and differentiation**

4. **Integration by parts as a "find the error" / single-step set.** A SymPy generator produces 8–10 items, each isolating one step (choose u, compute du, assemble uv − ∫v du, spot the sign error). Add a ManimCE animation of the tabular/LIATE flow. This directly demonstrates your "one step, test intuition not algebra" thesis.
5. **Playtest with 5–10 students** (your TA network). Record one change you made per artifact in `DESIGN_NOTES.md`. This is cheap and highly differentiating evidence of learning-design practice.

**Week 3: apply and reach out**

6. Submit through Lever:
   - Portfolio URL.
   - GitHub URL.
   - Two artifact links in the sample slots.
   - A one-page PDF titled "Design notes: Fourier square wave."
   - A "Why Brilliant" note that cites the problem-first method and the Mario/feedback philosophy in your own words, ties it to your TA experience, and states your availability date.
7. Send 3–5 LinkedIn notes (templates above). Log them and follow up once.

**Later (only after the above ships):**

8. Optimization surface (Plotly or React Three Fiber, orbitable). Learner predicts where gradient descent goes, then watches.
9. Prereq-graph sketch (D3), framed as exploration.
10. "Five levels of expertise" written piece, as a writing sample.
11. A clarifying-question diagnostic flow.
12. A CAD-like environment or subscription idea: park it. It's a startup, not a portfolio piece.

## Caveats

- GitHub star counts and versions are approximate snapshots, as of searches in late September/early October 2026. Licence notes for JSXGraph, GeoGebra, Desmos, and Remotion are from general knowledge. Verify them on the official sites before relying on them.
- Higgsfield pricing differs across sources, including Higgsfield's own blog versus third-party reviews.\[36\]\[72\] Check the live page.
- Glassdoor interview reports are anonymous and few. None explicitly describe a Math Learning Designer take-home.
- The LinkedIn response-rate data comes from recruiter outreach, not job-seeker outreach. Referral hire-odds figures come from vendor data (Greenhouse) and one peer-reviewed study.
- I could not verify the availability of OnInspire.life or whether Brilliant's "Remote" covers Canada-based hires. Ask the recruiter directly.
- The "Claude Code cloud sessions are GA" status comes from Anthropic's updated blog and docs. The exact GA date could not be confirmed.

## Sources

1. [Brilliant - Math Learning Designer](https://jobs.lever.co/brilliant/b0b97281-179b-4b47-b5d6-a0cfaad3f425)
2. [A Brilliant brand refresh. A collaboration between Koto and our…](https://pcho.medium.com/a-brilliant-brand-refresh-4af021c11486)
3. [Hand-crafted, machine-made: How we make learning games with AI](https://blog.brilliant.org/hand-crafted-machine-made/)
4. [Physion-Eval: Evaluating Physical Realism in Generated Video via Human Reasoning](https://arxiv.org/html/2603.19607v1)
5. [Refer a stranger, collect cash](https://www.linkedin.com/news/story/refer-a-stranger-collect-cash-6483649/)
6. [Brilliant - Math Learning Designer](https://jobs.lever.co/brilliant/b0b97281-179b-4b47-b5d6-a0cfaad3f425/apply)
7. [About](https://brilliant.org/about/)
8. [Careers](https://brilliant.org/careers/)
9. [Brilliant](https://brilliant.org/math/)
10. [pypi.org](https://pypi.org/project/manimgl/1.7.0)
11. [FAQ: Installation - Manim Community v0.21.0](https://docs.manim.community/en/stable/faq/installation.html)
12. [GitHub - ManimCommunity/manim: A community-maintained Python framework for creating mathematical animations. · GitHub](https://github.com/ManimCommunity/manim)
13. [Introduction](https://maloyan.github.io/manim-web/)
14. [maloyan/manim-web](https://deepwiki.com/maloyan/manim-web)
15. [Show HN: I ported Manim to TypeScript (run 3b1B math animations in the browser)](https://news.ycombinator.com/item?id=47155375)
16. [GitHub - stevenpetryk/mafs: React components for interactive math · GitHub](https://github.com/stevenpetryk/mafs)
17. [mafs/package.json at main · stevenpetryk/mafs](https://github.com/stevenpetryk/mafs/blob/main/package.json)
18. [GitHub - ubavic/awesome-interactive-math: A curated list of tools that can be used for creating interactive mathematical explorables. · GitHub](https://github.com/ubavic/awesome-interactive-math)
19. [GitHub - motion-canvas/motion-canvas: Visualize Your Ideas With Code · GitHub](https://github.com/motion-canvas/motion-canvas)
20. [GitHub - marcelo-earth/generative-manim: 🎨 GPT for video generation ⚡️](https://github.com/marcelo-earth/generative-manim)
21. [manim · GitHub Topics · GitHub](https://github.com/topics/manim)
22. [GitHub - HarleyCoops/Math-To-Manim: Create Epic Math and Physics Animations & Study Notes From Text and Images. · GitHub](https://github.com/HarleyCoops/Math-To-Manim)
23. [GitHub - VirajAnand-02/manimate\_uni: edu vid generation using LLM and manim · GitHub](https://github.com/VirajAnand-02/manimate_uni)
24. [GitHub - ashishjha-96/manim-gpt: AI-Powered Manim Video Generation - Transform text prompts into stunning mathematical animations using LLM-powered code generation. · GitHub](https://github.com/ashishjha-96/manim-gpt)
25. [GitHub - SuienS/manim-trainer: A toolkit for fine-tuning Large Language Models (LLMs) to generate Manim animation code using Supervised Fine-Tuning (SFT) and Visually Grounded Reinforcement Learning using Group Relative Policy Optimisation (GRPO/GSPO) techniques. · GitHub](https://github.com/SuienS/manim-trainer)
26. [GitHub - abhiemj/manim-mcp-server · GitHub](https://github.com/abhiemj/manim-mcp-server)
27. [GitHub - paulnegz/manim-mcp: Text-to-video animation via Manim. Text → Code → Video. CLI, agent mode, and MCP server](https://github.com/paulnegz/manim-mcp)
28. [Manimator: Transforming Research Papers and Mathematical Concepts into Visual Explanations](https://arxiv.org/html/2507.14306v1)
29. [Wan 2.2 Local Video Generation: 720p on a Single 24GB GPU](https://localaimaster.com/blog/wan-video-generation-guide)
30. [wan 2 2](https://www.mindstudio.ai/models/wan-2-2)
31. [The 6 Best AI Video Generators in 2026: Top Tools Tested and Compared](https://higgsfield.ai/blog/best-ai-video-generators-2026)
32. [Credits vs Unlimited Plans for AI Video Generation in 2026: Pricing and Services Explained](https://higgsfield.ai/blog/credits-vs-unlimited-ai-video-generation)
33. [8 Best Unlimited AI Video Generators in 2026: Plans and Costs Compared](https://higgsfield.ai/blog/best-unlimited-ai-video-generators)
34. [Higgsfield AI Pricing 2026 — Real Plans, Credits & Cost Per Veo 3 Video](https://www.vo3ai.com/higgsfield-ai-pricing)
35. [Higgsfield Pricing: How Much Does It Cost in 2026? - Luma AI](https://lumalabs.ai/news/higgsfield-pricing)
36. [Higgsfield AI Review 2026: Pricing, Credits, the Catch](https://aifunnelinsider.com/higgsfield-ai-review-2026/)
37. [Higgsfield AI Review 2026](https://fluxnote.io/guides/higgsfield-ai-review)
38. [Higgsfield AI Review 2026: Features, Quality and Verdict](https://aiforesight360.com/higgsfield-ai-review-2026/)
39. [Physion-Eval: Evaluating Physical Realism in Generated Video via Human Reasoning](https://www.alphaxiv.org/abs/2603.19607)
40. [V-ReasonBench: Toward Unified Reasoning Benchmark Suite for Video Generation Models](https://arxiv.org/html/2511.16668v1)
41. [V-ReasonBench: Toward Unified Reasoning Benchmark Suite for Video Generation Models](https://arxiv.org/pdf/2511.16668)
42. [MMGR: Multi-Modal Generative Reasoning Benchmark and Evaluation](https://arxiv.org/pdf/2512.14691)
43. [Benchmarking Scientific Understanding and Reasoning for Video Generation using VideoScience-Bench](https://arxiv.org/html/2512.02942)
44. [Repositories - Khan Academy](https://github.com/orgs/Khan/repositories)
45. [Release @khanacademy/perseus-core@39.2.0 · Khan/perseus](https://github.com/Khan/perseus/releases/tag/%40khanacademy/perseus-core%4039.2.0)
46. [Release @khanacademy/perseus-core@39.2.3 · Khan/perseus](https://github.com/Khan/perseus/releases/tag/%40khanacademy/perseus-core%4039.2.3)
47. [Release @khanacademy/perseus-core@40.1.0 · Khan/perseus](https://github.com/Khan/perseus/releases/tag/%40khanacademy/perseus-core%4040.1.0)
48. [GitHub - CAHLR/pyBKT: Python implementation of Bayesian Knowledge Tracing and extensions · GitHub](https://github.com/CAHLR/pyBKT)
49. [pyBKT: An Accessible Python Library of Bayesian Knowledge Tracing Models](https://educationaldatamining.org/EDM2021/virtual/static/pdf/EDM21_paper_237.pdf)
50. [Knowledge Tracing Blueprint — BKT, DKT, R, Python, and research use cases](https://educatian.github.io/knowledge-tracing/)
51. [@gotitinc/mathlive - npm](https://www.npmjs.com/package/@gotitinc/mathlive)
52. [compute engine](https://github.com/cortex-js/compute-engine)
53. [Claude Code comes to iOS and web as research preview - 9to5Mac](https://9to5mac.com/2025/10/20/claude-code-preview-ios-iphone/)
54. [Claude Code on the web](https://www.anthropic.com/news/claude-code-on-the-web)
55. [Claude Code on the web](https://claude.com/blog/claude-code-on-the-web)
56. [https://code.claude.com/docs/en/claude-code-on-the...](https://code.claude.com/docs/en/claude-code-on-the-web?f80ce999_sort_date=desc&fcdaa149_sort_date=desc)
57. [Use Claude Code in the cloud - Claude Code Docs](https://code.claude.com/docs/en/claude-code-on-the-web)
58. [porkbun.com](https://porkbun.com/products/domains)
59. [Best Domain Registrars in 2026](https://instantdomainsearch.com/learn/guides/best-domain-registrars-2026)
60. [Cheapest Domain Registrars 2026 — Real 5-Year Cost (Not Promo Prices)](https://domaindetails.com/registrars/cheapest)
61. [Managing a custom domain for your GitHub Pages site - GitHub Docs](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site)
62. [managing a custom domain for your github pages site](https://docs.github.com/en/enterprise-cloud@latest/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site)
63. [Custom domain github pages · community · Discussion #66102](https://github.com/orgs/community/discussions/66102)
64. [Using a custom domain name with your GitHub pages site](https://heardlibrary.github.io/digital-scholarship/manage/control/github/pages-urls/)
65. [Using a Custom Domain Name with GitHub Pages](https://medium.com/@isphinxs/using-a-custom-domain-name-with-github-pages-c9cdc2084d54)
66. [How to Setup a Custom Domain for GitHub Project Pages: Configuring A Records and CNAME for myexample.com & www — codegenes.net](https://www.codegenes.net/blog/custom-domain-for-github-project-pages/)
67. [Informational Interviews - Berkeley Career Engagement](https://career.berkeley.edu/start-exploring/informational-interviews/)
68. [Informational Interviewing](https://hr.ucdavis.edu/departments/learning/toolkits/career-dev/career-exploration/inform-interview)
69. [19 Brilliant.org Interview Questions & Answers (2025)](https://www.glassdoor.co.in/Interview/Brilliant-org-Interview-Questions-E825743.htm)
70. [21 Brilliant.org Interview Questions & Answers (2026)](https://www.glassdoor.ca/Interview/Brilliant-org-Interview-Questions-E825743.htm)
71. [CS Learning Designer - Brilliant.org](https://builtin.com/job/cs-producer/7862952)
72. [The Math on Higgsfield AI: Is \$110/Month Worth It? - Yangsweb](https://www.yangsweb.com/blog/higgsfield-ai-review-alternatives-pricing)
