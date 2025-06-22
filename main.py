# main.py

import tools # ✅ runs tools.py, executes @mcp.tool decorators
import uvicorn
import os

app = tools.app

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))