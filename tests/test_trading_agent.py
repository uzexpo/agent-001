import unittest
from unittest.mock import patch

from sources.agents.trading_agent import TradingAgent

class TestTradingAgent(unittest.TestCase):
    def setUp(self):
        self.agent = TradingAgent(
            name="TestTrader",
            prompt_path="prompts/base/trading_agent.txt",
            provider=None,
        )

    @patch("sources.agents.trading_agent.requests.get")
    def test_fetch_price(self, mock_get):
        mock_get.return_value.json.return_value = {"price": "100.0"}
        mock_get.return_value.raise_for_status.return_value = None
        price = self.agent.fetch_price("BTCUSDT")
        self.assertEqual(price, "100.0")

    @patch("sources.agents.trading_agent.requests.get")
    def test_determine_trade_signal(self, mock_get):
        klines_data = [[0, 0, 0, 0, "90"]] * 24
        responses = [
            {"json": lambda: {"price": "100"}},
            {"json": lambda: klines_data},
        ]
        def side_effect(url, params=None, timeout=10):
            resp = unittest.mock.MagicMock()
            data = responses.pop(0)
            resp.json = data["json"]
            resp.raise_for_status.return_value = None
            return resp
        mock_get.side_effect = side_effect
        signal = self.agent.determine_trade_signal("BTCUSDT")
        self.assertEqual(signal, "buy")

if __name__ == "__main__":
    unittest.main()
