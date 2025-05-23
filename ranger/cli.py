# /// script
# requires-python = ">=3.10"
# dependencies = ["fire", "rich"]
# ///

import fire
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.text import Text
from rich.spinner import Spinner
from rich.live import Live
from dotenv import load_dotenv
import os
import logging
from datetime import datetime
from pathlib import Path
from router import Router

class CLI(object):
    def __init__(self, debug: bool = False):
        self.console = Console()
        self.debug = debug
        # Load environment variables from .env file
        load_dotenv()
        self.console.print("[dim]Loaded environment variables from .env[/dim]")
        
        # Initialize the router
        self.router = Router(debug=debug)
        
        # Setup logging
        self._setup_logging()

    def _setup_logging(self):
        """Setup logging configuration"""
        # Create logs directory if it doesn't exist
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Use a single log file
        log_file = log_dir / "ranger.log"
        
        # Configure logging to only output to the log file
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s - %(pathname)s:%(lineno)d',
            handlers=[
                logging.FileHandler(log_file),
                # Removed StreamHandler to prevent console output
            ]
        )
        
        # Configure smolagents logger to only output to our log file
        smolagents_logger = logging.getLogger('smolagents')
        smolagents_logger.setLevel(logging.INFO)
        smolagents_logger.addHandler(logging.FileHandler(log_file))
        smolagents_logger.propagate = False  # Prevent propagation to root logger
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("="*50)  # Add a separator for new sessions
        self.logger.info("Ranger CLI started")

    def input(self, prompt: str) -> str:
        return Prompt.ask(prompt)

    def repl(self):
        """Start the Ranger REPL"""
        self.console.print(Panel.fit(
            "[bold green]Welcome to Ranger![/bold green]\n"
            "[dim]Type 'exit' or 'quit' to leave.[/dim]",
            title="[bold blue]Ranger REPL[/bold blue]",
            border_style="blue"
        ))
        
        while True:
            try:
                user_input = self.input("[bold green]ranger[/bold green] [dim]»[/dim] ")
                if user_input.strip().lower() in ("exit", "quit"):
                    self.logger.info("User exited the REPL")
                    self.console.print("[yellow]Goodbye! 👋[/yellow]")
                    break
                
                # Log the user input
                self.logger.info(f"User query: {user_input}")
                
                # Show spinner while processing
                spinner = Spinner("dots", text="Thinking...", style="bold green")
                with Live(spinner, refresh_per_second=10) as live:
                    # Route the query and get the response
                    response, thoughts = self.router.route(user_input)
                
                # Log the response
                self.logger.info(f"Response: {response}")
                
                # If debug mode is enabled, show the thoughts
                if self.debug and thoughts:
                    self.console.print(
                        Panel(
                            Text(thoughts, style="dim"),
                            title="[bold]System Thinking[/bold]",
                            border_style="dim"
                        )
                    )
                
                # Display the response in a complementary color scheme
                self.console.print(
                    Panel(
                        Text(response, style="magenta"),
                        title="[bold]Response[/bold]",
                        border_style="magenta"
                    )
                )
            except KeyboardInterrupt:
                self.logger.info("User interrupted with KeyboardInterrupt")
                self.console.print("\n[yellow]Goodbye! 👋[/yellow]")
                break
            except EOFError:
                self.logger.info("User interrupted with EOFError")
                self.console.print("\n[yellow]Goodbye! 👋[/yellow]")
                break
            except Exception as e:
                self.logger.error(f"Error occurred: {str(e)}", exc_info=True)
                self.console.print(
                    Panel(
                        Text(f"An error occurred: {str(e)}", style="red"),
                        title="[bold]Error[/bold]",
                        border_style="red"
                    )
                )

def main():
    """Start the Ranger CLI"""
    cli = CLI()
    cli.repl()

if __name__ == "__main__":
    fire.Fire({
        'repl': lambda debug=False: CLI(debug=debug).repl()
    })
