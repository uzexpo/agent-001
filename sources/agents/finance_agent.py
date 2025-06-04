import asyncio

from sources.utility import pretty_print, animate_thinking
from sources.agents.agent import Agent
from sources.tools.fileFinder import FileFinder
from sources.tools.BashInterpreter import BashInterpreter
from sources.tools.binanceTrader import BinanceTrader
from sources.tools.finePayment import FinePayment
from sources.tools.reportGenerator import ReportGenerator
from sources.memory import Memory

class FinanceAgent(Agent):
    """Agent specialised in financial operations"""
    def __init__(self, name, prompt_path, provider, verbose=False):
        super().__init__(name, prompt_path, provider, verbose, None)
        self.tools = {
            "file_finder": FileFinder(),
            "bash": BashInterpreter(),
            "trade": BinanceTrader(),
            "pay_fine": FinePayment(),
            "report": ReportGenerator(),
        }
        self.work_dir = self.tools["file_finder"].get_work_dir()
        self.role = "finance"
        self.type = "finance_agent"
        self.memory = Memory(
            self.load_prompt(prompt_path),
            recover_last_session=False,
            memory_compression=False,
            model_provider=provider.get_model_name()
        )

    async def process(self, prompt, speech_module) -> str:
        self.memory.push('user', f"{prompt}\nWorking directory: {self.work_dir}")
        exec_success = False
        while not exec_success:
            await self.wait_message(speech_module)
            animate_thinking("Thinking...", color="status")
            answer, reasoning = await self.llm_request()
            exec_success, _ = self.execute_modules(answer)
            answer = self.remove_blocks(answer)
            self.last_answer = answer
        self.status_message = "Ready"
        return answer, reasoning
