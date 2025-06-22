# main.py

import os
import uvicorn
from tools import mcp

app = mcp.app  # Get the underlying FastAPI app

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

