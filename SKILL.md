---
name: vc-prepare
description: >
  Investor meeting prep briefing. Researches an investor and generates a
  structured briefing with profile, portfolio, fit assessment, game plan,
  and alternative investors. Use when the user types /vc-prepare [investor],
  /vc-prepare example, /vc-prepare --setup, or /vc-prepare --quick [name].
  Also triggers on "prep me for [investor]", "investor brief for [name]",
  or "prepare for meeting with [name]".
argument-hint: "[investor-name | example | --setup | --quick name]"
---

# VC Prepare: Investor Meeting Briefing

Research an investor, produce a structured briefing, and render it in the
terminal. Supports **hosted mode** (calls the VC Decoder API, zero setup)
and **local mode** (user's own API keys, full privacy). Every section
degrades gracefully when data is missing.

## Commands

```
/vc-prepare example              See a sample briefing (Paul Graham + Flexport)
/vc-prepare [name]               Full investor briefing
/vc-prepare [name] --quick       Quick lookup (no company context)
/vc-prepare [name] --save        Research + save markdown brief
/vc-prepare --setup              Add API keys or update company info
```

## Argument Parsing

Parse `$ARGUMENTS` to determine the command:

- `example` → Example mode (Section 1)
- `--setup` → Setup mode (Section 8)
- `--quick [name]` → Quick mode (skip company context, no fit score)
- `--save [name]` → Full research + auto-save markdown
- `[name]` → Full briefing (default)
- Empty → Ask: "Which investor are you meeting with?"

## Section 0: First-Install Welcome

On first invocation (no `~/.vc-decoder/config.json` exists), show:

```
Welcome to VC Prepare — investor meeting prep in your terminal.

Commands:
  /vc-prepare example         See a sample briefing (Paul Graham + Flexport)
  /vc-prepare [name]          Full investor briefing
  /vc-prepare [name] --quick  Quick lookup (no company context)
  /vc-prepare [name] --save   Research + save markdown brief
  /vc-prepare --setup         Add API keys or update company info

Powered by VC Whisper (vcwhisper.com)
```

Then proceed with whatever command was invoked.

## Section 1: Example Mode

If the argument is `example`, render the cached Paul Graham + Flexport
briefing instantly. No API call needed — the data is embedded below.

Use the exact rendering format from Section 6 (Terminal Rendering) with
this data:

**Profile:**
- Name: Paul Graham
- Fund: Y Combinator
- Role: Co-founder
- About: Computer scientist, essayist, and co-founder of Y Combinator. Created the first web-based application (Viaweb). Known for essays on startups, programming, and technology. Funded companies like Airbnb, Stripe, Dropbox, and Reddit.
- LinkedIn: https://www.linkedin.com/in/paulgraham/
- X: https://x.com/paulg
- Sweet spot: $500K

**Career:**
- Co-founder, Y Combinator (2005–2014) — funded 2,000+ startups
- Co-founder & CEO, Viaweb (1995–1998) — acq. by Yahoo for $49M
- Essayist, paulgraham.com (2001–present)

**Education:** PhD Computer Science, Harvard University

**Portfolio:**
| Company | Stage | Categories | Date |
|---------|-------|------------|------|
| Stripe | Seed | Fintech, Payments | 2010 |
| Airbnb | Seed | Marketplace, Travel | 2009 |
| Dropbox | Seed | SaaS, Cloud Storage | 2007 |
| Reddit | Seed | Social, Community | 2005 |
| Instacart | Seed | Marketplace, Logistics | 2012 |
| Twitch | Seed | Media, Streaming | 2007 |

**Fit Assessment: 87%**
PG has written extensively about startups that look boring but are actually huge ("schlep blindness"). A licensed customs brokerage modernized with software is a textbook PG-thesis company: an unsexy, regulated industry with massive TAM, a founder with 12 years of domain expertise, and a distribution moat (300M shipping manifests).

**Fit Breakdown:**
- Thesis Alignment: 92% — PG's thesis centers on founders with deep domain expertise building software for unsexy industries — customs brokerage is a textbook match.
- Portfolio Pattern: 85% — Strong pattern match with Stripe (regulated fintech), Flexport (logistics), and Instacart (operationally heavy) — all YC companies that digitized complex, real-world workflows.
- Stage Fit: 90% — PG and YC specialize in seed-stage companies with working products and early traction, which matches your current stage perfectly.
- Check Size Fit: 80% — YC standard deal is $500K for 7%, plus MFN on the $375K safe. Your raise size aligns with YC-backed seed rounds, though PG's personal checks vary.

**Game Plan:**
- Style: Paul Graham fires rapid questions to understand the core business within 60 seconds. He values conciseness over polish — if you can't explain it simply, he'll assume you don't understand it. He gets visibly excited about unsexy, regulated industries being eaten by software, and he probes hard on "why now" and "why you." Don't present slides — just have a conversation.
- Emphasis:
  1. You own the customer list — PG obsesses over distribution advantages. "We have every importer in America in a database" is your strongest hook.
  2. Regulatory moat as an asset — He's written that the biggest opportunities hide behind things people don't want to deal with. Your customs license is that barrier.
  3. The "why now" is crisp — The 2007 rule change enabling remote clearance explains both why no one did this before and why it's possible today.
- Connections:
  1. YC customs alum — Flexport went through YC in W14 and PG was still actively advising. Mentioning YC signals you're in his tribe.
  2. Schlep blindness essay — PG's 2012 essay describes exactly what you're doing. Reference it directly.
  3. Regulatory moat portfolio pattern — Stripe had banking regs, Airbnb had housing laws. Position your customs license as the same playbook.
- Questions:
  1. "So what do you actually do?" — PG always opens with this. Try: "We're a licensed customs broker, but instead of fax machines, importers use our web app."
  2. "Why hasn't anyone done this before?" — Hit three beats: industry is 40 years behind, heavily licensed, and until 2007 you couldn't clear remotely.
  3. "How do you get customers if they already have brokers?" — Lead with the 300M manifests database — you know who every importer is.
  4. "What's the bigger play here?" — Customs brokerage is your wedge into the broader logistics stack.

**Recent Tweets:**
- "The most common mistake founders make is to solve problems no one has." — @paulg, Feb 2026
- "Schlep blindness is the single biggest source of overlooked startup ideas." — @paulg, Dec 2025

**Relevant Tweets:**
- "Schlep blindness is the single biggest source of overlooked startup ideas. People avoid the hard, boring stuff — and that's where the money is." — @paulg, Dec 2025
- "The best startup ideas look like bad ideas at first. Customs brokerage software? That's exactly the kind of thing that turns into a $10B company." — @paulg, Nov 2025

**Press:**
- "Paul Graham on Why Great Founders Think Differently" — youtube.com, Jan 2026
- "Y Combinator's Paul Graham: The Art of Fundraising" — theinformation.com, Nov 2025

**Other Investors:**
| Name | Fund | Fit | Why |
|------|------|-----|-----|
| Josh Wolfe | Lux Capital | 78% | Backs unsexy, hard-tech infrastructure plays |
| Ben Lerer | Lerer Hippeau | 72% | Operator-investor who favors durable value |
| Miriam Rivera | Ulu Ventures | 68% | Data-driven seed investor |
| Ali Hamed | CoVenture | 65% | Invests in fintech infrastructure |

After rendering the example, ask:

> "Want to set up your company context for personalized briefings? (30 seconds, everything optional)"

If yes, proceed to company context questions (Section 3).

## Section 2: API Key Detection

Check for environment variables using Bash:

```bash
echo "EXA:${EXA_API_KEY:+set}" "XAI:${XAI_API_KEY:+set}" "OPENAI:${OPENAI_API_KEY:+set}"
```

- If `OPENAI_API_KEY` is set, local mode is available
- `EXA_API_KEY` and `XAI_API_KEY` are optional enrichments for local mode
- These are only relevant for local mode or `--setup`

## Section 3: Company Context

After confirming the investor (Section 4), gather company context:

**If `~/.vc-decoder/config.json` exists:**

Read the config and show a summary:

> "I have your previous context on file:
> - Website: {companyWebsite}
> - Pitch deck: uploaded {updatedAt date}
> - Transcripts: {count}
>
> Use this? Or say 'update' to change anything."

If user says yes → proceed with saved context.
If user says update → ask which field to change, update config.

**If no config exists:**

Ask via AskUserQuestion:

> "I can generate a general briefing, but the real value is when I tailor
> it to your company. Can you share:
>
> 1. What's your company website? (optional)
> 2. Do you have a pitch deck? Provide a file path (optional)
> 3. Any call transcripts or notes from prior meetings? (optional)
>
> Or just say 'go' to skip all of this."

Save answers to `~/.vc-decoder/config.json`:

```json
{
  "apiUrl": "https://vcwhisper.com",
  "mode": "hosted",
  "companyWebsite": "",
  "pitchDeckText": "",
  "transcripts": [],
  "keys": {},
  "createdAt": "ISO-8601",
  "updatedAt": "ISO-8601"
}
```

If user provides a pitch deck file path:
1. Read the file with the Read tool
2. In hosted mode: call `POST {apiUrl}/api/prepare/parse-deck` with `{ pitchDeckBase64: base64_content }` to extract text
3. In local mode: read the PDF directly and extract text
4. Store the extracted text in config as `pitchDeckText`

**In `--quick` mode:** Skip company context entirely. No fit score,
no connections, no "Relevant to Your Pitch" section.

## Section 4: Investor Search and Confirmation

1. Take the investor name from `$ARGUMENTS`
2. Call the search API:

```bash
curl -s -X POST "{apiUrl}/api/prepare/search-investors" \
  -H "Content-Type: application/json" \
  -d '{"query": "INVESTOR_NAME"}'
```

Response: `{ results: [{ investor_id, name, fund, stage_focus, linkedin, x_link }] }`

3. **If 1 result:** Show and confirm:
   > "{Name} — {Fund}
   > LinkedIn: {linkedin}
   > X: {x_link}
   >
   > Is this the right investor? (y/n)"

4. **If multiple results:** Show numbered list, ask which one.

5. **If 0 results:** Ask:
   > "No results found for '{name}'. Want to provide their LinkedIn or X handle manually?"

6. User can edit/override LinkedIn and X URLs before confirming.

7. Map fields: `x_link` → `investorTwitter`, `linkedin` → `investorLinkedin`

## Section 5: Research (Hosted Mode)

This is the default mode. No API keys needed.

1. Read config from `~/.vc-decoder/config.json` (if exists)
2. Show progress: "Researching {investor name}... this usually takes 30-60 seconds."
3. Call the prepare API:

```bash
curl -s -X POST "{apiUrl}/api/prepare" \
  -H "Content-Type: application/json" \
  -d '{
    "investorName": "INVESTOR_NAME",
    "investorId": "ID_IF_AVAILABLE",
    "investorLinkedin": "LINKEDIN_URL",
    "investorTwitter": "TWITTER_URL",
    "companyWebsite": "WEBSITE_FROM_CONFIG",
    "pitchDeckText": "TEXT_FROM_CONFIG",
    "transcripts": ["TRANSCRIPT_TEXTS"]
  }'
```

4. Set timeout to 120 seconds. If exceeded: "Research is taking longer than usual. The API may be under heavy load."
5. Parse response → render terminal output (Section 6)

Response shape:
```json
{
  "success": true,
  "knowYourInvestor": {
    "profile": { "name", "fund", "role", "about", "linkedin", "twitter", "fundSize", "sweetSpot" },
    "career": [{ "role", "company", "period", "note" }],
    "education": { "degree", "school" },
    "investments": [{ "companyName", "description", "stage", "categories", "date", "url", "source", "round" }],
    "tweets": [{ "text", "url", "date", "author" }],
    "relevantTweets": [{ "text", "url", "date", "author" }],
    "press": [{ "title", "url", "source", "date", "snippet" }]
  },
  "gamePlan": {
    "style": "",
    "overlapScore": 85,
    "overlapWhy": "",
    "emphasis": [{ "title", "detail" }],
    "questions": [{ "question", "detail" }],
    "connections": [{ "title", "detail" }],
    "fitBreakdown": {
      "thesisAlignment": { "score": 90, "explanation": "" },
      "portfolioPattern": { "score": 85, "explanation": "" },
      "stageFit": { "score": 80, "explanation": "" },
      "checkSizeFit": { "score": 75, "explanation": "" }
    }
  },
  "otherInvestors": [{ "name", "fund", "fit", "why", "talkingPoint", "contact" }]
}
```

## Section 5b: Research (Local Mode)

Only available when `config.mode === "local"` and `config.keys.openai` is set.

Use Claude Code tools for research:

**Launch 3-4 parallel subagents using the Agent tool:**

**Agent 1: Career + LinkedIn + Education**
- WebSearch: `"{INVESTOR_NAME}" venture capital partner career biography`
- WebSearch: `"{INVESTOR_NAME}" education university degree`
- WebFetch: LinkedIn profile, personal website, fund team page
- Return: career array, education, investor profile fields

**Agent 2: Portfolio + Fund Details**
- WebSearch: `"{INVESTOR_NAME}" portfolio investments crunchbase`
- WebSearch: `"{FUND_NAME}" fund size AUM`
- WebSearch: `"{INVESTOR_NAME}" notable investments exits`
- WebFetch: Crunchbase, fund portfolio page
- If `config.keys.exa`: use Exa API for deeper search:
  ```bash
  curl -s "https://api.exa.ai/search" \
    -H "x-api-key: $EXA_API_KEY" \
    -H "Content-Type: application/json" \
    -d '{"query": "INVESTOR_NAME venture capital", "type": "neural", "numResults": 10, "contents": {"text": {"maxCharacters": 2000}}}'
  ```
- Return: portfolio array, fund details

**Agent 3: Tweets + Press + News**
- WebSearch: `"{INVESTOR_NAME}" site:x.com OR site:twitter.com`
- WebSearch: `"{INVESTOR_NAME}" interview podcast panel 2025 OR 2026`
- If `config.keys.xai`: use xAI Responses API:
  ```bash
  curl -s "https://api.x.ai/v1/responses" \
    -H "Authorization: Bearer $XAI_API_KEY" \
    -H "Content-Type: application/json" \
    -d '{"model": "grok-4-1-fast-non-reasoning", "input": [{"role": "user", "content": "Find recent tweets from INVESTOR_NAME about startups, investing. Return tweet text, date, URL."}], "tools": [{"type": "x_search"}]}'
  ```
- Return: tweets array, press array

**Agent 4 (only with company context): Industry Overlap**
- WebSearch: `"{INVESTOR_NAME}" {INDUSTRY_KEYWORDS}`
- WebSearch: `"{FUND_NAME}" portfolio {INDUSTRY}`
- Return: relevant content, connection points

After subagents complete, the main thread:
1. Merges all partial data
2. Synthesizes game plan (style, overlap, emphasis, questions, connections, fitBreakdown) — use OpenAI API:
   ```bash
   curl -s "https://api.openai.com/v1/chat/completions" \
     -H "Authorization: Bearer $OPENAI_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{"model": "gpt-4o", "messages": [{"role": "system", "content": "GAME_PLAN_PROMPT"}, {"role": "user", "content": "RESEARCH_DATA + COMPANY_CONTEXT"}]}'
   ```
3. Generates other investor recommendations
4. Renders terminal output (Section 6)

Sections requiring proprietary data (Seedlist investments, VECK tracking)
are omitted in local mode.

## Section 6: Terminal Rendering

Render the briefing as markdown in the terminal. Follow these rules:

**Graceful degradation (non-negotiable):**
- If a section has no data, show "No data found." under the header.
- Always show at minimum: investor name/role/fund, game plan, other investors.
- Fit Score and Connections only appear when company context was provided.

**Format:**

```markdown
# {INVESTOR_NAME}

**{Role} · {Fund}**
[LinkedIn]({url}) · [X]({url})

{Fund size} · {Sweet spot} · {Stage focus}

---

## Fit Assessment: {N}%

{overlapWhy — 2-3 sentences}

| Dimension | Score | Detail |
|-----------|-------|--------|
| Thesis Alignment | {X}% | {explanation} |
| Portfolio Pattern | {X}% | {explanation} |
| Stage Fit | {X}% | {explanation} |
| Check Size Fit | {X}% | {explanation} |

---

## Know Your Investor

### Career Path

- **{Role}, {Company}** ({period})
  {note}

### Education

- **{Degree}** — {Institution}

### Portfolio Companies

| Company | Stage | Categories | Date |
|---------|-------|------------|------|
| {Name} | {Stage} | {categories} | {date} |

### Press & Appearances

- **{Title}** — {Source} ({Date})
  {snippet}

---

## Relevant Tweets

> "{text}"
> — @{author} · {date}

{relevance to your company, if company context exists}

---

## Your Game Plan

### Style
{style paragraph}

### Connections
- **{title}**
  {detail}

### Emphasis Points
- **{title}**
  {detail}

### They'll Probably Ask
- **"{question}?"**
  {detail}

---

## Other Investors to Consider

| Name | Fund | Fit | Why |
|------|------|-----|-----|
| {Name} | {Fund} | {fit}% | {why} |

**{Name}** — {Fund} · {fit}% fit
{talkingPoint}

---
```

## Section 7: Markdown Export

Triggered by `--save` flag or when user says "save this" after viewing results.

**Slug:** lowercase investor name, spaces → hyphens, strip special chars
(e.g., "Marc Andreessen" → `marc-andreessen`)

**Path:** `~/investor-briefs/{slug}.md`

**Create directory** `~/investor-briefs/` if it doesn't exist.

**Overwrite** on collision (same investor = updated brief).

Use the same rendering format as Section 6, with an added header:

```markdown
# Investor Brief: {name}
**{role} at {fund}** | Generated {YYYY-MM-DD}

[... same sections as terminal rendering ...]
```

After saving, confirm: "Saved briefing to ~/investor-briefs/{slug}.md"

## Section 8: Setup (`/vc-prepare --setup`)

Interactive setup for API keys and company info.

1. Read existing `~/.vc-decoder/config.json` (if exists)
2. Show current config summary
3. Ask via AskUserQuestion:

> "What would you like to update?
>
> A) Company info (website, pitch deck, transcripts)
> B) API keys (for local privacy mode)
> C) API URL (default: https://vcwhisper.com)
> D) Switch mode (hosted ↔ local)"

