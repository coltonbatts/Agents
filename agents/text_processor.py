from typing import Any, Dict, List
from core import BaseAgent, AgentConfig
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

class TextProcessorAgent(BaseAgent):
    """An agent that processes text with various capabilities"""
    
    def _initialize(self) -> None:
        """Initialize text processing resources"""
        self.console = Console()
        self.history: List[Dict[str, Any]] = []
    
    async def process(self, input_data: str) -> Dict[str, Any]:
        """Process text input with various transformations"""
        result = {
            "original": input_data,
            "word_count": len(input_data.split()),
            "char_count": len(input_data),
            "uppercase": input_data.upper(),
            "lowercase": input_data.lower()
        }
        
        # Store in history
        self.history.append(result)
        
        # Create beautiful output
        text = Text()
        text.append("📝 ", style="bold green")
        text.append(input_data, style="bold")
        text.append("\n\nAnalysis:", style="bold blue")
        text.append(f"\n• Words: {result['word_count']}")
        text.append(f"\n• Characters: {result['char_count']}")
        
        self.console.print(Panel(
            text,
            title="Text Processor",
            border_style="blue"
        ))
        
        return result
    
    async def handle_error(self, error: Exception) -> None:
        """Handle text processing errors"""
        self.console.print(f"[red]Error processing text: {str(error)}[/red]")
    
    def get_history(self) -> List[Dict[str, Any]]:
        """Return processing history"""
        return self.history

async def main():
    # Create and test the text processor agent
    config = AgentConfig(
        name="TextProcessor",
        description="An agent that processes text with various capabilities",
        capabilities=["text analysis", "case conversion", "history tracking"]
    )
    
    agent = TextProcessorAgent(config)
    
    # Test the agent
    await agent.process("Hello! This is a test of our text processing agent.")
    await agent.process("It can process multiple inputs and track history.")
    
    # Show history
    console = Console()
    console.print("\n[bold]Processing History:[/bold]")
    for entry in agent.get_history():
        console.print(f"- Original: {entry['original']}")
        console.print(f"  Words: {entry['word_count']}")
        console.print()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
