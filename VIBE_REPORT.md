# Vibe Report — review-bot

## 0. TL;DR

- **What got built:** An AI-powered PR review bot that mimics Greptile-style code analysis, plus an independent approval agent that reads the review output and auto-approves or holds PRs. A Next.js dashboard visualizes the lifecycle. `[FACT]`
- **Stack:** Python 3.12 (httpx, litellm, pydantic) + Next.js 16 (React 19, Tailwind 4, shadcn/ui) `[FACT]`
- **Agent:** Cursor IDE with Claude (Opus 4.6) — single long-running session `[FACT]`
- **Session turns:** ~40+ user messages across a single extended conversation `[INFERRED]` (based on conversation summary listing 30+ user messages, continued further in this session)
- **LOC:** ~2,743 lines of hand-relevant source (Python + TypeScript + CSS), excluding lockfiles/generated `[FACT]`
- **Time span:** ~27 hours wall-clock (May 2 11:09 → May 3 13:08 UTC+3), with significant idle gaps `[FACT]`
- **One-line vibe:** Voice-driven hackathon sprint where the human steered architecture while the agent wrote 95%+ of the code `[SUBJECTIVE]`

## 1. The Build

- **Two Python agents** deployed via GitHub Actions on a Fastify fork: a review agent (LLM-powered via LiteLLM proxy) that posts Greptile-style PR summaries with severity findings, and an approval agent (rule-based) that parses the review output and submits GitHub APPROVE or posts an "ON HOLD" comment. `[FACT]`
- **Next.js dashboard** with shadcn/ui components showing PR list with stats, detail pages with review overview cards and findings tables, and a timeline showing the full PR lifecycle (opened → reviewed → approved → merged/closed). `[FACT]`
- **Working features:** LLM review with inline comments and emoji reactions, confidence scoring (1–5), severity classification (P0–P2), independent approval agent triggered by `issue_comment` webhook, dashboard with 5s polling, merged PR detection. **Stubbed/missing:** no deployment config for dashboard, no dark mode toggle, no error boundary UI, simulate script is hard-coded. `[FACT]`
- **How a judge runs it in <60s:** Clone repo → `cd backend && uv sync && just test` (39 tests pass). For the dashboard: `cd dashboard && npm install && npm run dev` with a `GITHUB_TOKEN` and `GITHUB_REPO` in `.env.local`. PRs are already live on `dawidbudaszewski/fastify` with bot comments visible. `[FACT]`

## 2. Code Metrics `[FACT]`

### Files & LOC by language (excluding lockfiles, node_modules, .venv, .next)

| Language | Files | LOC |
|----------|-------|-----|
| Python (.py) | 14 | 1,097 |
| TypeScript (.ts/.tsx) | 14 | 1,078 |
| CSS | 1 | 129 |
| Markdown (.md) | 4 | ~160 |
| Config (toml, json, yml, mjs) | 8 | ~280 |
| **Total** | **41** | **~2,743** |

### Top 10 dependencies

| # | Package | Role |
|---|---------|------|
| 1 | `litellm` | LLM gateway (OpenAI/Anthropic via corporate proxy) |
| 2 | `httpx` | Async HTTP client for GitHub API |
| 3 | `pydantic` | Structured data models for review findings |
| 4 | `next` 16.2.4 | React framework for dashboard |
| 5 | `react` 19.2.4 | UI library |
| 6 | `tailwindcss` 4 | Utility-first CSS |
| 7 | `shadcn` 4.6.0 | Component library (badge, card, table, button) |
| 8 | `pytest` | Python test framework |
| 9 | `class-variance-authority` | CSS variant management for shadcn |
| 10 | `lucide-react` | Icon library |

### Tests

- **39 tests**, all passing `[FACT]`
- Coverage: `test_review_agent.py` (247 LOC), `test_approval_agent.py` (206 LOC), `test_models.py` (84 LOC)
- No frontend tests `[FACT]`

## 3. AI vs Human Contribution

- **Estimated AI-written:** ~95% `[INFERRED]` — The agent (Cursor + Claude) wrote virtually all code, configuration, GitHub Actions workflows, tests, and dashboard components. The user directed architecture and made corrections but did not write code directly.
- **Human contribution:** Architecture decisions (two separate agents, decoupled workflows), naming (`review_agent` / `approval_agent`), LiteLLM proxy configuration (private vs public endpoints, API keys), workflow trigger design, UI feedback ("this is very ugly"), feature requests. `[INFERRED]`
- **Acceptance rate:** ~85% `[INFERRED]` — Most generated code was accepted. The user rejected or corrected: initial Greptile integration plan (pivoted to mock), monorepo move to `scaleapi/gps-sandbox` (reverted), folder structure naming, approval agent coupling, and some UI choices.
- **Moments human took over:** Providing LiteLLM API keys, creating the `BOT_PAT` GitHub token, granting GitHub Actions permissions in repo settings, re-authenticating `gh` CLI. `[FACT]`

