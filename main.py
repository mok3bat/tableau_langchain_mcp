# main.py

from dotenv import load_dotenv
from tools import mcp  # This now works correctly because it's one-way

load_dotenv()

if __name__ == "__main__":
    mcp.run()
