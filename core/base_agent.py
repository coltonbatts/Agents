from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pydantic import BaseModel

class AgentConfig(BaseModel):
    """Base configuration for all agents"""
    name: str
    description: str
    version: str = "0.1.0"
    capabilities: List[str] = []

class BaseAgent(ABC):
    """Abstract base class for all agents"""
    
    def __init__(self, config: AgentConfig):
        self.config = config
        self._initialize()
    
    @abstractmethod
    def _initialize(self) -> None:
        """Initialize agent-specific resources"""
        pass
    
    @abstractmethod
    async def process(self, input_data: Any) -> Any:
        """Process input and return results"""
        pass
    
    @abstractmethod
    async def handle_error(self, error: Exception) -> None:
        """Handle agent-specific errors"""
        pass
    
    def get_capabilities(self) -> List[str]:
        """Return list of agent capabilities"""
        return self.config.capabilities
    
    def get_info(self) -> Dict[str, Any]:
        """Return agent information"""
        return {
            "name": self.config.name,
            "description": self.config.description,
            "version": self.config.version,
            "capabilities": self.config.capabilities
        }
