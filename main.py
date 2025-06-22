from fastapi import FastAPI
from mcp.server.fastmcp import FastMCP

app = FastAPI()
mcp = FastMCP(app=app)

@mcp.tool()
def say_hi_world() -> str:
    return "Hi World from MCP!"

@app.get("/")
async def root():
    return {"message": "Hello World"}

# ✅ Used only for local testing
if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)