## 4. Prompting Style

- **Average length:** Medium-high. Many prompts were voice-transcribed (natural language, sometimes rambling), with occasional precise technical instructions. `[INFERRED]`
- **Context provided:** Generally good — the user referenced specific files, explained the Greptile/LiteLLM architecture, and shared Notion docs for LiteLLM setup. `[INFERRED]`

### 5 verbatim prompts

**Best (clearest direction):**
> "Agent 1: 'review_agent' (fetches diff, calls LLM, posts PR summary + inline comments) / Agent 2: 'approval_agent' (reads the review findings, decides approve or request changes)"

**Worst (vague, required clarification):**
> "Hi, I want to build like a project for a hackathon. In order to start, the project will be focusing on reviewing the code on PRS, right? So it's going to be integrating with GitHub. In order to start this project, I first need to get myself a proper repository..."

**Pivotal (changed project direction):**
> "Yeah, so like I described the current review bot is just a reptile simulator. What's really important as part of this hackathon is the approval agent bot. So in the production environment, Graptile is a black box. It just reviews the code and posts the output..."

**Most ambitious:**
> "Would you be able to please... Well, if you notice in my Cursor workspace, the source of everything is the developer folder. So at the developer folder level, I would love to clone this repository and start building the review bot..."

**Funniest (autocorrect/voice artifact):**
> "Reptile" (meant "Greptile") — used consistently in voice transcription for the first several messages before being clarified. Also "Ginger" (meant "Jinja") — immediately self-corrected.

**Patterns:** Voice-first prompting with natural speech patterns. The user thinks out loud, often starting with context before arriving at the actual request. Corrections come as follow-ups rather than re-prompts. `[INFERRED]`

## 5. Interaction Patterns

- **Iterative, not one-shot.** The project evolved through many small cycles: build → test → observe → correct → rebuild. `[FACT]`
- **Steering moments:** The user course-corrected several times:
  - "No, so basically the idea is that I want to be the owner of the repository" (after agent suggested using existing open-source PRs) `[FACT]`
  - "I don't think the approver triggered" → led to discovering `GITHUB_TOKEN` can't trigger other workflows → introduced `BOT_PAT` `[FACT]`
  - "This is very ugly, can we please install shadcn" → full UI overhaul `[FACT]`
  - "Also merged PRs don't appear here as merged" → added `merged_at` detection `[FACT]`
  - "approval decision is not shown" → discovered reviews API needed alongside comments API `[FACT]`
- **Longest unbroken accept-chain:** The initial scaffold → agent implementation → tests → simulate script sequence (~4 consecutive commits accepted without correction). `[INFERRED]`

## 6. Tools, MCPs & Agents

- **Primary agent:** Cursor IDE with Claude Opus 4.6 `[FACT]`
- **MCPs available:** `cursor-ide-browser`, `user-Linear`, `user-notion`, `user-Figma`, `user-eamodio.gitlens-extension-GitKraken` — of these, only Notion was referenced (user shared a LiteLLM setup doc link) `[FACT]`
- **Sub-agents used:** `explore` sub-agents for codebase analysis (examining `ips-applications` project structure, reviewing fastify workflows, auditing review-bot project) `[FACT]`
- **Non-AI tools:** `gh` CLI (GitHub auth, repo creation, PR management), `uv` (Python package management), `npm` (dashboard dependencies), `just` (task runner) `[FACT]`
- **Cursor skills available but not invoked for core work:** `create-rule`, `create-skill`, `canvas`, `babysit`, `split-to-prs` `[FACT]`

## 7. Debugging & Recovery

### Bug 1: LiteLLM authentication failure in CI
- **Symptom:** `openai.AuthenticationError: 401` when running in GitHub Actions `[FACT]`
- **Diagnosis:** Agent identified model name needed `openai/` prefix for LiteLLM proxy. User then identified the API base URL was wrong (private endpoint not reachable from GH runners). `[FACT]`
- **Fix:** Added `api_base` parameter, switched to public endpoint for CI, kept private for local. ~30 min. `[INFERRED]`

