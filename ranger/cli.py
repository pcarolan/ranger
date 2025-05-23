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
from ranger.router import Router

class CLI(object):
    def __init__(self):
        self.console = Console()
        # Load environment variables from .env file
        load_dotenv()
        self.console.print("[dim]Loaded environment variables from .env[/dim]")
        
        # Initialize the router
        self.router = Router()

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
                    self.console.print("[yellow]Goodbye! 👋[/yellow]")
                    break
                
                # Route the query and get the response
                response = self.router.route(user_input)
                
                # Display the response in a complementary color scheme
                self.console.print(
                    Panel(
                        Text(response, style="magenta"),
                        title="[bold]Response[/bold]",
                        border_style="magenta"
                    )
                )
            except KeyboardInterrupt:
                self.console.print("\n[yellow]Goodbye! 👋[/yellow]")
                break
            except EOFError:
                self.console.print("\n[yellow]Goodbye! 👋[/yellow]")
                break

def main():
    CLI().repl()

if __name__ == "__main__":
    main()
