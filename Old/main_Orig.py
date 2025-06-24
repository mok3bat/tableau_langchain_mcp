from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.responses import JSONResponse
from starlette.requests import Request
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from mcp.server.fastmcp import FastMCP
import logging
import os
from tools import mcp, tool_registry

# --------------------------
# Handler for /messages
# --------------------------

async def handle_messages(request: Request):
    try:
        data = await request.json()
        logging.info(f"📨 Received: {data}")

        action = data.get("action")

        if action == "introspect":
            response = {
                "type": "response",
                "data": {
                    "tools": mcp.get_tools()
                }
            }

        elif action == "execute":
            tool_name = data.get("tool")
            params = data.get("data", {})

            tool_func = tool_registry.get(tool_name)
            if not tool_func:
                raise ValueError(f"Tool '{tool_name}' not found")

            result = tool_func(**params)

            response = {
                "type": "response",
                "data": result
            }

        return JSONResponse(response)

    except Exception as e:
        logging.exception("❌ handle_messages error")
        return JSONResponse({"error": str(e)}, status_code=500)

# --------------------------
# Starlette App Setup
# --------------------------
middleware = [
    Middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
]

routes = [
    Mount("/mcp", routes=[
        Route("/messages", endpoint=handle_messages, methods=["POST"]),
    ]),
    Route("/messages", endpoint=handle_messages, methods=["POST"]),
]

app = Starlette(routes=routes, middleware=middleware)

# --------------------------
# Local Dev Entrypoint
# --------------------------
if __name__ == "__main__":
    import uvicorn
    logging.basicConfig(level=logging.INFO)
    port = int(os.getenv("PORT", 8000))
    print(f"🚀 Running at http://localhost:{port}")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
