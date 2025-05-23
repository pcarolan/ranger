# /// script
# requires-python = ">=3.13"
# dependencies = ["fire"]
# ///

import fire
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.text import Text

class CLI(object):
    def __init__(self):
        self.console = Console()

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
                
                # Echo the input with a nice format
                self.console.print(
                    Panel(
                        Text(user_input, style="cyan"),
                        title="[bold]Input[/bold]",
                        border_style="cyan"
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
