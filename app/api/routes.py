from fastapi import FastAPI, HTTPException
from typing import Dict, Any
from ..utils.registry import registry

app = FastAPI(title="DevTools Hub API")

@app.get("/tools")
async def list_tools():
    """List all available tools"""
    tools = registry.get_all_tools()
    return {
        name: {
            "name": tool.__name__,
            "description": tool.__doc__ or "No description available"
        }
        for name, tool in tools.items()
    }

@app.post("/tools/{tool_name}")
async def execute_tool(tool_name: str, params: Dict[str, Any]):
    """Execute a specific tool"""
    tool_class = registry.get_tool(tool_name)
    if not tool_class:
        raise HTTPException(status_code=404, message="Tool not found")

    tool = tool_class()
    result = tool.execute(params)
    return result
