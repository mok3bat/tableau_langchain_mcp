# tools.py

from fastapi import FastAPI
from mcp.server.fastmcp import FastMCP

# Create FastAPI app
app = FastAPI()

# Create MCP using that app
mcp = FastMCP(app=app)

# ✅ Define your tools using the MCP instance
@mcp.tool()
def say_hi_world() -> str:
    return "Hello from Railway MCP!"

# ✅ This activates the MCP tool binding
def activate_tools():
    return mcp
