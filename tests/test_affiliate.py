import unittest
from unittest.mock import patch

from utils.affiliate import shorten_link


class ShortenLinkTests(unittest.TestCase):
    def test_existing_amzn_to_links_are_preserved(self):
        with patch("utils.affiliate.SHORTENER_API", "https://example.test/shorten?url={url}"), patch(
            "utils.affiliate.requests.get"
        ) as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.text = "https://example.test/short"

            result = shorten_link("https://amzn.to/4vyERiW")

        self.assertEqual(result, "https://amzn.to/4vyERiW")
        mock_get.assert_not_called()

    def test_configured_shortener_is_used_for_non_amazon_links(self):
        with patch("utils.affiliate.SHORTENER_API", "https://example.test/shorten?url={url}"), patch(
            "utils.affiliate.requests.get"
        ) as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.text = "https://amzn.to/abc123"

            result = shorten_link("https://www.amazon.in/dp/TEST123")

        self.assertEqual(result, "https://amzn.to/abc123")
        self.assertEqual(mock_get.call_count, 1)


if __name__ == "__main__":
    unittest.main()
