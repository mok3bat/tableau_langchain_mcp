import asyncio
import json

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
