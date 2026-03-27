---
name: vc-prepare
description: >
  Investor meeting prep briefing. Researches an investor using parallel
  subagents and generates a structured JSON briefing (schema.json), then
  renders it as beautiful CLI output and optionally as a print-ready PDF
  via render.py. Handles missing data gracefully: every field is optional.
  Use when preparing for VC meetings, investor calls, pitch practice, or
  when the user mentions meeting an investor. Also triggers on "prep",
  "investor research", "who is [investor]", or "meeting with [investor]".
argument-hint: "[investor-name]"
---

# VC Prepare: Investor Meeting Briefing

Research an investor, produce a structured JSON briefing, render it as
terminal output, and optionally generate a print-ready PDF. The JSON
schema (`schema.json` in this skill directory) is the single source of
truth for all output formats. Every field is optional; both the CLI
renderer and the PDF renderer degrade gracefully when data is missing.

## Invocation

```
/vc-prepare Paul Graham
/vc-prepare example
```

Or Claude auto-triggers when the user mentions preparing for an investor
meeting.

## Example Mode

If the argument is `example` or `try with an example`, run the full
briefing for **Paul Graham** with this company context:

> VC Whisper (vcwhisper.com). AI-powered investor research tool for
> founders. Paste a pitch transcript or enter an investor name, and get
> a full briefing: career history, portfolio, relevant tweets, game plan,
> and predicted questions. Built using Exa, Seedlist, xAI, and
> Browserbase. 62K people watched the launch on X. Pre-seed, raising $1.5M.

Yes, we're using VC Prepare to prep a pitch for VC Prepare itself.

This demonstrates the complete flow: parallel research, JSON assembly,
CLI rendering with fit score, and PDF offer.

## Input Gathering

1. **Parse `$ARGUMENTS` for the investor name.** If no name is provided,
   ask: "Which investor are you meeting with?"

2. **Ask for company context.** This is the most important step for
   briefing quality. A tailored briefing is 10x more useful than a
   generic one. Ask:

   > I can generate a general briefing, but the real value is when I
   > tailor it to your company. Can you share:
   >
   > 1. What does your company do? (one line)
   > 2. Company website (if you have one)
   > 3. What stage are you at, and how much are you raising?
   >
   > I can also read your pitch deck if you point me to the file path.
   > Or just say "go" and I'll research the investor without tailoring.

   If the user provides context, ask 2-3 quick follow-ups to sharpen
   the game plan. Choose from these based on what's still unknown:

   > A few more to make the game plan sharp:
   >
   > 4. What's your traction? (users, revenue, growth, anything concrete)
   > 5. What's your moat or unfair advantage?
   > 6. What's the biggest objection an investor might raise?
   > 7. Have you talked to this investor or their firm before?

   Don't ask all of them. Skip any that are already answered by
   conversation context, the pitch deck, or the company website.
   Two follow-up questions max. Move fast.

   If the user says "go" or provides nothing, generate a general-purpose
   briefing (no fit score, no "Relevant to Your Pitch" section).

3. **Absorb conversation context.** If the user has already been
   discussing their startup, has a pitch deck open, or has mentioned
   their company in this session, use that context automatically. Don't
   re-ask for information that's already available.

4. **Read local files.** If a pitch deck PDF path is provided, read it
   with the Read tool. If a DocSend link is provided, WebFetch it (or
   use Browserbase if available). No upload needed, no file size limits.

5. **Check for prior correspondence.** If Gmail MCP tools are available,
   search for prior email threads with this investor or their firm.
   Summarize any existing relationship context (warm intro chains, prior
   conversations, commitments made). If not available, skip silently.

6. **Check calendar context.** If Google Calendar MCP tools are
   available, look up the meeting event for additional context: other
   attendees from the firm (research all of them), meeting notes in the
   event description, whether this is a first meeting or follow-up. If
   not available, skip silently.

## API Key Detection

Check for these environment variables using Bash (`echo $VAR_NAME`).
Each one unlocks richer data for specific sections. **All are optional.**
The skill works without any of them using only WebSearch and WebFetch.

