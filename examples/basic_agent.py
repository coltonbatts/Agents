import asyncio
from typing import Any
from core import BaseAgent, AgentConfig

class BasicAgent(BaseAgent):
    """A simple example agent implementation"""
    
    def _initialize(self) -> None:
        """Initialize basic agent resources"""
        self.startup_time = asyncio.get_event_loop().time()
    
    async def process(self, input_data: Any) -> Any:
        """Process input by echoing it back with timestamp"""
        current_time = asyncio.get_event_loop().time()
        return {
            "input": input_data,
            "uptime": current_time - self.startup_time,
            "processed": True
        }
    
    async def handle_error(self, error: Exception) -> None:
        """Log errors for the basic agent"""
        print(f"Error in BasicAgent: {str(error)}")

async def main():
    # Create and test a basic agent
    config = AgentConfig(
        name="BasicAgent",
        description="A simple example agent that echoes input",
        capabilities=["echo", "uptime"]
    )
    
    agent = BasicAgent(config)
    
    # Test the agent
    result = await agent.process("Hello, Agent!")
    print(f"Agent Info: {agent.get_info()}")
    print(f"Process Result: {result}")

if __name__ == "__main__":
    asyncio.run(main())
