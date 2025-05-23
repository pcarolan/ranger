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
from rich.table import Table
from dotenv import load_dotenv
import os
import logging
from datetime import datetime
from pathlib import Path
from .router import Router
import requests
import googlemaps

class CLI(object):
    # List of available tools
    TOOLS = [
        ("get_weather", "Get a detailed weather report for a specific location."),
        ("get_travel_duration", "Gets the travel time between two places.")
    ]

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
        log_dir = Path("../logs")
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

    def _get_system_status(self) -> Text:
        """Get the system status as a Rich Text object"""
        status_text = Text()
        
        # Add API Status section
        status_text.append("API Status\n", style="bold green")
        
        # Check OpenAI status
        openai_status = "❌ Not configured"
        if os.getenv("OPENAI_API_KEY"):
            try:
                response = requests.get(
                    "https://api.openai.com/v1/models",
                    headers={"Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}"},
                    timeout=5
                )
                openai_status = "✅ Connected" if response.status_code == 200 else "❌ Error connecting"
            except Exception as e:
                openai_status = f"❌ Error: {str(e)}"
        
        # Check Claude status
        claude_status = "❌ Not configured"
        if os.getenv("ANTHROPIC_API_KEY"):
            try:
                response = requests.get(
                    "https://api.anthropic.com/v1/messages",
                    headers={
                        "x-api-key": os.getenv("ANTHROPIC_API_KEY"),
                        "anthropic-version": "2023-06-01"
                    },
                    timeout=5
                )
                claude_status = "✅ Connected" if response.status_code == 200 else "❌ Error connecting"
            except Exception as e:
                claude_status = f"❌ Error: {str(e)}"
        
        # Check Google Maps API status
        gmaps_status = "❌ Not configured"
        if os.getenv("GMAPS_API_KEY"):
            try:
                gmaps = googlemaps.Client(os.getenv("GMAPS_API_KEY"))
                result = gmaps.geocode("New York")
                gmaps_status = "✅ Connected" if result else "❌ Error connecting"
            except Exception as e:
                gmaps_status = f"❌ Error: {str(e)}"
        
        # Add service statuses
        status_text.append("OpenAI\t\t", style="cyan")
        status_text.append(f"{openai_status}\n", style="green")
        
        status_text.append("Claude\t\t", style="cyan")
        status_text.append(f"{claude_status}\n", style="green")
        
        status_text.append("Google Maps\t", style="cyan")
        status_text.append(f"{gmaps_status}\n", style="green")
        
        # Add available tools section
        status_text.append("\nAvailable Tools\n", style="bold green")
        
        for tool_name, tool_doc in self.TOOLS:
            status_text.append(f"• {tool_name}", style="cyan")
            status_text.append(f" - {tool_doc}\n", style="dim")
        
        return status_text

    def status(self):
        """Show the status of the Ranger CLI"""
        status_text = self._get_system_status()
        status_text.append("\nVersion: 0.1.0", style="dim")

        self.console.print(Panel(
            status_text,
            title="[bold blue]Ranger CLI Status[/bold blue]",
            border_style="blue",
            expand=True
        ))

    def repl(self):
        """Start the Ranger REPL"""
        # Display welcome and status panels
        self.console.print(Panel(
            "[bold green]Welcome to Ranger![/bold green]\n"
            "[dim]Type 'exit' or 'quit' to leave.[/dim]",
            title="[bold blue]Ranger REPL[/bold blue]",
            border_style="blue",
            expand=True
        ))
        
        self.console.print(Panel(
            self._get_system_status(),
            title="[bold blue]System Status[/bold blue]",
            border_style="blue",
            expand=True
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
                    response, thoughts, tools_used = self.router.route(user_input)
                
                # Log the response
                self.logger.info(f"Response: {response}")
                
                # If debug mode is enabled, show the thoughts
                if self.debug and thoughts:
                    self.console.print(
                        Panel(
                            Text(thoughts, style="dim"),
                            title="[bold]System Thinking[/bold]",
                            border_style="dim",
                            expand=True
                        )
                    )
                
                # Display the response in a complementary color scheme
                tools_text = f"\n\n[gray]Tools used: {', '.join(tools_used)}[/gray]" if tools_used else ""
                self.console.print(
                    Panel(
                        Text(response + tools_text, style="magenta"),
                        title="[bold]Response[/bold]",
                        border_style="magenta",
                        expand=True
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
                        border_style="red",
                        expand=True
                    )
                )

def main():
    """Start the Ranger CLI"""
    fire.Fire(CLI)

if __name__ == "__main__":
    main()
