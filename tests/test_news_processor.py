import unittest
from unittest.mock import patch

from news_processor import NewsProcessor


class NewsProcessorTestCase(unittest.TestCase):
    def setUp(self):
        self.processor = NewsProcessor()
        self.raw_news = [
            {
                "id": "n1",
                "title": "Agent workflow is reshaping product UX",
                "url": "https://example.com/a?utm_source=x",
                "content": "A long article about agent workflow, product UX and automation.",
                "source": "Example",
                "published_at": "2026-04-14T08:00:00",
                "collected_at": "2026-04-14T09:00:00",
            }
        ]

    def test_process_news_uses_ai_scores(self):
        with patch.object(
            self.processor,
            "_score_news_with_ai",
            return_value={
                0: {
                    "importance": 9,
                    "relevance_to_me": 8,
                    "signal_strength": 9,
                    "actionability": 7,
                    "theme_tags": ["workflow", "ai_product"],
                    "reason": "High value signal",
                }
            },
        ):
            payload = self.processor.process_news(self.raw_news, date_str="2026-04-14")

        self.assertEqual(payload["date"], "2026-04-14")
        self.assertEqual(len(payload["news"]), 1)
        item = payload["news"][0]
        self.assertEqual(item["theme_tags"], ["workflow", "ai_product"])
        self.assertEqual(item["ai_scores"]["importance"], 9)
        self.assertEqual(item["score_reason"], "High value signal")
        self.assertGreaterEqual(item["final_score"], 5.5)

    def test_ai_scoring_retries_until_success(self):
        class Response:
            def __init__(self, status_code, content):
                self.status_code = status_code
                self._content = content
                self.text = content

            def json(self):
                return {"choices": [{"message": {"content": self._content}}]}

        response_success = Response(
            200,
            '{"items":[{"index":0,"importance":8,"relevance_to_me":8,"signal_strength":7,"actionability":7,"theme_tags":["workflow"],"reason":"retry ok"}]}',
        )

        with patch("news_processor.httpx.Client") as mocked_client:
            mocked_post = mocked_client.return_value.__enter__.return_value.post
            mocked_post.side_effect = [Exception("fail 1"), Exception("fail 2"), response_success]
            with patch("news_processor.time.sleep"):
                score_map = self.processor._score_news_with_ai(self.raw_news)

        self.assertEqual(mocked_post.call_count, 3)
        self.assertIn(0, score_map)
        self.assertEqual(score_map[0]["reason"], "retry ok")


if __name__ == "__main__":
    unittest.main()
