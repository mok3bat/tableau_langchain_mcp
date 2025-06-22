from mcp.server.fastmcp import FastMCP

mcp = FastMCP()

@mcp.tool()
def say_hi_world() -> str:
    return "Hi from MCP"

fastmcp_asgi_app = mcp.asgi()

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(fastmcp_asgi_app, host="0.0.0.0", port=port)
