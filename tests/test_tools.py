import unittest
from unittest.mock import MagicMock, patch
import httpx
from tools import with_retry, RetryableError, arxiv_search, hf_daily_papers, hf_search_papers, web_search, web_fetch


class TestTools(unittest.TestCase):
    @patch("time.sleep")
    def test_with_retry_success(self, mock_sleep):
        fn = MagicMock(return_value="ok")
        result = with_retry(fn, attempts=3)
        self.assertEqual(result, "ok")
        self.assertEqual(fn.call_count, 1)
        mock_sleep.assert_not_called()

    @patch("time.sleep")
    def test_with_retry_recovers(self, mock_sleep):
        fn = MagicMock(side_effect=[RetryableError("rate limit", retry_after=2), "ok"])
        result = with_retry(fn, attempts=3)
        self.assertEqual(result, "ok")
        self.assertEqual(fn.call_count, 2)
        mock_sleep.assert_called_once_with(2)

    @patch("time.sleep")
    def test_with_retry_exhausted_no_sleep_on_last(self, mock_sleep):
        fn = MagicMock(side_effect=RetryableError("fail"))
        with self.assertRaises(RetryableError):
            with_retry(fn, attempts=3)
        self.assertEqual(fn.call_count, 3)
        # Should have slept twice (attempts 0 and 1), but NOT after attempt 2 (the 3rd attempt)
        self.assertEqual(mock_sleep.call_count, 2)

    @patch("time.sleep")
    def test_with_retry_non_retryable_raises_immediately(self, mock_sleep):
        fn = MagicMock(side_effect=ValueError("bad argument"))
        with self.assertRaises(ValueError):
            with_retry(fn, attempts=3)
        self.assertEqual(fn.call_count, 1)
        mock_sleep.assert_not_called()

    def test_arxiv_empty_query_no_results(self):
        res = arxiv_search.invoke({"query": "   !@#$   "})
        self.assertEqual(res, "NO RESULTS")

    @patch("tools.with_retry")
    def test_arxiv_search_parsing(self, mock_retry):
        xml_content = (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<feed xmlns="http://www.w3.org/2005/Atom">\n'
            '  <entry>\n'
            '    <id>http://arxiv.org/abs/2501.00001v2</id>\n'
            '    <published>2025-01-01T12:00:00Z</published>\n'
            '    <title>  Sample   Title\nHere  </title>\n'
            '    <summary>  This is a\nsummary.  </summary>\n'
            '  </entry>\n'
            '</feed>'
        )
        mock_resp = MagicMock()
        mock_resp.text = xml_content
        mock_resp.raise_for_status = MagicMock()
        mock_retry.return_value = mock_resp

        res = arxiv_search.invoke({"query": "world model"})
        import json
        records = json.loads(res)
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["id"], "2501.00001")
        self.assertEqual(records[0]["url"], "https://arxiv.org/abs/2501.00001")
        self.assertEqual(records[0]["title"], "Sample Title Here")
        self.assertEqual(records[0]["published"], "2025-01-01")


if __name__ == "__main__":
    unittest.main()
