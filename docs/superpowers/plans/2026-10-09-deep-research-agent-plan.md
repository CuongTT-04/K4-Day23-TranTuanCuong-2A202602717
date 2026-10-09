# Deep Research Agent Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a robust, rate-limited multi-agent deep research pipeline using `deepagents` and Daytona/Docker sandboxes that produces verified research reports across 5 preset topics.

**Architecture:** A lead agent coordinates $N \ge 3$ researcher subagents across 4 source families (`arxiv`, `hf-daily`, `hf-search`, `web`). Network calls remain host-side wrapped in exponential backoff retry. Code analysis, note aggregation, citation finalization, and citation validation execute in an isolated sandbox.

**Tech Stack:** Python 3.11, `deepagents==0.7.21`, `langchain-openai`, `langchain-daytona`, `httpx`, `docker` / `daytona`.

## Global Constraints
- `model.py` and `sandbox.py` must NOT be modified.
- Sandbox runs with zero secrets: all network tools execute on the host.
- All tools return strings (`JSON` or `NO RESULTS` or `ERROR: ...`), never raise exceptions to caller.
- Citations must resolve 100% against `sources.json` and follow `REPORT_TEMPLATE.md`.
- `self_check.py` must pass completely without errors or secret leaks.

---

### Task 1: Implement and verify `check_citations.py`

**Files:**
- Modify: `check_citations.py`
- Test: `tests/test_check_citations.py`

**Interfaces:**
- Produces: `check(report_text: str, sources: list[dict]) -> list[str]`

