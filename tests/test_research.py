import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock
from langchain_core.messages import AIMessage
from research import slugify, summarize, save_outputs, REPORT_PATH, SOURCES_PATH


class TestResearch(unittest.TestCase):
    def test_slugify(self):
        self.assertEqual(slugify("survey about world model"), "survey-about-world-model")
        self.assertEqual(slugify(""), "topic")
        self.assertEqual(slugify("   "), "topic")
        # Path traversal prevention
        self.assertNotIn("/", slugify("../../etc/passwd"))
        self.assertNotIn("..", slugify("../../etc/passwd"))
        # Max 60 chars
        long_title = "a" * 100
        self.assertLessEqual(len(slugify(long_title)), 60)

    def test_summarize(self):
        msg1 = AIMessage(
            content="Delegating",
            tool_calls=[{"id": "c1", "name": "task", "args": {}}, {"id": "c2", "name": "write_todos", "args": {}}],
            usage_metadata={"input_tokens": 100, "output_tokens": 50, "total_tokens": 150},
        )
        msg2 = AIMessage(
            content="Another call",
            tool_calls=[{"id": "c3", "name": "task", "args": {}}],
            usage_metadata={"input_tokens": 80, "output_tokens": 20, "total_tokens": 100},
        )
        summary = summarize([msg1, msg2], 12.345, "test-model")
        self.assertEqual(summary["model"], "test-model")
        self.assertEqual(summary["elapsed_s"], 12.3)
        self.assertEqual(summary["subagent_calls"], 2)
        self.assertEqual(summary["tool_calls"]["task"], 2)
        self.assertEqual(summary["tool_calls"]["write_todos"], 1)
        self.assertEqual(summary["tokens"]["input"], 180)
        self.assertEqual(summary["tokens"]["output"], 70)

    def test_save_outputs_failure_on_missing_files(self):
        backend = MagicMock()
        # Mock download returning None
        with tempfile.TemporaryDirectory() as tmpdir:
            backend.download_files.return_value = [
                MagicMock(path=REPORT_PATH, content=None),
                MagicMock(path=SOURCES_PATH, content=None),
            ]
            with self.assertRaises(RuntimeError):
                save_outputs(backend, "test topic", [], 1.0, "m", tmpdir)

    def test_save_outputs_success(self):
        backend = MagicMock()
        sources_json = json.dumps([
            {"n": 1, "id": "1", "url": "https://arxiv.org/abs/1", "source": "arxiv"},
            {"n": 2, "id": "2", "url": "https://huggingface.co/papers/2", "source": "hf-search"},
            {"n": 3, "id": "3", "url": "https://example.com/3", "source": "web"},
        ]).encode("utf-8")
        report_md = b"# Report\n\nContent [1][2][3].\n\n## References\n[1] ..."

        backend.download_files.return_value = [
            MagicMock(path=REPORT_PATH, content=report_md),
            MagicMock(path=SOURCES_PATH, content=sources_json),
        ]

        with tempfile.TemporaryDirectory() as tmpdir:
            out_file = save_outputs(backend, "test topic", [], 2.0, "m", tmpdir)
            p = Path(tmpdir)
            self.assertTrue((p / "test-topic.md").exists())
            self.assertTrue((p / "test-topic.sources.json").exists())
            self.assertTrue((p / "test-topic.meta.json").exists())

            meta = json.loads((p / "test-topic.meta.json").read_text("utf-8"))
            self.assertEqual(meta["topic"], "test topic")
            self.assertEqual(meta["n_sources"], 3)
            self.assertEqual(meta["source_families"], ["arxiv", "hf-search", "web"])


if __name__ == "__main__":
    unittest.main()
