import os
import sys

if __name__ == "__main__":
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) )

from sources.tools.tools import Tools

class ReportGenerator(Tools):
    """Compile documents into a simple report"""
    def __init__(self):
        super().__init__()
        self.tag = "report"
        self.name = "Report Generator"
        self.description = "Combine documents and produce a summary report"

    def execute(self, blocks: list, safety: bool = False) -> str:
        report_parts = []
        for block in blocks:
            path = block.strip()
            file_path = os.path.join(self.work_dir, path)
            if not os.path.exists(file_path):
                return f"Error: {path} not found"
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                report_parts.append(f.read())
        return "\n\n".join(report_parts)

    def execution_failure_check(self, output: str) -> bool:
        return output.startswith("Error")

    def interpreter_feedback(self, output: str) -> str:
        if self.execution_failure_check(output):
            return output
        return f"Report generated with length {len(output)} characters"
