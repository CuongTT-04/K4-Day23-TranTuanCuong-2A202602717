"""research.py - STUDENT IMPLEMENTS.  The main script.   Guide: GUIDE.md, part 3.

Usage:  python research.py "survey about world model"
Result: reports/<slug>.md   reports/<slug>.sources.json   reports/<slug>.meta.json
"""
import json  # noqa: F401
import os  # noqa: F401
import re  # noqa: F401
import sys
import time  # noqa: F401
from collections import Counter  # noqa: F401
from pathlib import Path

from agents import FINALIZER_PATH, REPORT_PATH, SOURCES_PATH, VALIDATOR_PATH, WORKDIR, build_lead_agent  # noqa: F401
from model import make_model  # noqa: F401
from sandbox import download, open_sandbox, upload  # noqa: F401

ROOT = Path(__file__).parent
REPORTS = ROOT / "reports"
VALIDATOR_SOURCE = ROOT / "check_citations.py"
FINALIZER_SOURCE = ROOT / "finalize_citations.py"   # provided: uploaded next to your validator


def slugify(topic):
    """Turn a topic into a safe file name: lower case, runs of non-word characters become one "-", max 60 chars,
    never empty (fall back to "topic"). The topic is user input: "../../x" must not escape reports/."""
    raw = (topic or "").strip().lower()
    cleaned = re.sub(r"[^\w\s-]", "", raw)
    slug = re.sub(r"[-\s_]+", "-", cleaned).strip("-")
    if not slug:
        return "topic"
    truncated = slug[:60].rstrip("-")
    return truncated if truncated else "topic"


def build_prompt(topic):
    """The user message sent to the lead agent."""
    return (
        f"Conduct a comprehensive, multi-agent deep research survey on the topic: '{topic}'.\n\n"
        "Follow all system instructions:\n"
        "1. Plan with write_todos and split into >= 3 independent sub-questions.\n"
        "2. Delegate in parallel to researcher subagents with full context and note paths.\n"
        "3. Review notes and aggregate sources into sources.json with >= 3 distinct source families.\n"
        "4. Synthesize the report according to REPORT_TEMPLATE.md (without ## References).\n"
        "5. Execute finalize_citations.py to generate references.\n"
        "6. Execute check_citations.py to validate citations until it prints OK.\n"
        "7. Have citation-checker spot check claims.\n\n"
        "Ensure all output files (/tmp/work/report/report.md and /tmp/work/research/sources.json) are complete."
    )


def summarize(messages, elapsed, model_name):
    """Return {"model", "elapsed_s", "subagent_calls", "tool_calls": {name: count}, "tokens": {"input", "output"}}."""
    tool_counts = Counter()
    input_tokens = 0
    output_tokens = 0
    for msg in messages:
        tool_calls = getattr(msg, "tool_calls", None)
        if not tool_calls and hasattr(msg, "additional_kwargs"):
            tool_calls = msg.additional_kwargs.get("tool_calls", [])
        if tool_calls:
            for tc in tool_calls:
                name = tc.get("name") if isinstance(tc, dict) else getattr(tc, "name", str(tc))
                if name:
                    tool_counts[name] += 1
        usage = getattr(msg, "usage_metadata", None)
        if isinstance(usage, dict):
            input_tokens += int(usage.get("input_tokens", 0) or usage.get("prompt_tokens", 0))
            output_tokens += int(usage.get("output_tokens", 0) or usage.get("completion_tokens", 0))
        elif hasattr(msg, "response_metadata") and isinstance(msg.response_metadata, dict):
            token_usage = msg.response_metadata.get("token_usage", {})
            if isinstance(token_usage, dict):
                input_tokens += int(token_usage.get("prompt_tokens", 0))
                output_tokens += int(token_usage.get("completion_tokens", 0))

    return {
        "model": model_name,
        "elapsed_s": round(float(elapsed), 1),
        "subagent_calls": tool_counts.get("task", 0),
        "tool_calls": dict(tool_counts),
        "tokens": {
            "input": input_tokens,
            "output": output_tokens,
        },
    }


