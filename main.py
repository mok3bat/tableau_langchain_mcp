# main.py

import os
from tools import mcp  # This now works correctly because it's one-way
#

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))  # Railway sets this dynamically
    mcp.run(host="0.0.0.0", port=port)
