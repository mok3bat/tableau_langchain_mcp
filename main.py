# main.py

import os
import uvicorn
import tools  # ✅ Must import tools to run @mcp.tool decorators

# Use the app and activate the tool bindings
app = tools.app
tools.activate_tools()  # ✅ You must call this to bind the routes

# Run using Railway's PORT
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
