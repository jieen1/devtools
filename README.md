# devtools
tool collection for develops with web &amp; api access


## Features

- **Text Tools**: Convert text case, encode/decode URLs, and manipulate JSON.
- **Crypto Tools**: Encrypt/decrypt data, generate hashes, and sign/verify messages.
- **Class Generator**: Generate classes from templates with dynamic fields.
- **PDF/Excel Tools**: Convert PDFs to Excel and vice versa.


## Get Started:

### Using Virtual Environment (Recommended)

1. Create a virtual environment (if not already created):
   ```
   python -m venv venv
   ```

2. Activate the virtual environment:
   - Windows Command Prompt: 
     ```
     .\venv\Scripts\activate
     ```
   - Windows PowerShell: 
     ```
     .\venv\Scripts\Activate.ps1
     ```
     *Note: You might need to enable script execution with `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`*

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Run the app (choose one of the following options):

   a) **Web UI** (Streamlit interface):
   ```
   streamlit run app/main.py
   ```

   b) **API Server** (FastAPI):
   ```
   python run_api.py
   ```
   The API will be available at `http://localhost:8000`. Visit `http://localhost:8000/docs` for interactive API documentation.

### Without Virtual Environment

1. Install dependencies: `pip install -r requirements.txt`
2. Run the app (choose one):
   - Web UI: `streamlit run app/main.py`
   - API Server: `python run_api.py`

## API Endpoints

- `GET /tools` - List all available tools with descriptions
- `POST /tools/{tool_name}` - Execute a specific tool with parameters

Example API usage:
```bash
# List all tools
curl -X GET http://localhost:8000/tools

# Execute a tool
curl -X POST http://localhost:8000/tools/text_case_converter \
  -H "Content-Type: application/json" \
  -d '{"text": "hello world", "case_type": "upper"}'