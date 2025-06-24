from mcp.server.fastmcp import FastMCP
from fastapi import FastAPI

mcp = FastMCP(
    "hello-mcp",
    transport="streamable-http",
    stateless_http=True
)

@mcp.tool()
def say_hi() -> dict:
    return {
        "content": [
            { "type": "text", "text": "👋 Hello from deployed MCP!" }
        ]
    }

app = FastAPI()
app.mount("/mcp", mcp.streamable_http_app())
