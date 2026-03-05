"""
Call Claude with tools that query Spotify Postgres. Runs tool calls in a loop until Claude responds with text.
"""
from datetime import datetime
from typing import List, Dict, Any

import anthropic

from .config import ANTHROPIC_API_KEY, ANTHROPIC_MODEL
from . import db


def _system_prompt() -> str:
    today = datetime.now().date().isoformat()
    return (
        "You are a helpful assistant that answers questions about the user's Spotify listening history. "
        "The data comes from their personal Spotify API (recently played tracks and artist genres). "
        f"Today's local date is {today}. When the user asks about 'this month', 'last month', 'last year', "
        "or 'last 30 days', interpret them using this date and choose explicit date ranges (YYYY-MM-DD). "
        "Use the tools to query the database when needed. Be concise and friendly. "
        "When presenting lists (e.g. top artists or top songs), format them as a plain text table inside a "
        "single code block with aligned columns, NOT markdown pipe tables. Include play counts where relevant. "
    )


TOOLS = [
    {
        "name": "date_range_available",
        "description": "Get the earliest and latest listening dates in the database. Use when the user asks what data is available or the date range.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "total_listens",
        "description": "Get total number of plays and distinct days listened in a date range.",
        "input_schema": {
            "type": "object",
            "properties": {
                "start_date": {"type": "string", "description": "YYYY-MM-DD"},
                "end_date": {"type": "string", "description": "YYYY-MM-DD"},
            },
            "required": ["start_date", "end_date"],
        },
    },
    {
        "name": "top_artists",
        "description": "Get most played artists by play count for a date range.",
        "input_schema": {
            "type": "object",
            "properties": {
                "start_date": {"type": "string", "description": "YYYY-MM-DD"},
                "end_date": {"type": "string", "description": "YYYY-MM-DD"},
                "limit": {"type": "integer", "description": "Max artists to return.", "default": 20},
            },
            "required": ["start_date", "end_date"],
        },
    },
    {
        "name": "top_songs",
        "description": "Get most played tracks (song + artist) by play count for a date range.",
        "input_schema": {
            "type": "object",
            "properties": {
                "start_date": {"type": "string", "description": "YYYY-MM-DD"},
                "end_date": {"type": "string", "description": "YYYY-MM-DD"},
                "limit": {"type": "integer", "description": "Max songs to return.", "default": 20},
            },
            "required": ["start_date", "end_date"],
        },
    },
    {
        "name": "top_genres",
        "description": "Get most listened genres (from artist genres) for a date range.",
        "input_schema": {
            "type": "object",
            "properties": {
                "start_date": {"type": "string", "description": "YYYY-MM-DD"},
                "end_date": {"type": "string", "description": "YYYY-MM-DD"},
                "limit": {"type": "integer", "description": "Max genres to return.", "default": 20},
            },
            "required": ["start_date", "end_date"],
        },
    },
    {
        "name": "listening_activity_by_date",
        "description": "Get play count per day for a date range. Good for 'listening over time' or 'plays per day'.",
        "input_schema": {
            "type": "object",
            "properties": {
                "start_date": {"type": "string", "description": "YYYY-MM-DD"},
                "end_date": {"type": "string", "description": "YYYY-MM-DD"},
            },
            "required": ["start_date", "end_date"],
        },
    },
    {
        "name": "recent_tracks",
        "description": "List recent listens (played_at, song, artist) in a date range.",
        "input_schema": {
            "type": "object",
            "properties": {
                "start_date": {"type": "string", "description": "YYYY-MM-DD"},
                "end_date": {"type": "string", "description": "YYYY-MM-DD"},
                "limit": {"type": "integer", "description": "Max tracks to return.", "default": 20},
                "artist_filter": {"type": "string", "description": "Optional filter by artist name (partial match)."},
            },
            "required": ["start_date", "end_date"],
        },
    },
    {
        "name": "artist_genres",
        "description": "Look up genre(s) for an artist by name or artist_id.",
        "input_schema": {
            "type": "object",
            "properties": {
                "artist_name_or_id": {"type": "string", "description": "Artist name (partial) or Spotify artist ID."},
            },
            "required": ["artist_name_or_id"],
        },
    },
]


def answer_question(question: str) -> str:
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    messages = [{"role": "user", "content": question}]
    max_turns = 5

    for _ in range(max_turns):
        response = client.messages.create(
            model=ANTHROPIC_MODEL,
            max_tokens=1024,
            system=_system_prompt(),
            tools=TOOLS,
            messages=messages,
        )

        if response.stop_reason == "end_turn":
            for block in response.content:
                if block.type == "text":
                    return block.text
            return "I don't have a response for that."

        messages.append({"role": "assistant", "content": response.content})
        tool_results = []
        for block in response.content:
            if block.type != "tool_use":
                continue
            result = db.run_tool(block.name, **block.input)
            tool_results.append({"type": "tool_result", "tool_use_id": block.id, "content": result})

        if not tool_results:
            return "I don't have a response for that."

        messages.append({"role": "user", "content": tool_results})

    return "I hit the limit on query steps. Try a simpler question."


def answer_question_with_history(messages: List[Dict[str, Any]]) -> str:
    """Same as answer_question but with prior conversation context."""
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    api_messages = list(messages)
    max_turns = 5

    for _ in range(max_turns):
        response = client.messages.create(
            model=ANTHROPIC_MODEL,
            max_tokens=1024,
            system=_system_prompt(),
            tools=TOOLS,
            messages=api_messages,
        )

        if response.stop_reason == "end_turn":
            for block in response.content:
                if block.type == "text":
                    return block.text
            return "I don't have a response for that."

        api_messages.append({"role": "assistant", "content": response.content})
        tool_results = []
        for block in response.content:
            if block.type != "tool_use":
                continue
            result = db.run_tool(block.name, **block.input)
            tool_results.append({"type": "tool_result", "tool_use_id": block.id, "content": result})

        if not tool_results:
            return "I don't have a response for that."

        api_messages.append({"role": "user", "content": tool_results})

    return "I hit the limit on query steps. Try a simpler question."
