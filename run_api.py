import sys
import logging
from pathlib import Path
import uvicorn

# Get the absolute path to the project root
project_root = Path(__file__).parent.absolute()

# Add the project root to the path
sys.path.append(str(project_root))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("api.log"),
        logging.StreamHandler()
    ]
)

if __name__ == "__main__":
    logging.info("Starting DevTools Hub API server")
    # Run the FastAPI server
    uvicorn.run(
        "app.api.routes:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info"
    )