| Variable | Service | What it enriches |
|----------|---------|------------------|
| `EXA_API_KEY` | [Exa](https://exa.ai) | Career path, LinkedIn enrichment, deeper search |
| `XAI_API_KEY` | [xAI / Grok](https://x.ai) | Tweet discovery, tweet relevance ranking |
| `BROWSERBASE_API_KEY` | [Browserbase](https://browserbase.com) | Headless browser for blocked pages |

Seedlist (seedlist.com) requires no API key. Its data is free, static JSON
served from `seedlist.com`. The skill uses it automatically when researching
portfolio data. Attribution: link back to seedlist.com when showing results.

If any API keys are detected, ask before using them:

> I found API keys for Exa and xAI. Want me to use them for richer
> data, or stick with web search only?

If the user confirms, report which sources are active:

```
Data sources: WebSearch + WebFetch (default)
  + Exa (career enrichment)
  + xAI (tweet ranking)
```

If the user declines, proceed with WebSearch + WebFetch only.

### Exa API (when `EXA_API_KEY` is set)

```bash
curl -s "https://api.exa.ai/search" \
  -H "x-api-key: $EXA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "'\''Paul Graham'\'' venture capital partner career",
    "type": "neural",
    "numResults": 10,
    "contents": { "text": { "maxCharacters": 2000 } }
  }'
```

Also query for LinkedIn: same endpoint, query
`"'Paul Graham' site:linkedin.com/in"`, numResults 3, maxCharacters 3000.

### xAI API (when `XAI_API_KEY` is set)

Use the Responses API with the `x_search` tool for tweet discovery:

```bash
curl -s "https://api.x.ai/v1/responses" \
  -H "Authorization: Bearer $XAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "grok-4-1-fast-non-reasoning",
    "input": [{
      "role": "user",
      "content": "Find recent tweets from Paul Graham (@paulg) about startups, investing, technology. Return tweet text, date, and URL for each."
    }],
    "tools": [{
      "type": "x_search",
      "allowed_x_handles": ["paulg"]
    }]
  }'
```

The response includes `annotations` with `type: "url_citation"` containing
tweet URLs. The `x_search` tool supports `allowed_x_handles` (max 10),
`from_date`, and `to_date` parameters.

If company context exists, run a second query without `allowed_x_handles`
to find tweets from ANY account relevant to the investor + industry.

### Seedlist (no API key needed)

Seedlist serves free static JSON. No auth, no rate limits. Download and
filter client-side:

```bash
# Full investor index (~400KB)
curl -s "https://seedlist.com/enrichment-index.json" | \
  python3 -c "
import sys, json
data = json.load(sys.stdin)
matches = [i for i in data if 'paul graham' in i.get('name','').lower()]
print(json.dumps(matches, indent=2))
"
```

Each investor object has: `name`, `slug`, `firm`, `firm_name`, `role`,
`location`, `stage_focus`, `sector_focus`, `check_size`, `last_active`,
`thesis_summary`.

Other useful endpoints:
- `seedlist.com/investor-lookup.json` (slug-keyed O(1) lookup)
- `seedlist.com/investor-graph.json` (co-investment graph)
- `seedlist.com/startup-investor-map.json` (startup-to-investor map)
- `seedlist.com/rounds-feed.json` (500 most recent rounds)

Attribution: link back to seedlist.com when showing results.

### Browserbase (when `BROWSERBASE_API_KEY` is set)

Create a headless browser session for pages that block WebFetch:

```bash
curl -s -X POST "https://api.browserbase.com/v1/sessions" \
  -H "Content-Type: application/json" \
  -H "X-BB-API-Key: $BROWSERBASE_API_KEY" \
  -d '{}'
```

Returns a session with `connectUrl` (WebSocket for Playwright). Use for
LinkedIn profiles, DocSend decks, and other bot-blocked pages. Only invoke
when WebFetch fails on a URL.

## Research Phase

**CRITICAL: Use the Agent tool to launch 3-4 parallel subagents.**
Do NOT do all searches sequentially in the main thread. Each subagent
runs its own cluster of searches and returns structured partial data.
The main thread assembles the final JSON from all subagent results.

### Subagent Split

**Agent 1: Career + LinkedIn + Education**

Searches:
- `"{INVESTOR_NAME}" venture capital partner career biography`
- `"{INVESTOR_NAME}" site:linkedin.com/in`
- `"{INVESTOR_NAME}" education university degree`

WebFetch the LinkedIn profile, personal website, and fund team page.
Return: `career` array, `education` array, `investor.about`,
`investor.role`, `investor.fund`, `investor.linkedin`, `investor.website`.

**Agent 2: Portfolio + Fund Details + Seedlist**

Searches:
- `"{INVESTOR_NAME}" portfolio investments crunchbase`
- `"{FUND_NAME}" fund size AUM`
- `"{INVESTOR_NAME}" notable investments exits`
- Seedlist API call (if key available)

WebFetch Crunchbase, AngelList, or fund portfolio page.
Return: `portfolio` array, `investor.fundSize`, `investor.sweetSpot`,
`investor.stageFocus`.

**Agent 3: Tweets + Press + News**

Searches:
- `"{INVESTOR_NAME}" site:x.com OR site:twitter.com`
- `"{INVESTOR_NAME}" interview podcast panel 2025 OR 2026`
- `"{INVESTOR_NAME}" investment thesis blog interview`
- xAI API call (if key available)

WebFetch the investor's blog/essays and interview transcripts.
Return: `recentTweets` array, `press` array, `investor.twitter`,
partial `gamePlan.howTheyThink` notes.

**Agent 4 (only when company context exists): Industry Overlap**

Searches:
- `"{INVESTOR_NAME}" {INDUSTRY_KEYWORDS}`
- `"{FUND_NAME}" portfolio {INDUSTRY}`
- `"{INVESTOR_NAME}" {COMPANY_DESCRIPTION_KEYWORDS}`
- `"{INVESTOR_NAME}" anti-portfolio OR "passed on"`

Return: `relevantContent` array, `gamePlan.avoid` items, raw notes
for fit score calculation.

### After Subagents Complete

The main thread:
1. Merges all partial data into a single briefing object
2. Synthesizes `gamePlan` (howTheyThink, connections, predictedQuestions,
   avoid) from the combined research
3. Calculates `fitScore` (if company context exists)
4. Generates `otherInvestors` recommendations
5. Builds the `quickReference` card
6. Writes the complete JSON to disk

## JSON Output

Write the assembled briefing to:

```
/tmp/vc-prepare-{investor-slug}.json
```

Where `{investor-slug}` is the investor name lowercased with spaces
replaced by hyphens (e.g., `paul-graham`).

The JSON must conform to `schema.json` in the skill directory. Key rules:

- **Every field is optional.** Omit fields with no data rather than
  including empty strings or empty arrays.
- The only required field is `investor.name`.
- `fitScore` and `relevantContent` should only be present when company
  context was provided.
- `meta.dataSources` should list every source actually used.
- `meta.companyContext` should be `true` or `false`.

## CLI Output

After writing the JSON, render it as beautiful terminal markdown.
Read the JSON back and transform it section by section.

### Graceful Degradation Rules

These rules are non-negotiable:

- **If a section has no data, skip it entirely.** Never print "No data
  available", "Information not found", or empty section headers. Just
  omit the section.
- If `career` is empty but `investor.about` exists, show the bio under
  the investor header instead of a career section.
- If `recentTweets` is empty, skip the tweets section.
- If no company context was provided, skip Fit Score and Relevant to
  Your Pitch entirely.
- If `education` is empty, skip it. Many successful investors dropped
  out or have no public education records.
- If `press` is empty, skip Press & Appearances.
- If `gamePlan.connections` is empty, skip Where You Connect.
- **Always show at minimum:** investor name/role/fund, game plan
  (howTheyThink + predictedQuestions), other investors, quick reference.
- **Always end with the quick reference card** (compact summary for
  glancing at during the call).

### Output Structure

```markdown
# {INVESTOR_NAME}

**{Role} . {Fund}**
[LinkedIn]({url}) . [X]({url})

{Fund size} . {Sweet spot} . {Stage focus}

---

## {N}% Fit

{2-3 sentence explanation. Honest: a low score with reasoning beats an
inflated number.}

---

## Know Your Investor

### Career Path

- **{Role}, {Company}** ({startYear}-{endYear})
  {note}

- **{Degree}** -- {Institution}

### Portfolio Companies

| Company | Stage | Category | Date | Status |
|---------|-------|----------|------|--------|
| {Name} | {Seed/A/B} | {categories} | {date} | {status} |

### Press & Appearances

- **{Title}** -- {Source} ({Date})
  {summary}

---

## Relevant to Your Pitch

> "{text}"
> -- {source} . {date}

{relevance explanation}

---

## Recent Tweets

> "{text}"
> -- @{handle} . {date}

---

## Your Game Plan

### How They Think

{howTheyThink paragraph}

### Where You Connect

- **{title}**
  {detail}

### They'll Probably Ask

- **"{question}?"**
  {suggestedApproach}

### Don't Say

- **Avoid: {topic}**
  {reason}

---

## Other Investors to Talk To

**{Name}** . {Fund} . {fit}% fit
{why}
Lead with: {talkingPoint}

---

## Quick Reference Card

**{INVESTOR_NAME}** . {Fund} . {Stage} . {Sweet spot}
Thesis: {oneLinerThesis}
Style: {oneLinerStyle}
Top 3 questions: {topQuestions}
Your 3 proof points: {proofPoints}
Don't say: {doNotSay}
```

## PDF Output

After presenting the CLI briefing, offer:

> "Want a print-ready PDF?"

If the user says yes:

```bash
python3 ${CLAUDE_SKILL_DIR}/render.py /tmp/vc-prepare-{slug}.json
```

This produces `/tmp/vc-prepare-{slug}.pdf` and opens it.

If `render.py` is not available or fails, fall back:

1. Tell the user to open the HTML file in a browser and print to PDF.
   The HTML template at `${CLAUDE_SKILL_DIR}/templates/briefing.html`
   has `@media print` CSS that produces clean output.
2. If no HTML was generated either, the JSON file at
   `/tmp/vc-prepare-{slug}.json` is the portable artifact.

## Post-Meeting Follow-Up

If the user returns to the conversation after the meeting, offer:

> "How did it go? I can help with:"
> 1. Draft a follow-up email referencing what was discussed
> 2. Create calendar events for follow-up deadlines
> 3. Capture action items from the meeting

If Gmail MCP tools are available, draft and save the follow-up email
directly in Gmail. If Google Calendar MCP tools are available, create
follow-up events on the user's calendar.

## Quality Checklist

Before presenting the briefing, silently verify:

- Every section has real, verified data (not hallucinated)
- Career path has actual years and role titles from a real source
- Portfolio companies are real, verified investments
- Tweets and quotes have attributed sources and dates
- Game plan reflects THIS investor's specific style, not generic advice
- "They'll Probably Ask" questions are specific to this investor's
  known interests and patterns
- "Don't Say" items cite specific evidence
- Other investors are real people at real, active funds
- If fit score is included, the reasoning is honest and calibrated
- No section is padded with generic filler
- Quick reference card is genuinely useful for glancing at during a call

Never fabricate portfolio companies, career history, quotes, or tweets.

## Error Handling

- If WebSearch returns no results for a query, try 2-3 alternative
  phrasings before giving up on that data. Example: if
  `"Jane Smith" venture capital` fails, try `"Jane Smith" investor`
  or `"Jane Smith" {fund name}`.
- If an API key is set but the call fails, fall back to WebSearch and
  note the fallback briefly in `meta.dataSources`.
- If the investor is very obscure, say so honestly. Suggest the user
  provide a LinkedIn URL or fund website to improve results. Still
  produce whatever briefing is possible with the data found.
- Never fabricate data to fill gaps. Missing data is better than
  wrong data.
- If a WebFetch fails on a URL, try an alternative source rather than
  skipping the section entirely.
- If `render.py` fails or is missing, tell the user to open the HTML
  in a browser and print. The `@media print` CSS produces identical
  output to the PDF renderer.
