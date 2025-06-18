#!/usr/bin/env python3
"""
Setup script for development and testing purposes.
For production installation, use pyproject.toml with pip install.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="tableau-langchain-mcp",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="MCP Server for Tableau LangChain integration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mok3bat/tableau_langchain_mcp",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "mcp>=1.0.0",
        "httpx>=0.25.0",
        "langchain-tableau>=0.1.0",
        "langchain-openai>=0.1.0",
        "python-dotenv>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "mypy>=1.5.0",
            "pre-commit>=3.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "tableau-langchain-mcp=tableau_langchain_mcp.server:main",
        ],
    },
)
