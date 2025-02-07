# app/tools/core/url_tools.py
import streamlit as st
from typing import Dict, Any
from urllib.parse import quote
from ..base import BaseTool, ToolResult

class URLEncoder(BaseTool):
    """URL编码转换工具（支持完整编码和保留特殊字符）"""
    
    def execute(self, params: Dict[str, Any] = None) -> ToolResult:
        if not params or 'text' not in params:
            return ToolResult(success=False, message="缺少输入文本", data=None)
        
        text = params.get('text', '')
        encode_type = params.get('encode_type', 'full')
        
        try:
            if encode_type == 'full':
                encoded = quote(text, safe='')
            else:  # 保留特殊字符
                encoded = quote(text, safe=':/?&=')
            return ToolResult(success=True, data=encoded)
        except Exception as e:
            return ToolResult(success=False, message=str(e), data=None)

    def render_ui(self) -> None:
        st.write("## URL编码转换器")
        text = st.text_area("输入文本", "", key="url_encoder_input")
        encode_type = st.radio("编码类型", 
                             options=['full', '保留特殊字符'],
                             help="完整编码：转换所有特殊字符\n保留特殊字符：保留 :/?&= 不编码")
        
        if st.button("编码"):
            if not text:
                st.error("请输入需要编码的文本")
                return
                
            result = self.execute({
                "text": text,
                "encode_type": 'full' if encode_type == 'full' else 'partial'
            })
            
            if result.success:
                st.success("编码成功！")
                st.code(result.data, language="text")
            else:
                st.error(f"编码失败：{result.message}")