# tools.py
from mcp.server.fastmcp import FastMCP


# Create MCP using that app
mcp = FastMCP()

# ✅ Define your tools using the MCP instance
@mcp.tool()
def say_hi_world() -> str:
    return "Hello from Railway MCP!"