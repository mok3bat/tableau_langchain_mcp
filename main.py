# main.py

import os
from tools import mcp  # ✅ Must import tools to run @mcp.tool decorators
import asyncio

if __name__ == "__main__":
    # Could also use 'sse' transport, host="0.0.0.0" required for Cloud Run.
    asyncio.run(
        mcp.run_sse_async(
            transport="streamable-http", 
            host="0.0.0.0", 
            port=os.getenv("PORT", 8000),
        )
    )