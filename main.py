from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Header, Footer, Static, Label
from textual.reactive import reactive
from textual.binding import Binding
from rich.panel import Panel
from rich.text import Text


class SelectableCodeLine(Static):
    """A selectable line of code with line number."""
    
    def __init__(self, line_number: int, content: str, language: str) -> None:
        super().__init__()
        self.line_number = line_number
        self.content = content
        self.language = language
        self.is_selected = False
        self.update_display()
    
    def update_display(self) -> None:
        """Update display to reflect selection state."""
        # Create text with line number
        line_text = Text(f"{self.line_number:3} | {self.content}")
        
        # Apply selection styling if needed
        if self.is_selected:
            self.add_class("selected")
            self.remove_class("not-selected")
        else:
            self.add_class("not-selected") 
            self.remove_class("selected")
            
        self.update(line_text)
    
    def on_click(self) -> None:
        """Handle click on this line."""
        self.is_selected = not self.is_selected
        self.update_display()
        self.app.toggle_line_selection(self.line_number)
    

class CodeReviewer(App):
    """The Code Reviewer game application."""
    
    CSS = """
    Screen {
        background: #0c0c1f;
        color: #cccccc;
    }
    
    #sidebar {
        dock: left;
        width: 20;
        background: #000080;
        color: #ffffff;
        border: solid #ffffff;
        padding: 1;
    }
    
    #content {
        margin-left: 1;
        height: 100%;
    }
    
    .code-line {
        height: 1;
        width: 100%;
        padding: 0;
    }
    
    .code-line:hover {
        background: #333355;
    }
    
    .selected {
        background: #aa0000;
    }
    
    .not-selected {
        background: transparent;
    }
    
    #code-display {
        height: auto;
        overflow: auto;
    }
    
    Button {
        width: 100%;
        margin: 1 0;
        background: #0000aa;
        color: #ffffff;
    }
    
    Button:hover {
        background: #0000ff;
    }
    
    #title {
        text-align: center;
        background: #000088;
        color: #ffffff;
        padding: 1;
    }
    
    #status-bar {
        background: #000080;
        color: #ffffff;
        height: 1;
    }
    
    #message-display {
        height: auto;
        margin-bottom: 1;
    }
    """
    
    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("h", "help", "Help"),
        Binding("a", "approve", "Approve (LGTM)"),
        Binding("r", "reject", "Reject"),
    ]
    
    current_snippet_index = reactive(0)
    score = reactive(0)
    selected_lines = reactive(set())
    
    SNIPPETS = [
        {
            "code": """def authenticate(username, password):
    # Get user from database
    user = db.get_user(username)
    
    # Check if password matches
    if user.password == password:
        session['user_id'] = user.id
        return True
    return False""",
            "language": "python",
            "vulnerable_lines": [6],
            "should_reject": True,
            "vulnerability_details": "Plain text password comparison instead of using a secure hash comparison"
        },
        {
            "code": """function processUserInput(input) {
    // Sanitize input
    const sanitized = input.replace(/[<>]/g, '');
    
    // Execute SQL query
    const query = `SELECT * FROM users WHERE name='${sanitized}'`;
    db.execute(query);
    
    return "Input processed";
}""",
            "language": "javascript",
            "vulnerable_lines": [5, 6],
            "should_reject": True,
            "vulnerability_details": "SQL Injection vulnerability - improper sanitization"
        },
        {
            "code": """public string LoadFile(string filename) {
    // Check if file exists
    if (!File.Exists(filename)) {
        return "File not found";
    }
    
    // Read the file content
    string content = File.ReadAllText(Path.GetFileName(filename));
    return content;
}""",
            "language": "csharp",
            "vulnerable_lines": [7],
            "should_reject": True,
            "vulnerability_details": "Path traversal vulnerability: using GetFileName without validating path"
        }
    ]
    
    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header(show_clock=True)
        yield Horizontal(
            Vertical(
                Label("THE CODE REVIEWER", id="title"),
                Button("LGTM (Approve)", id="approve"),
                Button("Reject", id="reject"),
                Button("Help", id="help"),
                Button("Quit", id="quit"),
                id="sidebar"
            ),
            Vertical(
                Static(id="message-display"),
                Vertical(id="code-display"),
                id="content"
            )
        )
        yield Static("Score: 0 | Snippet: 1/" + str(len(self.SNIPPETS)), id="status-bar")
        yield Footer()
    
    def on_mount(self) -> None:
        """Event handler called when app is mounted."""
        self.show_instructions()
        self.load_current_snippet()
    
    def toggle_line_selection(self, line_number: int) -> None:
        """Toggle a line's selection state."""
        if line_number in self.selected_lines:
            self.selected_lines.remove(line_number)
        else:
            self.selected_lines.add(line_number)
    
    def load_current_snippet(self) -> None:
        """Load and display the current code snippet."""
        snippet = self.SNIPPETS[self.current_snippet_index]
        code_display = self.query_one("#code-display")
        
        # Clear current content
        code_display.remove_children()
        self.selected_lines.clear()
        
        # Split the code into lines
        lines = snippet["code"].split("\n")
        
        # Add each line as a selectable widget
        for i, line in enumerate(lines, 1):
            code_line = SelectableCodeLine(i, line, snippet["language"])
            code_line.add_class("code-line")
            code_line.add_class("not-selected")
            code_display.mount(code_line)
        
        # Update status bar
        status = f"Score: {self.score} | Snippet: {self.current_snippet_index + 1}/{len(self.SNIPPETS)}"
        self.query_one("#status-bar").update(status)
        
        # Display instructions for this snippet
        message = f"Review this code for security vulnerabilities.\nClick on vulnerable lines, then approve or reject."
        self.query_one("#message-display").update(Panel(message, title=f"Code Snippet ({snippet['language']})", border_style="blue"))
    
    def show_instructions(self) -> None:
        """Show initial instructions."""
        instructions = """
        Welcome to 'The Code Reviewer'!

        You are a security code reviewer at BigCorp Inc.
        Your job is to identify security vulnerabilities in code.

        HOW TO PLAY:
        1. Click on lines that contain security vulnerabilities
        2. Click "Reject" if the code has vulnerabilities
        3. Click "LGTM" (Looks Good To Me) if the code is secure

        Press 'H' for help at any time.
        """
        message_display = self.query_one("#message-display")
        message_display.update(Panel(instructions, title="Instructions", border_style="green"))
    
    def action_quit(self) -> None:
        """Quit the application."""
        self.exit()
    
    def action_help(self) -> None:
        """Show help information."""
        self.show_help()
    
    def action_approve(self) -> None:
        """Approve the current code snippet."""
        self.process_decision(approve=True)
    
    def action_reject(self) -> None:
        """Reject the current code snippet."""
        self.process_decision(approve=False)
    
    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Event handler for button presses."""
        button_id = event.button.id
        
        if button_id == "quit":
            self.exit()
        elif button_id == "help":
            self.show_help()
        elif button_id == "approve":
            self.process_decision(approve=True)
        elif button_id == "reject":
            self.process_decision(approve=False)
    
    def show_help(self) -> None:
        """Show help information."""
        help_text = """
        THE CODE REVIEWER - HELP
        
        You are a code reviewer at BigCorp Inc.
        Your job is to identify security vulnerabilities in code.
        
        1. Review the code snippet carefully
        2. Click on lines with security vulnerabilities
        3. Click "Reject" if the code has vulnerabilities
        4. Click "LGTM" if the code looks secure
        
        Keyboard shortcuts:
        - H: Show this help
        - A: Approve (LGTM)
        - R: Reject
        - Q: Quit
        
        Earn points for correct decisions!
        """
        message_display = self.query_one("#message-display")
        message_display.update(Panel(help_text, title="Help", border_style="yellow"))
    
    def process_decision(self, approve: bool) -> None:
        """Process the player's decision to approve or reject."""
        snippet = self.SNIPPETS[self.current_snippet_index]
        
        # Check if the player identified the correct vulnerable lines
        correct_lines_identified = all(line in self.selected_lines for line in snippet["vulnerable_lines"])
        no_false_positives = len(self.selected_lines) == len(snippet["vulnerable_lines"])
        
        # Check if the decision (approve/reject) was correct
        correct_decision = (approve != snippet["should_reject"])
        
        # Calculate score
        points = 0
        if correct_decision and correct_lines_identified and no_false_positives:
            points = 100  # Perfect score
        elif correct_decision:
            points = 50   # Correct decision but wrong lines
        elif correct_lines_identified and no_false_positives:
            points = 30   # Identified vulnerabilities but made wrong decision
        
        self.score += points
        
        # Prepare result message
        if correct_decision and correct_lines_identified and no_false_positives:
            result = "Perfect! You made the right decision and identified all vulnerabilities correctly."
        elif correct_decision and not snippet["should_reject"]:
            result = "Correct! This code was clean and you approved it."
        elif correct_decision and snippet["should_reject"]:
            if not correct_lines_identified:
                result = "Partially correct. You rejected the code, but didn't identify all vulnerabilities correctly."
            else:
                result = "Good job! You rejected the code and identified the vulnerabilities."
        else:
            if snippet["should_reject"]:
                result = "Incorrect. This code contained vulnerabilities and should have been rejected."
            else:
                result = "Incorrect. This code was clean and should have been approved."
        
        # Add vulnerability details if applicable
        if snippet["should_reject"]:
            details = f"\n\nVulnerability: {snippet['vulnerability_details']}"
            vulnerable_lines = ", ".join(str(line) for line in snippet["vulnerable_lines"])
            details += f"\nVulnerable lines: {vulnerable_lines}"
        else:
            details = "\n\nNo vulnerabilities in this code."
        
        # Show score
        score_text = f"\n\nPoints earned: +{points}"
        total_score = f"Total score: {self.score}"
        
        # Update message display
        message_display = self.query_one("#message-display")
        message_display.update(Panel(
            f"{result}{details}{score_text}\n{total_score}", 
            title="Review Result", 
            border_style="green" if points > 0 else "red"
        ))
        
        # Move to next snippet if available
        if self.current_snippet_index < len(self.SNIPPETS) - 1:
            self.current_snippet_index += 1
            self.load_current_snippet()
        else:
            self.show_game_over()
    
    def show_game_over(self) -> None:
        """Show game over screen."""
        max_possible_score = len(self.SNIPPETS) * 100
        performance = (self.score / max_possible_score) * 100
        
        if performance >= 90:
            evaluation = "Outstanding! You're a security expert!"
        elif performance >= 70:
            evaluation = "Great job! You have a good security mindset."
        elif performance >= 50:
            evaluation = "Good effort! Keep practicing your security skills."
        else:
            evaluation = "You need more practice with security code review."
        
        game_over_text = f"""
        GAME OVER!
        
        Final Score: {self.score} / {max_possible_score}
        
        {evaluation}
        
        Thank you for playing The Code Reviewer!
        Press 'Q' to quit.
        """
        
        message_display = self.query_one("#message-display")
        message_display.update(Panel(game_over_text, title="Game Over", border_style="blue"))
        
        # Clear code display
        code_display = self.query_one("#code-display")
        code_display.remove_children()


if __name__ == "__main__":
    app = CodeReviewer()
    app.run()