### Bug 2: Approval agent not triggering
- **Symptom:** Review bot posted comment but approval workflow never ran `[FACT]`
- **Diagnosis:** Agent identified that `GITHUB_TOKEN`-authored comments cannot trigger other workflows (GitHub security feature). `[FACT]`
- **Fix:** Introduced `BOT_PAT` (user's personal access token) for the review bot's GitHub operations. ~20 min. `[INFERRED]`

### Bug 3: Merged PRs showing as "Closed"
- **Symptom:** Dashboard showed "Closed" for merged PRs `[FACT]`
- **Diagnosis:** GitHub API returns `state: "closed"` for both closed and merged PRs; need to check `merged_at` field. Agent fixed. `[FACT]`
- **Fix:** Added `merged_at` to API types, computed display state. ~5 min. `[FACT]`

### Bug 4: Approval decision not appearing on detail page
- **Symptom:** "Approval Decision" card showed "--" even though approval comment existed `[FACT]`
- **Diagnosis:** Approval was submitted via `post_review(event="APPROVE")` (GitHub reviews API), but dashboard only searched issue comments. `[FACT]`
- **Fix:** Added reviews API fetch, searched both comments and reviews for approval marker. ~10 min. `[FACT]`

### Bug 5: `hatchling` build failure
- **Symptom:** `uv sync` failed with "Readme file does not exist: README.md" `[FACT]`
- **Diagnosis:** After monorepo restructure, `README.md` was at root but `pyproject.toml` was in `backend/`. `[FACT]`
- **Fix:** Copied README into `backend/`. ~2 min. `[FACT]`

### Rabbit hole: `scaleapi/gps-sandbox` monorepo
- Attempted to move the entire project into a corporate monorepo. CI failed because the `fastify` repo's `GITHUB_TOKEN` couldn't access the private `scaleapi` org. Fully reverted. ~30 min wasted. `[FACT]`

## 8. Creativity & Notable Moments

- **Cleverest workflow:** The two-workflow chain where the review bot uses a PAT to post comments (so they trigger `issue_comment` events), and the approval agent has a conditional `if` guard checking for the review marker in the comment body. This creates a clean producer-consumer pattern without direct coupling. `[FACT]`
- **Novel collaboration:** The user used voice transcription for most prompts, creating a "pair programming by conversation" dynamic. The agent had to interpret natural speech with autocorrect artifacts ("Reptile" → Greptile, "Ginger" → Jinja). `[FACT]`
- **"You had to be there" moment:** The agent created PR #8 against the *upstream* `fastify/fastify` repo (6,700+ stars) instead of the fork. Quickly closed, but for a brief moment there was an AI-generated docs PR on a major open-source project. `[FACT]`
- **Test PR design:** Created 5 PRs of intentionally varying quality to test the review bot: from clean docs changes to a file with `eval()`, hardcoded credentials, SQL injection, MD5 hashing, and expired token bypass — all in a fake auth middleware. `[FACT]`

## 9. Timeline

| Time | Milestone |
|------|-----------|
| T+0h (May 2, 11:09) | `f26f663` — Initialize Python project scaffold (pyproject.toml, justfile, ruff, pyright) |
| T+0h15m (11:23) | `54c611f` — Add Greptile-style AI code review agent (review_agent, github client, models, LLM prompt) |
| T+1h35m (12:44) | `43492a1` — Match Greptile review format, add tests (247 LOC test suite), simulation script |
| T+1h46m (12:55) | `f2fff82` — Make approval agent independent from review agent (rule-based, regex parsing) |
| T+1h48m (12:57) | `c36be0d` — Give approval agent its own visual identity (shield emoji, formatted comments) |
| T+2h22m (13:31) | `9869515` — **Major restructure:** monorepo with `backend/` + `dashboard/` (Next.js scaffold, shadcn, all pages) |
| T+2h26m (13:35) | `c09ebd3` — Fix hatchling build (README in backend/) |
| T+2h28m (13:37) | `f134837` — Fix LiteLLM proxy integration (api_base, provider-prefixed model) |
| T+2h44m (13:53) | `514f241` — Fully decouple review and approval agents (separate entry points) |
| ~T+3h–5h | **Rabbit hole:** attempted move to `scaleapi/gps-sandbox`, reverted. Debugged CI auth issues. |
| ~T+20h (May 3, 07:26) | Dashboard running locally, user gives "very ugly" feedback |
| ~T+21h (10:27) | **UI overhaul:** Inter font, shadcn cards, merged PR badges, polished table |
| ~T+21h30m (10:37) | Added PR lifecycle timeline (activity feed with colored dots) |
| ~T+21h45m (10:44) | Fixed approval data on list page (fetching reviews API), timeline dedup |
| ~T+25h (13:08) | Created 5 test PRs of varying quality for demo |
| ~T+26h (now) | Writing this report |

## 10. Honest Self-Reflection `[SUBJECTIVE]`

### What worked
- **Voice-driven prompting** was surprisingly effective for rapid iteration. The user could think out loud and the agent adapted.
- **Two-agent architecture** is genuinely clever for a hackathon — it demonstrates a real production pattern (third-party review tool + custom approval logic).
- **Test coverage** is solid for a hackathon project (39 tests, all passing, covering both agents).
- **The dashboard** went from zero to a polished shadcn UI with live polling in ~2 hours of active work.

### What the team could improve
- **Requirements up front:** The project direction changed several times (Greptile integration → mock, single pipeline → decoupled, same repo → monorepo → reverted). A 10-minute planning session would have saved the rabbit holes.
- **Voice prompts need editing:** Several prompts required follow-up clarification because the voice transcription was ambiguous.
- **Missing `.env.example` for dashboard** and outdated README (says Next 15, using 16) — documentation lagged behind code.

### What the agent did poorly
- **Created a PR against upstream fastify** instead of the fork — should have verified remote target before `gh pr create`.
- **Missed the reviews API gap** initially — the dashboard only searched issue comments for approval data, missing approvals submitted as GitHub reviews. Required user to spot it visually.
- **The `scaleapi/gps-sandbox` rabbit hole** — should have asked about repo access permissions *before* restructuring everything.
- **UI was genuinely ugly on first pass** — the initial dashboard was functional but visually poor. Should have used shadcn components from the start.

### Vibe-coded or autocomplete?
Neither. This was **agent-driven development** — the human provided architecture and taste, the agent wrote all the code. The user never touched a file directly. It's closer to "staff engineer directing a junior" than either vibe-coding or autocomplete. `[SUBJECTIVE]`

## 11. Judge Scorecard (honest first pass)

| Dimension | Score | Justification |
|---|---|---|
| Project usefulness | 7/10 | Solves a real problem (automated PR approval gating) but the review agent is a mock of Greptile, not a production tool. The approval agent is the real value. |
| Code quality | 7/10 | Clean Python with Pydantic models, proper error handling, 39 tests passing. Dashboard TypeScript is clean. Missing: error boundaries, input validation in some places, no frontend tests. |
| Prompting craft | 6/10 | Voice-driven prompts were natural but often vague. The user corrected course multiple times. Best prompts were the architectural ones; worst were the initial rambling voice messages. |
| Human–agent collaboration | 8/10 | Strong dynamic — human steered architecture and taste, agent executed. The user caught real bugs (approval not showing, merged state wrong) that the agent missed. Good division of labor. |
| Creativity of AI usage | 7/10 | The two-workflow chain (PAT-based comment triggering) is clever. Using voice transcription for all prompts is novel. Sub-agents for codebase exploration. Could have used MCPs more (Linear, Figma). |

## 12. Appendix

### File tree (depth ≤ 3)

```
review-bot/
├── README.md
├── VIBE_REPORT.md
├── .gitignore
├── backend/
│   ├── .env.example
│   ├── .python-version
│   ├── README.md
│   ├── justfile
│   ├── pyproject.toml
│   ├── prompts/
│   │   └── review_system.md
│   ├── scripts/
│   │   └── simulate_review.py
│   ├── src/
│   │   ├── main.py
│   │   ├── approval_main.py
│   │   ├── models.py
│   │   ├── review_agent/
│   │   ├── approval_agent/
│   │   └── github/
│   └── tests/
│       ├── test_review_agent.py
│       ├── test_approval_agent.py
│       └── test_models.py
└── dashboard/
    ├── package.json
    ├── next.config.ts
    ├── components.json
    ├── tsconfig.json
    └── src/
        ├── app/
        ├── components/
        └── lib/
```

### `git log --oneline`

```
514f241 refactor: fully decouple review and approval agents
94f178f chore: document private/public LiteLLM endpoint config in .env.example
f134837 fix: use LiteLLM proxy base URL and provider-prefixed model name
c09ebd3 fix: add README.md to backend/ for hatchling build
9869515 restructure: monorepo with backend/ and dashboard/
c36be0d Give approval agent its own visual identity
f2fff82 Make approval agent independent from review agent
43492a1 Match Greptile review format and add tests
54c611f Add Greptile-style AI code review agent
f26f663 Initialize Python project scaffold
```

### Data sources used

| Source | Status |
|--------|--------|
| Session memory (this chat) | Available — used extensively `[FACT]` |
| Conversation summary (pre-summary context) | Available — 30+ user messages reconstructed `[FACT]` |
| Agent transcripts (`agent-transcripts/`) | Available — transcript `e10d11a3` identified as this session `[FACT]` |
| Git history | Available — 10 commits, full stats `[FACT]` |
| Codebase files | Available — all 41 source files read `[FACT]` |
| Tooling fingerprints | Cursor IDE detected (`.cursor/` project directory), no `.claude/` or `AGENTS.md` found `[FACT]` |
| CI/CD logs | Unavailable — GitHub Actions logs not fetched (would require browser/API auth) |
| GitHub PR comments/reviews | Unavailable — not fetched for this report (visible on dashboard) |
