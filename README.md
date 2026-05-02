# review-bot

AI-powered PR review and approval bot — Hackathon project.

## Structure

```
backend/    Python agents (review + approval)
dashboard/  Next.js dashboard for visualizing runs
```

### Backend

The review agent fetches PR diffs, analyzes them with an LLM (via LiteLLM), and posts Greptile-style review summaries. The approval agent reads those reviews and auto-approves PRs with no blocking issues.

```bash
cd backend
uv sync
just test
```

### Dashboard

Next.js 15 app that pulls PR review data live from the GitHub API.

```bash
cd dashboard
cp .env.example .env.local   # add your GITHUB_TOKEN
npm install
npm run dev
```
