import contextlib
from fastapi import FastAPI
from tools import mcp as tab_mcp
#from tools_new import mcp as tab_mcp_new

import os


# Create a combined lifespan to manage both session managers
# One session is added for now, but we can add more if needed.
@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    async with contextlib.AsyncExitStack() as stack:
        await stack.enter_async_context(tab_mcp.session_manager.run())
        #await stack.enter_async_context(new_mcp.session_manager.run())
        yield


app = FastAPI(lifespan=lifespan)
app.mount("/tab", tab_mcp.streamable_http_app())
#app.mount("/tab", new_mcp.streamable_http_app())

PORT = os.environ.get("PORT", 8000)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)
