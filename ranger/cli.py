# /// script
# requires-python = ">=3.13"
# dependencies = ["fire"]
# ///

import fire
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.text import Text
from dotenv import load_dotenv
import os
import logging
from datetime import datetime
from pathlib import Path
from ranger.router import Router

class CLI(object):
    def __init__(self):
        self.console = Console()
        # Load environment variables from .env file
        load_dotenv()
        self.console.print("[dim]Loaded environment variables from .env[/dim]")
        
        # Initialize the router
        self.router = Router()
        
        # Setup logging
        self._setup_logging()

    def _setup_logging(self):
        """Setup logging configuration"""
        # Create logs directory if it doesn't exist
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Use a single log file
        log_file = log_dir / "ranger.log"
        
        # Configure logging with Apache format
        # Format: %h %l %u %t \"%r\" %>s %b \"%{Referer}i\" \"%{User-Agent}i\"
        # Where:
        # %h = remote host
        # %l = remote logname
        # %u = remote user
        # %t = time of request
        # %r = first line of request
        # %>s = status
        # %b = response length
        # %{Referer}i = referer
        # %{User-Agent}i = user agent
        apache_format = '%(asctime)s - %(levelname)s - %(message)s - %(pathname)s:%(lineno)d'
        
        logging.basicConfig(
            level=logging.INFO,
            format=apache_format,
            handlers=[
                logging.FileHandler(log_file, mode='a'),  # Append mode
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info("="*50)  # Add a separator for new sessions
        self.logger.info("Ranger CLI started")

    def input(self, prompt: str) -> str:
        return Prompt.ask(prompt)

    def repl(self):
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
                
                # Route the query and get the response
                response = self.router.route(user_input)
                
                # Log the response
                self.logger.info(f"Response: {response}")
                
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
    CLI().repl()

if __name__ == "__main__":
    main()