def save_outputs(backend, topic, messages, elapsed, model_name, reports_dir=REPORTS):
    """Download the report from the sandbox and write the three files into reports_dir. Return the report path."""
    reports_path = Path(reports_dir)
    reports_path.mkdir(parents=True, exist_ok=True)
    slug = slugify(topic)
    files = download(backend, [REPORT_PATH, SOURCES_PATH])

    report_bytes = files.get(REPORT_PATH)
    sources_bytes = files.get(SOURCES_PATH)

    if not report_bytes or not report_bytes.strip():
        raise RuntimeError(f"Report at {REPORT_PATH} is missing or empty")
    if not sources_bytes or not sources_bytes.strip():
        raise RuntimeError(f"Sources at {SOURCES_PATH} is missing or empty")

    try:
        sources_data = json.loads(sources_bytes.decode("utf-8"))
        if not isinstance(sources_data, list):
            raise ValueError("sources.json is not a list")
    except Exception as exc:
        raise RuntimeError(f"Invalid sources.json: {exc}") from exc

    report_text = report_bytes.decode("utf-8")
    summary = summarize(messages, elapsed, model_name)
    families = sorted(list({s.get("source") for s in sources_data if isinstance(s, dict) and s.get("source")}))

    meta = {
        "topic": topic,
        **summary,
        "n_sources": len(sources_data),
        "source_families": families,
    }

    report_file = reports_path / f"{slug}.md"
    sources_file = reports_path / f"{slug}.sources.json"
    meta_file = reports_path / f"{slug}.meta.json"

    sources_file.write_text(json.dumps(sources_data, ensure_ascii=False, indent=2), encoding="utf-8")
    meta_file.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    report_file.write_text(report_text, encoding="utf-8")

    return report_file


def main(topic):
    """Return the process exit code (0 ok, 1 failed run, 2 no topic)."""
    clean_topic = topic.strip()
    if not clean_topic:
        print('Usage: python research.py "<topic>"', file=sys.stderr)
        return 2

    model = make_model()
    model_name = getattr(model, "model_name", None) or getattr(model, "model", None) or os.getenv("LAB_MODEL", "model")
    start = time.monotonic()

    try:
        with open_sandbox() as backend:
            backend.execute(f"mkdir -p {WORKDIR}/research/notes {WORKDIR}/report")
            upload(
                backend,
                {
                    VALIDATOR_PATH: VALIDATOR_SOURCE.read_bytes(),
                    FINALIZER_PATH: FINALIZER_SOURCE.read_bytes(),
                },
            )
            agent = build_lead_agent(backend, model)
            result = agent.invoke(
                {"messages": [{"role": "user", "content": build_prompt(clean_topic)}]},
                config={"recursion_limit": 1000},
            )
            elapsed = time.monotonic() - start
            messages = result.get("messages", [])
            print(f"[run] Lead agent finished with {len(messages)} messages.", flush=True)
            for i, m in enumerate(messages):
                t_calls = getattr(m, "tool_calls", None)
                if t_calls:
                    print(f"Step {i}: Tool calls -> {[tc.get('name') for tc in t_calls]}", flush=True)
                elif hasattr(m, "content") and m.content:
                    snippet = str(m.content).strip().replace("\n", " ")[:150]
                    if snippet:
                        print(f"Step {i} ({type(m).__name__}): {snippet}", flush=True)

            saved_path = save_outputs(backend, clean_topic, messages, elapsed, str(model_name))
            print(f"SUCCESS: Report saved to {saved_path}", flush=True)
            return 0
    except Exception as exc:
        print(f"FAILED: {exc}", file=sys.stderr, flush=True)
        return 1


if __name__ == "__main__":
    sys.exit(main(" ".join(sys.argv[1:])))
