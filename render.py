#!/usr/bin/env python3
"""
Render a vc-prepare investor briefing JSON into a consultant-grade PDF.

Usage: python3 render.py path/to/briefing.json

Outputs .html and .pdf (if a converter is available) alongside the input JSON.
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from html import escape
from pathlib import Path


def get(data, *keys, default=None):
    current = data
    for key in keys:
        if isinstance(current, dict):
            current = current.get(key)
        else:
            return default
        if current is None:
            return default
    return current


def esc(value):
    if value is None:
        return ""
    return escape(str(value))


def render_html(data):
    investor = data.get("investor", {})
    meta = data.get("meta", {})
    company = data.get("company", {})
    fit_score = data.get("fitScore", {})
    career = data.get("career") or []
    education = data.get("education") or []
    portfolio = data.get("portfolio") or []
    press = data.get("press") or []
    relevant_content = data.get("relevantContent") or []
    recent_tweets = data.get("recentTweets") or []
    game_plan = data.get("gamePlan") or {}
    other_investors = data.get("otherInvestors") or []
    quick_reference = data.get("quickReference") or {}

    has_company_context = bool(meta.get("companyContext") or company.get("name"))
    has_fit_score = bool(fit_score and fit_score.get("score") is not None)

    investor_name = esc(investor.get("name", "Investor"))
    investor_role = esc(investor.get("role", ""))
    investor_fund = esc(investor.get("fund", ""))
    subtitle_parts = [p for p in [investor_role, investor_fund] if p]
    subtitle = " &middot; ".join(subtitle_parts)

    generated_date = ""
    if meta.get("generatedAt"):
        try:
            parsed = datetime.fromisoformat(meta["generatedAt"].replace("Z", "+00:00"))
            generated_date = parsed.strftime("%B %d, %Y")
        except (ValueError, AttributeError):
            generated_date = esc(meta["generatedAt"])
    if not generated_date:
        generated_date = datetime.now().strftime("%B %d, %Y")

    # -- Build sections --

    # Cover page meta lines
    cover_meta_lines = []
    if investor.get("fundSize"):
        cover_meta_lines.append(f'<span class="meta-label">Fund Size</span><span class="meta-value">{esc(investor["fundSize"])}</span>')
    if investor.get("sweetSpot"):
        cover_meta_lines.append(f'<span class="meta-label">Sweet Spot</span><span class="meta-value">{esc(investor["sweetSpot"])}</span>')
    if investor.get("stageFocus"):
        cover_meta_lines.append(f'<span class="meta-label">Stage</span><span class="meta-value">{esc(investor["stageFocus"])}</span>')
    if investor.get("linkedin"):
        cover_meta_lines.append(f'<span class="meta-label">LinkedIn</span><span class="meta-value"><a href="{esc(investor["linkedin"])}">{esc(investor["linkedin"])}</a></span>')
    if investor.get("twitter"):
        handle = investor["twitter"]
        if not handle.startswith("http"):
            handle_display = handle if handle.startswith("@") else f"@{handle}"
            cover_meta_lines.append(f'<span class="meta-label">X / Twitter</span><span class="meta-value">{esc(handle_display)}</span>')
        else:
            cover_meta_lines.append(f'<span class="meta-label">X / Twitter</span><span class="meta-value"><a href="{esc(handle)}">{esc(handle)}</a></span>')
    if investor.get("website"):
        cover_meta_lines.append(f'<span class="meta-label">Web</span><span class="meta-value"><a href="{esc(investor["website"])}">{esc(investor["website"])}</a></span>')

    cover_meta_html = "\n".join(f'<div class="meta-row">{line}</div>' for line in cover_meta_lines)

    # Fit badge
    fit_badge_html = ""
    if has_fit_score:
        score = fit_score["score"]
        fit_badge_html = f"""
        <div class="fit-section">
            <div class="fit-badge"><span class="fit-number">{score}</span><span class="fit-percent">%</span></div>
            <div class="fit-label-block">
                <div class="fit-label">Fit Score</div>
            </div>
        </div>"""
        if fit_score.get("explanation"):
            fit_badge_html += f'\n        <p class="fit-explanation">{esc(fit_score["explanation"])}</p>'

    # Prepared for
    prepared_for_html = ""
    if company.get("name"):
        prepared_for_html = f'<div class="prepared-for"><span class="meta-label">Prepared for</span><strong>{esc(company["name"])}</strong>'
        if company.get("description"):
            prepared_for_html += f'<br><span class="company-desc">{esc(company["description"])}</span>'
        prepared_for_html += "</div>"

    # About
    about_html = ""
    if investor.get("about"):
        about_html = f'<p class="about">{esc(investor["about"])}</p>'

    # Career section
    career_section = ""
    if career or education:
        career_section = '<h2>Career Path</h2>\n<div class="timeline">\n'
        for index, entry in enumerate(career):
            is_current = (entry.get("endYear", "").lower() == "present") or index == 0
            border_class = "current" if is_current else "past"
            role_text = esc(entry.get("role", ""))
            company_text = esc(entry.get("company", ""))
            period_parts = []
            if entry.get("startYear"):
                period_parts.append(esc(entry["startYear"]))
            if entry.get("endYear"):
                period_parts.append(esc(entry["endYear"]))
            period = " &ndash; ".join(period_parts)
            career_section += f'<div class="career-entry {border_class}">\n'
            career_section += f'  <div class="career-header"><span class="role"><strong>{role_text}</strong>'
            if company_text:
                career_section += f', {company_text}'
            career_section += '</span>'
            if period:
                career_section += f'<span class="period">{period}</span>'
            career_section += '</div>\n'
            if entry.get("note"):
                career_section += f'  <div class="note">{esc(entry["note"])}</div>\n'
            career_section += "</div>\n"

        for entry in education:
            parts = []
            if entry.get("degree"):
                parts.append(esc(entry["degree"]))
            if entry.get("institution"):
                parts.append(esc(entry["institution"]))
            text = " &mdash; ".join(parts) if parts else ""
            if entry.get("year"):
                text += f' <span class="edu-year">({esc(entry["year"])})</span>'
            if text:
                career_section += f'<div class="education">{text}</div>\n'
        career_section += '</div>\n'

    # Portfolio section
    portfolio_section = ""
    if portfolio:
        portfolio_section = '<h2>Portfolio Companies</h2>\n<table>\n<thead>\n<tr>'
        portfolio_section += "<th>Company</th><th>Stage</th><th>Category</th><th>Date</th><th>Status</th>"
        portfolio_section += "</tr>\n</thead>\n<tbody>\n"
        for index, entry in enumerate(portfolio):
            row_class = ' class="alt"' if index % 2 == 1 else ""
            categories = ", ".join(entry.get("categories", [])) if entry.get("categories") else ""
            note = ""
            if entry.get("note"):
                note = f' <span class="portfolio-note">{esc(entry["note"])}</span>'
            portfolio_section += f"<tr{row_class}>"
            portfolio_section += f"<td><strong>{esc(entry.get('company', ''))}</strong>{note}</td>"
            portfolio_section += f"<td>{esc(entry.get('stage', ''))}</td>"
            portfolio_section += f"<td>{esc(categories)}</td>"
            portfolio_section += f"<td>{esc(entry.get('date', ''))}</td>"
            portfolio_section += f"<td>{esc(entry.get('status', ''))}</td>"
            portfolio_section += "</tr>\n"
        portfolio_section += '</tbody>\n</table>\n<p class="source-note">Portfolio data from public sources; may be incomplete.</p>\n'

    # Press section
    press_section = ""
    if press:
        press_section = '<h2>Press &amp; Appearances</h2>\n'
        for entry in press:
            title = esc(entry.get("title", ""))
            source = esc(entry.get("source", ""))
            date = esc(entry.get("date", ""))
            summary = esc(entry.get("summary", ""))
            url = entry.get("url", "")
            press_section += '<div class="press-item">\n'
            if title:
                if url:
                    press_section += f'  <div class="press-title"><a href="{esc(url)}" class="press-link">{title}</a></div>\n'
                else:
                    press_section += f'  <div class="press-title">{title}</div>\n'
            source_parts = [p for p in [source, date] if p]
            if source_parts:
                press_section += f'  <div class="press-source">{" &middot; ".join(source_parts)}</div>\n'
            if summary:
                press_section += f'  <div class="press-summary">{summary}</div>\n'
            press_section += "</div>\n"

    # Relevant content section (only with company context)
    relevant_section = ""
    if has_company_context and relevant_content:
        relevant_section = '<h2>Relevant to Your Pitch</h2>\n'
        for entry in relevant_content:
            text = esc(entry.get("text", ""))
            source = esc(entry.get("source", ""))
            date = esc(entry.get("date", ""))
            relevance = esc(entry.get("relevance", ""))
            attribution_parts = [p for p in [source, date] if p]
            attribution = " &middot; ".join(attribution_parts)
            relevant_section += '<div class="quote-block">\n<blockquote>\n'
            relevant_section += f"  <p>{text}</p>\n"
            if attribution:
                relevant_section += f'  <cite>{attribution}</cite>\n'
            relevant_section += "</blockquote>\n"
            if relevance:
                relevant_section += f'<p class="relevance-note">{relevance}</p>\n'
            relevant_section += "</div>\n"

    # Recent tweets section
    tweets_section = ""
    if recent_tweets:
        twitter_handle = ""
        if investor.get("twitter"):
            handle = investor["twitter"]
            if handle.startswith("@"):
                twitter_handle = handle
            elif handle.startswith("http"):
                twitter_handle = "@" + handle.rstrip("/").split("/")[-1]
            else:
                twitter_handle = f"@{handle}"

        tweets_section = '<h2>Recent Posts</h2>\n'
        for entry in recent_tweets:
            text = esc(entry.get("text", ""))
            date = esc(entry.get("date", ""))
            attribution_parts = [p for p in [twitter_handle, date] if p]
            attribution = " &middot; ".join(attribution_parts)
            tweets_section += '<div class="quote-block">\n<blockquote>\n'
            tweets_section += f"  <p>{text}</p>\n"
            if attribution:
                tweets_section += f'  <cite>{attribution}</cite>\n'
            tweets_section += "</blockquote>\n</div>\n"

    # Game plan section
    game_plan_section = ""
    game_plan_parts = []
    if game_plan.get("howTheyThink"):
        game_plan_parts.append(
            f'<h3>How They Think</h3>\n<div class="how-they-think">{esc(game_plan["howTheyThink"])}</div>\n'
        )
    if game_plan.get("connections"):
        connections_html = "<h3>Where You Connect</h3>\n"
        for item in game_plan["connections"]:
            connections_html += '<div class="dot-item connection-item">\n'
            connections_html += f'  <div class="dot-title">{esc(item.get("title", ""))}</div>\n'
            if item.get("detail"):
                connections_html += f'  <div class="dot-detail">{esc(item["detail"])}</div>\n'
            connections_html += "</div>\n"
        game_plan_parts.append(connections_html)
    if game_plan.get("predictedQuestions"):
        questions_html = "<h3>Predicted Questions</h3>\n"
        for item in game_plan["predictedQuestions"]:
            questions_html += '<div class="dot-item question-item">\n'
            questions_html += f'  <div class="dot-title">&ldquo;{esc(item.get("question", ""))}&rdquo;</div>\n'
            if item.get("suggestedApproach"):
                questions_html += f'  <div class="dot-detail">{esc(item["suggestedApproach"])}</div>\n'
            questions_html += "</div>\n"
        game_plan_parts.append(questions_html)
    if game_plan.get("avoid"):
        avoid_html = "<h3>Do Not Mention</h3>\n"
        for item in game_plan["avoid"]:
            avoid_html += '<div class="dot-item avoid-item">\n'
            avoid_html += f'  <div class="dot-title">{esc(item.get("topic", ""))}</div>\n'
            if item.get("reason"):
                avoid_html += f'  <div class="dot-detail">{esc(item["reason"])}</div>\n'
            avoid_html += "</div>\n"
        game_plan_parts.append(avoid_html)
    if game_plan_parts:
        game_plan_section = '<h2>Your Game Plan</h2>\n' + "\n".join(game_plan_parts)

    # Other investors section (only with company context)
    other_section = ""
    if has_company_context and other_investors:
        other_section = '<h2>Other Investors to Pursue</h2>\n<div class="investor-cards">\n'
        for entry in other_investors:
            fit = entry.get("fit")
            other_section += '<div class="investor-card">\n'
            other_section += '  <div class="investor-card-header">\n'
            other_section += f'    <div class="investor-card-name"><strong>{esc(entry.get("name", ""))}</strong>'
            if entry.get("fund"):
                other_section += f' <span class="investor-card-fund">&middot; {esc(entry["fund"])}</span>'
            other_section += '</div>\n'
            if fit is not None:
                other_section += f'    <div class="investor-card-fit">{fit}%</div>\n'
            other_section += '  </div>\n'
            if entry.get("why"):
                other_section += f'  <div class="investor-card-why">{esc(entry["why"])}</div>\n'
            if entry.get("talkingPoint"):
                other_section += f'  <div class="investor-card-lead"><em>Lead with:</em> {esc(entry["talkingPoint"])}</div>\n'
            links = []
            if entry.get("linkedin"):
                links.append(f'<a href="{esc(entry["linkedin"])}">LinkedIn</a>')
            if entry.get("twitter"):
                links.append(f'<a href="{esc(entry["twitter"])}">X</a>')
            if links:
                other_section += f'  <div class="investor-card-links">{" &middot; ".join(links)}</div>\n'
            other_section += "</div>\n"
        other_section += "</div>\n"

    # Quick reference section
    quick_ref_section = ""
    if quick_reference and any(quick_reference.get(k) for k in ["oneLinerThesis", "oneLinerStyle", "topQuestions", "proofPoints", "doNotSay"]):
        quick_ref_section = '<div class="quick-ref">\n<div class="qr-heading">Quick Reference</div>\n'
        if quick_reference.get("oneLinerThesis"):
            quick_ref_section += f'<div class="qr-row"><span class="qr-label">Thesis</span><span class="qr-value">{esc(quick_reference["oneLinerThesis"])}</span></div>\n'
        if quick_reference.get("oneLinerStyle"):
            quick_ref_section += f'<div class="qr-row"><span class="qr-label">Style</span><span class="qr-value">{esc(quick_reference["oneLinerStyle"])}</span></div>\n'
        if quick_reference.get("topQuestions"):
            items = "".join(f"<li>{esc(q)}</li>" for q in quick_reference["topQuestions"])
            quick_ref_section += f'<div class="qr-row"><span class="qr-label">Key Questions</span><div class="qr-value"><ol class="qr-list">{items}</ol></div></div>\n'
        if quick_reference.get("proofPoints"):
            items = "".join(f"<li>{esc(p)}</li>" for p in quick_reference["proofPoints"])
            quick_ref_section += f'<div class="qr-row"><span class="qr-label">Proof Points</span><div class="qr-value"><ul class="qr-list">{items}</ul></div></div>\n'
        if quick_reference.get("doNotSay"):
            quick_ref_section += f'<div class="qr-row qr-warn"><span class="qr-label">Avoid</span><span class="qr-value">{esc(quick_reference["doNotSay"])}</span></div>\n'
        quick_ref_section += "</div>\n"

    # Fit details section
    fit_details_section = ""
    if has_fit_score:
        detail_rows = []
        if fit_score.get("thesisAlignment"):
            detail_rows.append(("Thesis Alignment", fit_score["thesisAlignment"]))
        if fit_score.get("portfolioPatternMatch"):
            detail_rows.append(("Portfolio Pattern", fit_score["portfolioPatternMatch"]))
        if fit_score.get("stageFit"):
            detail_rows.append(("Stage Fit", fit_score["stageFit"]))
        if fit_score.get("checkSizeFit"):
            detail_rows.append(("Check Size Fit", fit_score["checkSizeFit"]))
        if detail_rows:
            fit_details_section = '<div class="fit-details">\n<div class="fit-details-heading">Fit Analysis</div>\n'
            for label, value in detail_rows:
                fit_details_section += f'<div class="fit-detail-row"><span class="fit-detail-label">{esc(label)}</span><span class="fit-detail-value">{esc(value)}</span></div>\n'
            fit_details_section += "</div>\n"

    # Assemble body
    body_parts = []
    if about_html:
        body_parts.append(about_html)
    if career_section:
        body_parts.append(career_section)
    if portfolio_section:
        body_parts.append(portfolio_section)
    if press_section:
        body_parts.append(press_section)
    if fit_details_section:
        body_parts.append(fit_details_section)
    if relevant_section:
        body_parts.append(relevant_section)
    if tweets_section:
        body_parts.append(tweets_section)
    if game_plan_section:
        body_parts.append(game_plan_section)
    if other_section:
        body_parts.append(other_section)
    if quick_ref_section:
        body_parts.append(quick_ref_section)

    body_html = "\n".join(body_parts)

    # Data sources
    sources_html = ""
    if meta.get("dataSources"):
        sources_html = " &middot; Sources: " + ", ".join(esc(s) for s in meta["dataSources"])

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Investor Briefing: {investor_name}</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;0,700;1,400;1,500&family=Inter:wght@400;500;600;700&family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,500;0,8..60,600;1,8..60,400;1,8..60,500&display=swap');

  @page {{
    size: letter;
    margin: 0.9in 1.1in 1in 1.1in;
  }}

  *, *::before, *::after {{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
  }}

  body {{
    font-family: "Source Serif 4", "Georgia", "Times New Roman", serif;
    font-size: 10.5pt;
    line-height: 1.6;
    color: #1a1a1a;
    background: #fff;
    -webkit-font-smoothing: antialiased;
    font-feature-settings: "liga" 1, "kern" 1;
  }}

  a {{
    color: #92400e;
    text-decoration: none;
  }}
  a:hover {{
    text-decoration: underline;
  }}

  p {{
    margin-bottom: 0.65rem;
    text-align: justify;
    hyphens: auto;
    -webkit-hyphens: auto;
  }}

  /* ========== COVER ========== */

  .cover {{
    page-break-after: always;
    min-height: 90vh;
    display: flex;
    flex-direction: column;
    justify-content: center;
    padding: 3rem 0 2rem;
  }}

  .cover-rule {{
    width: 60px;
    height: 3px;
    background: #92400e;
    margin-bottom: 2.5rem;
    border: none;
  }}

  .cover h1 {{
    font-family: "Cormorant Garamond", "Georgia", serif;
    font-size: 42pt;
    font-weight: 700;
    letter-spacing: -0.02em;
    line-height: 1.05;
    color: #1a1a1a;
    margin-bottom: 0.35rem;
  }}

  .cover .subtitle {{
    font-family: "Source Serif 4", "Georgia", serif;
    font-size: 14pt;
    color: #6b5d4d;
    font-style: italic;
    margin-bottom: 2.25rem;
  }}

  /* Fit badge */
  .fit-section {{
    display: flex;
    align-items: center;
    gap: 1rem;
    margin: 1.5rem 0 0.6rem;
  }}

  .fit-badge {{
    width: 80px;
    height: 80px;
    border: 2px solid #92400e;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
  }}

  .fit-number {{
    font-family: "Inter", "Helvetica Neue", sans-serif;
    font-size: 28pt;
    font-weight: 700;
    color: #92400e;
    line-height: 1;
  }}

  .fit-percent {{
    font-family: "Inter", "Helvetica Neue", sans-serif;
    font-size: 13pt;
    font-weight: 600;
    color: #92400e;
    vertical-align: super;
    margin-left: 1px;
  }}

  .fit-label-block {{
    display: flex;
    flex-direction: column;
    gap: 0.15rem;
  }}

  .fit-label {{
    font-family: "Inter", "Helvetica Neue", sans-serif;
    font-size: 8.5pt;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #8c7e6a;
  }}

  .fit-explanation {{
    font-size: 11pt;
    color: #6b5d4d;
    font-style: italic;
    max-width: 540px;
    margin-bottom: 1.75rem;
    line-height: 1.55;
    text-align: left;
  }}

  /* Cover metadata */
  .cover-meta {{
    margin-top: 0.5rem;
  }}

  .meta-row {{
    line-height: 1.9;
  }}

  .meta-label {{
    font-family: "Inter", "Helvetica Neue", sans-serif;
    font-weight: 600;
    font-size: 8.5pt;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #8c7e6a;
    display: inline-block;
    width: 110px;
  }}

  .meta-value {{
    font-family: "Source Serif 4", "Georgia", serif;
    font-size: 9.5pt;
    color: #44403c;
  }}

  .meta-value a {{
    color: #44403c;
  }}

  .prepared-for {{
    margin-top: 2rem;
    padding-top: 1.25rem;
    border-top: 1px solid #e5e0d8;
    font-size: 10pt;
    color: #6b5d4d;
  }}

  .prepared-for strong {{
    color: #1a1a1a;
    font-size: 10.5pt;
  }}

  .company-desc {{
    font-size: 9pt;
    font-style: italic;
    color: #8c7e6a;
    display: block;
    margin-top: 0.2rem;
    line-height: 1.5;
  }}

  .cover .date-line {{
    font-family: "Inter", "Helvetica Neue", sans-serif;
    font-size: 8.5pt;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #8c7e6a;
    margin-top: 1.25rem;
  }}

  /* ========== HEADINGS ========== */

  h2 {{
    font-family: "Cormorant Garamond", "Georgia", serif;
    font-size: 20pt;
    font-weight: 600;
    color: #1a1a1a;
    margin-top: 2rem;
    margin-bottom: 0.75rem;
    padding-bottom: 0.3rem;
    border-bottom: 1.5px solid #e5e0d8;
    letter-spacing: -0.01em;
    page-break-after: avoid;
  }}

  h3 {{
    font-family: "Cormorant Garamond", "Georgia", serif;
    font-size: 14pt;
    font-weight: 600;
    color: #44403c;
    margin-top: 1.5rem;
    margin-bottom: 0.4rem;
    page-break-after: avoid;
  }}

  /* ========== ABOUT ========== */

  .about {{
    font-size: 11pt;
    color: #44403c;
    line-height: 1.65;
    margin-bottom: 0.5rem;
    font-style: italic;
  }}

  /* ========== CAREER TIMELINE ========== */

  .timeline {{
    margin-top: 0.25rem;
  }}

  .career-entry {{
    margin-bottom: 0.7rem;
    padding-left: 1.1rem;
    border-left: 2px solid #d6d3d1;
    page-break-inside: avoid;
  }}

  .career-entry.current {{
    border-left-color: #92400e;
  }}

  .career-header {{
    display: flex;
    justify-content: space-between;
    align-items: baseline;
  }}

  .career-entry .role {{
    font-family: "Source Serif 4", "Georgia", serif;
    font-size: 10.5pt;
    color: #1a1a1a;
  }}

  .career-entry .period {{
    font-family: "Inter", "Helvetica Neue", sans-serif;
    font-size: 8pt;
    font-weight: 500;
    color: #8c7e6a;
    font-style: italic;
    white-space: nowrap;
    margin-left: 1rem;
    flex-shrink: 0;
  }}

  .career-entry .note {{
    font-size: 10pt;
    color: #6b5d4d;
    margin-top: 0.15rem;
    line-height: 1.5;
  }}

  .education {{
    margin-top: 0.5rem;
    margin-bottom: 0.5rem;
    padding-left: 1.1rem;
    border-left: 2px solid #d6d3d1;
    font-style: italic;
    font-size: 10pt;
    color: #6b5d4d;
  }}

  .edu-year {{
    font-style: normal;
    font-size: 9pt;
    color: #8c7e6a;
  }}

  /* ========== PORTFOLIO TABLE ========== */

  table {{
    width: 100%;
    border-collapse: collapse;
    margin: 0.5rem 0 0.75rem;
    font-size: 9.5pt;
  }}

  thead th {{
    font-family: "Inter", "Helvetica Neue", sans-serif;
    text-align: left;
    font-weight: 600;
    font-size: 8pt;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #8c7e6a;
    padding: 0.5rem 0.65rem;
    border-bottom: 1.5px solid #e5e0d8;
  }}

  tbody td {{
    padding: 0.45rem 0.65rem;
    color: #44403c;
    vertical-align: top;
    line-height: 1.4;
    border-bottom: none;
  }}

  tbody tr.alt td {{
    background: #faf8f5;
  }}

  .portfolio-note {{
    font-size: 8.5pt;
    color: #8c7e6a;
    font-style: italic;
    display: block;
    margin-top: 0.1rem;
  }}

  .source-note {{
    font-family: "Inter", "Helvetica Neue", sans-serif;
    font-size: 7.5pt;
    color: #8c7e6a;
    letter-spacing: 0.02em;
    text-align: left;
    margin-top: 0;
  }}

  /* ========== PRESS ========== */

  .press-item {{
    margin-bottom: 0.85rem;
    page-break-inside: avoid;
  }}

  .press-title {{
    font-family: "Source Serif 4", "Georgia", serif;
    font-weight: 600;
    font-size: 10.5pt;
    color: #1a1a1a;
  }}

  .press-link {{
    color: #1a1a1a;
  }}

  .press-source {{
    font-family: "Inter", "Helvetica Neue", sans-serif;
    font-size: 8.5pt;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #8c7e6a;
    margin-top: 0.05rem;
  }}

  .press-summary {{
    font-size: 10pt;
    color: #6b5d4d;
    margin-top: 0.2rem;
    line-height: 1.5;
  }}

  /* ========== BLOCKQUOTES ========== */

  .quote-block {{
    margin-bottom: 1rem;
    page-break-inside: avoid;
  }}

  blockquote {{
    margin: 0.5rem 0;
    padding: 0.85rem 1.15rem;
    border-left: 3px solid #92400e;
    background: #faf8f5;
    font-style: italic;
    font-size: 10.5pt;
    color: #44403c;
    line-height: 1.55;
    page-break-inside: avoid;
  }}

  blockquote p {{
    margin: 0;
    text-align: left;
  }}

  blockquote cite {{
    font-family: "Inter", "Helvetica Neue", sans-serif;
    font-size: 8.5pt;
    color: #8c7e6a;
    font-style: normal;
    display: block;
    margin-top: 0.5rem;
    letter-spacing: 0.02em;
  }}

  .relevance-note {{
    font-size: 10pt;
    color: #6b5d4d;
    margin-top: 0.25rem;
    margin-bottom: 0;
    padding-left: 1.15rem;
    font-style: normal;
    line-height: 1.5;
  }}

  /* ========== GAME PLAN ========== */

  .how-they-think {{
    background: #faf8f5;
    padding: 1rem 1.25rem;
    border-left: 4px solid #92400e;
    margin-bottom: 1rem;
    font-style: italic;
    font-size: 10.5pt;
    color: #44403c;
    line-height: 1.6;
  }}

  /* Dot items: connections, questions, avoid */
  .dot-item {{
    margin-bottom: 0.75rem;
    padding-left: 1.1rem;
    position: relative;
    page-break-inside: avoid;
  }}

  .dot-item::before {{
    content: "";
    position: absolute;
    left: 0;
    top: 0.55em;
    width: 7px;
    height: 7px;
    border-radius: 50%;
  }}

  .connection-item::before {{
    background: #4a8b3f;
  }}

  .question-item::before {{
    background: #5b7b8d;
  }}

  .avoid-item::before {{
    background: #b5542a;
  }}

  .dot-title {{
    font-weight: 600;
    font-size: 10.5pt;
    color: #1a1a1a;
  }}

  .question-item .dot-title {{
    font-style: italic;
  }}

  .avoid-item .dot-title {{
    color: #b5542a;
  }}

  .dot-detail {{
    font-size: 10pt;
    color: #6b5d4d;
    margin-top: 0.15rem;
    line-height: 1.5;
    padding-left: 0;
  }}

  /* ========== FIT DETAILS ========== */

  .fit-details {{
    background: #faf8f5;
    border: 1px solid #e5e0d8;
    padding: 1rem 1.25rem;
    margin-top: 0.5rem;
    margin-bottom: 0.5rem;
  }}

  .fit-details-heading {{
    font-family: "Inter", "Helvetica Neue", sans-serif;
    font-size: 8.5pt;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #8c7e6a;
    margin-bottom: 0.65rem;
  }}

  .fit-detail-row {{
    margin-bottom: 0.45rem;
    font-size: 10pt;
    line-height: 1.5;
    display: flex;
    gap: 0.5rem;
  }}

  .fit-detail-label {{
    font-family: "Inter", "Helvetica Neue", sans-serif;
    font-weight: 600;
    font-size: 8pt;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #92400e;
    width: 140px;
    flex-shrink: 0;
    padding-top: 0.15rem;
  }}

  .fit-detail-value {{
    color: #44403c;
    font-size: 10pt;
  }}

  /* ========== OTHER INVESTORS ========== */

  .investor-cards {{
    display: flex;
    flex-direction: column;
    gap: 0.65rem;
  }}

  .investor-card {{
    padding: 0.85rem 1.1rem;
    border: 1px solid #e5e0d8;
    background: #faf8f5;
    page-break-inside: avoid;
  }}

  .investor-card-header {{
    display: flex;
    justify-content: space-between;
    align-items: baseline;
  }}

  .investor-card-name {{
    font-family: "Source Serif 4", "Georgia", serif;
    font-size: 11pt;
    color: #1a1a1a;
  }}

  .investor-card-fund {{
    font-size: 10pt;
    color: #8c7e6a;
    font-weight: 400;
  }}

  .investor-card-fit {{
    font-family: "Inter", "Helvetica Neue", sans-serif;
    font-weight: 700;
    font-size: 15pt;
    color: #92400e;
    white-space: nowrap;
  }}

  .investor-card-why {{
    font-size: 10pt;
    color: #6b5d4d;
    margin-top: 0.25rem;
    line-height: 1.5;
  }}

  .investor-card-lead {{
    font-size: 9.5pt;
    color: #44403c;
    margin-top: 0.2rem;
    line-height: 1.45;
  }}

  .investor-card-links {{
    font-family: "Inter", "Helvetica Neue", sans-serif;
    font-size: 7.5pt;
    margin-top: 0.3rem;
    letter-spacing: 0.02em;
  }}

  /* ========== QUICK REFERENCE CARD ========== */

  .quick-ref {{
    font-family: "Inter", "Helvetica Neue", sans-serif;
    background: #faf8f5;
    border: 1px solid #e5e0d8;
    padding: 1.25rem 1.5rem;
    margin-top: 2rem;
    page-break-inside: avoid;
  }}

  .qr-heading {{
    font-family: "Inter", "Helvetica Neue", sans-serif;
    font-size: 11pt;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #1a1a1a;
    margin-bottom: 0.85rem;
    padding-bottom: 0.4rem;
    border-bottom: 1.5px solid #e5e0d8;
  }}

  .qr-row {{
    margin-bottom: 0.55rem;
    font-size: 9.5pt;
    color: #44403c;
    line-height: 1.5;
    display: flex;
    gap: 0.5rem;
  }}

  .qr-label {{
    font-family: "Inter", "Helvetica Neue", sans-serif;
    font-weight: 600;
    font-size: 8pt;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #92400e;
    width: 110px;
    flex-shrink: 0;
    padding-top: 0.1rem;
  }}

  .qr-value {{
    flex: 1;
    font-family: "Inter", "Helvetica Neue", sans-serif;
    font-size: 9.5pt;
    color: #44403c;
  }}

  .qr-list {{
    margin: 0;
    padding-left: 1.1rem;
    font-size: 9.5pt;
  }}

  .qr-list li {{
    margin-bottom: 0.15rem;
  }}

  .qr-warn {{
    color: #b5542a;
  }}

  .qr-warn .qr-label {{
    color: #b5542a;
  }}

  /* ========== FOOTER ========== */

  .page-footer {{
    margin-top: 3rem;
    padding-top: 0.75rem;
    border-top: 1px solid #e5e0d8;
    text-align: right;
  }}

  .footer-text {{
    font-family: "Inter", "Helvetica Neue", sans-serif;
    font-size: 8pt;
    color: #8c7e6a;
    letter-spacing: 0.02em;
  }}

  /* ========== PRINT ========== */

  @media print {{
    body {{
      font-size: 10.5pt;
    }}

    .cover {{
      min-height: 88vh;
    }}

    h2 {{
      page-break-after: avoid;
      page-break-inside: avoid;
    }}

    h3 {{
      page-break-after: avoid;
      page-break-inside: avoid;
    }}

    blockquote,
    .quote-block,
    .investor-card,
    .dot-item,
    .career-entry,
    .press-item,
    .quick-ref,
    .fit-section,
    .how-they-think,
    .fit-details {{
      page-break-inside: avoid;
    }}

    p {{
      orphans: 4;
      widows: 4;
    }}

    table {{
      page-break-inside: auto;
    }}

    tr {{
      page-break-inside: avoid;
    }}

    thead {{
      display: table-header-group;
    }}

    .quick-ref {{
      page-break-before: auto;
    }}
  }}
</style>
</head>
<body>

<div class="cover">
  <div class="cover-rule"></div>
  <h1>{investor_name}</h1>
  {"<div class='subtitle'>" + subtitle + "</div>" if subtitle else ""}
  {fit_badge_html}
  <div class="cover-meta">
    {cover_meta_html}
  </div>
  {prepared_for_html}
  <div class="date-line">{generated_date}</div>
</div>

{body_html}

<div class="page-footer">
  <span class="footer-text">Generated {generated_date} &middot; vc-prepare{sources_html}</span>
</div>

</body>
</html>"""

    return html


