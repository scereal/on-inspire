# Claude Skills, Plugins & Open Tooling for Writing, Coding, Apps, Websites, Animation and Teaching: A Field Guide (October 2026)

The best free starting kit as of October 2026 is Anthropic's official **anthropics/skills** repo (about 177k GitHub stars), **obra/superpowers** for disciplined agentic coding (about 294k stars), **Remotion's and Manim's agent skills** for animation, **kepano/obsidian-skills** plus the **MCP memory server** for idea networks, and Claude's built-in **artifacts + Learning mode/output styles** for teaching. Install them as plugins or folders in Claude Code, or as ZIP uploads in Claude.ai. Anything beyond that set is a long tail of community repos. Some are excellent, many are thin, and all of them should be vetted before you run them.

## TL;DR

- **Start with the official layer, then add one coding methodology and one domain pack.** That means `anthropics/skills` (17 skills, including frontend-design, web-artifacts-builder, algorithmic-art, skill-creator and the docx/pdf/pptx/xlsx engines), Anthropic's `claude-plugins-official` marketplace, `obra/superpowers` (or GitHub Spec Kit if you want a heavier spec process), and then domain packs such as `remotion-dev/skills`, a Manim skill, `vercel-labs/agent-skills`, or `kepano/obsidian-skills`.
- **Claude.ai and Claude Code link skills differently.** In Claude.ai you upload a zipped skill folder under Settings → Capabilities (code execution must be on). In Claude Code you drop folders into `~/.claude/skills/` or `.claude/skills/`, or run `/plugin marketplace add owner/repo` and then `/plugin install name@marketplace`. Because skills follow the open Agent Skills standard (agentskills.io, December 18, 2025), the same SKILL.md works in Codex, Cursor, Copilot, Gemini CLI and others.
- **For teaching and idea networks, build from evidence, not "learning styles."** Matching instruction to VAK-type styles lacks experimental support (Pashler et al., 2008). Use Claude to generate retrieval practice, spaced repetition (Anki skills), worked examples and interactive explorables (artifacts, Manim, D3, React Flow). Use Obsidian, the MCP memory knowledge graph, or InfraNodus to map concepts.

## Start Here: The Shortlist

| # | Pick | URL | Use it for | Where it runs |
|---|---|---|---|---|
| 1 | Anthropic Skills (official) | https://github.com/anthropics/skills | Artifacts, frontend design, generative art, docs, skill authoring | Claude.ai (built in on paid plans), Claude Code (plugin), API |
| 2 | Claude Code official plugin marketplace | https://github.com/anthropics/claude-plugins-official | Curated plugins (commands, agents, hooks, MCP, LSP) | Claude Code (auto-registered) |
| 3 | Superpowers | https://github.com/obra/superpowers | Brainstorm → plan → TDD → subagent build → verify | Claude Code, Codex, Cursor, Gemini CLI and others |
| 4 | Remotion Agent Skills | https://www.remotion.dev/docs/ai/skills | Video and motion graphics written as React code | Claude Code / any skills agent |
| 5 | A Manim skill (e.g., adithya-s-k/manim_skill) | https://github.com/adithya-s-k/manim_skill | 3Blue1Brown-style math and science animation | Claude Code |
| 6 | Vercel agent-skills + skills CLI | https://github.com/vercel-labs/agent-skills · https://www.skills.sh/ | React/Next.js best practices, web design guidelines; cross-agent installer | Claude Code and ~18 other agents |
| 7 | Obsidian Skills | https://github.com/kepano/obsidian-skills | Read/write Obsidian Markdown, Bases, JSON Canvas | Claude Code (plugin or npx) |
| 8 | Playwright MCP + Context7 MCP | https://github.com/microsoft/playwright-mcp · https://github.com/upstash/context7 | Browser testing/verification; current library docs | Claude Code, Claude Desktop |
| 9 | MCP Memory (knowledge graph) server | https://github.com/modelcontextprotocol/servers/tree/main/src/memory | Persistent entity–relation graph of your ideas | Claude Desktop, Claude Code |
| 10 | Claude's Learning mode + Claude Code "Learning" output style | https://code.claude.com/docs/en/output-styles | Socratic tutoring; learn-by-doing coding | Claude.ai, Claude Code |

If you install only three things, install `anthropics/skills`, `obra/superpowers`, and whichever domain pack fits your main project.

---

## Part 1 — Anthropic's Official Skills Ecosystem

### 1.1 What a skill actually is

A skill is a folder with a `SKILL.md` file. That file has YAML frontmatter (the required fields are `name` and `description`) followed by Markdown instructions.\[1\]\[2\] The folder can also hold optional scripts, references and assets.\[3\] Skills use **progressive disclosure**. Anthropic's platform docs say only the metadata, roughly 100 tokens per skill, is loaded at startup. The SKILL.md body (under about 5k tokens) loads when the skill is triggered, and bundled files and scripts load only as needed.\[4\] This is why you can keep dozens of skills installed without flooding the context window.\[5\] It is also why the `description` field decides whether a skill ever fires.\[6\]

Official docs to bookmark:
- Agent Skills overview (platform): https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview
- Skill authoring best practices: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices
- Claude Code skills reference: https://code.claude.com/docs/en/skills
- Help Center: "What are skills?", "Using skills in Claude", "How to create custom skills" (linked from the anthropics/skills README at support.claude.com)
- Engineering post: "Equipping agents for the real world with Agent Skills" (anthropic.com/engineering)

### 1.2 The `anthropics/skills` repository (verified October 2026)

- **URL:** https://github.com/anthropics/skills
- **Signals:** about 177.5k stars, about 21.0k forks, about 1.1k watchers, 355 open issues and 908 open PRs at time of fetch.\[1\] It is the most-starred skills repo and Anthropic's most-starred public repository, ahead of `claude-code` itself.\[7\]
- **Structure:** `skills/` (the skills themselves), `spec/` (Agent Skills specification), `template/` (starter skill), and `.claude-plugin/` (which makes the repo a plugin marketplace).\[1\]
- **Licensing:** The README says "many skills in this repo are open source (Apache 2.0)". The **docx, pdf, pptx and xlsx** skills are **source-available, not open source**. Anthropic shares them as reference implementations of the production skills behind Claude's file-creation features.\[1\] Read them, learn from them, but do not assume you may redistribute them.
- **Disclaimer:** Anthropic labels them "for demonstration and educational purposes only," and notes that the behaviour inside Claude may differ.\[1\]

**Skill inventory (17 top-level skills).** Multiple independent catalogues from July–October 2026 agree on this list, which matches the repo's marketplace manifest:\[8\]\[9\]\[10\]

| Group | Skill | What it does | Best for |
|---|---|---|---|
| Document (source-available) | `docx` | Create/edit Word files with tracked changes, comments, formatting\[11\] | Writing, reports |
| | `pdf` | Extract text, fill forms, create/merge PDFs | Research, handouts |
| | `pptx` | Build/edit PowerPoint decks | Lectures, pitches |
| | `xlsx` | Spreadsheets with formulas and formatting | Gradebooks, data |
| Creative & design | `algorithmic-art` | p5.js generative art with seeded randomness, flow fields, particles; writes an "algorithmic philosophy" then an interactive HTML viewer\[5\]\[9\] | Generative art, inspiration |
| | `canvas-design` | Poster/cover-quality visual art as PNG/PDF from a "design philosophy"\[5\] | Visual assets |
| | `frontend-design` | Pushes Claude away from generic "AI slop" UIs toward bold, distinctive, production-grade design\[5\]\[12\] | Whole websites, landing pages |
| | `theme-factory` | Apply or generate professional themes for artifacts/slides\[13\] | Consistent styling |
| | `brand-guidelines` | Applies Anthropic's brand colours and type (fork it for your own brand)\[13\] | Brand systems |
| | `slack-gif-creator` | Animated GIFs optimised for Slack's constraints | Small animations |
| Web & dev | `web-artifacts-builder` | Elaborate multi-component claude.ai HTML artifacts using React, Tailwind CSS and shadcn/ui, bundled into one file\[14\] | Artifacts, interactive teaching widgets |
| | `webapp-testing` | Playwright-based testing of local web apps (recon-then-act pattern)\[5\] | Builds, QA |
| | `mcp-builder` | Guide for building production-quality MCP servers | Connecting Claude to anything |
| | `claude-api` | Current Claude API/SDK reference (models, tool use, caching, agents)\[14\] | Building AI apps |
| Writing & comms | `doc-coauthoring` | Structured workflow for co-writing documents\[14\] | Long-form writing |
| | `internal-comms` | Status reports, newsletters, FAQs in house formats\[13\] | Business writing |
| Meta | `skill-creator` | Scaffold, test/evaluate and improve your own skills\[12\] | Making new skills |

