from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Static
from textual.binding import Binding
from rich.syntax import Syntax
from rich.panel import Panel
import random
from snippets import CODE_SNIPPETS

from rich.console import RenderableType
from textual.widgets import Static
from rich.syntax import Syntax
from rich.panel import Panel

class CodeDisplay(Static):
    """A Static widget that displays syntax-highlighted code with selectable lines."""
    
    def __init__(
        self, 
        code: str = "", 
        language: str = "python",
        *args, 
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.code = code
        self.language = language
        self.selected_lines = set()
        self.update_content()
    
    def update_content(self) -> None:
        """Update the displayed content with current code and selected lines."""
        syntax = Syntax(
            self.code,
            self.language,
            line_numbers=True,
            theme="monokai",
            word_wrap=False,
            highlight_lines=self.selected_lines
        )
        self.update(Panel(syntax))
    
    def on_click(self, event) -> None:
        """Handle click events on the widget."""
        # Get the relative position within the widget
        relative_y = event.y
        
        # Calculate which line was clicked (simple approach)
        # We need to account for potential offsets from borders, padding, etc.
        # This offset may need to be adjusted based on exact rendering details
        offset = 1  # Adjust this based on your layout
        
        line_number = relative_y + offset
        line_count = len(self.code.splitlines())
        
        if 1 <= line_number <= line_count:
            # Toggle the line selection
            if line_number in self.selected_lines:
                self.selected_lines.remove(line_number)
            else:
                self.selected_lines.add(line_number)
            
            # Update the display
            self.update_content()




class SelectableCodeView(Static):
    """A widget that displays code with selectable lines."""
    
    def __init__(self, code, language):
        super().__init__("")
        self.code = code
        self.language = language
        self.selected_lines = set()
        self.line_count = len(code.splitlines()) if code else 0
        self.update_content()

    def update_content(self):
        """Update the displayed code with highlighted selected lines."""
        self.line_count = len(self.code.splitlines()) if self.code else 0
        
        syntax = Syntax(
            self.code,
            self.language,
            line_numbers=True,
            theme="monokai",
            word_wrap=False,
            highlight_lines=self.selected_lines
        )
        self.update(Panel(syntax))

    def on_mouse_up(self, event):
        """Handle mouse events to select/deselect lines."""
        # Only process clicks in the code container
        code_container = self.query_one("#code-container")
        
        # Get the region of the code container
        container_region = code_container.region
        
        # Check if click is within the container bounds
        if (container_region.x <= event.screen_x < container_region.x + container_region.width and
            container_region.y <= event.screen_y < container_region.y + container_region.height):
            
            # Get relative position within the code container (account for panel borders)
            relative_y = event.screen_y - container_region.y - 1  # -1 for the panel border
            
            # Calculate which line was clicked
            line_number = relative_y + 1  # +1 because line numbers start from 1
            
            # Get the current snippet code
            if hasattr(self, 'current_snippet_data'):
                line_count = len(self.current_snippet_data["code"].splitlines())
                
                if 1 <= line_number <= line_count:
                    # Toggle line selection
                    if line_number in self.selected_lines:
                        self.selected_lines.remove(line_number)
                    else:
                        self.selected_lines.add(line_number)
                    
                    # Redraw the code with highlighted lines
                    syntax = Syntax(
                        self.current_snippet_data["code"],
                        self.current_snippet_data["language"],
                        line_numbers=True,
                        theme="monokai",
                        word_wrap=False,
                        highlight_lines=self.selected_lines
                    )
                    code_container.update(Panel(syntax))



class TitleScreen(Screen):
    """The game's title screen."""
    
    BINDINGS = [
        Binding("space", "start_game", "Start Game"),
    ]
    
    def compose(self) -> ComposeResult:
        yield Container(
            Static("[bold yellow]THE CODE REVIEWER[/bold yellow]", id="title"),
            Static("[green]You are a code reviewer at MegaCorp Inc.[/green]", id="subtitle"),
            Static("[green]Find security issues and approve or reject code.[/green]"),
            Static("[white]Press SPACE to start[/white]", id="press-key"),
            id="title-screen"
        )
    
    def action_start_game(self):
        """Start the game when space is pressed."""
        self.app.start_new_game()


class GameScreen(Screen):
    """The main game screen."""
    
    def __init__(self):
        super().__init__()
        self.reset_game()
    
    def reset_game(self):
        """Reset the game to initial state."""
        self.current_snippet = 0
        self.correct_answers = 0
        self.total_snippets = 5
        self.snippets = random.sample(CODE_SNIPPETS, self.total_snippets)
        self.code_display = None
        
        # If we're already mounted, update the UI elements
        if self.is_mounted:
            self.query_one("#progress").update(f"[bold]Snippets: 1/{self.total_snippets}[/bold]")
            self.query_one("#score").update(f"[bold]Score: 0[/bold]")
            self.code_display = self.query_one(CodeDisplay)
            self.load_snippet()
    
    def compose(self) -> ComposeResult:
        """Create the game UI."""
        yield Static("[bold white on blue] THE CODE REVIEWER v1.0 [/bold white on blue]", id="game-header")
        
        # Action panel
        yield Horizontal(
            Vertical(
                Static("[reverse]ACTIONS[/reverse]", id="control-title"),
                Button("LGTM", variant="success", id="lgtm-button"),
                Button("REJECT", variant="error", id="reject-button"),
                Static(f"[bold]Snippets: 1/{self.total_snippets}[/bold]", id="progress"),
                Static(f"[bold]Score: 0[/bold]", id="score"),
                id="control-panel"
            ),
            Vertical(
                Static("[reverse]CODE SNIPPET - CLICK ON LINES WITH ISSUES[/reverse]", id="code-title"),
                CodeDisplay(id="code-display"),  # Our custom widget
                id="code-panel"
            ),
            id="game-container"
        )
        
        yield Static("[white on blue]F1: Help  ESC: Quit[/white on blue]", id="status-bar")
    
    def on_mount(self):
        """When the screen is mounted, initialize the first snippet."""
        self.code_display = self.query_one(CodeDisplay)
        self.load_snippet()
    
    def load_snippet(self):
        """Update with current snippet content."""
        if self.current_snippet < self.total_snippets:
            snippet = self.snippets[self.current_snippet]
            
            # Update the code display
            self.code_display.code = snippet["code"]
            self.code_display.language = snippet["language"]
            self.code_display.selected_lines = set()  # Clear selections
            self.code_display.update_content()
            
            # Update progress display
            self.query_one("#progress").update(f"[bold]Snippets: {self.current_snippet+1}/{self.total_snippets}[/bold]")
        else:
            # All snippets done, show results
            results_screen = self.app.get_screen("results")
            results_screen.score = self.correct_answers
            results_screen.total = self.total_snippets
            self.app.push_screen("results")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses (LGTM or REJECT)."""
        if self.current_snippet < self.total_snippets:
            snippet = self.snippets[self.current_snippet]
            button_id = event.button.id
            decision = button_id == "lgtm-button"  # True if LGTM, False if REJECT
            
            # Check if the decision is correct
            correct_decision = (not snippet["should_reject"]) == decision
            
            # Check if the selected lines are correct
            correct_lines = False
            if snippet["should_reject"]:
                if self.code_display.selected_lines == set(snippet["issue_lines"]):
                    correct_lines = True
            else:
                if not self.code_display.selected_lines:  # No lines should be selected for good code
                    correct_lines = True
            
            # Update score
            if correct_decision and correct_lines:
                self.correct_answers += 1
                self.query_one("#score").update(f"[bold]Score: {self.correct_answers}[/bold]")
                self.notify("[green]Correct![/green]")
            else:
                self.notify("[red]Incorrect![/red] " + snippet["explanation"])
            
            # Move to next snippet
            self.current_snippet += 1
            self.load_snippet()



class ResultsScreen(Screen):
    """Screen to display game results."""
    
    BINDINGS = [
        Binding("enter", "continue", "Continue"),
    ]
    
    def __init__(self):
        super().__init__()
        self.score = 0
        self.total = 5
    
    def compose(self) -> ComposeResult:
        yield Container(
            Static("[bold yellow]RESULTS[/bold yellow]", id="results-title"),
            Static("", id="results-content"),
            Static("[white]Press ENTER to continue[/white]", id="press-enter"),
            id="results-screen"
        )
    
    def on_mount(self):
        """Update the results content when screen is mounted."""
        percentage = (self.score / self.total) * 100
        
        result_message = f"[bold]You scored {self.score} out of {self.total}[/bold]\n\n"
        result_message += f"Accuracy: {percentage:.0f}%\n\n"
        
        if percentage >= 80:
            result_message += "[green]Excellent! You're a security expert![/green]"
        elif percentage >= 60:
            result_message += "[yellow]Good job! Keep practicing.[/yellow]"
        else:
            result_message += "[red]You need more practice with security issues.[/red]"
        
        self.query_one("#results-content").update(result_message)
    
    def action_continue(self):
        """Continue to credits screen."""
        self.app.push_screen("credits")


class CreditsScreen(Screen):
    """Screen to display game credits."""
    
    BINDINGS = [
        Binding("enter", "back_to_title", "Back to Title"),
    ]
    
    def compose(self) -> ComposeResult:
        yield Container(
            Static("[bold yellow]CREDITS[/bold yellow]", id="credits-title"),
            Static("[green]THE CODE REVIEWER[/green]"),
            Static("A game about finding security issues in code"),
            Static("Created with Python and Textual"),
            Static("\n[white]Press ENTER to return to title screen[/white]"),
            id="credits-screen"
        )
    
    def action_back_to_title(self):
        """Return to title screen."""
        # Reset the game screen before returning to title
        game_screen = self.app.get_screen("game")
        game_screen.reset_game()
        self.app.switch_screen("title")



class CodeReviewerApp(App):
    """The main application class."""
    
    TITLE = "The Code Reviewer"
    CSS_PATH = None
    SCREENS = {
        "title": TitleScreen,
        "game": GameScreen,
        "results": ResultsScreen,
        "credits": CreditsScreen
    }
    
    CSS = """
    Screen {
        background: #000080;
    }
    
    #title-screen, #results-screen, #credits-screen {
        align: center middle;
    }
    
    #title, #results-title, #credits-title {
        width: 100%;
        text-align: center;
        margin-bottom: 1;
        color: #FFFF00;
        
    }
    
    #subtitle, #press-key, #press-enter {
        width: 100%;
        text-align: center;
        margin-top: 1;
    }
    
    #results-content {
        width: 60;
        height: auto;
        margin: 2 0;
        text-align: center;
    }
    
    #game-header, #status-bar {
        width: 100%;
        height: 1;
        color: #FFFFFF;
        background: #0000AA;
    }
    
    #status-bar {
        dock: bottom;
    }
    
    #game-container {
        height: 100%;
    }
    
    #control-panel {
        width: 20;
        background: #000080;
        color: #FFFFFF;
        padding: 1;
    }
    
    #code-panel {
        width: 1fr;
        background: #000000;
        color: #FFFFFF;
    }
    
    #control-title, #code-title {
        background: #FFFFFF;
        color: #000000;
        text-align: center;
        margin-bottom: 1;
    }
    
    #code-view {
        padding: 0 1;
        height: 1fr;
        overflow: auto;
    }
    
    Button {
        width: 100%;
        margin: 1 0;
    }
    
    #lgtm-button {
        background: #00AA00;
        color: #FFFFFF;
    }
    
    #reject-button {
        background: #AA0000;
        color: #FFFFFF;
    }
    
    #progress, #score {
        margin-top: 2;
        text-align: center;
    }
    """
    
    def on_mount(self):
        """Start with the title screen."""
        self.push_screen("title")
    
    def start_new_game(self):
        """Start a new game by resetting and showing the game screen."""
        game_screen = self.get_screen("game")
        game_screen.reset_game()
        self.push_screen("game")

if __name__ == "__main__":
    app = CodeReviewerApp()
    app.run()
