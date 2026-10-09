"""tools.py - STUDENT IMPLEMENTS.  Source tools for the research agents.   Guide: GUIDE.md, part 1.

Rules for every tool:
  * runs on the HOST (not in the sandbox): API keys must never enter the sandbox;
  * returns a STRING (JSON text of compact records) and NEVER raises:
        "NO RESULTS"  when the source answers with nothing,
        "ERROR: ..."  when the source keeps failing after the retries (the agent then tries another source);
  * the docstring is the tool description the LLM reads: keep it precise (what it does, what it returns, when to use it).
Try your tools without any agent:   python tools.py
"""
import json  # noqa: F401
import os  # noqa: F401
import time  # noqa: F401
import xml.etree.ElementTree  # noqa: F401  (arXiv answers with Atom XML)

import httpx  # noqa: F401
from langchain_core.tools import tool

# ---- constants (given) ----
ARXIV_URL = "https://export.arxiv.org/api/query"  # https only: http answers 301
HF_DAILY_URL = "https://huggingface.co/api/daily_papers"
HF_SEARCH_URL = "https://huggingface.co/api/papers/search"
EXA_URL = "https://mcp.exa.ai/mcp"


class RetryableError(Exception):
    """Given. Raise it inside a call to ask with_retry to wait and try again (retry_after in seconds, optional)."""

    def __init__(self, message, retry_after=None):
        super().__init__(message)
        self.retry_after = retry_after


import random
import re

# Track time for arXiv to ensure >= 3 seconds between successive calls
_LAST_ARXIV_CALL = 0.0


def _arxiv_rate_limit():
    global _LAST_ARXIV_CALL
    now = time.monotonic()
    elapsed = now - _LAST_ARXIV_CALL
    if elapsed < 3.0:
        time.sleep(3.0 - elapsed)
    _LAST_ARXIV_CALL = time.monotonic()


# ---- TODO 1: retry helper ----
def with_retry(fn, *, attempts=5, base=1.0, cap=30.0):
    """Call fn(); when it raises RetryableError, wait and call it again."""
    for attempt in range(attempts):
        try:
            return fn()
        except Exception as exc:
            is_retryable = False
            retry_after = None

            if isinstance(exc, RetryableError):
                is_retryable = True
                retry_after = exc.retry_after
            elif isinstance(exc, httpx.HTTPStatusError):
                if exc.response.status_code in {429, 500, 502, 503, 504}:
                    is_retryable = True
                    header = exc.response.headers.get("Retry-After")
                    if header:
                        try:
                            retry_after = float(header)
                        except ValueError:
                            pass
            elif isinstance(exc, httpx.TransportError):
                is_retryable = True

            if not is_retryable:
                raise

            if attempt == attempts - 1:
                raise

            if retry_after is not None:
                delay = min(float(retry_after), cap)
            else:
                delay = min(base * (2 ** attempt), cap) + random.uniform(0.0, 0.5)

            time.sleep(delay)


# ---- TODO 2: arXiv ----
@tool
def arxiv_search(query: str, max_results: int = 10) -> str:
    """Search arXiv papers by keywords, newest first. Returns a JSON list of {id, url, published, title, summary}."""
    try:
        clean_terms = re.findall(r"[\w-]+", query)
        if not clean_terms:
            return "NO RESULTS"
        search_query = " AND ".join(f"all:{t}" for t in clean_terms)
        clamped_results = max(1, min(max_results, 3))

        def fetch():
            _arxiv_rate_limit()
            with httpx.Client(timeout=30.0) as client:
                resp = client.get(
                    ARXIV_URL,
                    params={
                        "search_query": search_query,
                        "sortBy": "submittedDate",
                        "sortOrder": "descending",
                        "max_results": clamped_results,
                    },
                )
                resp.raise_for_status()
                return resp

        resp = with_retry(fetch, attempts=5, base=2.0, cap=60.0)

        root = xml.etree.ElementTree.fromstring(resp.text)
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        entries = root.findall("atom:entry", ns)
        records = []
        for entry in entries:
            raw_id = entry.findtext("atom:id", "", ns).strip()
            paper_id = raw_id.split("/abs/")[-1].strip() if "/abs/" in raw_id else raw_id
            paper_id = re.sub(r"v\d+$", "", paper_id)
            if not paper_id:
                continue
            url = f"https://arxiv.org/abs/{paper_id}"
            published = entry.findtext("atom:published", "", ns).strip()[:10]
            title = " ".join(entry.findtext("atom:title", "", ns).split())
            summary = " ".join(entry.findtext("atom:summary", "", ns).split())[:250]
            records.append({
                "id": paper_id,
                "url": url,
                "published": published,
                "title": title,
                "summary": summary,
            })

        if not records:
            return "NO RESULTS"
        return json.dumps(records, ensure_ascii=False)
    except Exception as exc:
        return f"ERROR: {type(exc).__name__}: {exc}"