**Partner skills:** The README highlights Notion's "Notion Skills for Claude".\[1\] Unite.ai (December 19, 2025) reported that "Partner-built skills from Canva, Stripe, Notion, and Zapier are available at launch," and The Decoder (December 18, 2025) noted that the partner directory lives at claude.com/connectors.

**Install:**
- *Claude Code:* `/plugin marketplace add anthropics/skills`, then `/plugin install document-skills@anthropic-agent-skills` and/or `/plugin install example-skills@anthropic-agent-skills`. You can also use `/plugin` → Browse and install plugins → `anthropic-agent-skills`.\[1\]
- *Claude.ai:* According to the README, "these example skills are all already available to paid plans in Claude.ai".\[1\] You toggle them in Settings, and custom ones are uploaded there too.
- *API:* Skills API quickstart at docs.claude.com (now platform.claude.com).\[1\]

### 1.3 The Agent Skills open standard

- **Spec:** https://agentskills.io/specification · **Repo:** https://github.com/agentskills/agentskills
- Anthropic released Skills on **October 16, 2025** and published them as an **open standard on December 18, 2025**.\[15\]\[16\] Simon Willison (weblog, December 19, 2025) called it "a deliciously tiny specification - you can read the entire thing in just a few minutes," while also describing it as "quite heavily under-specified."
- **Adoption:** Simon Willison noted on December 19, 2025 that "The Agent Skills homepage promotes adoption by OpenCode, Cursor, Amp, Letta, goose, GitHub, and VS Code," and his December 20 update added that OpenAI "added Skills to the Codex documentation"; Gemini CLI and others have since followed. VS Code's docs describe Agent Skills as "an open standard that works across multiple AI agents."\[17\]
- **Why it matters for you:** a skill you write for Claude Code is portable, so your writing-style skill or course-builder skill keeps working if you switch tools.\[18\]

### 1.4 Claude Code plugins and marketplaces

A **plugin** bundles skills, slash commands, subagents, hooks, MCP servers and LSP servers.\[19\] A **marketplace** is a catalogue, usually a Git repo with `.claude-plugin/marketplace.json`.\[20\]

- **Anthropic's official marketplace:** https://github.com/anthropics/claude-plugins-official (about 37k stars). Claude Code registers it automatically the first time you start an interactive session. Install with `/plugin install <name>@claude-plugins-official`. The docs' worked example is `commit-commands`.\[7\]\[19\] Language-server plugins such as `pyright-lsp` and `typescript-lsp` are listed there too.\[21\]
- **Web catalogue:** https://claude.com/marketplace. Its "Claude Code" button copies a `claude plugin install <name>@claude-plugins-official` command.\[19\]
- **Demo marketplace:** `anthropics/claude-code` registers as `claude-code-plugins` (e.g., `/plugin install commit-commands@claude-code-plugins`).\[22\] It includes the `learning-output-style` and `explanatory-output-style` plugins.\[23\]
- **Community marketplace:** A mirror of the docs references `anthropics/claude-plugins-community` (installs as `@claude-community`). The official "Install and manage plugins" page also mentions "Anthropic's community marketplace."\[19\]\[22\] Check the exact repo name in `/plugin` before relying on it.
- **Role-based plugins:** `anthropics/knowledge-work-plugins` is reported to contain about 11 role plugins (sales, support, PM, finance, data).\[24\] This comes from a secondary source, so verify it before use.

