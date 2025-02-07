import json
import streamlit as st
from typing import Dict, List, Optional


class ClassGenerator:
    def get_name(self):
        return "class_generator"
    
    def get_description(self):
        return "将JSON对象转换为Java/Python实体类"
    
    def _generate_java_class(self, class_name: str, properties: Dict) -> str:
        class_code = f"public class {class_name} {{\n"
        for prop, prop_type in properties.items():
            camel_prop = self._convert_to_camel_case(prop)
            class_code += f"    private {prop_type} {camel_prop};\n"
        class_code += "\n"
        for prop, prop_type in properties.items():
            camel_prop = self._convert_to_camel_case(prop)
            class_code += f"    public {prop_type} get{camel_prop[0].upper() + camel_prop[1:]}() {{\n"
            class_code += f"        return this.{camel_prop};\n"
            class_code += "    }\n\n"
            class_code += f"    public void set{camel_prop[0].upper() + camel_prop[1:]}({prop_type} {camel_prop}) {{\n"
            class_code += f"        this.{camel_prop} = {camel_prop};\n"
            class_code += "    }\n\n"
        class_code += "}"
        return class_code
    
    def _generate_python_class(self, class_name: str, properties: Dict) -> str:
        class_code = f"class {class_name}:\n"
        for prop, prop_type in properties.items():
            snake_prop = self._convert_to_snake_case(prop)
            class_code += f"    {snake_prop}: {prop_type}\n\n"
        class_code += "    def __init__(self"
        for prop in properties:
            snake_prop = self._convert_to_snake_case(prop)
            class_code += f", {snake_prop}: {properties[prop]} = None"
        class_code += "):\n"
        for prop in properties:
            snake_prop = self._convert_to_snake_case(prop)
            class_code += f"        self.{snake_prop} = {snake_prop}\n"
        return class_code
    
    def _parse_json(self, json_str: str) -> Dict:
        try:
            data = json.loads(json_str)
            if not isinstance(data, dict):
                raise ValueError("输入必须是JSON对象")
            return data
        except json.JSONDecodeError as e:
            raise ValueError(f"无效的JSON格式: {str(e)}")
    
    def _get_properties(self, data: Dict) -> Dict:
        properties = {}
        for key, value in data.items():
            if isinstance(value, str):
                properties[key] = "String"
            elif isinstance(value, bool):
                properties[key] = "boolean"
            elif isinstance(value, int):
                properties[key] = "int"
            elif isinstance(value, float):
                properties[key] = "double"
            elif isinstance(value, list):
                properties[key] = "List<Object>"
            elif isinstance(value, dict):
                properties[key] = "Object"
            else:
                properties[key] = "Object"
        return properties
    
    def render_ui(self):
        st.header("🛠️ JSON转实体类工具")
        json_input = st.text_area("输入JSON对象", height=200)
        language = st.selectbox("选择目标语言", ["Java", "Python"])
        class_name = st.text_input("类名", "MyClass")
        
        if st.button("生成代码"):
            try:
                data = self._parse_json(json_input)
                properties = self._get_properties(data)
                if language == "Java":
                    code = self._generate_java_class(class_name, properties)
                else:
                    code = self._generate_python_class(class_name, properties)
                st.code(code, language=language.lower())
            except ValueError as e:
                st.error(f"错误: {str(e)}")

    def _convert_to_camel_case(self, name: str) -> str:
        parts = name.split('_')
        return parts[0] + ''.join(part.capitalize() for part in parts[1:])

    def _convert_to_snake_case(self, name: str) -> str:
        return ''.join(['_'+char.lower() if char.isupper() else char for char in name]).lstrip('_')