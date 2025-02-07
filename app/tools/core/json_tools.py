import json

class JSONTool:
    def get_name(self):
        return "json_formatter"

    def get_description(self):
        return "Validates and formats JSON documents with configurable indentation"

    def process(self, input_data: str, action: str = 'format', indent: int = 4) -> dict:
        try:
            data = json.loads(input_data)
            
            if action == 'validate':
                return {
                    "valid": True,
                    "message": "✅ 有效的JSON文档",
                    "detail": {
                        "document_length": len(input_data),
                        "object_count": len(data) if isinstance(data, dict) else 1
                    }
                }
            
            return {
                "valid": True,
                "formatted": json.dumps(data, indent=indent, ensure_ascii=False)
            }
            
        except json.JSONDecodeError as e:
            error_line = input_data.split('\n')[e.lineno - 1] if e.lineno else ""
            return {
                "valid": False,
                "error_type": "语法错误",
                "message": "🚨 JSON格式错误",
                "detail": {
                    "position": f"第{e.lineno}行, 第{e.colno}列",
                    "error": e.msg,
                    "context": error_line[:100] + "..." if len(error_line) > 100 else error_line,
                    "suggestion": self._get_error_suggestion(e.msg)
                }
            }
        except Exception as e:
            return {
                "valid": False,
                "error_type": "处理错误",
                "message": "⚠️ 处理JSON时发生意外错误",
                "detail": str(e)
            }

    def _get_error_suggestion(self, error_msg: str) -> str:
        suggestions = {
            "Expecting property name enclosed in double quotes": "请检查属性名是否使用双引号包裹",
            "Expecting ':' delimiter": "属性名和值之间需要冒号分隔",
            "Expecting ',' delimiter": "多个属性/元素之间需要逗号分隔",
            "Unterminated string starting at": "字符串缺少结束引号",
            "Invalid control character": "包含非法控制字符，建议转义",
            "Extra data": "文档末尾有多余内容"
        }
        return suggestions.get(error_msg, "请检查JSON语法是否正确")

    def render_ui(self):
        import streamlit as st
        
        st.header("JSON格式化与验证")
        input_json = st.text_area("输入JSON内容", height=200)
        indent = st.slider("缩进空格数", 2, 8, 4)
        action = st.radio("操作类型", ["格式化", "验证"])
        
        if st.button("执行"):
            result = self.process(input_json, 
                                action='format' if action == "格式化" else 'validate',
                                indent=indent)
            
            if result['valid']:
                if action == "格式化":
                    st.code(result['formatted'], language='json')
                else:
                    st.success("✅ 验证通过")
                    st.json(result['detail'])
            else:
                st.error(f"❌ {result['message']}")
                st.code(f"错误位置：{result['detail']['position']}\n{result['detail']['context']}")
                st.warning(f"修复建议：{result['detail']['suggestion']}")
