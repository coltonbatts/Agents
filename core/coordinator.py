from typing import Dict, List, Optional, Type, Any
import asyncio
from pydantic import BaseModel
from .base_agent import BaseAgent, AgentConfig

class Message(BaseModel):
    """Message passed between agents"""
    sender: str
    receiver: str
    content: Any
    message_type: str
    context: Dict[str, Any] = {}

class AgentCoordinator:
    """Coordinates communication and task delegation between agents"""
    
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.message_queue: asyncio.Queue[Message] = asyncio.Queue()
        self._running = False
    
    def register_agent(self, agent: BaseAgent) -> None:
        """Register a new agent with the coordinator"""
        self.agents[agent.config.name] = agent
    
    async def send_message(self, message: Message) -> None:
        """Send a message to the message queue"""
        await self.message_queue.put(message)
    
    async def route_message(self, message: Message) -> None:
        """Route a message to its intended recipient"""
        if message.receiver in self.agents:
            receiver = self.agents[message.receiver]
            try:
                result = await receiver.process(message.content)
                # If sender expects a response, send it back
                if message.context.get("requires_response", False):
                    response = Message(
                        sender=message.receiver,
                        receiver=message.sender,
                        content=result,
                        message_type="response",
                        context=message.context
                    )
                    await self.send_message(response)
            except Exception as e:
                await receiver.handle_error(e)
        else:
            print(f"No agent found for receiver: {message.receiver}")
    
    async def start(self) -> None:
        """Start the coordinator's message processing loop"""
        self._running = True
        while self._running:
            message = await self.message_queue.get()
            await self.route_message(message)
            self.message_queue.task_done()
    
    def stop(self) -> None:
        """Stop the coordinator's message processing loop"""
        self._running = False
    
    def get_agent_capabilities(self) -> Dict[str, List[str]]:
        """Get a mapping of agent names to their capabilities"""
        return {
            name: agent.get_capabilities()
            for name, agent in self.agents.items()
        }
    
    async def delegate_task(self, task: Any, task_type: str) -> Optional[BaseAgent]:
        """Find the most suitable agent for a given task"""
        for agent in self.agents.values():
            if task_type in agent.get_capabilities():
                return agent
        return None

class Workflow:
    """Represents a multi-step workflow involving multiple agents"""
    
    def __init__(self, coordinator: AgentCoordinator):
        self.coordinator = coordinator
        self.steps: List[Message] = []
        self.results: List[Any] = []
    
    def add_step(self, message: Message) -> None:
        """Add a step to the workflow"""
        self.steps.append(message)
    
    async def execute(self) -> List[Any]:
        """Execute all steps in the workflow"""
        for step in self.steps:
            await self.coordinator.send_message(step)
            # If we need to wait for the result, we could implement
            # a way to track message responses here
        return self.results
