from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from pydantic import BaseModel

class ToolResult(BaseModel):
    success: bool
    data: Any
    message: Optional[str] = None

class BaseTool(ABC):
    def __init__(self):
        self.name: str = self.__class__.__name__
        self.description: str = self.__doc__ or "No description available"

    @abstractmethod
    def execute(self, params: Dict[str, Any] = None) -> ToolResult:
        """Execute the tool with given parameters"""
        pass

    @abstractmethod
    def render_ui(self) -> None:
        """Render the tool's UI using Streamlit"""
        pass
