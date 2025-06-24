from mcp.server.fastmcp import FastMCP
from fastapi import FastAPI

headers= {"Accept": "application/json, text/event-stream"}
mcp = FastMCP("strava", stateless_http=True, headers=headers, host="127.0.0.1", port=8000)

@mcp.tool()
def get_activities():
    print('hello')
    return "hello from MCP!"


app = FastAPI(title="Strava", lifespan=lambda app: mcp.session_manager.run())
app.mount("/mcp", mcp.streamable_http_app())

if __name__ == "__main__":
    mcp.run(transport='streamable-http')