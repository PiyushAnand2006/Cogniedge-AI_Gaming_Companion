"""
Controlled Tool Registry for Qwen3-4B
Ensures Qwen can inspect structured state (game, telemetry, memory) without
having arbitrary shell or OS modification permissions.
"""

from typing import Dict, Any, Callable, List, Optional
from pydantic import BaseModel


class ToolDefinition(BaseModel):
    name: str
    description: str
    parameters: Dict[str, Any]


class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, Callable] = {}
        self._definitions: Dict[str, ToolDefinition] = {}

    def register(self, name: str, description: str, parameters: Dict[str, Any], func: Callable):
        self._definitions[name] = ToolDefinition(
            name=name,
            description=description,
            parameters=parameters
        )
        self._tools[name] = func

    def get_definitions(self) -> List[Dict[str, Any]]:
        return [t.model_dump() for t in self._definitions.values()]

    def execute(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        if name not in self._tools:
            return {"error": f"Tool '{name}' is not registered in CogniEdge tool registry."}
        try:
            result = self._tools[name](**arguments)
            return {"status": "success", "result": result}
        except Exception as e:
            return {"status": "error", "message": str(e)}
