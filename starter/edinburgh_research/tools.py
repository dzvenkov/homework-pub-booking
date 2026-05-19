"""Ex5 tools. Four tools the agent uses to research an Edinburgh booking.

Each tool:
  1. Reads its fixture from sample_data/ (DO NOT modify the fixtures).
  2. Logs its arguments and output into _TOOL_CALL_LOG (see integrity.py).
  3. Returns a ToolResult with success=True/False, output=dict, summary=str.

The grader checks for:
  * Correct parallel_safe flags (reads True, generate_flyer False).
  * Every tool's results appear in _TOOL_CALL_LOG.
  * Tools fail gracefully on missing fixtures or bad inputs (ToolError,
    not RuntimeError).
"""

from __future__ import annotations

import json
from html import escape
from pathlib import Path

from sovereign_agent.errors import ToolError
from sovereign_agent.session.directory import Session
from sovereign_agent.tools.registry import ToolRegistry, ToolResult, _RegisteredTool

from starter.edinburgh_research.integrity import record_tool_call

_SAMPLE_DATA = Path(__file__).parent / "sample_data"


def _load_json_fixture(filename: str) -> object:
    path = _SAMPLE_DATA / filename
    if not path.exists():
        raise ToolError(
            code="SA_TOOL_DEPENDENCY_MISSING",
            message=f"required fixture missing: {filename}",
            context={"path": str(path)},
        )
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def _invalid_input_result(
    tool_name: str, arguments: dict, message: str, **context: object
) -> ToolResult:
    error = ToolError(
        code="SA_TOOL_INVALID_INPUT",
        message=message,
        context=context,
    )
    output = {"error": message}
    record_tool_call(tool_name, arguments, output)
    return ToolResult(success=False, output=output, summary=message, error=error)


# ---------------------------------------------------------------------------
# TODO 1 — venue_search
# ---------------------------------------------------------------------------
def venue_search(near: str, party_size: int, budget_max_gbp: int = 1000) -> ToolResult:
    """Search for Edinburgh venues near <near> that can seat the party.

    Reads sample_data/venues.json. Filters by:
      * open_now == True
      * area contains <near> (case-insensitive substring match)
      * seats_available_evening >= party_size
      * hire_fee_gbp + min_spend_gbp <= budget_max_gbp

    Returns a ToolResult with:
      output: {"near": ..., "party_size": ..., "results": [<venue dicts>], "count": int}
      summary: "venue_search(<near>, party=<N>): <count> result(s)"

    MUST call record_tool_call(...) before returning so the integrity
    check can see what data was produced.
    """
    venues = _load_json_fixture("venues.json")
    if not isinstance(venues, list):
        raise ToolError(
            code="SA_TOOL_EXECUTION_FAILED",
            message="venues fixture is malformed",
            context={"expected": "list"},
        )

    near_normalized = near.strip().lower()
    results = [
        venue
        for venue in venues
        if isinstance(venue, dict)
        and venue.get("open_now") is True
        and near_normalized in str(venue.get("area", "")).lower()
        and int(venue.get("seats_available_evening", 0)) >= party_size
        and int(venue.get("hire_fee_gbp", 0)) + int(venue.get("min_spend_gbp", 0)) <= budget_max_gbp
    ]

    output = {
        "near": near,
        "party_size": party_size,
        "results": results,
        "count": len(results),
    }
    record_tool_call(
        "venue_search",
        {"near": near, "party_size": party_size, "budget_max_gbp": budget_max_gbp},
        output,
    )
    return ToolResult(
        success=True,
        output=output,
        summary=f"venue_search({near}, party={party_size}): {len(results)} result(s)",
    )


# ---------------------------------------------------------------------------
# TODO 2 — get_weather
# ---------------------------------------------------------------------------
def get_weather(city: str, date: str) -> ToolResult:
    """Look up the scripted weather for <city> on <date> (YYYY-MM-DD).

    Reads sample_data/weather.json. Returns:
      output: {"city": str, "date": str, "condition": str, "temperature_c": int, ...}
      summary: "get_weather(<city>, <date>): <condition>, <temp>C"

    If the city or date is not in the fixture, return success=False with
    a clear ToolError (SA_TOOL_INVALID_INPUT). Do NOT raise.

    MUST call record_tool_call(...) before returning.
    """
    weather_by_city = _load_json_fixture("weather.json")
    if not isinstance(weather_by_city, dict):
        raise ToolError(
            code="SA_TOOL_EXECUTION_FAILED",
            message="weather fixture is malformed",
            context={"expected": "object"},
        )

    city_key = city.strip().lower()
    city_forecast = weather_by_city.get(city_key)
    if not isinstance(city_forecast, dict):
        return _invalid_input_result(
            "get_weather",
            {"city": city, "date": date},
            f"weather unavailable for city {city!r}",
            city=city,
            date=date,
        )

    forecast = city_forecast.get(date)
    if not isinstance(forecast, dict):
        return _invalid_input_result(
            "get_weather",
            {"city": city, "date": date},
            f"weather unavailable for {city!r} on {date!r}",
            city=city,
            date=date,
        )

    output = {"city": city, "date": date, **forecast}
    record_tool_call("get_weather", {"city": city, "date": date}, output)
    return ToolResult(
        success=True,
        output=output,
        summary=f"get_weather({city}, {date}): {forecast['condition']}, {forecast['temperature_c']}C",
    )


