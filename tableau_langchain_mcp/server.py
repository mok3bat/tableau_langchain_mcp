#!/usr/bin/env python3
"""
Tableau LangChain MCP Server

This server provides MCP (Model Context Protocol) tools for querying Tableau datasources
using LangChain's tableau integration.
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Sequence
import os
from contextlib import asynccontextmanager

import httpx
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
)

# LangChain imports
try:
    from langchain_tableau.tools.simple_datasource_qa import initialize_simple_datasource_qa
    from langchain_openai import ChatOpenAI
    LANGCHAIN_TABLEAU_AVAILABLE = True
except ImportError:
    LANGCHAIN_TABLEAU_AVAILABLE = False
    logging.warning("langchain-tableau not available. Install with: pip install langchain-tableau")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TableauMCPServer:
    """MCP Server for Tableau LangChain integration"""
    
    def __init__(self):
        self.server = Server("tableau-langchain")
        self.tableau_config = self._load_tableau_config()
        self.analyze_datasource_tool = None
        
        # Register handlers
        self._register_handlers()
        
    def _load_tableau_config(self) -> Dict[str, Any]:
        """Load Tableau configuration from environment variables"""
        return {
            "domain": os.getenv("TABLEAU_DOMAIN"),
            "site": os.getenv("TABLEAU_SITE", ""),
            "jwt_client_id": os.getenv("TABLEAU_JWT_CLIENT_ID"),
            "jwt_secret_id": os.getenv("TABLEAU_JWT_SECRET_ID"),
            "jwt_secret": os.getenv("TABLEAU_JWT_SECRET"),
            "api_version": os.getenv("TABLEAU_API_VERSION", "3.22"),
            "user": os.getenv("TABLEAU_USER"),
            "datasource_luid": os.getenv("TABLEAU_DATASOURCE_LUID"),
            "tooling_llm_model": os.getenv("TOOLING_LLM_MODEL", "gpt-4o-mini"),
            "openai_api_key": os.getenv("OPENAI_API_KEY")
        }
    
    def _register_handlers(self):
        """Register all MCP handlers"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            """List available tools"""
            return [
                Tool(
                    name="query_tableau_datasource",
                    description="Query a Tableau Published Datasource using natural language",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "question": {
                                "type": "string",
                                "description": "Natural language question to ask about the data"
                            },
                            "datasource_luid": {
                                "type": "string",
                                "description": "Optional: Override the default datasource LUID",
                                "default": self.tableau_config.get("datasource_luid", "")
                            }
                        },
                        "required": ["question"]
                    }
                ),
                Tool(
                    name="list_tableau_datasources",
                    description="List available Tableau datasources in the configured site",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                ),
                Tool(
                    name="get_datasource_info",
                    description="Get detailed information about a specific Tableau datasource",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "datasource_luid": {
                                "type": "string",
                                "description": "The LUID of the datasource to get information about"
                            }
                        },
                        "required": ["datasource_luid"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Handle tool calls"""
            
            if name == "query_tableau_datasource":
                return await self._query_tableau_datasource(arguments)
            elif name == "list_tableau_datasources":
                return await self._list_tableau_datasources(arguments)
            elif name == "get_datasource_info":
                return await self._get_datasource_info(arguments)
            else:
                return [TextContent(
                    type="text",
                    text=f"Unknown tool: {name}"
                )]
        
        @self.server.list_resources()
        async def handle_list_resources() -> List[Resource]:
            """List available resources"""
            return [
                Resource(
                    uri="tableau://config",
                    name="Tableau Configuration",
                    description="Current Tableau server configuration",
                    mimeType="application/json"
                )
            ]
        
        @self.server.read_resource()
        async def handle_read_resource(uri: str) -> str:
            """Read a resource"""
            if uri == "tableau://config":
                # Return config without sensitive information
                safe_config = {k: v for k, v in self.tableau_config.items() 
                             if k not in ["jwt_secret", "openai_api_key"]}
                return json.dumps(safe_config, indent=2)
            else:
                raise ValueError(f"Unknown resource: {uri}")
    
    async def _initialize_tableau_tool(self, datasource_luid: Optional[str] = None):
        """Initialize the Tableau datasource query tool"""
        if not LANGCHAIN_TABLEAU_AVAILABLE:
            raise ValueError("langchain-tableau is not installed")
        
        # Validate required configuration
        required_fields = ["domain", "jwt_client_id", "jwt_secret_id", "jwt_secret", "user"]
        missing_fields = [field for field in required_fields if not self.tableau_config.get(field)]
        
        if missing_fields:
            raise ValueError(f"Missing required Tableau configuration: {', '.join(missing_fields)}")
        
        if not self.tableau_config.get("openai_api_key"):
            raise ValueError("OpenAI API key is required for the LLM")
        
        # Use provided datasource_luid or fall back to configured one
        target_datasource_luid = datasource_luid or self.tableau_config.get("datasource_luid")
        if not target_datasource_luid:
            raise ValueError("No datasource LUID provided or configured")
        
        try:
            # Initialize the Tableau tool
            self.analyze_datasource_tool = initialize_simple_datasource_qa(
                domain=self.tableau_config["domain"],
                site=self.tableau_config["site"],
                jwt_client_id=self.tableau_config["jwt_client_id"],
                jwt_secret_id=self.tableau_config["jwt_secret_id"],
                jwt_secret=self.tableau_config["jwt_secret"],
                tableau_api_version=self.tableau_config["api_version"],
                tableau_user=self.tableau_config["user"],
                datasource_luid=target_datasource_luid,
                tooling_llm_model=self.tableau_config["tooling_llm_model"]
            )
            logger.info(f"Initialized Tableau tool for datasource {target_datasource_luid}")
        except Exception as e:
            logger.error(f"Failed to initialize Tableau tool: {str(e)}")
            raise
    
    async def _query_tableau_datasource(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Query a Tableau datasource with natural language"""
        question = arguments.get("question")
        datasource_luid = arguments.get("datasource_luid")
        
        if not question:
            return [TextContent(type="text", text="No question provided")]
        
        try:
            # Initialize or reinitialize the tool if needed
            if (not self.analyze_datasource_tool or 
                (datasource_luid and datasource_luid != self.tableau_config.get("datasource_luid"))):
                await self._initialize_tableau_tool(datasource_luid)
            
            # Execute the query
            result = await asyncio.get_event_loop().run_in_executor(
                None, self.analyze_datasource_tool.invoke, {"input": question}
            )
            
            return [TextContent(
                type="text",
                text=f"Query: {question}\n\nAnswer: {result}"
            )]
            
        except Exception as e:
            logger.error(f"Error querying Tableau datasource: {str(e)}")
            return [TextContent(
                type="text",
                text=f"Error querying Tableau datasource: {str(e)}"
            )]
    
    async def _list_tableau_datasources(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """List available Tableau datasources"""
        try:
            # This would require direct Tableau REST API calls
            # For now, return a placeholder implementation
            return [TextContent(
                type="text",
                text="Listing Tableau datasources requires additional REST API implementation. "
                     "Currently configured datasource LUID: " + 
                     str(self.tableau_config.get("datasource_luid", "Not configured"))
            )]
        except Exception as e:
            logger.error(f"Error listing Tableau datasources: {str(e)}")
            return [TextContent(
                type="text",
                text=f"Error listing Tableau datasources: {str(e)}"
            )]
    
    async def _get_datasource_info(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Get information about a specific Tableau datasource"""
        datasource_luid = arguments.get("datasource_luid")
        
        if not datasource_luid:
            return [TextContent(type="text", text="No datasource LUID provided")]
        
        try:
            # This would require direct Tableau REST API calls
            # For now, return a placeholder implementation
            return [TextContent(
                type="text",
                text=f"Getting info for datasource {datasource_luid} requires additional REST API implementation."
            )]
        except Exception as e:
            logger.error(f"Error getting datasource info: {str(e)}")
            return [TextContent(
                type="text",
                text=f"Error getting datasource info: {str(e)}"
            )]

    async def run(self):
        """Run the MCP server"""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream, 
                write_stream, 
                InitializationOptions(
                    server_name="tableau-langchain",
                    server_version="1.0.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=None,
                        experimental_capabilities=None
                    )
                )
            )

async def main():
    """Main entry point"""
    server = TableauMCPServer()
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())