Key behaviours from the current docs (https://code.claude.com/docs/en/discover-plugins):
- `/plugin install x@y` opens a details pane before installing. It shows what "Will install" (commands, agents, skills, hooks, MCP/LSP servers) and, for official-marketplace plugins, a **context cost** estimate ("Every turn" and "When invoked").\[19\]
- There are three **scopes**: user (`~/.claude/settings.json`), project (`.claude/settings.json`, committed to the repo), and local (`.claude/settings.local.json`).\[19\]
- `/plugin install name --marketplace owner/repo` adds a marketplace and installs in one step (Claude Code v2.1.275+).\[19\]
- Plugins you enable on your **claude.ai account** sync into Claude Code as `<name>@synced`. Plugins installed locally do not sync back.\[19\]
- Cloud sessions (claude.ai/code) do not load your local plugins.\[19\]

---

## Part 2 — How to Install / Link Skills (Current Steps)

### 2.1 Claude.ai (web and Desktop app)

1. **Turn on code execution.** Settings → Capabilities → enable "Code execution and file creation."\[25\] Skills need the sandbox.
2. **Enable built-in skills.** In the Skills section of Capabilities, toggle Anthropic's example and document skills (paid plans).
3. **Upload a custom skill.** Zip the skill *folder* (the one containing `SKILL.md`), then choose Settings → Capabilities → Skills → "Upload skill" / "Add". Toggle it on.\[26\]\[27\]\[28\]
4. **Or have Claude make one.** Ask Claude to use `skill-creator`. It writes the SKILL.md, packages a `.skill`/.zip, and you upload that. You can later "Edit with Claude" from the same settings page.\[25\]
5. **Scope:** Uploaded skills are per-user on individual plans.\[24\] Since December 18, 2025, per The Decoder, "Administrators on Team and Enterprise plans can now manage skills from a central hub and push them to every user in their organization, though individuals still have the option to turn them off."
6. **Limits:** There are no hot reloads. To change a skill you re-upload the ZIP, and network access inside the sandbox depends on your admin settings.\[24\]\[27\]

Menu labels have shifted over time between "Capabilities" and "Features."\[24\] If you can't find the option, search Settings for "Skills."

### 2.2 Claude Code (terminal, desktop Code tab, VS Code, JetBrains)

**Option A: plain folders (no plugin needed).**
```bash
# Personal (all projects)
mkdir -p ~/.claude/skills/my-skill && $EDITOR ~/.claude/skills/my-skill/SKILL.md
# Project (commit to the repo so collaborators share it)
mkdir -p .claude/skills/my-skill
# Copy a community skill
git clone https://github.com/<owner>/<repo> /tmp/x && cp -r /tmp/x/<skill-folder> ~/.claude/skills/
```
The directory name (or the frontmatter `name`) becomes a slash command, e.g. `.claude/skills/deploy-staging/SKILL.md` → `/deploy-staging`. Claude also loads skills automatically when the description matches the task. Validate frontmatter with `claude plugin validate ~/.claude/skills`.\[29\]

**Option B: plugin marketplaces.**
```text
/plugin marketplace add anthropics/skills
/plugin install example-skills@anthropic-agent-skills
/plugin                      # browse Discover / Installed / Marketplaces / Errors tabs
/reload-plugins              # activate without restarting
```
From your shell: `claude plugin install <name>@<marketplace> --scope project`.\[19\]

**Option C: the cross-agent `skills` CLI (Vercel).**
```bash
npx skills find "browser testing"
npx skills add vercel-labs/agent-skills
npx skills add remotion-dev/skills
npx skills update
```
It detects the agents you have installed and writes files into each one's skills folder.\[30\] Vercel says it has installed to amp, antigravity, claude-code, codex, cursor, gemini-cli, github-copilot, goose, opencode, windsurf and more.\[31\]

**MCP servers** are added separately: `claude mcp add <name> -- <command>` (e.g., `claude mcp add playwright -- npx @playwright/mcp@latest`). Use `--scope user` to make one available everywhere.\[32\] They can also be bundled inside a plugin.

### 2.3 Other skill-like extension points (Claude Code)

- **CLAUDE.md** is project memory and rules, loaded every session. Keep it short and put procedures in skills.
- **Slash commands** are now unified with skills (a skill folder becomes `/name`).
- **Subagents** are specialised agents with their own context. Superpowers' "subagent-driven development" relies on them.
- **Hooks** run shell commands on events (pre-tool-use, etc.). They are powerful, and they are also the main attack surface (see Safety).
- **Output styles** change *how* Claude talks. The built-ins include Explanatory and Learning (Part 6).

---

## Part 3 — Community Collections, Directories and Registries

| Resource | URL | What it is | Signals (approx., Oct 2026) | Verdict |
|---|---|---|---|---|
| obra/superpowers | https://github.com/obra/superpowers | Full dev methodology as about 14 composable skills\[33\] | ~294k stars, ~26k forks, MIT; #1 trending Jan 14, 2026\[34\]\[35\] | Essential for coding |
| hesreallyhim/awesome-claude-code | https://github.com/hesreallyhim/awesome-claude-code | Hand-curated list: skills, hooks, slash commands, agents, CLAUDE.md files, status lines, plugins | ~55k stars, ~4.8k forks, ~1,945 commits\[36\] | Best curated Claude Code index |
| ComposioHQ/awesome-claude-skills | https://github.com/ComposioHQ/awesome-claude-skills | "1000+" skills and plugins list, plus Composio app-connection plugin\[16\] | ~76k stars, ~8.9k forks\[16\] | Broad, but vendor-promotional |
| travisvn/awesome-claude-skills | https://github.com/travisvn/awesome-claude-skills | Tighter curated skills list with a good explainer | ~15k stars, ~2k forks\[5\] | Good, readable |
| heilcheng/awesome-agent-skills | https://github.com/heilcheng/awesome-agent-skills | Cross-agent skills list and tutorials\[13\] | n/a | Useful secondary |
| skills.sh (Vercel) | https://www.skills.sh/ | Directory and install leaderboard tied to `npx skills` | Top skills include find-skills, mattpocock's grill-me, vercel web-design-guidelines\[37\] | Best discovery-by-popularity |
| SkillsMP | https://skillsmp.com | Aggregated catalogue of GitHub skills with refresh dates | Indexes e.g. 14 skills from superpowers\[33\] | Handy search; not curated |
| punkpeye/awesome-mcp-servers | https://github.com/punkpeye/awesome-mcp-servers | Largest MCP server list | High | For MCP discovery |

Other aggregators exist (claudemarketplaces.com, mcpmarket.com, agentskill.sh, skillsllm.com, claudewave.com, awesomeclaude.ai). They are useful for search, but they scrape GitHub, inflate "installs," and sometimes carry stale star counts. **Always click through to the GitHub source.** Treat `affaan-m/everything-claude-code` (reported at about 141k stars by one secondary source) as a firehose and not as a curated list.\[38\] I did not verify it directly.

**Star counts are noisy.** The figures in this guide disagree across sources taken a few weeks apart (superpowers shows 154k, 211k, 277k and 294k in different snapshots).\[33\]\[34\]\[39\]\[40\] Use them for order of magnitude only.

---

## Part 4 — By Category

### 4.1 Writing

| Resource | URL | What/why | Link into |
|---|---|---|---|
| `doc-coauthoring` (official) | anthropics/skills | Structured co-writing workflow (context → draft → reader-test)\[8\] | Claude.ai toggle; Claude Code plugin |
| `internal-comms` (official) | anthropics/skills | Status updates, newsletters, FAQs\[13\] | Same |
| `docx` / `pdf` / `pptx` (official) | anthropics/skills | Real Office/PDF output for manuscripts, handouts, decks\[41\] | Same |
| The Elements of Style | https://github.com/obra/the-elements-of-style | Strunk's 1918 text as a `writing-clearly-and-concisely` skill; about 12k-token reference loaded only while editing; ships as a plugin\[42\] | Claude Code plugin; zip the skill folder for Claude.ai |
| "Humanizer"-type skills | e.g., listings on mcpmarket.com | Strip AI tells (hedging, significance inflation) using Wikipedia's AI-writing signs plus Strunk\[43\] | Low-star; vet first |
| Claude.ai Styles (built-in) | https://www.anthropic.com/news/styles | Preset Formal/Concise/Explanatory plus custom styles trained on your writing samples\[44\]\[45\] | Claude.ai only |

**Recommendation:** For voice, build your *own* style skill with `skill-creator`. Feed it 3–5 of your best pieces and a list of banned phrases. This beats generic "humanizer" skills, which are mostly thin prompt wrappers aimed at evading AI detectors. Pair it with the Elements of Style skill for edits, and use `doc-coauthoring` for long-form work.

### 4.2 Coding

| Resource | URL | What/why | Signals |
|---|---|---|---|
| **Superpowers** | https://github.com/obra/superpowers | Starts by asking what you are really building, writes a spec in digestible chunks, plans, then executes with subagents under TDD. Skills include `brainstorming`, `systematic-debugging` (4-phase root cause), `verification-before-completion`, `writing-skills`, `using-superpowers`, `diagnosing-superpowers`\[33\]\[34\] | ~294k stars, MIT, active (7 pushes/week in late Sept 2026)\[34\]\[35\] |
| superpowers-developing-for-claude-code | https://github.com/obra/superpowers-developing-for-claude-code | Skills and docs for building plugins, skills, MCP servers and hooks\[46\] | ~142 stars\[46\] |
| superpowers-skills (archived) | https://github.com/obra/superpowers-skills | Old community repo, **archived Oct 27, 2025**; don't install\[47\] | Read-only |
| GitHub Spec Kit | https://github.com/github/spec-kit | Spec-driven development: `specify init` → `/speckit.specify` → `/speckit.plan` → `/speckit.tasks` → `/speckit.implement`; constitution file; 30+ agents\[48\]\[49\] | ~126k stars (Aug 2026), MIT\[50\] |
| BMAD-METHOD | https://github.com/bmad-code-org/BMAD-METHOD | Simulated agile team (Analyst, PM, Architect, UX, SM, Dev, QA personas);\[51\] `npx bmad-method install`; v6\[50\]\[52\] | ~49–52k stars, MIT\[48\]\[53\]\[54\] |
| OpenSpec | https://github.com/Fission-AI/OpenSpec | Lightweight "delta specs" for brownfield code; `/opsx:*` commands\[50\]\[53\] | ~52k stars (mid-2026)\[53\] |
| mattpocock/skills | via https://www.skills.sh/ | `grill-me`, `grill-with-docs`, `diagnosing-bugs` (top of the skills.sh leaderboard)\[37\] | High installs |
| `webapp-testing`, `mcp-builder`, `claude-api` | anthropics/skills | Official testing, MCP and API skills | Official |
| LSP plugins | claude-plugins-official | `pyright-lsp`, `typescript-lsp` for real code intelligence\[21\] | Official |

**How to choose a spec framework.** Independent comparisons in 2026 broadly agree:
- **Superpowers or OpenSpec** are the lightest and cheapest in tokens.\[53\]
- **Spec Kit** is the "safe default for a scaling team."\[53\]
- **BMAD** is the heaviest and most expensive, but the strongest at iterative refinement.\[49\]\[53\]
- One hands-on evaluation (ranthebuilder.cloud) scored **OpenSpec highest overall** on a brownfield serverless backend, and noted that the ranking shifts with your priorities.\[49\]\[55\]
- My recommendation for a solo builder is **Superpowers by default**, with Spec Kit if you need artefacts other people will review.

### 4.3 Building apps

| Resource | URL | Use |
|---|---|---|
| vercel-labs/agent-skills | https://github.com/vercel-labs/agent-skills | 16 skills including `vercel-react-best-practices` (about 70 React/Next.js performance rules), `vercel-composition-patterns`, `vercel-react-native-skills`, `web-design-guidelines`, and a deploy skill\[12\]\[56\] |
| `claude-api` (official) | anthropics/skills | Build apps on Claude correctly (models, tool use, caching, Agent SDK)\[57\] |
| `mcp-builder` (official) | anthropics/skills | Give your app or Claude new tools via MCP\[13\] |
| Context7 MCP | https://github.com/upstash/context7 | Pulls *current* library docs at query time to cut API hallucinations; `claude mcp add context7 -- npx -y @upstash/context7-mcp` (or HTTP transport `https://mcp.context7.com/mcp`) \[58\]\[59\] |
| GitHub MCP (official hosted) | GitHub's MCP server | Issues, PRs, Actions, code search. Note that it exposes dozens of tools and so has a high context cost; many teams just let Claude use the `gh` CLI\[59\]\[60\] |
| Claude Agent SDK | platform.claude.com docs | Build your own agents; it can load plugins via the SDK's plugin option\[19\] |
| Spec Kit / BMAD / Superpowers | above | Orchestration for full builds |

**Agentic build loop that works in practice:**
1. Brainstorm and spec with Superpowers `brainstorming` or `/speckit.specify`.
2. Plan.
3. Run subagent TDD.
4. Verify in a real browser with Playwright MCP or `webapp-testing`.
5. Let `verification-before-completion` block "done" claims until the tests have actually run.
6. Commit/PR with `commit-commands`.

### 4.4 Building entire websites

| Resource | URL | Use |
|---|---|---|
| `frontend-design` (official) | anthropics/skills (also an official plugin) | Distinctive typography, layout and motion; explicitly anti-"AI slop"\[11\]\[12\] |
| `web-design-guidelines` (Vercel) | vercel-labs/agent-skills | Web interface review checklist |
| VoltAgent/awesome-design-md | (listed by claudefa.st, about 18k stars; verify) | DESIGN.md references to give agents a design system\[38\] |
| `theme-factory`, `brand-guidelines` (official) | anthropics/skills | Consistent theme and brand tokens |
| Figma MCP | Figma's official Dev Mode MCP (OAuth; needs a Figma plan with API) | Pull tokens, components and layouts for design-to-code\[58\] |
| Playwright MCP | https://github.com/microsoft/playwright-mcp | Drives a real browser via accessibility snapshots; `claude mcp add playwright -- npx @playwright/mcp@latest`. **Caution:** its `browser_run_code_unsafe` tool is "RCE-equivalent" per Playwright's docs\[32\]\[61\] |
| Web-asset generator skill | listed in travisvn/awesome-claude-skills | Favicons, app icons, social images\[5\] |

**Stack suggestion:** Next.js or Astro, plus Tailwind and shadcn/ui (the same stack `web-artifacts-builder` uses). Prototype in a Claude.ai artifact, move to Claude Code with `frontend-design` and the Vercel skills, then verify with Playwright MCP. SEO and deployment skills exist in the aggregators, but none that I found has verified maturity. Ask Claude to audit meta tags, sitemaps and Core Web Vitals directly, or write a small SEO skill yourself.

### 4.5 Building animations

| Resource | URL | What/why | Install |
|---|---|---|---|
| **Remotion Agent Skills (official)** | https://www.remotion.dev/docs/ai/skills | Maintained best practices for React-to-MP4 (`useCurrentFrame`, `interpolate`, `<Sequence>`, rendering, captions).\[62\]\[63\] Reported as one of skills.sh's most-installed skills\[64\] | `npx skills add remotion-dev/skills`, or accept the prompt during `bun create video` / `npx create-video`\[62\] |
| adithya-s-k/manim_skill | https://github.com/adithya-s-k/manim_skill | Best practices for both Manim Community Edition and ManimGL, with tested examples\[65\] | ~900+ stars; clone into skills dir\[66\] |
| Yusuke710/manim-skill | https://github.com/Yusuke710/manim-skill | Plan → code → render → iterate loop as a Claude Code plugin\[67\] | `/plugin marketplace add Yusuke710/manim-skill` then `/plugin install manim-skill/manim-skill`\[68\]\[69\] |
| AmitSubhash/3brown1blue | https://github.com/AmitSubhash/3brown1blue | CLI plus skill generating 3B1B-style explainers from a topic or slide deck; can use Claude Code with no API key\[70\] | pip/CLI |
| do-gongil/manimgl-skill | via awesomeclaudeplugins.com | ManimGL (3b1b's fork) specifically; new (July 2026)\[71\] | Low maturity |
| wilwaldon/Claude-Code-Video-Toolkit | https://github.com/wilwaldon/Claude-Code-Video-Toolkit | Curated index of video skills/MCP (Remotion, Manim, FFmpeg, screen capture)\[68\] | Reference list |
| haidrrrry/claude-remotion-skill | https://github.com/haidrrrry/claude-remotion-skill | Motion-graphics "taste" layer on Remotion (springs, grain, captions, sound design)\[72\] | Copy to `~/.claude/skills/`\[72\] |
| `algorithmic-art` / `slack-gif-creator` (official) | anthropics/skills | p5.js generative motion; GIFs | Built in |

**Libraries Claude drives well for motion** (long-standing projects; URLs are canonical but were not re-checked in this session): GSAP (gsap.com), Motion/Framer Motion (motion.dev), Three.js (threejs.org), p5.js (p5js.org), Lottie (airbnb.io/lottie / LottieFiles), Rive (rive.app), plus plain SVG/CSS keyframes. **Pick by output:**
- **Remotion** for marketing and explainer *videos*.
- **Manim** for math and science.
- **GSAP/Motion** for web interaction.
- **Three.js** for 3D.
- **p5.js** for generative sketches.
- **Lottie/Rive** for app UI animation.

Remotion uses a company licence for larger organisations, so check remotion.dev/license before commercial team use.

---

## Part 5 — Use Case: Artifacts

**What artifacts are.** Claude.ai renders HTML, React (JSX), SVG, Mermaid diagrams, Markdown and code in a side panel. Artifacts can be published to a public link that anyone can open without an account, and Claude account holders can click "Customize" to remix a published one.\[73\]\[74\] The sidebar has **Artifacts → Inspiration**, a curated gallery with categories such as "Learn something," "Play a game," and "Be creative" (on mobile it shows as a "Get inspired" banner). Team and Enterprise users don't see the public gallery and share within their organisation instead.\[75\]\[76\] These details come from a mirror of the Help Center and third-party guides, and I found no public URL for the gallery. It lives inside claude.ai.

**Artifacts in Claude Code (new).** Anthropic's blog (https://claude.com/blog/artifacts-in-claude-code) and docs (https://code.claude.com/docs/en/artifacts) describe live-updating, versioned pages with a gallery at claude.ai/code/artifacts. They can be private, organisation-wide, or public when an admin enables Organization settings → Artifacts → External sharing. The launch blog said organisation artifacts "cannot be made public," while the current docs describe admin-enabled public links.\[77\]\[78\] The docs are probably newer.

**How to get great artifacts:**
- Use the **`web-artifacts-builder`** skill for anything multi-component: it scaffolds React, Tailwind and shadcn/ui and bundles it into a single HTML artifact.\[5\]\[14\]\[79\]
- Add **`frontend-design`** and **`theme-factory`** so artifacts don't all look alike.
- Use **`algorithmic-art`** for generative pieces. It writes a design philosophy first, which is a good pattern to copy for any creative skill.\[10\]
- Mermaid artifacts are the fastest concept maps and flowcharts, and SVG artifacts are good for diagrams you will export.
- Ask for **"single-file, no external network calls, state in React hooks"**. The artifact sandbox restricts outside requests,\[80\] and only certain CDN libraries are available. Common ones are Recharts, D3, Three.js, Lodash, Papaparse, lucide-react and shadcn/ui, but check the current list in Claude's docs because it changes.

---

## Part 6 — Use Case: Builds, Teaching and Pedagogical Tools

### 6.1 Builds

Covered in 4.2–4.4. The short version is Superpowers or Spec Kit for process, Context7 for correct APIs, Playwright MCP for verification, Vercel and official skills for frontend quality, and LSP plugins for code intelligence.

### 6.2 Built-in teaching modes (free, no install)

- **Learning mode (Claude.ai).** It was introduced in **Claude for Education on April 2, 2025** (https://www.anthropic.com/news/introducing-claude-for-education). It started inside Projects, with partners including Northeastern, LSE, Champlain College and Instructure.\[81\] On **August 14, 2025**, Engadget reported that "Claude.ai users will find a new option within the style dropdown menu titled 'Learning,'" which guides with Socratic questions instead of handing over answers; Claude Code got the Explanatory and Learning output styles the same day.
- **Claude Code output styles** (https://code.claude.com/docs/en/output-styles). **Explanatory** adds "Insight" blocks explaining the choices behind the code. **Learning** adds Insights *and* asks you to write small pieces yourself, marked `TODO(human)`. Switch with `/output-style`, or set `"outputStyle": "Learning"` (case-sensitive). Both use more output tokens.\[82\]\[83\] These are ideal for teaching programming: the student writes the key lines while Claude scaffolds.

### 6.3 Pedagogy skills and tools

| Need | Resource | Notes |
|---|---|---|
| Anki flashcards (CSV) | https://github.com/mcbieda/ANKI-card-maker | Turns a topic, article or *your own chat transcript* into an importable CSV; mines a conversation for your weak spots\[84\] |
| Anki via AnkiConnect | https://github.com/ishiko732/anki-skills | Deck ops, batch cards from PDF/CSV/Excel, stats; needs the AnkiConnect add-on (code 2055492159)\[85\] |
| Anki (alt) | https://github.com/b0r1sp/claude-skill-anki | Clusters by concept rather than one card per slide; imports via AnkiConnect\[86\] |
| Card-writing principles | Andy Matuschak's "How to write good prompts" / minimum-information principle | Several Anki skills encode these; prefer ones that do\[87\]\[88\] |
| Quizzes/simulations | `web-artifacts-builder` + an artifact | Self-grading quizzes, sliders and simulations in one shareable file |
| Lecture decks/handouts | `pptx`, `docx`, `pdf` (official) | Real files |
| Math/science animation | Manim skills (4.5) | 3B1B-style explainers |
| Video lessons | Remotion skills | Captioned explainer videos |
| In-browser Python labs | Pyodide (pyodide.org), marimo (marimo.io), Jupyter | Claude can generate marimo notebooks (reactive, `.py` files) or Pyodide-powered pages for runnable exercises |

**Build your own course-builder skill.** I found no mature, widely adopted "curriculum generator" skill. The ones in aggregators are low-star. A personal skill is better. Ask `skill-creator` for a skill that:
1. Writes learning objectives using revised **Bloom's taxonomy** verbs (remember → create).
2. Generates **retrieval-practice** questions for each objective.
3. Schedules **spaced** review.
4. **Interleaves** problem types.
5. Pairs every concept with a **worked example** and a **visual** (dual coding).
6. Outputs a Mermaid concept map, an artifact quiz and an Anki CSV.

### 6.4 What the learning science says (use this to design prompts)

- **Learning styles (meshing).** Pashler, McDaniel, Rohrer & Bjork, *Psychological Science in the Public Interest* 9(3), 2008 (DOI 10.1111/j.1539-6053.2009.01038.x), concluded "there is no adequate evidence base to justify incorporating learning-styles assessments into general educational practice."\[89\]\[90\] Few studies even used the right crossover design, and several of those that did "flatly contradict" the meshing hypothesis.\[91\] People do have *preferences*, but teaching to them doesn't improve learning.\[92\]
- **Better-evidenced alternatives.** Dunlosky, Rawson, Marsh, Nathan & Willingham (2013, *PSPI* 14(1):4–58) reviewed 10 techniques: "Practice testing and distributed practice received high utility assessments… Elaborative interrogation, self-explanation, and interleaved practice received moderate utility assessments." Add worked examples, dual coding (words *plus* visuals for everyone, not matched to "visual learners"), and Socratic questioning.
- **Practical rule for Claude.** Don't ask "make this for a visual learner." Ask "explain with a diagram *and* words, then quiz me in 3 days."

---

## Part 7 — Use Case: Networks of Ideas, Knowledge Graphs and PKM

| Resource | URL | What/why | Signals | Link into |
|---|---|---|---|---|
| **kepano/obsidian-skills** | https://github.com/kepano/obsidian-skills | By Obsidian's CEO Steph Ango. Five skills: `obsidian-markdown` (wikilinks, callouts, properties), `obsidian-bases`, `json-canvas`, `obsidian-cli`, `defuddle` (clean web extraction)\[93\]\[94\] | MIT; ~15–22k stars (sources vary)\[93\]\[95\]\[96\] | `/plugin marketplace add kepano/obsidian-skills` → `/plugin install obsidian@obsidian-skills`, or `npx skills add kepano/obsidian-skills`, or clone into the vault's `.claude/`\[94\]\[95\] |
| **MCP Memory server** (official reference) | https://github.com/modelcontextprotocol/servers/tree/main/src/memory | Local knowledge graph of entities, relations and observations that persists across chats\[97\]\[98\] | Still listed as maintained by the MCP steering group; npm `@modelcontextprotocol/server-memory` v2026.8.31\[99\]\[100\] | `npx -y @modelcontextprotocol/server-memory`; set `MEMORY_FILE_PATH`\[100\]\[101\] |
| MarkusPfundstein/mcp-obsidian | https://github.com/MarkusPfundstein/mcp-obsidian | MCP access to a vault via the Obsidian Local REST API plugin\[102\] | ~4.5k stars, MIT\[102\] | `uvx mcp-obsidian` in Claude Desktop config\[103\] |
| InfraNodus MCP (official) | https://github.com/infranodus/mcp-server-infranodus | Text → network graph analysis: topical clusters, structural gaps, bridging ideas\[104\] | ~97 stars; updated Aug 2026; needs API key\[105\]\[106\] | `claude mcp add infranodus … npx -y infranodus-mcp-server` or remote https://mcp.infranodus.com \[107\] |
| Notion skills / MCP | Notion partner skill (anthropics/skills README) | Notion workspace as a knowledge base | Partner | Claude.ai connectors; Claude Code MCP |

**Graph and diagram libraries for idea maps** (canonical, long-standing; not re-verified here): **Mermaid** (mermaid.js.org; native in artifacts), **D3** (d3js.org; force-directed graphs), **Observable Plot**, **Cytoscape.js** (js.cytoscape.org; network analysis plus layouts), **vis-network**, **React Flow** (reactflow.dev; editable node UIs), **Excalidraw** and **tldraw** (whiteboards, both open-source and embeddable), and **JSON Canvas** (Obsidian's open canvas format, which Claude can write directly via the skill). A community **claude-d3js-skill** is listed in travisvn/awesome-claude-skills.\[5\]

**Recommended idea-network stack:**
1. Use an Obsidian vault as the source of truth (files over apps), with obsidian-skills in Claude Code.
2. Have Claude atomise notes Zettelkasten-style and add `[[wikilinks]]`.
3. Generate a `.canvas` concept map.
4. Use the MCP memory server for cross-session "what do I know about X."
5. Run InfraNodus to find structural gaps.
6. Export a D3 or React Flow artifact to explore or share.

Logseq, MarginNote and other PKM tools have no first-party Claude skills that I could verify. Use their Markdown/OPML exports with the generic skills above.

---

## Part 8 — Use Case: Inspiration (What's Now Possible)

- **Claude.ai Artifacts → Inspiration gallery** (in-app). Remix published games, learning tools and creative toys. This is the fastest way to see what a single prompt can produce.
- **`algorithmic-art` outputs.** Ask for "a flow-field piece seeded by my name." It writes a manifesto and an interactive p5.js viewer.
- **Remotion + Claude Code promo videos.** Since Remotion launched its agent skills in January 2026, creators have reported near-one-shot 30-second product videos with transitions, brand colours and music.\[108\]\[109\] These are anecdotal social posts, so expect iteration in practice.
- **Manim explainers from a slide deck** (3brown1blue `from-slides lecture.pptx`).\[70\]
- **Explorable explanations canon:**
  - Bret Victor's 2011 essay that coined the term (https://worrydream.com/ExplorableExplanations/). \[110\]\[111\]
  - Nicky Case's work (https://ncase.me, e.g. *The Evolution of Trust*, https://ncase.me/trust/; *Parable of the Polygons* with Vi Hart).\[112\]\[113\]
  - The explorabl.es hub.
  - **Distill.pub** (https://distill.pub). It has been on **indefinite hiatus since 2021** but is still the gold standard for interactive ML articles.\[114\]\[115\] Its archive is the best style guide for Claude-generated explainers.
- **3Blue1Brown's manim** (https://github.com/3b1b/manim, about 94k stars) and the **Manim Community** fork (https://github.com/ManimCommunity/manim, about 41k stars).\[116\]\[117\] Both are drivable by Claude.
- **The Claude Code Ticker** in awesome-claude-code samples Claude Code projects across GitHub,\[118\] which is a running feed of what people are shipping.
- **Game-studio-scale agents.** A plugin advertised as "49 AI agents, 72 workflow skills" for game dev is listed (about 21.6k stars) in a mirror of jqueryscript's awesome-claude-code.\[66\] I did not verify it, so treat it as a sign of ambition rather than a recommendation.

---

## Part 9 — Safety and Vetting

Skills and plugins are **code plus instructions written by strangers**. A skill can include scripts that Claude runs, and a plugin can add **hooks** that run shell commands automatically and **MCP servers** that run as processes. PromptArmor's "Hijacking Claude Code via Injected Marketplace Plugins" showed that a malicious marketplace plugin can "Bypass human-in-the-loop protections" (its hook rewrote Claude Code's permission settings) and "Exfiltrate a user's files via indirect prompt injection." They also pointed out look-alike forks (e.g., `anthropics-claude/claude-code` vs the real `anthropics/claude-code`). Anthropic's docs state that marketplaces are responsible for their own plugins.

**Checklist before installing anything third-party:**
1. **Check the org/owner** exactly. Prefer `anthropics/*`, vendor-official repos (`remotion-dev`, `vercel-labs`, `microsoft`, `kepano`) and high-reputation maintainers.
2. **Read SKILL.md and every script.** Look for `curl | sh`, base64 blobs, network calls, and writes to `~/.claude/settings*.json`.
3. **In `/plugin`, read the "Will install" list.** Be wary of any hooks or MCP servers you didn't expect.
4. **Pin versions**, e.g. `/plugin marketplace add owner/repo#v1.2.0`, and avoid auto-update for unknown sources.
5. **Prefer project or local scope** for experiments, and use a throwaway repo or container for anything that runs code.
6. **Keep permission prompts on.** Don't enable "unsafe" tools such as Playwright's `browser_run_code_unsafe` unless you need them.\[61\]
7. **Watch context cost.** Large MCP servers (GitHub's has dozens of tools) eat tokens every turn.\[59\]
8. In Claude.ai, uploaded skills run in Anthropic's sandbox. That limits the damage, but it doesn't stop a malicious skill from feeding you bad instructions or leaking data you paste in.

## Part 10 — Licensing Notes

- **anthropics/skills:** Example skills are mostly Apache 2.0. **docx/pdf/pptx/xlsx are source-available only**,\[1\] and THIRD_PARTY_NOTICES.md covers bundled assets such as fonts.
- **superpowers, obsidian-skills, mcp-obsidian, InfraNodus MCP, Spec Kit, BMAD:** MIT.\[48\]\[52\]\[95\]
- **awesome lists:** Typically CC0 or similar for the list itself. Each linked project keeps its own licence.
- **Remotion:** Free for individuals and small teams; larger companies need a company licence.
- **Manim CE:** MIT. **3b1b/manim:** MIT.
- **Anki:** AGPL (desktop).
- **Skill output:** What Claude generates for you is governed by Anthropic's terms, not by the skill's licence. But if a skill bundles fonts, templates or brand assets, check those before you ship them commercially.

---

## Caveats

- **Fast-moving ground.** Star counts, CLI version numbers (e.g., v2.1.275 for one-step marketplace installs), menu labels in Claude.ai, and the membership of the official marketplace all change monthly. Re-check anything critical on the source page.
- **Partially verified items:** the Claude.ai Inspiration gallery (no public URL; in-app), `anthropics/claude-plugins-community` and `knowledge-work-plugins` (secondary sources), VoltAgent/awesome-design-md and everything-claude-code (secondary), the exact artifact library allow-list, and third-party claims about mcp-obsidian's release cadence.
- **Not fetched directly in this research:** explorabl.es, ncase.me, and the canonical homepages of the JS/Python libraries listed. These are long-established, but their URLs were not re-confirmed in this session.
- **Aggregator noise.** Install counts on directories (e.g., "126,000+ installs" for Remotion's skill) come from those sites' own telemetry\[64\] and are not independently audited.
- **Most community pedagogy skills are young and low-star.** For teaching, the most reliable assets are the official skills, built-in Learning mode and output styles, Manim/Remotion, and skills you write yourself grounded in retrieval practice and spacing.

## Sources

1. [GitHub - anthropics/skills: Public repository for Agent Skills](https://github.com/anthropics/skills)
2. [Claude Code Skills Complete Guide: SKILL.md, MCP, Subagents & Teams (2026)](https://duet.so/guides/claude-code-skills-complete-guide)
3. [claude-code-skills/CLAUDE.md at main · daymade/claude-code-skills](https://github.com/daymade/claude-code-skills/blob/main/CLAUDE.md)
4. [Agent Skills - Claude Platform Docs](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)
5. [GitHub - travisvn/awesome-claude-skills: A curated list of awesome Claude Skills, resources, and tools for customizing Claude AI workflows — particularly Claude Code](https://github.com/travisvn/awesome-claude-skills)
6. [SKILL.md Format Specification: Complete YAML Frontmatter…](https://www.agensi.io/learn/skill-md-format-reference)
7. [Anthropic · GitHub](https://github.com/anthropics)
8. [A Tour of Anthropic's 17 Official Skills — What the anthropics/skills Repo Can Do](https://codenote.net/en/posts/anthropic-official-skills-catalog-overview/)
9. [Anthropic Official Skills: Complete Guide to 17 Open-Source Agent Skills - ClaudeWorld](https://claude-world.com/articles/anthropic-official-skills-complete-guide/)
10. [Anthropic Official Skills Repository: 17 Skills — What to Install, How, and Why](https://claudecn.com/en/blog/claude-official-skills-walkthrough/)
11. [Top 50 Claude Skills & GitHub Repos for AI — The Only List You Need.](https://x.com/zodchiii/article/2034924354337714642?lang=en)
12. [Awesome Claude Code Skills: The Curated List (2026)](https://designrevision.com/blog/awesome-claude-code-skills)
13. [GitHub - heilcheng/awesome-agent-skills: Tutorials, Guides and Agent Skills Directories · GitHub](https://github.com/heilcheng/awesome-agent-skills)
14. [anthropics — 507 agent skills on @skills](https://atskills.one/anthropics)
15. [What Are Agent Skills and How To Use Them](https://strapi.io/blog/what-are-agent-skills-and-how-to-use-them)
16. [GitHub - ComposioHQ/awesome-claude-skills: A curated list of awesome Claude Skills, resources, and tools for customizing Claude AI workflows · GitHub](https://github.com/ComposioHQ/awesome-claude-skills)
17. [Use Agent Skills in VS Code](https://code.visualstudio.com/docs/agent-customization/agent-skills)
18. [Anthropic Opens Agent Skills Standard, Continuing Its Pattern of Building Industry Infrastructure](https://www.unite.ai/anthropic-opens-agent-skills-standard-continuing-its-pattern-of-building-industry-infrastructure/)
19. <https://code.claude.com/docs/en/discover-plugins>
20. [Claude Plugins Marketplace: What It Is & How to Use It](https://lagrowthmachine.com/claude-plugins-marketplace/)
21. [Claude Code: Install Plugins from Marketplaces](https://codingnomads.com/claude-code-discover-install-plugins-marketplace-98852281)
22. [Discover and install prebuilt plugins through marketplaces — Claude API Docs](https://doc.jarvisuni.com/claude/code/en/discover-plugins)
23. [claude-code/plugins/learning-output-style/README.md at main · anthropics/claude-code](https://github.com/anthropics/claude-code/blob/main/plugins/learning-output-style/README.md)
24. [Agent Skills: Complete Getting-Up-To-Speed Guide](https://codeagentsalpha.substack.com/p/claude-agent-skills-complete-getting)
25. [Claude Skills](https://technicallycurious.substack.com/p/claude-skills)
26. [How Claude Skills Work: From Metadata to Automation](https://zerofuturetech.substack.com/p/how-claude-skills-work-from-metadata)
27. [The Definitive Guide to Claude SKILLS: Code vs Web vs Desktop vs API](https://limitededitionjonathan.substack.com/i/176860442/claude-api-skills-programmatic-access-claude-api-skills)
28. [Claude Skills are here — and they might be the smartest AI feature you’re not using yet](https://www.tomsguide.com/ai/claude-skills-are-here-and-they-might-be-the-smartest-ai-feature-youre-not-using-yet)
29. [Extend Claude with skills - Claude Code Docs](https://code.claude.com/docs/en/skills)
30. [Dan Stroot · Vercel Skills.sh](https://www.danstroot.com/posts/2026-01-21-vercel-skills-directory)
31. [Introducing skills, the open agent skills ecosystem - Vercel](https://vercel.com/changelog/introducing-skills-the-open-agent-skills-ecosystem)
32. [How to Add Playwright MCP to Claude Code (Setup Guide)](https://www.vibecodingacademy.ai/blog/playwright-mcp-claude-code-complete-guide)
33. [obra/superpowers Agent Skills on GitHub](https://skillsmp.com/creators/obra/superpowers)
34. [GitHub - obra/superpowers: An agentic skills framework & software development methodology that works. · GitHub](https://github.com/obra/superpowers)
35. [obra/superpowers - 293.8k Stars · Global Rank #12](https://www.star-history.com/obra/superpowers/)
36. [GitHub - hesreallyhim/awesome-claude-code: A hand-picked collection of the finest of resources for the most awesome of agents, Claude Code, the undisputed champion of coding companions, from the unstoppable team at Anthropic PBC. A delectable showcase of top tier skills, ambidextrous agents, scintillating status lines, top notch developer tooling, and also we have plugins · GitHub](https://github.com/hesreallyhim/awesome-claude-code)
37. [The Agent Skills Directory](https://www.skills.sh/)
38. [Awesome Claude Code: 11 Curated Lists Worth Bookmarking](https://claudefa.st/blog/tools/resources/awesome-claude-code)
39. [Add: obra/superpowers (211K stars) — agentic skills framework · Issue #293 · ksimback/hermes-ecosystem](https://github.com/ksimback/hermes-ecosystem/issues/293)
40. [Obra/Superpowers: A Developer's Guide to Agentic Skills Framework](https://www.gitsurfer.com/blog/obra-superpowers-a-developer-s-guide-to-agentic-skills-framework)
41. [🧠 I Tried 100 Claude Skills. These Are The Best. - DEV Community](https://dev.to/suraj_khaitan_f893c243958/i-tried-100-claude-skills-these-are-the-best-1m4a)
42. [GitHub - obra/the-elements-of-style: William Strunk Jr.'s Elements of Style (1918) in markdown format for AI agents · GitHub](https://github.com/obra/the-elements-of-style)
43. [Humanize: Claude Code Skill for Natural AI Writing](https://mcpmarket.com/tools/skills/humanize-ai-writing-1)
44. [Claude gets custom style feature — makes the AI chatbot write just like you](https://tomsguide.com/ai/claude-gets-custom-style-feature-makes-the-ai-chatbot-write-just-like-you)
45. [www.anthropic.com](https://www.anthropic.com/news/styles)
46. [GitHub - obra/superpowers-developing-for-claude-code · GitHub](https://github.com/obra/superpowers-developing-for-claude-code)
47. [GitHub - obra/superpowers-skills: Community-editable skills for Claude Code's superpowers plugin · GitHub](https://github.com/obra/superpowers-skills)
48. [2026 AI Specification Frameworks Compared: OpenSpec, Spec Kit, Superpowers, BMAD & GSD](https://docs.bswen.com/blog/2026-08-07-ai-spec-frameworks-compared/)
49. [I Tested Three Spec-Driven AI Tools. Here’s My Honest Take.](https://ranthebuilder.cloud/blog/i-tested-three-spec-driven-ai-tools-here-s-my-honest-take/)
50. [OpenSpec vs Spec Kit vs BMAD: Which Spec Framework Should You Pick?](https://aicodingpatterns.com/en/patterns/openspec-vs-spec-kit-vs-bmad/)
51. [BMAD vs Spec Kit vs OpenSpec: Choosing Your Spec-Driven AI Framework in 2026](https://medium.com/@reenbit/bmad-vs-spec-kit-vs-openspec-choosing-your-spec-driven-ai-framework-in-2026-a6996b3ebb8d)
52. [GitHub Spec Kit vs BMAD-METHOD: which spec-driven approach fits your workflow?](https://defract.dev/blog/github-spec-kit-vs-bmad-method)
53. [ToolTwist](https://tooltwist.com/insights/spec-driven-frameworks-cxo-guide)
54. [Research digest: spec-kit, BMAD, OpenSpec, MADR, log4brains — 4 integration candidates, 3 settled non-candidates · Issue #38 · codenamev/ai-software-architect](https://github.com/codenamev/ai-software-architect/issues/38)
55. [9 Best AI Tools for Spec-Driven Development in 2026: Kiro, BMAD, GSD, and More Compare - MarkTechPost](https://www.marktechpost.com/2026/05/08/9-best-ai-tools-for-spec-driven-development-in-2026-kiro-bmad-gsd-and-more-compare/)
56. [vercel-labs/agent-skills — Agent skills](https://www.skills.sh/vercel-labs/agent-skills)
57. [Skills Catalog](https://deepwiki.com/anthropics/skills/3-skills-catalog)
58. [Top 12 MCP servers for Claude Code in 2026 - Bito](https://bito.ai/ai-tools/claude-code-mcp-servers/)
59. [Best MCP Servers for Claude Code in 2026 (Ranked and Tested)](https://nimbalyst.com/blog/best-claude-code-mcp-servers/)
60. [feat: add context7, postgres and playwright MCP servers by LeongWZ · Pull Request #83 · AY2627S1-CS3219-P23/foc](https://github.com/AY2627S1-CS3219-P23/foc/pull/83)
61. [Playwright MCP](https://playwright.dev/docs/getting-started-mcp)
62. [Agent Skills](https://www.remotion.dev/docs/ai/skills)
63. [Claude Code + Remotion — how to make videos with an AI agent](https://snapcn.dev/claude-code-remotion-videos)
64. [Remotion Agent Skills Guide 2026: Programmatic Video with Claude Code](https://aividpipeline.com/blog/remotion-agent-skills-guide-2026)
65. [Manim Skill - Create 3Blue1Brown Style Animations](https://shyft.ai/skills/manim-skill)
66. [GitHub - lognorm/jqueryscript-awesome-claude-code: A curated list of awesome tools, IDE integrations, frameworks, and other resources for developers working with Anthropic's Claude Code. · GitHub](https://github.com/lognorm/jqueryscript-awesome-claude-code)
67. [GitHub - Yusuke710/manim-skill: SKILL.md for creating animations with Manim. Coding Agent autonomously plans scenes, writes Manim code, renders videos, and refines based on feedback. · GitHub](https://github.com/Yusuke710/manim-skill)
68. [GitHub - wilwaldon/Claude-Code-Video-Toolkit: Skills, MCP servers, and tools for producing video with Claude Code. Covers programmatic video (Remotion, Manim), screen recording, YouTube clipping, and FFmpeg post-processing. · GitHub](https://github.com/wilwaldon/Claude-Code-Video-Toolkit)
69. [manim-skill - AI Agents on GitHub](https://skillsllm.com/skill/manim-skill)
70. [GitHub - AmitSubhash/3brown1blue: First-principles Manim skill for Claude Code — mathematical animation from scratch, paper-explainer patterns, 21 rule files.](https://github.com/AmitSubhash/3brown1blue)
71. [do-gongil/manimgl-skill](https://awesomeclaudeplugins.com/do-gongil/manimgl-skill)
72. [GitHub - haidrrrry/claude-remotion-skill: Open-source Claude agent skill that teaches Claude Code, Claude Desktop & Claude AI to create and edit professional motion graphics videos with Remotion. AI video editing, B-roll, captions, sound design — from one prompt.](https://github.com/haidrrrry/claude-remotion-skill)
73. [What Are Claude Artifacts and How to Use Them (2026) - Albato](https://albato.com/blog/publications/how-to-use-claude-artifacts-guide)
74. [Claude Artifacts for Marketers: The Definitive 2026 Guide](https://www.getmasset.com/resources/claude-artifacts-for-marketers)
75. [claude-wiki/15-Claude-AI-Features/publishing-and-sharing-artifacts.md at master · johnzfitch/claude-wiki](https://github.com/johnzfitch/claude-wiki/blob/master/15-Claude-AI-Features/publishing-and-sharing-artifacts.md)
76. [How to Use Claude Artifacts: Create, Share & Remix AI Content](https://www.guvi.in/blog/how-to-use-claude-artifacts/)
77. [Share session output as artifacts - Claude Code Docs](https://code.claude.com/docs/en/artifacts)
78. [Claude Code now supports artifacts](https://claude.com/blog/artifacts-in-claude-code)
79. [awesome-claude-skills — 77 curated resources](https://www.context-awesome.com/list/ComposioHQ/awesome-claude-skills)
80. [How to Use Claude Artifacts: Create, Share, and Remix AI Content](https://www.codecademy.com/article/how-to-use-claude-artifacts-create-share-and-remix-ai-content)
81. [introducing claude for education](https://www.anthropic.com/news/introducing-claude-for-education?)
82. [Output styles - Claude Code Docs](https://code.claude.com/docs/en/output-styles)
83. [Claude Code Output Styles: All 5, Including Concise](https://www.getclaudeskills.com/blog/claude-code-output-styles-explained)
84. [GitHub - mcbieda/ANKI-card-maker: A Claude Code skill that turns a topic, article, or LLM chat into Anki flashcards, saved as a CSV ready to import. · GitHub](https://github.com/mcbieda/ANKI-card-maker)
85. [anki - Claude Code Plugin](https://agentskill.sh/plugins/ishiko732/anki)
86. [anki](https://skills.cat/skills/b0r1sp/claude-skill-anki)
87. [Anki Flashcards Generator](https://mcpmarket.com/tools/skills/anki-flashcards-generator)
88. [Anki Flashcard Generator - Claude Code Skill](https://mcpmarket.com/tools/skills/anki-flashcard-generator)
89. ["Learning Styles: Concepts and Evidence" by H. Pashler, Marshall D. McDaniel et al.](https://digitalcommons.usf.edu/psy_facpub/1765/)
90. [Learning Styles Concepts and Evidence](https://bjorklab.psych.ucla.edu/wp-content/uploads/sites/13/2016/07/Pashler_McDaniel_Rohrer_Bjork_2009_PSPI.pdf)
91. [Pashler, H., McDaniel, M., Rohrer, D. & Bjork, R. (2008). “Learning styles: Concepts and evidence”. Psychological Science in the Public Interest, (9):106-119](https://www.scribd.com/doc/228751903/Pashler-H-McDaniel-M-Rohrer-D-Bjork-R-2008-Learning-styles-Concepts-and-evidence-Psychological-Science-in-the-Public-Interest-9)
92. [The problem with learning styles: debunking the meshing hypothesis in English language teaching](https://my.chartered.college/impact_article/the-problem-with-learning-styles-debunking-the-meshing-hypothesis-in-english-language-teaching/)
93. [Obsidian Skills: Let Your Agent Manage Your Second Brain - DEV Community](https://dev.to/stevengonsalvez/obsidian-skills-let-your-agent-manage-your-second-brain-4fel)
94. [Kepano Obsidian Skills — Install for Claude Code & Codex](https://easyskill.net/en/skill/obsidian-skills/)
95. [Obsidian’s Official Skills Are Here! It’s time to let AI plug into your local Vault.](https://kurtis-redux.medium.com/obsidians-official-skills-are-here-it-s-time-to-let-ai-plug-into-your-local-vault-6c149aae84f6)
96. [Obsidian Skills - Claude Code Skill](https://cultofclaude.com/skills/obsidian-skills/)
97. [servers/src/memory at main · modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers/tree/main/src/memory)
98. [Knowledge Graph Memory MCP server for AI agents](https://playbooks.com/mcp/modelcontextprotocol-knowledge-graph-memory)
99. [@modelcontextprotocol/server-memory - npm](https://www.npmjs.com/package/@modelcontextprotocol/server-memory)
100. [GitHub - modelcontextprotocol/servers: Model Context Protocol Servers · GitHub](https://github.com/modelcontextprotocol/servers)
101. [Knowledge Graph Memory Server by modelcontextprotocol](https://glama.ai/mcp/servers/@modelcontextprotocol/knowledge-graph-memory-server)
102. [GitHub - MarkusPfundstein/mcp-obsidian: MCP server that interacts with Obsidian via the Obsidian rest API community plugin · GitHub](https://github.com/MarkusPfundstein/mcp-obsidian)
103. [Best Obsidian MCP Server: 4 Compared + Setup (2026)](https://contextbolt.com/blog/obsidian-mcp-claude/)
104. [InfraNodus MCP Server](https://glama.ai/mcp/servers/@infranodus/mcp-server-infranodus)
105. [InfraNodus SAS · GitHub](https://github.com/infranodus)
106. [Knowledge Graphs for LLM Workflows](https://www.blog.brightcoding.dev/2026/09/27/infranodusmcp-server-infranodus-knowledge-graphs-for-llm-workflows)
107. [GitHub - infranodus/mcp-server-infranodus: The official InfraNodus MCP server · GitHub](https://github.com/infranodus/mcp-server-infranodus)
108. [Remotion now has Agent Skills — make videos just with Claude Code. \$ npx skills add remotion-dev/skills This animation was created entirely by prompting. This is a big step toward agent-driven video creation, where code, design, and motion come together with almost no manual work.](https://www.threads.com/@naveed_ullah600/post/DTx-TbWDPQo/video-remotion-now-has-agent-skills-make-videos-just-with-claude-code-npx-skills-add)
109. [Claude Code Video with Remotion: Best Motion Guide 2026](https://www.dplooy.com/blog/claude-code-video-with-remotion-best-motion-guide-2026)
110. [GitHub - RascalTwo/explorables: Interactive, mostly AI-generated educational visualizations (explorable explanations), plus the /viz skill that makes them. · GitHub](https://github.com/RascalTwo/explorables)
111. [Explorable Explanations](https://worrydream.com/ExplorableExplanations/)
112. [Nicky Case](https://en.wikipedia.org/wiki/Nicky_Case)
113. [Parable of the Polygons](https://en.wikipedia.org/wiki/Parable_of_the_Polygons)
114. [Publishing in the Distill Research Journal](https://distill.pub/journal/)
115. [Distill is dedicated to making machine learning clear and dynamic](https://distill.pub/about/)
116. [GitHub - ManimCommunity/manim: A community-maintained Python framework for creating mathematical animations. · GitHub](https://github.com/ManimCommunity/manim)
117. [GitHub - 3b1b/manim: Animation engine for explanatory math videos · GitHub](https://github.com/3b1b/manim)
118. [awesome-claude-code - AI Agents on GitHub (54.8k★)](https://skillsllm.com/skill/hesreallyhim-awesome-claude-code)
