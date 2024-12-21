import aiohttp
from typing import Dict, Any, List, Optional
import json
from urllib.parse import urljoin
import os
from core import BaseAgent, AgentConfig
from rich.console import Console

class APIAgent(BaseAgent):
    """Agent for handling external API interactions"""
    
    def _initialize(self) -> None:
        self.console = Console()
        self.session = aiohttp.ClientSession()
        self.api_configs: Dict[str, Dict[str, Any]] = {}
        self._load_api_configs()
    
    def _load_api_configs(self) -> None:
        """Load API configurations from environment variables"""
        # Load API keys from environment
        self.api_configs = {
            "openai": {
                "api_key": os.getenv("OPENAI_API_KEY"),
                "base_url": "https://api.openai.com/v1/"
            },
            "github": {
                "api_key": os.getenv("GITHUB_TOKEN"),
                "base_url": "https://api.github.com/"
            },
            # Add more API configurations as needed
        }
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process API requests"""
        service = input_data.get("service", "")
        endpoint = input_data.get("endpoint", "")
        method = input_data.get("method", "GET")
        data = input_data.get("data", {})
        params = input_data.get("params", {})
        headers = input_data.get("headers", {})
        
        if not service:
            raise ValueError("Service name is required")
        
        return await self._make_request(
            service, endpoint, method,
            data=data, params=params,
            headers=headers
        )
    
    async def _make_request(
        self,
        service: str,
        endpoint: str,
        method: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make an HTTP request to the specified API"""
        if service not in self.api_configs:
            raise ValueError(f"Unknown service: {service}")
        
        config = self.api_configs[service]
        url = urljoin(config["base_url"], endpoint)
        
        # Add API key to headers if available
        if config.get("api_key"):
            headers = headers or {}
            headers["Authorization"] = f"Bearer {config['api_key']}"
        
        try:
            async with getattr(self.session, method.lower())(
                url,
                json=data,
                params=params,
                headers=headers
            ) as response:
                response_data = await response.json()
                return {
                    "status": response.status,
                    "data": response_data
                }
                
        except Exception as e:
            await self.handle_error(e)
            return {"error": str(e)}
    
    async def handle_error(self, error: Exception) -> None:
        """Handle API errors"""
        self.console.print(f"[red]API error: {str(error)}[/red]")
    
    async def cleanup(self) -> None:
        """Clean up resources"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    def get_capabilities(self) -> List[str]:
        """Return agent capabilities"""
        return [
            "api_integration",
            "http_requests",
            "openai_integration",
            "github_integration"
        ]
