import pandas as pd
import json
from typing import Dict, Any, Union, List
import sqlite3
from pathlib import Path
import yaml
from core import BaseAgent, AgentConfig
from rich.console import Console

class DataAgent(BaseAgent):
    """Agent for handling various data formats and sources"""
    
    def _initialize(self) -> None:
        self.console = Console()
        self.supported_formats = ["csv", "json", "sqlite", "yaml"]
        self.connections: Dict[str, Any] = {}
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process data based on input configuration"""
        operation = input_data.get("operation", "read")
        data_format = input_data.get("format", "csv")
        source = input_data.get("source", "")
        query = input_data.get("query", "")
        
        if operation == "read":
            return await self._read_data(data_format, source, query)
        elif operation == "write":
            return await self._write_data(
                data_format,
                source,
                input_data.get("data", {}),
                input_data.get("options", {})
            )
        elif operation == "query":
            return await self._query_data(data_format, source, query)
        else:
            raise ValueError(f"Unsupported operation: {operation}")
    
    async def _read_data(self, data_format: str, source: str, query: str = "") -> Dict[str, Any]:
        """Read data from various sources"""
        try:
            if data_format == "csv":
                df = pd.read_csv(source)
                if query:
                    df = df.query(query)
                return {"data": df.to_dict(orient="records")}
            
            elif data_format == "json":
                with open(source) as f:
                    data = json.load(f)
                return {"data": data}
            
            elif data_format == "sqlite":
                conn = sqlite3.connect(source)
                df = pd.read_sql_query(query if query else "SELECT * FROM main", conn)
                conn.close()
                return {"data": df.to_dict(orient="records")}
            
            elif data_format == "yaml":
                with open(source) as f:
                    data = yaml.safe_load(f)
                return {"data": data}
            
            else:
                raise ValueError(f"Unsupported format: {data_format}")
                
        except Exception as e:
            await self.handle_error(e)
            return {"error": str(e)}
    
    async def _write_data(
        self,
        data_format: str,
        target: str,
        data: Union[List[Dict[str, Any]], Dict[str, Any]],
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Write data to various targets"""
        try:
            if data_format == "csv":
                df = pd.DataFrame(data)
                df.to_csv(target, **options)
            
            elif data_format == "json":
                with open(target, "w") as f:
                    json.dump(data, f, **options)
            
            elif data_format == "sqlite":
                table_name = options.get("table_name", "main")
                if_exists = options.get("if_exists", "replace")
                
                df = pd.DataFrame(data)
                conn = sqlite3.connect(target)
                df.to_sql(table_name, conn, if_exists=if_exists, index=False)
                conn.close()
            
            elif data_format == "yaml":
                with open(target, "w") as f:
                    yaml.dump(data, f, **options)
            
            else:
                raise ValueError(f"Unsupported format: {data_format}")
            
            return {"status": "success", "target": target}
            
        except Exception as e:
            await self.handle_error(e)
            return {"error": str(e)}
    
    async def _query_data(self, data_format: str, source: str, query: str) -> Dict[str, Any]:
        """Query data using format-specific query languages"""
        try:
            if data_format == "csv":
                df = pd.read_csv(source)
                result = df.query(query)
                return {"data": result.to_dict(orient="records")}
            
            elif data_format == "sqlite":
                conn = sqlite3.connect(source)
                df = pd.read_sql_query(query, conn)
                conn.close()
                return {"data": df.to_dict(orient="records")}
            
            else:
                raise ValueError(f"Querying not supported for format: {data_format}")
                
        except Exception as e:
            await self.handle_error(e)
            return {"error": str(e)}
    
    async def handle_error(self, error: Exception) -> None:
        """Handle data processing errors"""
        self.console.print(f"[red]Data processing error: {str(error)}[/red]")
    
    def get_capabilities(self) -> List[str]:
        """Return agent capabilities"""
        return [
            "data_processing",
            "csv_handling",
            "json_handling",
            "sqlite_handling",
            "yaml_handling",
            "data_querying"
        ]
