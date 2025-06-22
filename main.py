# main.py

import os
from tools import mcp, say_hi_world  # ✅ Must import tools to run @mcp.tool decorators

if __name__ == "__main__":
    # Could also use 'sse' transport, host="0.0.0.0" required for Cloud Run.
    
    mcp.register_tool(say_hi_world)

    # Expose ASGI app
    fastmcp_asgi_app = mcp.asgi()