# ---------------------------------------------------------------------------
# TODO 3 — calculate_cost
# ---------------------------------------------------------------------------
def calculate_cost(
    venue_id: str,
    party_size: int,
    duration_hours: int,
    catering_tier: str = "bar_snacks",
) -> ToolResult:
    """Compute the total cost for a booking.

    Formula:
      base_per_head = base_rates_gbp_per_head[catering_tier]
      venue_mult    = venue_modifiers[venue_id]
      subtotal      = base_per_head * venue_mult * party_size * max(1, duration_hours)
      service       = subtotal * service_charge_percent / 100
      total         = subtotal + service + <venue's hire_fee_gbp + min_spend_gbp>
      deposit_rule  = per deposit_policy thresholds

    Returns:
      output: {
        "venue_id": str,
        "party_size": int,
        "duration_hours": int,
        "catering_tier": str,
        "subtotal_gbp": int,
        "service_gbp": int,
        "total_gbp": int,
        "deposit_required_gbp": int,
      }
      summary: "calculate_cost(<venue>, <party>): total £<N>, deposit £<M>"

    MUST call record_tool_call(...) before returning.
    """
    venues = _load_json_fixture("venues.json")
    catering = _load_json_fixture("catering.json")
    if not isinstance(venues, list) or not isinstance(catering, dict):
        raise ToolError(
            code="SA_TOOL_EXECUTION_FAILED",
            message="cost fixtures are malformed",
        )

    venue = next(
        (item for item in venues if isinstance(item, dict) and item.get("id") == venue_id), None
    )
    if venue is None:
        return _invalid_input_result(
            "calculate_cost",
            {
                "venue_id": venue_id,
                "party_size": party_size,
                "duration_hours": duration_hours,
                "catering_tier": catering_tier,
            },
            f"unknown venue_id {venue_id!r}",
            venue_id=venue_id,
        )

    base_rates = catering.get("base_rates_gbp_per_head", {})
    venue_modifiers = catering.get("venue_modifiers", {})
    if catering_tier not in base_rates:
        return _invalid_input_result(
            "calculate_cost",
            {
                "venue_id": venue_id,
                "party_size": party_size,
                "duration_hours": duration_hours,
                "catering_tier": catering_tier,
            },
            f"unsupported catering_tier {catering_tier!r}",
            catering_tier=catering_tier,
        )
    if venue_id not in venue_modifiers:
        return _invalid_input_result(
            "calculate_cost",
            {
                "venue_id": venue_id,
                "party_size": party_size,
                "duration_hours": duration_hours,
                "catering_tier": catering_tier,
            },
            f"missing venue modifier for {venue_id!r}",
            venue_id=venue_id,
        )

    base_per_head = float(base_rates[catering_tier])
    venue_mult = float(venue_modifiers[venue_id])
    subtotal = round(base_per_head * venue_mult * party_size * max(1, duration_hours))
    service_percent = float(catering.get("service_charge_percent", 0))
    service = round(subtotal * service_percent / 100)
    venue_charge = int(venue.get("hire_fee_gbp", 0)) + int(venue.get("min_spend_gbp", 0))
    total = subtotal + service + venue_charge

    if total < 300:
        deposit = 0
    elif total <= 1000:
        deposit = round(total * 0.2)
    else:
        deposit = round(total * 0.3)

    output = {
        "venue_id": venue_id,
        "party_size": party_size,
        "duration_hours": duration_hours,
        "catering_tier": catering_tier,
        "subtotal_gbp": subtotal,
        "service_gbp": service,
        "total_gbp": total,
        "deposit_required_gbp": deposit,
    }
    arguments = {
        "venue_id": venue_id,
        "party_size": party_size,
        "duration_hours": duration_hours,
        "catering_tier": catering_tier,
    }
    record_tool_call("calculate_cost", arguments, output)
    return ToolResult(
        success=True,
        output=output,
        summary=f"calculate_cost({venue_id}, {party_size}): total £{total}, deposit £{deposit}",
    )


