from fastapi import FastAPI
from mcp.server.fastmcp import FastMCP

app = FastAPI()
mcp = FastMCP(app=app)

@mcp.tool()
def say_hi_world() -> str:
    return "Hi World from MCP!"


import os
import uvicorn


port = int(os.getenv("PORT", 8000))
uvicorn.run(app, host="0.0.0.0", port=port)
