from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.responses import JSONResponse, StreamingResponse
from starlette.requests import Request
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from mcp.server.fastmcp import FastMCP
import logging
import os
from tools import mcp, tool_registry
import asyncio
import json

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
    
async def sse_messages(request: Request):
    try:
        data = await request.json()
        action = data.get("action")

        async def event_stream():
            yield "retry: 1000\n"  # Optional retry delay

            if action == "introspect":
                tools = mcp.get_tools()
                message = {
                    "type": "response",
                    "data": {
                        "tools": tools
                    }
                }
                yield f"data: {json.dumps(message)}\n\n"

            elif action == "execute":
                tool_name = data.get("tool")
                params = data.get("data", {})

                tool_func = tool_registry.get(tool_name)
                if not tool_func:
                    yield f"data: {json.dumps({'error': f'Tool {tool_name} not found'})}\n\n"
                    return

                # Optional: simulate streaming tokens or progress
                yield f"data: {{\"status\": \"executing\", \"tool\": \"{tool_name}\"}}\n\n"
                await asyncio.sleep(1)

                result = tool_func(**params)
                yield f"data: {json.dumps({'type': 'response', 'data': result})}\n\n"

            else:
                yield f"data: {json.dumps({'error': 'Unknown action'})}\n\n"

        return StreamingResponse(event_stream(), media_type="text/event-stream")

    except Exception as e:
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
    # 🔧 These are the key SSE routes
    Route("/sse/messages", endpoint=sse_messages, methods=["POST"]),
    Route("/sse", endpoint=sse_messages, methods=["POST"]),
    Route("/sse/message", endpoint=sse_messages, methods=["POST"]),
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