# ---------------------------------------------------------------------------
# TODO 4 — generate_flyer
# ---------------------------------------------------------------------------
def generate_flyer(session: Session, event_details: dict) -> ToolResult:
    """Produce an HTML flyer and write it to workspace/flyer.html.

    event_details is expected to contain at least:
      venue_name, venue_address, date, time, party_size, condition,
      temperature_c, total_gbp, deposit_required_gbp

    Write a self-contained HTML flyer (inline CSS, no external assets). Tag every key fact with data-testid="<n>" so the integrity check can parse it.

    Write a formatted HTML flyer with an H1 title, the event
    facts, a weather summary, and the cost breakdown.

    Returns:
      output: {"path": "workspace/flyer.html", "bytes_written": int}
      summary: "generate_flyer: wrote <path> (<N> chars)"

    MUST call record_tool_call(...) before returning — the integrity
    check compares the flyer's contents against earlier tool outputs.

    IMPORTANT: this tool MUST be registered with parallel_safe=False
    because it writes a file.
    """
    required_fields = [
        "venue_name",
        "venue_address",
        "date",
        "time",
        "party_size",
        "condition",
        "temperature_c",
        "total_gbp",
        "deposit_required_gbp",
    ]
    missing = [field for field in required_fields if field not in event_details]
    if missing:
        return _invalid_input_result(
            "generate_flyer",
            {"event_details": event_details},
            f"missing required flyer field(s): {', '.join(missing)}",
            missing_fields=missing,
        )

    facts = {
        "venue_name": str(event_details["venue_name"]),
        "venue_address": str(event_details["venue_address"]),
        "date": str(event_details["date"]),
        "time": str(event_details["time"]),
        "party_size": str(event_details["party_size"]),
        "condition": str(event_details["condition"]),
        "temperature_c": f"{event_details['temperature_c']}C",
        "total_gbp": f"£{event_details['total_gbp']}",
        "deposit_required_gbp": f"£{event_details['deposit_required_gbp']}",
    }
    optional_facts = {}
    for key in ["venue_id", "subtotal_gbp", "service_gbp"]:
        if key in event_details:
            value = event_details[key]
            optional_facts[key] = f"£{value}" if key.endswith("_gbp") else str(value)

    all_facts = {**facts, **optional_facts}
    flyer_path = session.path("workspace/flyer.html")
    flyer_path.parent.mkdir(parents=True, exist_ok=True)

    fact_items = "\n".join(
        f'      <div class="fact"><span class="label">{escape(key.replace("_", " ").title())}</span><span data-testid="{escape(key)}">{escape(value)}</span></div>'
        for key, value in all_facts.items()
    )
    weather_summary = (
        f"{escape(str(event_details['condition']).replace('_', ' '))}, "
        f"{escape(str(event_details['temperature_c']))}C"
    )
    html = f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{escape(facts["venue_name"])} Event Flyer</title>
    <style>
      :root {{
        color-scheme: light;
        --bg: #f5efe3;
        --panel: #fffaf0;
        --ink: #1f2a30;
        --accent: #9b4d1f;
        --border: #d8c3a5;
      }}
      body {{
        margin: 0;
        font-family: Georgia, "Times New Roman", serif;
        background: linear-gradient(180deg, #efe3cf 0%, var(--bg) 100%);
        color: var(--ink);
      }}
      main {{
        max-width: 720px;
        margin: 40px auto;
        padding: 32px;
        background: var(--panel);
        border: 2px solid var(--border);
        border-radius: 18px;
        box-shadow: 0 14px 40px rgba(31, 42, 48, 0.12);
      }}
      h1 {{
        margin-top: 0;
        color: var(--accent);
        letter-spacing: 0.04em;
      }}
      .lede {{
        font-size: 1.1rem;
        margin-bottom: 24px;
      }}
      .grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 14px;
      }}
      .fact {{
        padding: 12px 14px;
        border: 1px solid var(--border);
        border-radius: 12px;
        background: #fff;
      }}
      .label {{
        display: block;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #6a655f;
        margin-bottom: 6px;
      }}
      .note {{
        margin-top: 24px;
        padding-top: 18px;
        border-top: 1px dashed var(--border);
      }}
    </style>
  </head>
  <body>
    <main>
      <h1>Edinburgh Pub Night</h1>
      <p class="lede">Join us at <strong data-testid="venue_name">{escape(facts["venue_name"])}</strong> for an evening booking in Edinburgh.</p>
      <section class="grid">
{fact_items}
      </section>
      <section class="note">
        <p>Weather outlook: <span data-testid="weather_summary">{weather_summary}</span></p>
        <p>Total estimated cost: <strong data-testid="total_gbp">{escape(facts["total_gbp"])}</strong></p>
        <p>Deposit required: <strong data-testid="deposit_required_gbp">{escape(facts["deposit_required_gbp"])}</strong></p>
      </section>
    </main>
  </body>
