# Deep Research Agent Design Specification

## Overview
This document specifies the technical design for the Deep Research Agent system in compliance with `README.md`, `GUIDE.md`, and `RUBRIC.md`. The system leverages `deepagents` (LangChain), runs in an isolated sandbox (Daytona or local Docker), calls LLM (configured with Groq via OpenAI-compatible endpoint), retrieves data from 4 source families (`arxiv`, `hf-daily`, `hf-search`, `web`), synthesizes evidence into topic reports adhering to `REPORT_TEMPLATE.md`, validates citations via `check_citations.py` and `finalize_citations.py`, and outputs verifiable reports with metadata.

## Global Constraints & Requirements
- **Language**: Python 3.11+.
- **Sandbox Architecture**:
  - Hosted tools for network operations: `arxiv_search`, `hf_daily_papers`, `hf_search_papers`, `web_search`, `web_fetch`.
  - Sandboxed execution: `execute` runs `finalize_citations.py` and `check_citations.py`. Notes, `sources.json`, and `report.md` reside in `/tmp/work/` inside the sandbox.
  - Zero secrets in sandbox: API keys stay strictly on the host.
  - Sandbox lifecycle managed with `open_sandbox()` context manager (always cleans up containers).
- **Rate Limiting & Resilience**:
  - `with_retry`: Exponential backoff with random jitter, respects `Retry-After` header/field, bounded by `cap`. Retries `RetryableError`, HTTP 429, 500, 502, 503, 504, and `httpx.TransportError`.
  - arXiv rate limiting: strictly >= 3 seconds between successive calls. Query sanitized of bad punctuation.
  - Exa MCP over HTTP POST: detects rate limit in `result._meta`, redacts `EXA_API_KEY` from error outputs.
  - Tools return string representations (JSON strings or compact text) and never raise unhandled exceptions (`"NO RESULTS"` or `"ERROR: ..."`).
- **Multi-Agent Coordination & Safety**:
  - Lead agent:
    - Plans with `write_todos` (via `TodoListMiddleware`).
    - Splits topic into $N \ge 3$ sub-questions and delegates to `researcher` subagents via `task` tool in parallel.
    - Delegation message provides full context: topic, sub-question, note file path (`/tmp/work/research/notes/<NN>-<slug>.md`), note format.
    - Aggregates notes into `/tmp/work/research/sources.json` ensuring $\ge 3$ distinct source families (`arxiv`, `hf-daily`, `hf-search`, `web`).
    - Writes report body according to `REPORT_TEMPLATE.md` (no `## References` section).
    - Runs `finalize_citations.py` via `execute`, then verifies with `check_citations.py` via `execute`.
    - Asks `citation-checker` subagent to spot-check sample claims.
  - Cost & recursion protection (Rubric 2.5):
    - Lead limits: `ModelCallLimitMiddleware(run_limit=150, exit_behavior="end")`, `ToolCallLimitMiddleware(run_limit=300)`.
    - Subagent limits: `ModelCallLimitMiddleware(run_limit=40, exit_behavior="end")`, `ToolCallLimitMiddleware(run_limit=60)`.
    - `recursion_limit` set to 1000 in `agent.invoke(...)`.

## Component Design

### 1. Citation Validator (`check_citations.py`)
- Standard library only. Runs inside sandbox and host verification.
- Checks:
  1. `sources` is a non-empty list of dicts.
  2. For every source: `n` is an integer, `url` starts with `http://` or `https://`, no duplicate URLs.
  3. Report contains `## References` heading. Text before it is the body.
  4. Body citations `[n]` (ignoring code blocks, backticks, and markdown links `[n](...)`) are extracted. Grouped formats like `[1, 2]` or `[1-3]` are expanded.
  5. Every cited number exists in `sources.json`.
  6. Every source in `sources.json` is cited at least once in body.
  7. References section has exactly one line per source starting with `[n]`.
  8. Each reference line contains exactly one HTTP/HTTPS URL which matches that source's `url`.
- Returns list of problem strings (`[]` on OK).

### 2. Network Tools & Resilience (`tools.py`)
- `with_retry(fn, *, attempts=5, base=1.0, cap=30.0)`
- `arxiv_search(query: str, max_results: int = 10)`
- `hf_daily_papers(limit: int = 30, date: str = "", keyword: str = "")`
- `hf_search_papers(query: str, limit: int = 10)`
- `web_search(query: str, objective: str = "", num_results: int = 5)`
- `web_fetch(url: str)`
- `SOURCE_TOOLS = [arxiv_search, hf_daily_papers, hf_search_papers, web_search, web_fetch]`

### 3. Agent Prompts & Definitions (`agents.py`)
- `LEAD_PROMPT`: Instructions for planning, sub-question delegation, source family validation, report generation, executing finalizer & validator, and spot checking.
- `RESEARCHER_PROMPT`: Instructs researcher that web text is untrusted, prohibits hallucinations, mandates $\ge 2$ source families per sub-question, defines exact note structure.
- `CHECKER_PROMPT`: Fetches URLs using `web_fetch` to verify claims (SUPPORTED / PARTIAL / UNSUPPORTED / UNVERIFIABLE).
- `build_subagents()`: Creates `researcher` and `citation-checker` with `SUB_LIMITS`.
- `build_lead_agent(backend, model)`: Creates `create_deep_agent` with `TodoListMiddleware()` and `LEAD_LIMITS`.

### 4. Runner Pipeline (`research.py`)
- `slugify(topic)`: Safe sanitization, regex `[a-z0-9]+`, joined with `-`, max 60 chars.
- `build_prompt(topic)`: Clear initial instructions for lead agent.
- `summarize(messages, elapsed, model_name)`: Parses `subagent_calls` (count of `task`), `tool_calls` by name, input/output tokens from `usage_metadata`, elapsed seconds.
- `save_outputs(...)`: Validates downloaded files (`report.md` non-empty, `sources.json` valid), extracts `source_families` and writes `<slug>.md`, `<slug>.sources.json`, `<slug>.meta.json`.
- `main(topic)`: Sets up sandbox directories, uploads `check_citations.py` and `finalize_citations.py`, invokes agent, saves outputs.
