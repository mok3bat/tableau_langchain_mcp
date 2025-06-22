from fastapi import FastAPI
from mcp.server.fastmcp import FastMCP

app = FastAPI()
mcp = FastMCP(app=app)

@mcp.tool()
def say_hi_world() -> str:
    return "Hi World from MCP!"

