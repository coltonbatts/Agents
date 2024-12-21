from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import json
from typing import Dict, List, Any
import asyncio
from pathlib import Path
import os
from mangum import Mangum

from core import AgentCoordinator, Message, Workflow
from core.coordinator import BaseAgent, AgentConfig
from examples.coordinated_workflow import DataPreprocessor, Analyzer, Reporter

# Initialize FastAPI app
app = FastAPI(
    title="AGENTS Web Interface",
    description="A retro-inspired web interface for the AGENTS framework",
    version="0.1.0"
)

# Setup static files and templates
BASE_DIR = Path(__file__).resolve().parent
static_path = BASE_DIR / "static"
templates = Jinja2Templates(directory=str(static_path))

# Ensure static directory exists
static_path.mkdir(parents=True, exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# Initialize coordinator and agents
coordinator = AgentCoordinator()
coordinator_task = None

def setup_agents():
    """Initialize and register all agents"""
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

@app.on_event("startup")
async def startup_event():
    """Initialize the coordinator on startup"""
    global coordinator_task
    setup_agents()
    coordinator_task = asyncio.create_task(coordinator.start())

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up coordinator on shutdown"""
    coordinator.stop()
    if coordinator_task:
        await coordinator_task

@app.get("/", response_class=HTMLResponse)
async def get_home(request: Request):
    """Render the main UI"""
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )

@app.get("/api/agents")
async def get_agents():
    """Get list of available agents and their capabilities"""
    return {
        "agents": [
            {
                "name": name,
                "capabilities": capabilities,
                "description": coordinator.agents[name].config.description
            }
            for name, capabilities in coordinator.get_agent_capabilities().items()
        ]
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time agent communication"""
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            
            # Create workflow from request
            workflow = Workflow(coordinator)
            
            # Add steps based on selected agents
            for step in data.get("steps", []):
                workflow.add_step(Message(
                    sender="web_client",
                    receiver=step["agent"],
                    content=step["input"],
                    message_type=step["type"],
                    context={"requires_response": True}
                ))
            
            # Execute workflow and collect results
            results = await workflow.execute()
            
            # Send results back to client
            await websocket.send_json({
                "status": "success",
                "results": results
            })
            
    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        await websocket.send_json({
            "status": "error",
            "message": str(e)
        })

# Create handler for serverless deployment
handler = Mangum(app)
