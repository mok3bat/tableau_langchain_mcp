"""
Tableau LangChain MCP Server

A Model Context Protocol (MCP) server that provides tools for querying
Tableau datasources using LangChain's tableau integration.
"""

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .server import TableauMCPServer, main

__all__ = ["TableauMCPServer", "main"]
