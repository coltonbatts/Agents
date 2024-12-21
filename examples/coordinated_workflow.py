import asyncio
from typing import Dict, Any
from core import BaseAgent, AgentConfig, AgentCoordinator, Message, Workflow
from rich.console import Console
from rich.panel import Panel

class DataPreprocessor(BaseAgent):
    """Agent that preprocesses input data"""
    
    def _initialize(self) -> None:
        self.console = Console()
    
    async def process(self, input_data: str) -> Dict[str, Any]:
        self.console.print(Panel(
            f"Preprocessing: {input_data}",
            title="Data Preprocessor",
            border_style="yellow"
        ))
        return {
            "cleaned_text": input_data.strip().lower(),
            "word_count": len(input_data.split())
        }
    
    async def handle_error(self, error: Exception) -> None:
        self.console.print(f"[red]Preprocessing error: {str(error)}[/red]")

class Analyzer(BaseAgent):
    """Agent that analyzes preprocessed data"""
    
    def _initialize(self) -> None:
        self.console = Console()
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        self.console.print(Panel(
            f"Analyzing: {input_data}",
            title="Analyzer",
            border_style="blue"
        ))
        return {
            "analysis": {
                "complexity": "high" if input_data["word_count"] > 10 else "low",
                "processed_text": input_data["cleaned_text"].upper()
            }
        }
    
    async def handle_error(self, error: Exception) -> None:
        self.console.print(f"[red]Analysis error: {str(error)}[/red]")

class Reporter(BaseAgent):
    """Agent that generates final reports"""
    
    def _initialize(self) -> None:
        self.console = Console()
    
    async def process(self, input_data: Dict[str, Any]) -> str:
        report = f"""
        📊 Analysis Report
        ─────────────────
        Complexity: {input_data['analysis']['complexity']}
        Processed Text: {input_data['analysis']['processed_text']}
        """
        
        self.console.print(Panel(
            report,
            title="Final Report",
            border_style="green"
        ))
        return report
    
    async def handle_error(self, error: Exception) -> None:
        self.console.print(f"[red]Reporting error: {str(error)}[/red]")

async def main():
    # Create coordinator
    coordinator = AgentCoordinator()
    
    # Create and register agents
    preprocessor = DataPreprocessor(AgentConfig(
        name="preprocessor",
        description="Preprocesses input data",
        capabilities=["text_preprocessing"]
    ))
    
    analyzer = Analyzer(AgentConfig(
        name="analyzer",
        description="Analyzes preprocessed data",
        capabilities=["data_analysis"]
    ))
    
    reporter = Reporter(AgentConfig(
        name="reporter",
        description="Generates reports",
        capabilities=["reporting"]
    ))
    
    coordinator.register_agent(preprocessor)
    coordinator.register_agent(analyzer)
    coordinator.register_agent(reporter)
    
    # Create a workflow
    workflow = Workflow(coordinator)
    
    # Add workflow steps
    input_text = "This is a sample text that needs to be processed by our coordinated agents!"
    
    workflow.add_step(Message(
        sender="main",
        receiver="preprocessor",
        content=input_text,
        message_type="preprocess",
        context={"requires_response": True}
    ))
    
    workflow.add_step(Message(
        sender="main",
        receiver="analyzer",
        content={"cleaned_text": "", "word_count": 0},  # Will be filled by preprocessor
        message_type="analyze",
        context={"requires_response": True}
    ))
    
    workflow.add_step(Message(
        sender="main",
        receiver="reporter",
        content={"analysis": {}},  # Will be filled by analyzer
        message_type="report",
        context={"requires_response": True}
    ))
    
    # Start the coordinator
    coordinator_task = asyncio.create_task(coordinator.start())
    
    # Execute the workflow
    await workflow.execute()
    
    # Wait a bit for all messages to be processed
    await asyncio.sleep(1)
    
    # Stop the coordinator
    coordinator.stop()
    await coordinator_task

if __name__ == "__main__":
    asyncio.run(main())
