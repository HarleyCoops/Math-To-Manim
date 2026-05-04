import os
import logging
from typing import Optional, Any, Dict
from rich.console import Console
from rich.panel import Panel
from rich.logging import RichHandler

# Configuration
DEFAULT_MODEL = "gemini-3-pro-preview" 
API_KEY_ENV_VAR = "GOOGLE_API_KEY"

class RichLogger:
    """
    A centralized logger using Rich to provide better terminal output.
    """
    def __init__(self):
        self.console = Console()
        self.console.print("[bold green]Gemini 3 ADK Pipeline Initialized[/bold green]")

        # Configure standard python logging to use rich
        logging.basicConfig(
            level="INFO",
            format="%(message)s",
            datefmt="[%X]",
            handlers=[RichHandler(console=self.console, rich_tracebacks=True)]
        )
        self.logger = logging.getLogger("Gemini3")

    def log_agent_start(self, agent_name: str, task: str):
        self.console.print(Panel(f"[bold cyan]Agent Started:[/bold cyan] {agent_name}\n\n[italic]{task}[/italic]", title="Pipeline Step", border_style="blue"))

    def log_agent_thought(self, agent_name: str, thought: str):
        self.console.print(f"[bold magenta]{agent_name} (Thought):[/bold magenta] {thought}")

    def log_tool_use(self, tool_name: str, input_data: Any):
        self.console.print(f"[bold yellow]Tool Call ({tool_name}):[/bold yellow] {input_data}")

    def log_agent_completion(self, agent_name: str, output: str):
        # Truncate output for display if too long
        display_output = output[:500] + "..." if len(output) > 500 else output
        self.console.print(Panel(f"[bold green]Agent Completed:[/bold green] {agent_name}\n\n{display_output}", title="Result", border_style="green"))

    def error(self, message: str):
        self.console.print(f"[bold red]ERROR:[/bold red] {message}")

# Global Logger Instance
logger = RichLogger()

def get_model_config(model_name: str = DEFAULT_MODEL) -> Dict[str, Any]:
    """
    Returns the configuration dictionary for the Google ADK agents.
    """
    # Check for GEMINI_API_KEY and map it to GOOGLE_API_KEY if needed
    if not os.getenv("GOOGLE_API_KEY") and os.getenv("GEMINI_API_KEY"):
        os.environ["GOOGLE_API_KEY"] = os.getenv("GEMINI_API_KEY")

    api_key = os.getenv(API_KEY_ENV_VAR)
    if not api_key:
        logger.console.print("[bold red]WARNING:[/bold red] GOOGLE_API_KEY environment variable not set.")

    return {
        "model": model_name,
        # ADK might require 'api_key' passed explicitly or picked up from env
        # "api_key": api_key
    }
