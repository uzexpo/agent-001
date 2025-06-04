import os
import time
import hmac
import hashlib
from typing import List, Tuple

import requests

from sources.agents.agent import Agent
from sources.memory import Memory

class TradingAgent(Agent):
    """Basic cryptocurrency trading agent using Binance public API."""
    def __init__(self, name, prompt_path, provider, verbose=False):
        super().__init__(name, prompt_path, provider, verbose)
        self.role = "trading"
        self.type = "trading_agent"
        self.base_url = "https://api.binance.com"
        self.api_key = os.getenv("BINANCE_API_KEY", "")
        self.api_secret = os.getenv("BINANCE_API_SECRET", "")
        self.memory = Memory(
            self.load_prompt(prompt_path),
            recover_last_session=False,
            memory_compression=False,
            model_provider=provider.get_model_name(),
        )

    def fetch_price(self, symbol: str) -> str:
        """Return latest price for given symbol."""
        endpoint = f"{self.base_url}/api/v3/ticker/price"
        resp = requests.get(endpoint, params={"symbol": symbol.upper()}, timeout=10)
        resp.raise_for_status()
        return resp.json()["price"]

    def fetch_klines(self, symbol: str, interval: str = "1h", limit: int = 24) -> List[Tuple[float, float]]:
        """Return klines (open time, close price) for a symbol."""
        endpoint = f"{self.base_url}/api/v3/klines"
        params = {"symbol": symbol.upper(), "interval": interval, "limit": limit}
        resp = requests.get(endpoint, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return [(float(d[0]), float(d[4])) for d in data]

    @staticmethod
    def moving_average(data: List[Tuple[float, float]]) -> float:
        """Compute simple moving average from kline close prices."""
        if not data:
            return 0.0
        return sum(price for _, price in data) / len(data)

    def determine_trade_signal(self, symbol: str) -> str:
        """Return a simple buy/sell signal using last price vs MA."""
        klines = self.fetch_klines(symbol)
        current_price = float(self.fetch_price(symbol))
        ma = self.moving_average(klines)
        return "buy" if current_price > ma else "sell"

    def _sign_params(self, params: dict) -> dict:
        """Sign parameters for Binance order endpoints."""
        if not self.api_key or not self.api_secret:
            raise RuntimeError("Missing Binance API credentials")
        params["timestamp"] = int(time.time() * 1000)
        query = "&".join([f"{k}={v}" for k, v in sorted(params.items())])
        signature = hmac.new(self.api_secret.encode(), query.encode(), hashlib.sha256).hexdigest()
        params["signature"] = signature
        return params

    def place_order(self, symbol: str, side: str, quantity: float) -> str:
        """Place a test order using Binance API."""
        endpoint = f"{self.base_url}/api/v3/order/test"
        params = self._sign_params({"symbol": symbol.upper(), "side": side.upper(), "type": "MARKET", "quantity": quantity})
        headers = {"X-MBX-APIKEY": self.api_key}
        resp = requests.post(endpoint, params=params, headers=headers, timeout=10)
        resp.raise_for_status()
        return "Order placed"

    async def process(self, prompt, speech_module):
        self.memory.push("user", prompt)
        parts = prompt.strip().split()
        if len(parts) == 0:
            return "No command", ""

        cmd = parts[0].lower()
        if cmd == "test" and len(parts) >= 2:
            symbol = parts[1]
            signal = self.determine_trade_signal(symbol)
            answer = f"Test signal for {symbol}: {signal}"
        elif cmd == "trade" and len(parts) >= 3:
            symbol = parts[1]
            qty = float(parts[2])
            try:
                resp = self.place_order(symbol, "BUY", qty)
                answer = resp
            except Exception as exc:
                answer = f"Trade error: {exc}"
        else:
            symbol = parts[0]
            try:
                price = self.fetch_price(symbol)
                answer = f"Current price of {symbol.upper()} is {price} USDT."
            except Exception as exc:
                answer = f"Error fetching price for {symbol}: {exc}"

        self.last_answer = answer
        self.memory.push("assistant", answer)
        self.status_message = "Ready"
        return answer, ""

