# tools.py
from mcp.server.fastmcp import FastMCP
import os


# Create MCP using that app
mcp = FastMCP(host="0.0.0.0", 
            port=os.getenv("PORT", 8000))

# ✅ Define your tools using the MCP instance
@mcp.tool()
def say_hi_world() -> str:
    return "Hello from Railway MCP!"