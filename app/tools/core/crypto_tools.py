# 文件：app/tools/core/crypto_tools.py
from Crypto.Cipher import AES, DES3
import base64
import rsa
import streamlit as st

class CryptoTool:

    def get_name(self):
        return "crypto_tool"
    
    def get_description(self):
        return "AES/RSA/DES3/Base64加解密工具"
    
    def process(self, input_data: str, algorithm: str, mode: str, key: str = None) -> dict:
        try:
            if algorithm == "AES":
                return self._handle_aes(input_data, mode, key)
            elif algorithm == "RSA":
                return self._handle_rsa(input_data, mode, key)
            elif algorithm == "DES3":
                return self._handle_des3(input_data, mode, key)
            elif algorithm == "Base64":
                return self._handle_base64(input_data, mode)
            else:
                raise ValueError("不支持的算法类型")
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "suggestion": self._get_error_suggestion(e)
            }

    def _handle_aes(self, data: str, mode: str, key: str):
        if not key:
            key = "4133439984133439"
        cipher = AES.new(key.encode(), AES.MODE_GCM)
        if mode == "encrypt":
            ciphertext, tag = cipher.encrypt_and_digest(data.encode())
            return {
                "ciphertext": base64.b64encode(ciphertext).decode(),
                "tag": base64.b64encode(tag).decode(),
                "nonce": base64.b64encode(cipher.nonce).decode()
            }
        else:
            decrypted = cipher.decrypt_and_verify(
                base64.b64decode(data["ciphertext"]),
                base64.b64decode(data["tag"])
            )
            return {"plaintext": decrypted.decode()}

    def _handle_rsa(self, data: str, mode: str, key: str):
        if mode == "encrypt":
            pubkey = rsa.PublicKey.load_pkcs1(key.encode())
            encrypted = rsa.encrypt(data.encode(), pubkey)
            return {"ciphertext": base64.b64encode(encrypted).decode()}
        else:
            privkey = rsa.PrivateKey.load_pkcs1(key.encode())
            decrypted = rsa.decrypt(base64.b64decode(data), privkey)
            return {"plaintext": decrypted.decode()}

    def _handle_des3(self, data: str, mode: str, key: str):
        if not key:
            key = "4133439984133439"
        cipher = DES3.new(key.encode(), DES3.MODE_EAX)
        if mode == "encrypt":
            ciphertext, tag = cipher.encrypt_and_digest(data.encode())
            return {
                "ciphertext": base64.b64encode(ciphertext).decode(),
                "tag": base64.b64encode(tag).decode(),
                "nonce": base64.b64encode(cipher.nonce).decode()
            }
        else:
            decrypted = cipher.decrypt_and_verify(
                base64.b64decode(data["ciphertext"]),
                base64.b64decode(data["tag"])
            )
            return {"plaintext": decrypted.decode()}

    def _handle_base64(self, data: str, mode: str):
        try:
            if mode == "encrypt":
                encoded = base64.b64encode(data.encode()).decode()
                return {"result": encoded}
            else:
                # 自动补全缺失的等号
                missing_padding = len(data) % 4
                if missing_padding:
                    data += '=' * (4 - missing_padding)
                decoded = base64.b64decode(data).decode()
                return {"result": decoded}
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "suggestion": "请检查输入是否为有效的Base64编码字符串"
            }

    def _get_error_suggestion(self, error: Exception) -> str:
        error_map = {
            "Incorrect padding": "检查Base64编码是否正确",
            "Invalid signature": "验证密钥是否匹配",
            "ValueError": "检查输入参数格式",
            "Invalid key length": "密钥长度需符合算法要求（AES: 16/24/32字节）"
        }
        return error_map.get(str(error), "请检查输入参数和密钥")

    def render_ui(self):
        st.header("🔐 加解密工具")
        algo = st.selectbox("算法选择", ["AES", "RSA", "DES3", "Base64"])
        mode = st.radio("操作模式", ["encrypt", "decrypt"])
        
        input_data = st.text_area("输入内容", height=150)
        key = None
        
        if algo in ["AES", "RSA", "DES3"]:
            key = st.text_input(f"{algo}密钥", 
                              help="AES: 16/24/32字节, RSA: PKCS#1格式, DES3: 24字节")
        
        if st.button("执行操作"):
            result = self.process(
                input_data=input_data,
                algorithm=algo,
                mode=mode.lower(),
                key=key
            )
            
            if result.get("success", True):
                st.success("操作成功！")
                st.json(result)
            else:
                st.error(f"操作失败：{result['error']}")
                st.warning(f"建议：{result['suggestion']}")