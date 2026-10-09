"""check_citations.py - STUDENT IMPLEMENTS `check`.   Runs INSIDE the sandbox (standard library only).

research.py uploads this file to the sandbox and the lead agent runs it with the `execute` tool:
    python3 /tmp/work/research/check_citations.py [report.md] [sources.json]
It must exit 0 and print "OK: ..." when the report is consistent, else print each problem and exit 1.
"""
import json
import sys

REPORT = "/tmp/work/report/report.md"
SOURCES = "/tmp/work/research/sources.json"


def check(report_text, sources):
    """Return a list of problem strings (empty list = OK)."""
    import re

    problems = []
    if not isinstance(sources, list) or len(sources) == 0:
        return ["no sources in sources.json"]

    seen_urls = set()
    source_by_n = {}
    for idx, s in enumerate(sources):
        if not isinstance(s, dict):
            problems.append(f"source item {idx} is not an object")
            continue
        n = s.get("n")
        if not isinstance(n, int):
            problems.append(f"source n={n!r} must be an integer")
        elif n in source_by_n:
            problems.append(f"duplicate source number [{n}] in sources.json")
        else:
            source_by_n[n] = s

        url = str(s.get("url") or "").strip()
        if not (url.startswith("http://") or url.startswith("https://")):
            problems.append(f"source [{n}] url must start with http:// or https://: {url!r}")
        elif url in seen_urls:
            problems.append(f"duplicate url in sources.json: {url}")
        else:
            seen_urls.add(url)

    ref_heading = re.compile(r"(?m)^##[ \t]+References[ \t]*$")
    matches = list(ref_heading.finditer(report_text))
    if not matches:
        problems.append("missing '## References' heading in report")
        body = report_text
        ref_text = ""
    else:
        body = report_text[:matches[-1].start()]
        ref_text = report_text[matches[-1].end():]

    # Extract citations in body, ignoring code blocks and markdown links [n](url)
    code_pattern = re.compile(r"(```.*?```|`[^`\n]*`)", re.DOTALL)
    group_pattern = re.compile(r"\[(\d+(?:\s*[,–-]\s*\d+)*)\](?!\()")
    segments = code_pattern.split(body)

    cited_numbers = set()
    for i, segment in enumerate(segments):
        if i % 2 == 1:
            continue  # Inside code block
        for match in group_pattern.finditer(segment):
            group_str = match.group(1)
            for part in re.split(r"\s*,\s*", group_str):
                span = re.fullmatch(r"(\d+)\s*[–-]\s*(\d+)", part)
                if span:
                    a, b = int(span.group(1)), int(span.group(2))
                    if a <= b and b - a <= 500:
                        cited_numbers.update(range(a, b + 1))
                    else:
                        cited_numbers.update([a, b])
                else:
                    if part.isdigit():
                        cited_numbers.add(int(part))

    for n in sorted(cited_numbers):
        if n not in source_by_n:
            problems.append(f"[{n}] cited in text but missing from sources.json")

    for n in sorted(source_by_n):
        if n not in cited_numbers:
            problems.append(f"source [{n}] never cited in report body")

    ref_line_pattern = re.compile(r"^\s*\[(\d+)\]\s*(.*)$")
    ref_entries = {}
    for line in ref_text.splitlines():
        line_clean = line.strip()
        if not line_clean:
            continue
        m = ref_line_pattern.match(line_clean)
        if m:
            ref_n = int(m.group(1))
            if ref_n in ref_entries:
                problems.append(f"reference list contains duplicate entry for [{ref_n}]")
            ref_entries[ref_n] = line_clean

    for n in sorted(source_by_n):
        if n not in ref_entries:
            problems.append(f"missing reference line for source [{n}] in ## References")

    for n in sorted(ref_entries):
        if n not in source_by_n:
            problems.append(f"reference [{n}] exists in ## References but not in sources.json")

    url_pattern = re.compile(r"https?://[^\s)\]>]+")
    for n, line_content in ref_entries.items():
        if n not in source_by_n:
            continue
        expected_url = (source_by_n[n].get("url") or "").strip()
        urls_found = url_pattern.findall(line_content)
        if len(urls_found) == 0:
            problems.append(f"reference line [{n}] has no URL")
        elif len(urls_found) > 1:
            problems.append(f"reference line [{n}] bundles multiple URLs (found {len(urls_found)}): {line_content}")
        else:
            found_url = urls_found[0].rstrip(".,;)")
            exp_clean = expected_url.rstrip(".,;)")
            if found_url != exp_clean:
                problems.append(f"reference line [{n}] URL mismatch: expected {expected_url}, found {found_url}")

    return problems


def main(argv):
    report_path = argv[1] if len(argv) > 1 else REPORT
    sources_path = argv[2] if len(argv) > 2 else SOURCES
    try:
        with open(report_path, encoding="utf-8") as f:
            report = f.read()
        with open(sources_path, encoding="utf-8") as f:
            sources = json.load(f)
    except (OSError, ValueError) as exc:
        print(f"cannot read inputs: {exc}")
        return 1
    problems = check(report, sources)
    if problems:
        print("\n".join(problems))
        return 1
    print(f"OK: {len(sources)} sources, all citations resolve")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
