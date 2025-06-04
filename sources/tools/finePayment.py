import os
import sys

if __name__ == "__main__":
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) )

from sources.tools.tools import Tools

class FinePayment(Tools):
    """Simple tool to automate fine payments via an external API"""
    def __init__(self):
        super().__init__()
        self.tag = "pay_fine"
        self.name = "Fine Payment"
        self.description = "Pay traffic fines using a payment service"

    def execute(self, blocks: list, safety: bool = True) -> str:
        for block in blocks:
            account = self.get_parameter_value(block, "account")
            amount = self.get_parameter_value(block, "amount")
            if not account or not amount:
                return "Error: account and amount parameters required."
            if safety and input(f"Pay {amount} from {account}? y/n ") != "y":
                return "Payment cancelled."
            # Placeholder for real payment API integration
            return f"Paid {amount} from {account}"
        return "No payment executed"

    def execution_failure_check(self, output: str) -> bool:
        return output.startswith("Error")

    def interpreter_feedback(self, output: str) -> str:
        if self.execution_failure_check(output):
            return output
        return f"Payment result: {output}"