# ---- TODO 3: Hugging Face ----
@tool
def hf_daily_papers(limit: int = 5, date: str = "", keyword: str = "") -> str:
    """Hugging Face Daily Papers = trending AI papers. Returns JSON list of
    {id, url, published, title, summary, upvotes, github, stars}."""
    try:
        clamped_limit = max(1, min(limit, 5))
        params = {"limit": clamped_limit}
        if date:
            params["date"] = date

        def fetch():
            with httpx.Client(timeout=30.0) as client:
                resp = client.get(HF_DAILY_URL, params=params)
                resp.raise_for_status()
                return resp.json()

        data = with_retry(fetch, attempts=5, base=1.0, cap=30.0)
        if not isinstance(data, list):
            return "NO RESULTS"

        records = []
        for item in data:
            paper = item.get("paper") if isinstance(item, dict) and "paper" in item else item
            if not isinstance(paper, dict):
                continue
            paper_id = paper.get("id")
            if not paper_id:
                continue
            url = f"https://huggingface.co/papers/{paper_id}"
            title = " ".join(str(paper.get("title") or item.get("title") or "").split())
            summary = " ".join(str(paper.get("summary") or item.get("summary") or "").split())[:250]
            published = str(paper.get("publishedAt") or item.get("publishedAt") or "")[:10]
            upvotes = int(paper.get("upvotes") or 0)
            github = str(paper.get("githubRepo") or "")
            stars = int(paper.get("githubStars") or 0)

            if keyword:
                combined = (title + " " + summary).lower()
                if keyword.lower() not in combined:
                    continue

            records.append({
                "id": paper_id,
                "url": url,
                "published": published,
                "title": title,
                "summary": summary,
                "upvotes": upvotes,
                "github": github,
                "stars": stars,
            })

        records.sort(key=lambda r: r.get("upvotes", 0), reverse=True)
        if not records:
            return "NO RESULTS"
        return json.dumps(records[:5], ensure_ascii=False)
    except Exception as exc:
        return f"ERROR: {type(exc).__name__}: {exc}"


@tool
def hf_search_papers(query: str, limit: int = 3) -> str:
    """Search Hugging Face papers by topic. Returns JSON list of
    {id, url, published, title, summary, upvotes, github, stars}."""
    try:
        clamped_limit = max(1, min(limit, 3))

        def fetch():
            with httpx.Client(timeout=30.0) as client:
                resp = client.get(HF_SEARCH_URL, params={"q": query, "limit": clamped_limit})
                resp.raise_for_status()
                return resp.json()

        data = with_retry(fetch, attempts=5, base=1.0, cap=30.0)
        if not isinstance(data, list):
            return "NO RESULTS"

        records = []
        for item in data:
            paper = item.get("paper") if isinstance(item, dict) and "paper" in item else item
            if not isinstance(paper, dict):
                continue
            paper_id = paper.get("id")
            if not paper_id:
                continue
            url = f"https://huggingface.co/papers/{paper_id}"
            title = " ".join(str(paper.get("title") or item.get("title") or "").split())
            raw_summary = paper.get("ai_summary") or paper.get("summary") or item.get("summary") or ""
            summary = " ".join(str(raw_summary).split())[:250]
            published = str(paper.get("publishedAt") or item.get("publishedAt") or "")[:10]
            upvotes = int(paper.get("upvotes") or 0)
            github = str(paper.get("githubRepo") or "")
            stars = int(paper.get("githubStars") or 0)

            records.append({
                "id": paper_id,
                "url": url,
                "published": published,
                "title": title,
                "summary": summary,
                "upvotes": upvotes,
                "github": github,
                "stars": stars,
            })

        if not records:
            return "NO RESULTS"
        return json.dumps(records[:3], ensure_ascii=False)
    except Exception as exc:
        return f"ERROR: {type(exc).__name__}: {exc}"


