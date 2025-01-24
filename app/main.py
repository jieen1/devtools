import streamlit as st
from tools.examples.text_tools import TextCaseConverter
from utils.registry import registry

# Register tools
registry.register(TextCaseConverter)

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