**For API keys (option B):**

> "Local mode runs everything on your machine. Required:
>
> - OpenAI API key (required for local mode)
>
> Optional (enrich results):
> - Exa API key — deeper search, LinkedIn enrichment
> - xAI API key — tweet discovery via Grok
>
> Paste your OpenAI key (or press enter to skip):"

Save keys to `config.keys.openai`, `config.keys.exa`, `config.keys.xai`.
If `config.keys.openai` is set, set `config.mode = "local"`.

## Section 9: Error Handling

| Scenario | Response |
|----------|----------|
| API unreachable / timeout (>120s) | "Could not reach the VC Decoder API. Check your internet connection." |
| API returns 500 | "The research service encountered an error. Try again in a minute." |
| API returns `success: false` | Show the error message from the API |
| 0 search results | Ask for manual LinkedIn/X URLs |
| Pitch deck file not found | "File not found at {path}. Check the path and try again." |
| Pitch deck >10MB | "Pitch deck is too large (>10MB). Try a compressed version." |
| Config corrupted | Delete `~/.vc-decoder/config.json` and re-onboard |
| Missing investor name | Ask: "Which investor are you meeting with?" |

## Section 10: Post-Meeting Follow-Up

If the user returns to the conversation after the meeting, offer:

> "How did it go? I can help with:
> 1. Draft a follow-up email referencing what was discussed
> 2. Create action items from the meeting
> 3. Note feedback for your next pitch"

## Quality Checklist

Before presenting any briefing, silently verify:

- Every section has real, sourced data (not hallucinated)
- Career entries have actual years and titles from a real source
- Portfolio companies are verified investments
- Tweets have attributed sources and dates
- Game plan reflects THIS investor's specific style
- "They'll Probably Ask" questions are specific to this investor
- Connections cite specific evidence (a shared alma mater, adjacent portfolio company, etc.)
- Other investors are real people at real, active funds
- Fit score reasoning is honest and calibrated
- No section is padded with generic filler

Never fabricate portfolio companies, career history, quotes, or tweets.