def convert_to_pdf(html_path, pdf_path):
    # Try weasyprint
    try:
        import weasyprint
        doc = weasyprint.HTML(filename=str(html_path))
        doc.write_pdf(str(pdf_path))
        return True
    except ImportError:
        pass
    except Exception as error:
        print(f"weasyprint failed: {error}")

    # Try wkhtmltopdf
    try:
        result = subprocess.run(
            [
                "wkhtmltopdf",
                "--page-size", "Letter",
                "--margin-top", "25mm",
                "--margin-bottom", "25mm",
                "--margin-left", "30mm",
                "--margin-right", "30mm",
                "--enable-local-file-access",
                "--encoding", "UTF-8",
                "--no-header-line",
                "--no-footer-line",
                "--header-left", "",
                "--header-right", "",
                "--footer-left", "",
                "--footer-center", "",
                "--footer-right", "",
                str(html_path),
                str(pdf_path),
            ],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            return True
        print(f"wkhtmltopdf failed: {result.stderr.strip()}")
    except FileNotFoundError:
        pass

    # Try Chrome headless
    chrome_paths = [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
        "google-chrome",
        "chromium",
        "chrome",
    ]
    for chrome in chrome_paths:
        try:
            result = subprocess.run(
                [
                    chrome,
                    "--headless",
                    "--disable-gpu",
                    "--no-sandbox",
                    "--no-pdf-header-footer",
                    f"--print-to-pdf={pdf_path}",
                    str(html_path),
                ],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0 and Path(pdf_path).exists():
                return True
        except FileNotFoundError:
            continue

    return False


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 render.py path/to/briefing.json")
        sys.exit(1)

    json_path = Path(sys.argv[1]).resolve()
    if not json_path.exists():
        print(f"File not found: {json_path}")
        sys.exit(1)

    with open(json_path, "r") as file:
        data = json.load(file)

    html = render_html(data)

    output_dir = json_path.parent
    stem = json_path.stem
    html_path = output_dir / f"{stem}.html"
    pdf_path = output_dir / f"{stem}.pdf"

    with open(html_path, "w") as file:
        file.write(html)
    print(f"HTML saved: {html_path}")

    if convert_to_pdf(html_path, pdf_path):
        print(f"PDF saved: {pdf_path}")
        if sys.platform == "darwin":
            subprocess.run(["open", str(pdf_path)])
        elif sys.platform == "linux":
            subprocess.run(["xdg-open", str(pdf_path)])
    else:
        print(f"\nNo PDF converter found. Install one of:")
        print(f"  pip install weasyprint")
        print(f"  brew install wkhtmltopdf")
        print(f"  (or use Chrome)")
        print(f"\nHTML file ready at: {html_path}")
        print(f"Open it in a browser and print to PDF.")


if __name__ == "__main__":
    main()
