import unittest
from check_citations import check


class TestCheckCitations(unittest.TestCase):
    def setUp(self):
        self.valid_sources = [
            {"n": 1, "id": "2501.00001", "url": "https://arxiv.org/abs/2501.00001", "title": "Paper 1", "source": "arxiv"},
            {"n": 2, "id": "2501.00002", "url": "https://huggingface.co/papers/2501.00002", "title": "Paper 2", "source": "hf-search"},
        ]
        self.valid_report = (
            "# Survey\n\n"
            "## Background\n"
            "This is a claim [1] and another claim [2].\n\n"
            "## References\n"
            "[1] Paper 1. arxiv. https://arxiv.org/abs/2501.00001 (2025-01-01)\n"
            "[2] Paper 2. hf-search. https://huggingface.co/papers/2501.00002 (2025-01-02)\n"
        )

    def test_valid_report(self):
        problems = check(self.valid_report, self.valid_sources)
        self.assertEqual(problems, [])

    def test_empty_sources(self):
        problems = check(self.valid_report, [])
        self.assertTrue(any("no sources" in p.lower() or "empty" in p.lower() for p in problems))

    def test_invalid_source_entry(self):
        bad_sources = [
            {"n": "not-int", "url": "https://arxiv.org/abs/1"},
            {"n": 2, "url": "ftp://bad-url"},
            {"n": 3, "url": "https://arxiv.org/abs/1"},  # duplicate url
        ]
        problems = check(self.valid_report, bad_sources)
        self.assertGreater(len(problems), 0)

    def test_missing_references_heading(self):
        report = "# Survey\nClaim [1] and [2]."
        problems = check(report, self.valid_sources)
        self.assertTrue(any("references" in p.lower() for p in problems))

    def test_uncited_source(self):
        report = (
            "# Survey\n\nClaim [1].\n\n"
            "## References\n"
            "[1] Paper 1. arxiv. https://arxiv.org/abs/2501.00001 (2025-01-01)\n"
            "[2] Paper 2. hf-search. https://huggingface.co/papers/2501.00002 (2025-01-02)\n"
        )
        problems = check(report, self.valid_sources)
        self.assertTrue(any("never cited" in p.lower() or "2" in p for p in problems))

    def test_cited_missing_source(self):
        report = (
            "# Survey\n\nClaim [1] and [99].\n\n"
            "## References\n"
            "[1] Paper 1. arxiv. https://arxiv.org/abs/2501.00001 (2025-01-01)\n"
            "[2] Paper 2. hf-search. https://huggingface.co/papers/2501.00002 (2025-01-02)\n"
        )
        problems = check(report, self.valid_sources)
        self.assertTrue(any("99" in p for p in problems))

    def test_grouped_citations_expanded(self):
        report = (
            "# Survey\n\nBoth approaches agree [1, 2].\n\n"
            "## References\n"
            "[1] Paper 1. arxiv. https://arxiv.org/abs/2501.00001 (2025-01-01)\n"
            "[2] Paper 2. hf-search. https://huggingface.co/papers/2501.00002 (2025-01-02)\n"
        )
        problems = check(report, self.valid_sources)
        self.assertEqual(problems, [])

    def test_ranged_citations_expanded(self):
        sources = [
            {"n": 1, "url": "https://arxiv.org/abs/1", "title": "P1"},
            {"n": 2, "url": "https://arxiv.org/abs/2", "title": "P2"},
            {"n": 3, "url": "https://arxiv.org/abs/3", "title": "P3"},
        ]
        report = (
            "# Survey\n\nBroad range [1-3].\n\n"
            "## References\n"
            "[1] P1. https://arxiv.org/abs/1\n"
            "[2] P2. https://arxiv.org/abs/2\n"
            "[3] P3. https://arxiv.org/abs/3\n"
        )
        problems = check(report, sources)
        self.assertEqual(problems, [])

    def test_code_blocks_and_markdown_links_ignored(self):
        report = (
            "# Survey\n\n"
            "Check [1] for details. Look at [link](http://example.com) and `arr[2]` or ```python\nx[3] = 1\n```.\n\n"
            "## References\n"
            "[1] Paper 1. arxiv. https://arxiv.org/abs/2501.00001 (2025-01-01)\n"
        )
        sources = [{"n": 1, "url": "https://arxiv.org/abs/2501.00001", "title": "P1"}]
        problems = check(report, sources)
        self.assertEqual(problems, [])

    def test_reference_line_multiple_urls_or_mismatch(self):
        report = (
            "# Survey\n\nClaim [1].\n\n"
            "## References\n"
            "[1] Paper 1. https://arxiv.org/abs/2501.00001 and https://extra.com\n"
        )
        sources = [{"n": 1, "url": "https://arxiv.org/abs/2501.00001", "title": "P1"}]
        problems = check(report, sources)
        self.assertGreater(len(problems), 0)


if __name__ == "__main__":
    unittest.main()
