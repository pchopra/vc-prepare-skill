#!/bin/bash
# Generate example outputs by running the vc-prepare skill through Claude Code.
#
# This script invokes Claude Code in non-interactive mode, telling it to
# run the full vc-prepare pipeline: research the investor, assemble JSON,
# render CLI output, and generate a PDF. All three artifacts are saved
# to examples/.
#
# Requirements:
#   - Claude Code CLI (`claude`) installed and authenticated
#   - Python 3 (for render.py PDF generation)
#   - Internet access (for WebSearch/WebFetch during research)
#
# Usage:
#   ./generate-examples.sh                              # Generate all default examples
#   ./generate-examples.sh "Paul Graham"                # One investor, default company
#   ./generate-examples.sh "Elad Gil" "custom context"  # One investor, custom company
#
# Each run produces three files in examples/:
#   {slug}.json  - Structured briefing data (schema.json)
#   {slug}.md    - CLI terminal output (markdown)
#   {slug}.pdf   - Print-ready research document

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
EXAMPLES_DIR="$SCRIPT_DIR/examples"
SCHEMA="$SCRIPT_DIR/schema.json"
RENDERER="$SCRIPT_DIR/render.py"

mkdir -p "$EXAMPLES_DIR"

# Default company context (VC Prepare pitching itself)
DEFAULT_COMPANY="VC Whisper (vcwhisper.com). AI-powered investor research tool for founders. Parth Chopra and Tyler Richards built it. Enter an investor name or paste a pitch transcript, and get a full briefing: career history, portfolio, relevant tweets, game plan, and predicted questions. Built using Exa for search, Seedlist for investor data, xAI/Grok for tweet discovery, and Browserbase for web scraping. 62K people watched the launch on X (174 likes, 20 retweets). The Prepare feature launched March 2026. Pre-seed stage, raising \$1.5M. Freemium model: free basic briefings, \$49/mo pro tier with API-enriched data and PDF exports."

generate() {
  local investor="$1"
  local company_context="${2:-$DEFAULT_COMPANY}"
  local slug
  slug=$(echo "$investor" | tr '[:upper:]' '[:lower:]' | tr ' ' '-' | tr -cd 'a-z0-9-')

  local json_out="$EXAMPLES_DIR/$slug.json"
  local md_out="$EXAMPLES_DIR/$slug.md"

  echo ""
  echo "================================================================"
  echo "  Generating briefing: $investor"
  echo "  Company context: ${company_context:0:80}..."
  echo "  Output: $EXAMPLES_DIR/$slug.{json,md,pdf}"
  echo "================================================================"
  echo ""

  # The prompt tells Claude to run the full vc-prepare pipeline and save
  # outputs to specific file paths. It's detailed so Claude doesn't cut
  # corners or skip the research phase.
  local prompt
  prompt=$(cat <<PROMPT
You have the vc-prepare skill installed. Run the full briefing pipeline for
the investor "$investor" with this company context:

$company_context

Execute these steps in order:

STEP 1: RESEARCH
Launch 3-4 parallel subagents to research the investor:
- Agent 1: Career history, LinkedIn, education, personal website
- Agent 2: Portfolio companies, fund details, check size, stage focus
- Agent 3: Recent tweets, press mentions, podcast appearances, blog posts
- Agent 4: Content relevant to VC Whisper specifically, anti-portfolio

Use WebSearch and WebFetch. Do real research. Do not use cached knowledge.

STEP 2: ASSEMBLE JSON
Combine all research into a single JSON object conforming to the schema
at $SCHEMA. Write it to: $json_out

Key rules:
- Every field is optional. Omit fields with no verified data.
- investor.name is the only required field.
- Include fitScore since company context is provided.
- Include relevantContent with investor quotes/tweets relevant to VC Whisper.
- Include gamePlan with howTheyThink, connections (5), predictedQuestions (4-5),
  and avoid (2-3).
- Include otherInvestors (3-4) with fit scores and talking points.
- Include quickReference card.
- meta.dataSources should list the actual sources used.
- meta.companyContext should be true.

STEP 3: RENDER CLI OUTPUT
Read the JSON back from $json_out and render it as beautiful terminal
markdown following the SKILL.md output template. Write the markdown to:
$md_out

Add these comment lines at the top of the markdown file:
<!-- Generated: $(date -u +%Y-%m-%dT%H:%M:%SZ) -->
<!-- Regenerate: ./generate-examples.sh "$investor" -->
<!-- Company: VC Whisper (vcwhisper.com) -->

STEP 4: RENDER PDF
Run: python3 $RENDERER $json_out
This generates the PDF alongside the JSON file.

STEP 5: VERIFY
Confirm all three files exist and report their sizes.

IMPORTANT:
- Do REAL web research. Do not fabricate career history, portfolio companies,
  tweets, or quotes. If you can't verify something, omit it.
- The JSON must be valid and conform to schema.json.
- The CLI output must follow the exact format in SKILL.md.
- The PDF must render without errors.
PROMPT
)

  echo "Running Claude Code..."
  if claude -p "$prompt" 2>/dev/null; then
    echo ""
    echo "Done: $investor"
    ls -lh "$EXAMPLES_DIR/$slug".{json,md,pdf} 2>/dev/null || echo "Warning: some output files missing"
  else
    echo "Error: Claude Code failed for $investor"
    return 1
  fi
}

# Single investor mode
if [ $# -ge 1 ]; then
  generate "$1" "${2:-$DEFAULT_COMPANY}"
  exit 0
fi

# Default examples
generate "Paul Graham"
generate "Elad Gil"
generate "Sarah Tavel" ""

echo ""
echo "================================================================"
echo "  All examples generated in $EXAMPLES_DIR/"
echo "================================================================"
ls -lh "$EXAMPLES_DIR/"
