import unittest
from unittest.mock import MagicMock, patch
from tools import SOURCE_TOOLS, web_fetch
from agents import (
    LEAD_PROMPT,
    RESEARCHER_PROMPT,
    CHECKER_PROMPT,
    NOTES_DIR,
    SOURCES_PATH,
    VALIDATOR_PATH,
    FINALIZER_PATH,
    REPORT_PATH,
    build_subagents,
    build_lead_agent,
)


class TestAgents(unittest.TestCase):
    def test_prompts_contain_required_contract_and_paths(self):
        self.assertIn(NOTES_DIR, LEAD_PROMPT)
        self.assertIn(SOURCES_PATH, LEAD_PROMPT)
        self.assertIn(VALIDATOR_PATH, LEAD_PROMPT)
        self.assertIn(FINALIZER_PATH, LEAD_PROMPT)
        self.assertIn(REPORT_PATH, LEAD_PROMPT)
        self.assertIn("write_todos", LEAD_PROMPT)
        self.assertIn("task", LEAD_PROMPT)
        self.assertIn("execute", LEAD_PROMPT)

        self.assertIn("untrusted", RESEARCHER_PROMPT.lower())
        self.assertIn("untrusted", CHECKER_PROMPT.lower())

    def test_build_subagents(self):
        subagents = build_subagents()
        self.assertEqual(len(subagents), 2)
        by_name = {s["name"]: s for s in subagents}

        self.assertIn("researcher", by_name)
        researcher = by_name["researcher"]
        self.assertEqual(len(researcher["tools"]), len(SOURCE_TOOLS))
        self.assertIn("middleware", researcher)
        self.assertGreater(len(researcher["middleware"]), 0)

        self.assertIn("citation-checker", by_name)
        checker = by_name["citation-checker"]
        self.assertEqual(checker["tools"], [web_fetch])
        self.assertIn("middleware", checker)
        self.assertGreater(len(checker["middleware"]), 0)

    @patch("agents.create_deep_agent")
    def test_build_lead_agent(self, mock_create):
        mock_backend = MagicMock()
        mock_model = MagicMock()
        mock_create.return_value = "mock_agent"

        agent = build_lead_agent(mock_backend, mock_model)
        self.assertEqual(agent, "mock_agent")
        mock_create.assert_called_once()
        kwargs = mock_create.call_args.kwargs
        self.assertEqual(kwargs["model"], mock_model)
        self.assertEqual(kwargs["backend"], mock_backend)
        self.assertIn("middleware", kwargs)
        # Check TodoListMiddleware is present
        middleware_names = [type(m).__name__ for m in kwargs["middleware"]]
        self.assertIn("TodoListMiddleware", middleware_names)
        self.assertIn("ModelCallLimitMiddleware", middleware_names)
        self.assertIn("ToolCallLimitMiddleware", middleware_names)


if __name__ == "__main__":
    unittest.main()