- [ ] **Step 1: Write test suite for `check_citations.py`**
Create `tests/test_check_citations.py` covering:
- Valid report and matching sources returns `[]`.
- Empty `sources` returns problem.
- Source with invalid URL, non-integer `n`, or duplicate URLs returns problem.
- Missing `## References` section returns problem.
- Body citing a number not in `sources` returns problem.
- Source not cited in body returns problem.
- References list line with duplicate number or number not matching source returns problem.
- References line with multiple URLs or URL mismatch returns problem.
- Grouped citations `[1, 2]` or `[1-3]` properly detected and expanded.
- Numbers inside markdown code blocks (``` ` ```) or links `[1](http://...)` ignored.

- [ ] **Step 2: Run test suite to verify failure**
Run: `python -m unittest tests/test_check_citations.py`
Expected: FAIL with `NotImplementedError`

- [ ] **Step 3: Implement `check()` in `check_citations.py`**
Implement logic following `GUIDE.md` section 4 and docstring:
- Extract body before last `## References`.
- Parse sources validation (`n` integer, `url` starts with `http://` or `https://`, unique URLs).
- Clean body by removing code blocks (``` and `) and markdown links `[n](url)`.
- Extract citations and expand grouped forms (`[1, 2]`, `[1-3]`).
- Validate references section line-by-line (`[n] Title. <source>. <URL> (<date>)`).
- Check exact 1 URL per reference line matching `sources.json`.

- [ ] **Step 4: Run test suite to verify pass**
Run: `python -m unittest tests/test_check_citations.py`
Expected: PASS all tests.

---

### Task 2: Implement and verify `tools.py`

**Files:**
- Modify: `tools.py`
- Test: `tests/test_tools.py`

**Interfaces:**
- Produces:
  - `with_retry(fn, *, attempts=5, base=1.0, cap=30.0)`
  - `arxiv_search(query: str, max_results: int = 10) -> str`
  - `hf_daily_papers(limit: int = 30, date: str = "", keyword: str = "") -> str`
  - `hf_search_papers(query: str, limit: int = 10) -> str`
  - `web_search(query: str, objective: str = "", num_results: int = 5) -> str`
  - `web_fetch(url: str) -> str`
  - `SOURCE_TOOLS`

- [ ] **Step 1: Write unit tests for `tools.py`**
Create `tests/test_tools.py` testing:
- `with_retry`: backoff delays, jitter, retry on `RetryableError`, HTTP 429/5xx, `httpx.TransportError`, honors `retry_after`, fails on non-retryable errors without sleep on last attempt.
- `arxiv_search`: query sanitation (empty returns `NO RESULTS`), 3s rate-limiting logic, XML parsing.
- `hf_daily_papers` & `hf_search_papers`: response formatting, keyword filtering, sorting by upvotes.
- `web_search` & `web_fetch`: Exa JSON-RPC over HTTP, rate limit detection in `_meta`, `EXA_API_KEY` redaction in error messages.

- [ ] **Step 2: Run test suite to verify failure**
Run: `python -m unittest tests/test_tools.py`
Expected: FAIL with `NotImplementedError`

- [ ] **Step 3: Implement `with_retry` and the 5 source tools in `tools.py`**
- Implement `with_retry` with exponential backoff `base * (2 ** attempt) + random.uniform(0, 0.5)`, capped at `cap`, respecting `Retry-After`.
- Implement `arxiv_search` with HTTPS query, timestamp tracking for >= 3s interval, XML parsing for title, published date, summary.
- Implement `hf_daily_papers` and `hf_search_papers` using `httpx.get`.
- Implement `web_search` and `web_fetch` using HTTP POST to `https://mcp.exa.ai/mcp`, parsing SSE lines (`data: ...`), checking `_meta` for rate limit signals, redacting keys in errors.
- Wrap all network tools so they never raise exceptions to caller.

- [ ] **Step 4: Run test suite to verify pass**
Run: `python -m unittest tests/test_tools.py`
Expected: PASS

- [ ] **Step 5: Run `python tools.py` live check**
Run: `python tools.py`
Expected: Output printed for tools without crashing.

---

### Task 3: Implement `agents.py`

**Files:**
- Modify: `agents.py`
- Test: `tests/test_agents.py`

**Interfaces:**
- Produces:
  - `LEAD_PROMPT: str`
  - `RESEARCHER_PROMPT: str`
  - `CHECKER_PROMPT: str`
  - `build_subagents() -> list[dict]`
  - `build_lead_agent(backend, model)`

- [ ] **Step 1: Write test for agent configuration**
Create `tests/test_agents.py` verifying:
- `build_subagents()` returns dicts with names `researcher` and `citation-checker`.
- Researcher contains all tools in `SOURCE_TOOLS`.
- Citation-checker contains `[web_fetch]`.
- Both subagents configure `SUB_LIMITS` middleware.
- `build_lead_agent` registers `TodoListMiddleware` and `LEAD_LIMITS`.

- [ ] **Step 2: Run test suite to verify failure**
Run: `python -m unittest tests/test_agents.py`
Expected: FAIL with `NotImplementedError`

- [ ] **Step 3: Implement prompts and builder functions in `agents.py`**
- Write `LEAD_PROMPT`: explicit steps for planning (`write_todos`), breaking topic into $\ge 3$ sub-questions, parallel `task` delegation with note paths, checking notes, merging into `sources.json` with $\ge 3$ families, writing report body matching `REPORT_TEMPLATE.md`, running `finalize_citations.py` and `check_citations.py` via `execute`, requesting citation spot-check.
- Write `RESEARCHER_PROMPT`: source tool usage, untrusted web text warning, $\ge 2$ source families per question, note format.
- Write `CHECKER_PROMPT`: verifying claims against source content with `web_fetch`.
- Implement `build_subagents()` with `SUB_LIMITS` (`ModelCallLimitMiddleware(run_limit=40, exit_behavior="end")`, `ToolCallLimitMiddleware(run_limit=60)`).
- Implement `build_lead_agent(backend, model)` with `TodoListMiddleware()` and `LEAD_LIMITS` (`ModelCallLimitMiddleware(run_limit=150, exit_behavior="end")`, `ToolCallLimitMiddleware(run_limit=300)`).

- [ ] **Step 4: Run test suite to verify pass**
Run: `python -m unittest tests/test_agents.py`
Expected: PASS

---

### Task 4: Implement `research.py`

**Files:**
- Modify: `research.py`
- Test: `tests/test_research.py`

**Interfaces:**
- Produces:
  - `slugify(topic: str) -> str`
  - `build_prompt(topic: str) -> str`
  - `summarize(messages, elapsed, model_name) -> dict`
  - `save_outputs(backend, topic, messages, elapsed, model_name, reports_dir) -> Path`
  - `main(topic: str) -> int`

- [ ] **Step 1: Write test suite for helper functions in `research.py`**
Create `tests/test_research.py` testing:
- `slugify`: sanitizes special characters, lowercases, clamps length to 60, handles empty input (`topic`), prevents path traversal `../../`.
- `summarize`: counts `subagent_calls` (calls to `task`), groups `tool_calls` by name, aggregates tokens from `usage_metadata`, rounds elapsed time to 0.1s.
- `save_outputs`: validates downloaded files, refuses to write when files missing/empty/corrupted, writes `.md`, `.sources.json`, `.meta.json`.

- [ ] **Step 2: Run test suite to verify failure**
Run: `python -m unittest tests/test_research.py`
Expected: FAIL with `NotImplementedError`

- [ ] **Step 3: Implement `research.py` functions**
- Implement `slugify(topic)`.
- Implement `build_prompt(topic)`.
- Implement `summarize(messages, elapsed, model_name)`.
- Implement `save_outputs(backend, topic, messages, elapsed, model_name, reports_dir)`.
- Implement `main(topic)`: checks topic, prepares sandbox, uploads validator and finalizer scripts, invokes lead agent, saves output.

- [ ] **Step 4: Run test suite to verify pass**
Run: `python -m unittest tests/test_research.py`
Expected: PASS

---

### Task 5: Integration Verification & Report Generation

- [ ] **Step 1: Verify environment and test sandbox connection**
Run a test script in python to verify `make_model()` works with Groq and `open_sandbox()` works with Docker/Daytona.

- [ ] **Step 2: Run research on the 5 preset topics from `topics.md`**
Run:
1. `python research.py "survey about world model"`
2. `python research.py "survey about reinforcement learning for LLM reasoning"`
3. `python research.py "survey about LLM agents and tool use"`
4. `python research.py "survey about video and multimodal generation"`
5. `python research.py "survey about efficient inference and small language models"`

- [ ] **Step 3: Run `self_check.py`**
Run: `python self_check.py`
Verify: All 5 reports OK, citations OK, source families $\ge 3$, subagent calls $\ge 3$, git secrets check OK.