</html>
"""
    flyer_path.write_text(html, encoding="utf-8")

    output = {"path": "workspace/flyer.html", "bytes_written": len(html.encode("utf-8"))}
    record_tool_call("generate_flyer", {"event_details": event_details}, output)
    return ToolResult(
        success=True,
        output=output,
        summary=f"generate_flyer: wrote {output['path']} ({len(html)} chars)",
    )


# ---------------------------------------------------------------------------
# Registry builder — DO NOT MODIFY the name, signature, or registration calls.
# The grader imports and calls this to pick up your tools.
# ---------------------------------------------------------------------------
def build_tool_registry(session: Session) -> ToolRegistry:
    """Build a session-scoped tool registry with all four Ex5 tools plus
    the sovereign-agent builtins (read_file, write_file, list_files,
    handoff_to_structured, complete_task).

    DO NOT change the tool names — the tests and grader call them by name.
    """
    from sovereign_agent.tools.builtin import make_builtin_registry

    reg = make_builtin_registry(session)

    # venue_search
    reg.register(
        _RegisteredTool(
            name="venue_search",
            description="Search Edinburgh venues by area, party size, and max budget.",
            fn=venue_search,
            parameters_schema={
                "type": "object",
                "properties": {
                    "near": {"type": "string"},
                    "party_size": {"type": "integer"},
                    "budget_max_gbp": {"type": "integer", "default": 1000},
                },
                "required": ["near", "party_size"],
            },
            returns_schema={"type": "object"},
            is_async=False,
            parallel_safe=True,  # read-only
            examples=[
                {
                    "input": {"near": "Haymarket", "party_size": 6, "budget_max_gbp": 800},
                    "output": {"count": 1, "results": [{"id": "haymarket_tap"}]},
                }
            ],
        )
    )

    # get_weather
    reg.register(
        _RegisteredTool(
            name="get_weather",
            description="Get scripted weather for a city on a YYYY-MM-DD date.",
            fn=get_weather,
            parameters_schema={
                "type": "object",
                "properties": {
                    "city": {"type": "string"},
                    "date": {"type": "string"},
                },
                "required": ["city", "date"],
            },
            returns_schema={"type": "object"},
            is_async=False,
            parallel_safe=True,  # read-only
            examples=[
                {
                    "input": {"city": "Edinburgh", "date": "2026-04-25"},
                    "output": {"condition": "cloudy", "temperature_c": 12},
                }
            ],
        )
    )

    # calculate_cost
    reg.register(
        _RegisteredTool(
            name="calculate_cost",
            description="Compute total cost and deposit for a booking.",
            fn=calculate_cost,
            parameters_schema={
                "type": "object",
                "properties": {
                    "venue_id": {"type": "string"},
                    "party_size": {"type": "integer"},
                    "duration_hours": {"type": "integer"},
                    "catering_tier": {
                        "type": "string",
                        "enum": ["drinks_only", "bar_snacks", "sit_down_meal", "three_course_meal"],
                        "default": "bar_snacks",
                    },
                },
                "required": ["venue_id", "party_size", "duration_hours"],
            },
            returns_schema={"type": "object"},
            is_async=False,
            parallel_safe=True,  # pure compute, no shared state
            examples=[
                {
                    "input": {
                        "venue_id": "haymarket_tap",
                        "party_size": 6,
                        "duration_hours": 3,
                    },
                    "output": {"total_gbp": 540, "deposit_required_gbp": 0},
                }
            ],
        )
    )

    # generate_flyer — parallel_safe=False because it writes a file
    def _flyer_adapter(event_details: dict) -> ToolResult:
        return generate_flyer(session, event_details)

    reg.register(
        _RegisteredTool(
            name="generate_flyer",
            description="Write an HTML flyer for the event to workspace/flyer.html.",
            fn=_flyer_adapter,
            parameters_schema={
                "type": "object",
                "properties": {"event_details": {"type": "object"}},
                "required": ["event_details"],
            },
            returns_schema={"type": "object"},
            is_async=False,
            parallel_safe=False,  # writes a file — MUST be False
            examples=[
                {
                    "input": {
                        "event_details": {
                            "venue_name": "Haymarket Tap",
                            "date": "2026-04-25",
                            "party_size": 6,
                        }
                    },
                    "output": {"path": "workspace/flyer.html"},
                }
            ],
        )
    )

    return reg


__all__ = [
    "build_tool_registry",
    "venue_search",
    "get_weather",
    "calculate_cost",
    "generate_flyer",
]
