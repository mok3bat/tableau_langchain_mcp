# main.py

import os
# from tools import mcp  # ✅ Must import tools to run @mcp.tool decorators
import asyncio

# tools.py
from mcp.server.fastmcp import FastMCP


# Create MCP using that app
mcp = FastMCP(host="0.0.0.0", 
            port=os.getenv("PORT", 8000))

# ✅ Define your tools using the MCP instance
@mcp.tool()
def say_hi_world() -> str:
    return "Hello from Railway MCP!"

if __name__ == "__main__":
    # Could also use 'sse' transport, host="0.0.0.0" required for Cloud Run.
    asyncio.run(
        mcp.run_sse_async()
    )