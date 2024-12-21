import typer
from typing import Optional, List
from pathlib import Path
import asyncio
import json
from datetime import datetime
import yaml
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
import aiocron
from enum import Enum

from core import AgentCoordinator, Message, Workflow
from core.coordinator import AgentConfig
from examples.coordinated_workflow import DataPreprocessor, Analyzer, Reporter

app = typer.Typer(help="AGENTS CLI - Manage and run agent workflows from the command line")
console = Console()

# Initialize coordinator
coordinator = AgentCoordinator()

class OutputFormat(str, Enum):
    """Output format options"""
    JSON = "json"
    YAML = "yaml"
    TABLE = "table"

def setup_agents():
    """Initialize and register default agents"""
    agents = [
        DataPreprocessor(AgentConfig(
            name="preprocessor",
            description="Preprocesses input data",
            capabilities=["text_preprocessing"]
        )),
        Analyzer(AgentConfig(
            name="analyzer",
            description="Analyzes preprocessed data",
            capabilities=["data_analysis"]
        )),
        Reporter(AgentConfig(
            name="reporter",
            description="Generates reports",
            capabilities=["reporting"]
        ))
    ]
    
    for agent in agents:
        coordinator.register_agent(agent)

@app.command()
def list_agents(
    format: OutputFormat = typer.Option(
        OutputFormat.TABLE,
        "--format", "-f",
        help="Output format"
    )
):
    """List all available agents and their capabilities"""
    agents_data = [
        {
            "name": name,
            "capabilities": capabilities,
            "description": coordinator.agents[name].config.description
        }
        for name, capabilities in coordinator.get_agent_capabilities().items()
    ]
    
    if format == OutputFormat.JSON:
        console.print_json(json.dumps(agents_data))
    elif format == OutputFormat.YAML:
        console.print(yaml.dump(agents_data))
    else:
        table = Table(title="Available Agents")
        table.add_column("Name", style="cyan")
        table.add_column("Capabilities", style="green")
        table.add_column("Description", style="yellow")
        
        for agent in agents_data:
            table.add_row(
                agent["name"],
                ", ".join(agent["capabilities"]),
                agent["description"]
            )
        
        console.print(table)

@app.command()
def run(
    workflow_file: Path = typer.Argument(
        ...,
        exists=True,
        help="Path to workflow YAML file"
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output", "-o",
        help="Save output to file"
    )
):
    """Run a workflow from a YAML file"""
    try:
        with open(workflow_file) as f:
            workflow_data = yaml.safe_load(f)
        
        async def execute_workflow():
            workflow = Workflow(coordinator)
            
            for step in workflow_data["steps"]:
                workflow.add_step(Message(
                    sender="cli",
                    receiver=step["agent"],
                    content=step["input"],
                    message_type=step.get("type", "process"),
                    context={"requires_response": True}
                ))
            
            coordinator_task = asyncio.create_task(coordinator.start())
            results = await workflow.execute()
            coordinator.stop()
            await coordinator_task
            
            return results
        
        results = asyncio.run(execute_workflow())
        
        if output:
            with open(output, "w") as f:
                json.dump(results, f, indent=2)
        else:
            console.print_json(json.dumps(results))
            
    except Exception as e:
        console.print(f"[red]Error running workflow: {str(e)}[/red]")
        raise typer.Exit(1)

@app.command()
def schedule(
    workflow_file: Path = typer.Argument(
        ...,
        exists=True,
        help="Path to workflow YAML file"
    ),
    cron: str = typer.Option(
        ...,
        "--cron", "-c",
        help="Cron expression (e.g. '*/5 * * * *' for every 5 minutes)"
    ),
    output_dir: Optional[Path] = typer.Option(
        None,
        "--output-dir", "-o",
        help="Directory to save outputs"
    )
):
    """Schedule a workflow to run on a cron schedule"""
    try:
        # Ensure output directory exists
        if output_dir:
            output_dir.mkdir(parents=True, exist_ok=True)
        
        async def run_scheduled_workflow():
            # Load workflow
            with open(workflow_file) as f:
                workflow_data = yaml.safe_load(f)
            
            # Execute workflow
            workflow = Workflow(coordinator)
            for step in workflow_data["steps"]:
                workflow.add_step(Message(
                    sender="cli_scheduler",
                    receiver=step["agent"],
                    content=step["input"],
                    message_type=step.get("type", "process"),
                    context={"requires_response": True}
                ))
            
            results = await workflow.execute()
            
            # Save results if output directory specified
            if output_dir:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = output_dir / f"workflow_result_{timestamp}.json"
                with open(output_file, "w") as f:
                    json.dump(results, f, indent=2)
            
            return results
        
        async def start_scheduler():
            # Start coordinator
            coordinator_task = asyncio.create_task(coordinator.start())
            
            # Setup cron job
            job = aiocron.crontab(cron, func=run_scheduled_workflow)
            console.print(f"[green]Scheduled workflow to run with cron: {cron}[/green]")
            
            try:
                while True:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                job.stop()
                coordinator.stop()
                await coordinator_task
                console.print("[yellow]Scheduler stopped[/yellow]")
        
        # Run the scheduler
        asyncio.run(start_scheduler())
        
    except Exception as e:
        console.print(f"[red]Error scheduling workflow: {str(e)}[/red]")
        raise typer.Exit(1)

@app.command()
def create_workflow(
    output: Path = typer.Argument(
        ...,
        help="Output YAML file path"
    )
):
    """Create a new workflow YAML file interactively"""
    workflow = {"steps": []}
    
    while True:
        add_step = typer.confirm("Add a workflow step?")
        if not add_step:
            break
        
        # Show available agents
        list_agents()
        
        agent = typer.prompt("Enter agent name")
        input_data = typer.prompt("Enter input data")
        step_type = typer.prompt("Enter step type", default="process")
        
        workflow["steps"].append({
            "agent": agent,
            "input": input_data,
            "type": step_type
        })
    
    with open(output, "w") as f:
        yaml.dump(workflow, f)
    
    console.print(f"[green]Workflow saved to {output}[/green]")

def main():
    """Initialize agents and start the CLI"""
    setup_agents()
    app()
