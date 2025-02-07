from typing import Dict, Type
from ..tools.base import BaseTool

class ToolRegistry:
    _instance = None
    _tools: Dict[str, Type[BaseTool]] = {}

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance._tools = {}
        return cls._instance

    def register(self, tool_class: Type[BaseTool]) -> None:
        """Register a new tool"""
        self._tools[tool_class.__name__] = tool_class

    def get_tool(self, name: str) -> Type[BaseTool]:
        """Get a tool by name"""
        return self._tools.get(name)

    def get_all_tools(self) -> Dict[str, Type[BaseTool]]:
        """Get all registered tools"""
        return self._tools

registry = ToolRegistry()
