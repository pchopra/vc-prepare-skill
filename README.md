# VC Prepare

**Know your investor before you walk in.**

A [Claude Code skill](https://docs.anthropic.com/en/docs/claude-code/skills) that generates investor meeting briefings. Profile, portfolio, fit assessment, game plan, predicted questions, and alternative investors — all in your terminal.

By [Parth Chopra](https://x.com/pchopra28) and [Tyler Richards](https://x.com/tylerjrichards), powered by [VC Whisper](https://vcwhisper.com).

## Install

In Claude Code:

```
add skill from vcwhisper.com/vc-prepare-skill.md
```

**Alternative:**

```bash
claude skill add --from https://github.com/pchopra/vc-prepare-skill
```

## Usage

```
/vc-prepare example              See a sample briefing (Paul Graham + Flexport)
/vc-prepare Paul Graham           Full investor briefing
/vc-prepare Paul Graham --quick   Quick lookup (no company context)
/vc-prepare Paul Graham --save    Research + save markdown brief
/vc-prepare --setup               Add API keys or update company info
```

### First Time

Run `/vc-prepare example` to see a full briefing instantly. Then the skill asks if you want to set up your company context for personalized briefings.

### Normal Use

```
/vc-prepare Marc Andreessen
```

1. Searches for the investor and confirms identity (LinkedIn, X)
2. Asks about your company (remembers previous answers)
3. Researches the investor (30-60 seconds)
4. Renders the full briefing in your terminal
5. Offers to save as markdown

### Quick Mode

```
/vc-prepare Marc Andreessen --quick
```

Profile, career, portfolio, and tweets only. Skips company context questions — no fit score, no connections.

## What You Get

- **Fit Assessment** — Thesis alignment, portfolio pattern, stage fit, check size. Honest scoring with sub-dimension breakdown.
- **Know Your Investor** — Career path, education, 6-10 portfolio companies, press appearances.
- **Relevant Tweets** — Their tweets and writing matched to your company.
- **Game Plan** — Their style. Connection points. Emphasis points. Predicted questions with suggested approaches. All specific to this investor.
- **Other Investors** — 4-6 similar investors with fit scores and talking points.

## Modes

### Hosted Mode (Default)

Calls the VC Whisper API. Zero API keys needed. Works out of the box.

```
/vc-prepare Paul Graham
```

### Local Mode

Everything runs on your machine. Nothing leaves except direct API calls.

```
/vc-prepare --setup
```

Then choose "API keys" and add your OpenAI key. Optional: Exa (deeper search), xAI (tweet discovery).

| Key | Required | What it adds |
|-----|----------|-------------|
| `OPENAI_API_KEY` | Yes (for local mode) | Synthesis, analysis, game plan |
| `EXA_API_KEY` | No | Neural search, LinkedIn enrichment |
| `XAI_API_KEY` | No | Tweet discovery via Grok |

## Company Context

The skill asks for your company details to personalize the briefing:

1. Company website (optional)
2. Pitch deck file path (optional — reads directly from disk)
3. Call transcripts or notes (optional)

Your context is saved to `~/.vc-decoder/config.json` and reused across briefings. Update anytime with `/vc-prepare --setup` or say "update" when prompted.

## Markdown Export

```
/vc-prepare Marc Andreessen --save
```

Saves to `~/investor-briefs/marc-andreessen.md`. You can also say "save this" after viewing any briefing.

## Architecture

```
/vc-prepare [name]
     |
     v
Investor Search ──> Confirm identity (LinkedIn, X)
     |
     v
Company Context ──> Read config or ask questions
     |
     v
┌─────────────────────────────────────────────┐
│  Hosted Mode          │  Local Mode         │
│  POST /api/prepare    │  Parallel subagents │
│  (30-60s, zero setup) │  + OpenAI synthesis │
└─────────────────────────────────────────────┘
     |
     v
Terminal Rendering ──> Markdown Export (optional)
```

## Based On

Forked from [cruhl/vc-prepare](https://github.com/cruhl/vc-prepare) by [Connor](https://github.com/cruhl). The original skill uses parallel subagents for fully local research with PDF rendering. This fork adds hosted API mode, onboarding, config persistence, fit score breakdown, connection points, and markdown export.

## License

MIT
