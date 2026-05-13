import os
from typing import Generator
import anthropic

SYSTEM_PROMPT = """\
You are an expert career advisor helping software professionals craft compelling \
performance reviews and work summaries.

When given work log entries you:
- Identify key themes, accomplishments, and measurable impact
- Group related work by project or area
- Use active, achievement-focused language ("Delivered", "Reduced", "Led", etc.)
- Quantify impact wherever the context supports it
- Write in first person, professionally

For PERIOD SUMMARIES: provide a concise narrative summary with bullet-point highlights.

For ANNUAL REVIEWS, use this structure:
## Executive Summary
## Key Accomplishments (grouped by project/area)
## Technical Growth
## Collaboration & Leadership
## Impact & Results
## Looking Ahead
"""


def _format_entries(entries) -> str:
    lines = []
    for e in entries:
        lines.append(f"Date: {e['date']}")
        lines.append(f"Title: {e['title']}")
        if e["project"]:
            lines.append(f"Project: {e['project']}")
        if e["category"]:
            lines.append(f"Category: {e['category']}")
        if e["description"]:
            lines.append(f"Notes: {e['description']}")
        lines.append("")
    return "\n".join(lines)


def stream_summary(entries, prompt: str) -> Generator[str, None, None]:
    """Stream AI-generated summary text chunk by chunk."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError(
            "ANTHROPIC_API_KEY environment variable is not set.\n"
            "Export it before launching the app:\n  export ANTHROPIC_API_KEY=sk-ant-..."
        )

    client = anthropic.Anthropic(api_key=api_key)
    entries_text = _format_entries(entries)

    with client.messages.stream(
        model="claude-opus-4-7",
        max_tokens=4096,
        thinking={"type": "adaptive"},
        system=[
            {
                "type": "text",
                "text": SYSTEM_PROMPT,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[
            {
                "role": "user",
                "content": f"{prompt}\n\n---\n\n{entries_text}",
            }
        ],
    ) as stream:
        for text in stream.text_stream:
            yield text


def stream_period_summary(entries, start_date: str, end_date: str) -> Generator[str, None, None]:
    date_range = f"from {start_date} to {end_date}" if start_date and end_date else "(all dates)"
    prompt = (
        f"Please summarize the work I did {date_range}. "
        "Include a narrative overview and bullet-point highlights of key accomplishments."
    )
    yield from stream_summary(entries, prompt)


def stream_annual_review(entries, year: int) -> Generator[str, None, None]:
    prompt = (
        f"Please write a comprehensive end-of-year self-review for {year} "
        "that I can share with my manager during my annual performance review. "
        "Use the structured format specified in your instructions."
    )
    yield from stream_summary(entries, prompt)
