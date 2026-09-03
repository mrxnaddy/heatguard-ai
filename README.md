# HeatGuard AI

An AI-powered hyperlocal heat-risk intelligence and action platform, built for the
**"Building the World's Temperature AI"** hackathon (FortyGuard Temperature API).

> **Current status: Phase 2 — Project Foundation.**
> The app runs end-to-end on mock data with a polished dashboard shell. Risk
> scoring, hotspot detection, the AI analysis panel, the tool-calling agent,
> the action planner, and location comparison are **not implemented yet** —
> they are Phase 3. Their sections currently render as clearly labeled
> placeholders, not fake data.

## Problem

City-wide temperature forecasts hide dangerous hyperlocal variation — one
paved area can run 8–12°C hotter than a shaded park a few blocks away.
Citizens can't tell if *their* location is dangerous right now, city
authorities can't prioritize limited cooling-center budgets across dozens of
hotspots, and businesses can't quantify outdoor-worker heat exposure. The
missing layer isn't temperature data — it's turning that data into a
specific, defensible decision.

HeatGuard AI's core loop: **Temperature → Risk Score → AI Reasoning →
Prioritized Action → Measurable Impact.**

## Architecture

```
Streamlit UI (app/main.py)
  └─ app/components/        reusable UI pieces (badges, cards, placeholders)
  └─ app/services/
       fortyguard_client.py   adapter: mock provider ⇄ real FortyGuard API (same interface)
       cache.py                simple in-memory TTL cache
  └─ app/ai/
       llm_client.py           config scaffold only — generation logic is Phase 3
  └─ app/data/
       models.py                Pydantic models: TemperatureReading, RiskScore, AIAnalysis, Hotspot
       mock_data.py             realistic, clearly-labeled mock dataset
  └─ app/utils/
       errors.py                typed exceptions + safe_call() — no raw tracebacks reach the UI
  └─ app/config.py            environment-variable configuration, fails loudly if misconfigured
```

Design principle carried through the whole codebase: **code computes every
number** (temperatures, risk scores, deltas); **the LLM only interprets and
recommends**, and only starting in Phase 3, on data it's explicitly given —
never on numbers it invents.

## Tech Stack

- **Frontend:** Streamlit
- **Data validation:** Pydantic
- **Maps (Phase 3):** Folium / streamlit-folium
- **HTTP:** requests (retry + backoff for the real FortyGuard path)
- **Tests:** pytest
- **Deployment target:** Streamlit Community Cloud

## FortyGuard Integration Status

We do not yet have verified FortyGuard API documentation/credentials. Per the
project's accuracy rule, we have **not** invented endpoint URLs, headers, or
response schemas. Instead:

- `app/services/fortyguard_client.py` defines the adapter interface
  (`get_temperature`, `get_temperatures_bulk`, `health_check`) that both a
  mock provider and the real provider implement identically.
- The mock provider (`MockProvider`) is fully working and is the default
  (`USE_MOCK_DATA=true`).
- The real provider (`RealFortyGuardProvider`) has retry/backoff and
  rate-limit handling scaffolded, but its actual request/response logic is
  marked `# TODO: FortyGuard integration point` and raises
  `NotImplementedError` until verified API docs are available. Wiring in
  the real API is designed to be a small, isolated change.

## Installation

```bash
git clone <this-repo>
cd heatguard-ai
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Environment Configuration

```bash
cp .env.example .env
```

| Variable | Required | Default | Notes |
|---|---|---|---|
| `USE_MOCK_DATA` | no | `true` | Set `false` only once real FortyGuard credentials exist |
| `FORTYGUARD_API_KEY` | only if `USE_MOCK_DATA=false` | — | Never commit this |
| `FORTYGUARD_BASE_URL` | no | placeholder URL | Update once verified |
| `LLM_API_KEY` | no (yet) | — | Used starting Phase 3 |
| `LLM_MODEL` | no | `not-configured` | Used starting Phase 3 |
| `CACHE_TTL_SECONDS` | no | `300` | TTL for the in-memory cache |

## Running Locally

```bash
streamlit run app/main.py
```

Runs entirely on mock data by default — no credentials required.

## Mock Mode

Mock mode is the default and the recommended way to run/demo this app right
now. Every mock reading is tagged `source="mock"` in the data model, and the
dashboard shows a persistent **"MOCK DATA"** badge — mock data is never
presented as live.

## Running Tests

```bash
pytest
```

Covers: config loading (mock/real mode branching), Pydantic model
validation (including rejection of out-of-bounds/invalid data), the mock
provider contract, the TTL cache (including stale-fallback behavior), and
the FortyGuardClient adapter's validation/caching behavior.

## Project Structure

```
heatguard-ai/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── services/
│   │   ├── fortyguard_client.py
│   │   └── cache.py
│   ├── ai/
│   │   └── llm_client.py
│   ├── data/
│   │   ├── models.py
│   │   └── mock_data.py
│   ├── utils/
│   │   └── errors.py
│   └── components/
│       └── ui_helpers.py
├── tests/
├── .env.example
├── requirements.txt
└── README.md
```

## Explicitly Out of Scope (MoSCoW WON'T)

User accounts/auth, real-time push notifications, a native mobile app,
multi-language UI. Descoped intentionally to keep the hackathon build
reliable, not as an oversight.

## Roadmap

- **Phase 3:** risk scoring, hotspot detection, AI heat analysis, the
  tool-calling agent, action planner, location comparison.
- **Phase 4:** UI/UX polish pass, resilience testing, accessibility.
- **Phase 5:** demo script, pitch deck, judge Q&A prep.
