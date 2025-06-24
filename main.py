from mcp.server.fastmcp import FastMCP
from fastapi import FastAPI

headers= {"Accept": "application/json, text/event-stream"}
mcp = FastMCP("strava", stateless_http=True, headers=headers, host="0.0.0.0", port=8000)

@mcp.tool()
def get_activities():
    print('hello')
    return {
        "content": [
            { "type": "text", "text": "✅ Hello from deployed MCP!" }
        ]
    }


app = FastAPI(title="Strava")
app.mount("/mcp")

if __name__ == "__main__":
    mcp.run(transport='streamable-http')