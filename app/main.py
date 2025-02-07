import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import streamlit as st
from tools.core.text_tools import TextCaseConverter
from utils.registry import registry
from tools.core.url_tools import URLEncoder
from tools.core.json_tools import JSONTool
from tools.core.crypto_tools import CryptoTool
from tools.core.class_generator import ClassGenerator

# Register tools
registry.register(TextCaseConverter)
registry.register(URLEncoder)
registry.register(JSONTool)
registry.register(CryptoTool)
registry.register(ClassGenerator)

def main():
    st.set_page_config(
        page_title="DevTools Hub",
        page_icon="🛠️",
        layout="wide"
    )

    st.title("🛠️ DevTools Hub")
    st.write("Welcome to DevTools Hub! Select a tool to get started.")

    # Sidebar tool selection
    tools = registry.get_all_tools()
    tool_name = st.sidebar.selectbox(
        "Select Tool",
        options=list(tools.keys()),
        format_func=lambda x: tools[x].__name__
    )
    # Create and render selected tool
    if tool_name:
        tool = tools[tool_name]()
        tool.render_ui()

if __name__ == "__main__":
    main()
