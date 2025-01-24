import streamlit as st
from typing import Dict, Any
from ..base import BaseTool, ToolResult

class TextCaseConverter(BaseTool):
    """Convert text between different cases (upper, lower, title)"""

    def execute(self, params: Dict[str, Any] = None) -> ToolResult:
        if not params or 'text' not in params or 'case' not in params:
            return ToolResult(success=False, message="Missing parameters", data=None)

        text = params['text']
        case = params['case']

        try:
            if case == 'upper':
                result = text.upper()
            elif case == 'lower':
                result = text.lower()
            elif case == 'title':
                result = text.title()
            else:
                return ToolResult(success=False, message="Invalid case option", data=None)

            return ToolResult(success=True, data=result)
        except Exception as e:
            return ToolResult(success=False, message=str(e), data=None)

    def render_ui(self) -> None:
        st.write("## Text Case Converter")
        text = st.text_area("Input Text", "Enter your text here...")
        case = st.selectbox("Select Case", ['upper', 'lower', 'title'])

        if st.button("Convert"):
            result = self.execute({"text": text, "case": case})
            if result.success:
                st.success("Conversion successful!")
                st.write("Result:", result.data)
            else:
                st.error(f"Error: {result.message}")