def _redact_key(msg: str) -> str:
    key = os.getenv("EXA_API_KEY", "").strip()
    if key:
        msg = msg.replace(key, "[REDACTED]")
    return msg


def _call_exa_mcp(tool_name: str, arguments: dict) -> str:
    key = os.getenv("EXA_API_KEY", "").strip()
    endpoint = f"{EXA_URL}?exaApiKey={key}" if key else EXA_URL
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
    }
    if key:
        headers["Authorization"] = f"Bearer {key}"

    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": arguments,
        },
    }

    def fetch():
        with httpx.Client(timeout=45.0) as client:
            resp = client.post(endpoint, headers=headers, json=payload)
            if resp.status_code == 429:
                raise RetryableError("Exa rate limit (HTTP 429)", retry_after=20.0)
            resp.raise_for_status()

            text = resp.text
            data_payload = None
            if "data:" in text:
                for line in text.splitlines():
                    if line.startswith("data:"):
                        raw = line[5:].strip()
                        try:
                            data_payload = json.loads(raw)
                            break
                        except json.JSONDecodeError:
                            continue
            else:
                try:
                    data_payload = resp.json()
                except Exception:
                    pass

            if not data_payload:
                raise RetryableError("Empty response from Exa")

            if "error" in data_payload:
                err = data_payload["error"]
                err_msg = str(err.get("message") if isinstance(err, dict) else err)
                if "rate limit" in err_msg.lower():
                    raise RetryableError(f"Exa rate limit: {err_msg}", retry_after=20.0)
                raise RuntimeError(f"Exa error: {err_msg}")

            result = data_payload.get("result", {})
            meta = result.get("_meta", {})
            if meta and any("rate" in str(k).lower() or "limit" in str(k).lower() for k in meta):
                raise RetryableError("Exa rate limited (_meta flag)", retry_after=20.0)

            contents = result.get("content", [])
            texts = []
            for item in contents:
                if isinstance(item, dict) and item.get("type") == "text":
                    t = item.get("text", "")
                    if "rate limit" in t.lower() and "exceeded" in t.lower():
                        raise RetryableError(f"Exa rate limit text: {t}", retry_after=20.0)
                    texts.append(t)

            res_text = "\n\n".join(texts).strip()
            return res_text

    return with_retry(fetch, attempts=5, base=2.0, cap=60.0)


# ---- TODO 4: web search / fetch through the Exa MCP endpoint ----
@tool
def web_search(query: str, objective: str = "", num_results: int = 5) -> str:
    """Search the web (Exa). Describe the ideal page in natural language. Returns clean text of the top results with URLs."""
    try:
        if not objective:
            objective = f"find papers and technical information about {query}"
        clamped_num = max(1, min(num_results, 10))
        args = {"query": query, "objective": objective, "numResults": clamped_num}
        res = _call_exa_mcp("web_search_exa", args)
        if not res:
            return "NO RESULTS"
        return res
    except Exception as exc:
        return f"ERROR: {_redact_key(f'{type(exc).__name__}: {exc}')}"


@tool
def web_fetch(url: str) -> str:
    """Read content of one web page as markdown."""
    try:
        args = {"urls": [url]}
        res = _call_exa_mcp("web_fetch_exa", args)
        if not res:
            return "NO RESULTS"
        return res[:2500]
    except Exception as exc:
        return f"ERROR: {_redact_key(f'{type(exc).__name__}: {exc}')}"


# ---- TODO 5: registry (the researcher subagent gets exactly these) ----
SOURCE_TOOLS = [arxiv_search, hf_daily_papers, hf_search_papers, web_search, web_fetch]


if __name__ == "__main__":
    for name, fn, args in [
        ("arxiv_search", arxiv_search, {"query": "world model", "max_results": 3}),
        ("hf_daily_papers", hf_daily_papers, {"limit": 20}),
        ("hf_search_papers", hf_search_papers, {"query": "world model", "limit": 3}),
        ("web_search", web_search, {"query": "survey paper on world models", "num_results": 2}),
        ("web_fetch", web_fetch, {"url": "https://arxiv.org/abs/1803.10122"}),
    ]:
        try:
            print(f"== {name}\n{fn.invoke(args)[:400]}\n")
        except NotImplementedError as exc:
            print(f"== {name}: not implemented yet ({exc})\n")
