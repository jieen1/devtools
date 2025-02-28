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
   - Linux/macOS: 
     ```
     source venv/bin/activate
     ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Run the app (choose one of the following options):

   a) **Web UI** (Streamlit interface):
   - Windows:
   ```
   streamlit run app/main.py
   ```
   - Linux/macOS:
   ```
   streamlit run app/main.py
   ```

   b) **API Server** (FastAPI):
   - Windows:
   ```
   python run_api.py
   ```
   - Linux/macOS:
   ```
   python run_api.py
   ```
   The API will be available at `http://localhost:8000`. Visit `http://localhost:8000/docs` for interactive API documentation.

### Without Virtual Environment

1. Install dependencies: 
   - Windows: `pip install -r requirements.txt`
   - Linux/macOS: `pip install -r requirements.txt`
2. Run the app (choose one):
   - Web UI: 
     - Windows: `streamlit run app/main.py`
     - Linux/macOS: `streamlit run app/main.py`
   - API Server: 
     - Windows: `python run_api.py`
     - Linux/macOS: `python run_api.py`

### Running as a Service on Linux

To run the application as a service on Linux, you can use systemd:

1. Create a service file:
   ```bash
   sudo nano /etc/systemd/system/devtools.service
   ```

2. Add the following content (adjust paths as needed):
   ```
   [Unit]
   Description=DevTools Hub
   After=network.target

   [Service]
   User=<your-username>
   WorkingDirectory=/path/to/devtools
   ExecStart=/path/to/devtools/venv/bin/python -m streamlit run app/main.py --server.headless=true --server.port=8501
   Restart=always
   RestartSec=5
   StandardOutput=journal
   StandardError=journal

   [Install]
   WantedBy=multi-user.target
   ```

3. For the API server, create a separate service file:
   ```bash
   sudo nano /etc/systemd/system/devtools-api.service
   ```

4. Add the following content:
   ```
   [Unit]
   Description=DevTools Hub API
   After=network.target

   [Service]
   User=<your-username>
   WorkingDirectory=/path/to/devtools
   ExecStart=/path/to/devtools/venv/bin/python run_api.py
   Restart=always
   RestartSec=5
   StandardOutput=journal
   StandardError=journal

   [Install]
   WantedBy=multi-user.target
   ```

5. Enable and start the services:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable devtools.service
   sudo systemctl start devtools.service
   sudo systemctl enable devtools-api.service
   sudo systemctl start devtools-api.service
   ```

6. Check status:
   ```bash
   sudo systemctl status devtools.service
   sudo systemctl status devtools-api.service
   ```

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