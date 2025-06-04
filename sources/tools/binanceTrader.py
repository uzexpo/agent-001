import os
import sys

if __name__ == "__main__":
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) )

from sources.tools.tools import Tools

try:
    from binance.client import Client
except Exception:
    Client = None

class BinanceTrader(Tools):
    """Tool for trading on Binance using python-binance"""
    def __init__(self, api_key: str = None, api_secret: str = None, testnet: bool = False):
        super().__init__()
        self.tag = "binance_trade"
        self.name = "Binance Trader"
        self.description = "Execute trade orders on Binance"
        self.api_key = api_key or os.getenv("BINANCE_API_KEY")
        self.api_secret = api_secret or os.getenv("BINANCE_API_SECRET")
        self.testnet = testnet
        self.client = None
        if Client is not None and self.api_key and self.api_secret:
            self.client = Client(self.api_key, self.api_secret, testnet=self.testnet)

    def execute(self, blocks: list, safety: bool = True) -> str:
        if self.client is None:
            return "Error: Binance client not configured."
        for block in blocks:
            symbol = self.get_parameter_value(block, "symbol")
            qty = self.get_parameter_value(block, "qty")
            side = self.get_parameter_value(block, "side")
            order_type = self.get_parameter_value(block, "type") or "MARKET"
            if not symbol or not qty or not side:
                return "Error: symbol, qty and side parameters required."
            try:
                if safety and input(f"Execute {side} {qty} {symbol}? y/n ") != "y":
                    return "Order cancelled by user."
                order = self.client.create_order(
                    symbol=symbol,
                    side=side.upper(),
                    type=order_type.upper(),
                    quantity=float(qty)
                )
                return str(order)
            except Exception as e:
                return f"Error placing order: {e}"
        return "No trade executed"

    def execution_failure_check(self, output: str) -> bool:
        return output.startswith("Error")

    def interpreter_feedback(self, output: str) -> str:
        if self.execution_failure_check(output):
            return output
        return f"Trade executed: {output}"
