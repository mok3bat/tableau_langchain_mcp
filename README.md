# Tableau LangChain MCP Server

A Model Context Protocol (MCP) server that provides tools for querying Tableau datasources using LangChain's tableau integration. This allows you to interact with your Tableau data through natural language queries via MCP-compatible clients.

## Features

- **Natural Language Queries**: Ask questions about your Tableau data in plain English
- **MCP Integration**: Works with any MCP-compatible client (Claude Desktop, etc.)
- **Secure Authentication**: Uses Tableau Connected Apps for secure JWT-based authentication
- **LangChain Integration**: Leverages the powerful langchain-tableau package

## Installation

### Prerequisites

1. Python 3.8 or higher
2. Access to a Tableau Server or Tableau Cloud instance
3. A Tableau Connected App configured with JWT authentication
4. OpenAI API key (for the LLM used by langchain-tableau)

### Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/mok3bat/tableau_langchain_mcp.git
   cd tableau_langchain_mcp
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

   Or install in development mode:
   ```bash
   pip install -e .
   ```

3. **Configure environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your Tableau and OpenAI credentials
   ```

4. **Set up Tableau Connected App**:
   - In Tableau Server/Cloud, create a new Connected App
   - Enable JWT authentication
   - Note down the Client ID, Secret ID, and Secret Value
   - Add these to your `.env` file

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `TABLEAU_DOMAIN` | Your Tableau server URL | Yes |
| `TABLEAU_SITE` | Tableau site name (content URL) | No |
| `TABLEAU_JWT_CLIENT_ID` | Connected App Client ID | Yes |
| `TABLEAU_JWT_SECRET_ID` | Connected App Secret ID | Yes |
| `TABLEAU_JWT_SECRET` | Connected App Secret Value | Yes |
| `TABLEAU_API_VERSION` | Tableau REST API version | No (default: 3.22) |
| `TABLEAU_USER` | Tableau username for queries | Yes |
| `TABLEAU_DATASOURCE_LUID` | Default datasource LUID | Yes |
| `OPENAI_API_KEY` | OpenAI API key | Yes |
| `TOOLING_LLM_MODEL` | LLM model for queries | No (default: gpt-4o-mini) |

### MCP Client Configuration

Add this to your MCP client configuration (e.g., Claude Desktop):

```json
{
  "mcpServers": {
    "tableau-langchain": {
      "command": "python",
      "args": ["/path/to/tableau_langchain_mcp/server.py"],
      "env": {
        "TABLEAU_DOMAIN": "https://your-tableau-server.com",
        "TABLEAU_SITE": "your-site-name",
        "TABLEAU_JWT_CLIENT_ID": "your-client-id",
        "TABLEAU_JWT_SECRET_ID": "your-secret-id",
        "TABLEAU_JWT_SECRET": "your-secret-value",
        "TABLEAU_USER": "your-user@example.com",
        "TABLEAU_DATASOURCE_LUID": "your-datasource-luid",
        "OPENAI_API_KEY": "your-openai-key"
      }
    }
  }
}
```

Or if you installed the package:

```json
{
  "mcpServers": {
    "tableau-langchain": {
      "command": "tableau-langchain-mcp",
      "env": {
        "TABLEAU_DOMAIN": "https://your-tableau-server.com",
        "TABLEAU_SITE": "your-site-name",
        "TABLEAU_JWT_CLIENT_ID": "your-client-id",
        "TABLEAU_JWT_SECRET_ID": "your-secret-id",
        "TABLEAU_JWT_SECRET": "your-secret-value",
        "TABLEAU_USER": "your-user@example.com",
        "TABLEAU_DATASOURCE_LUID": "your-datasource-luid",
        "OPENAI_API_KEY": "your-openai-key"
      }
    }
  }
}
```

## Usage

### Available Tools

1. **query_tableau_datasource**: Query a Tableau datasource with natural language
   - Input: `question` (string) - Your natural language question
   - Optional: `datasource_luid` (string) - Override default datasource

2. **list_tableau_datasources**: List available datasources (placeholder)

3. **get_datasource_info**: Get information about a specific datasource (placeholder)

### Example Queries

Once configured, you can ask questions like:

- "What are the top 5 sales regions by revenue?"
- "Show me the trend of profits over the last 12 months"
- "Which products have the highest profit margins?"
- "Compare sales performance between regions"

## Development

### Project Structure

```
tableau_langchain_mcp/
├── tableau_langchain_mcp/
│   ├── __init__.py
│   └── server.py
├── requirements.txt
├── pyproject.toml
├── .env.example
└── README.md
```

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black tableau_langchain_mcp/
isort tableau_langchain_mcp/
```

## Troubleshooting

### Common Issues

1. **"langchain-tableau not available"**
   - Install with: `pip install langchain-tableau`

2. **Authentication errors**
   - Verify your Connected App configuration
   - Ensure JWT secret values are correct
   - Check that the user has access to the datasource

3. **"No datasource LUID provided"**
   - Set `TABLEAU_DATASOURCE_LUID` in your environment
   - Or provide it as a parameter to the query tool

4. **OpenAI API errors**
   - Verify your `OPENAI_API_KEY` is correct
   - Ensure you have sufficient API credits

### Getting Help

- Check the [langchain-tableau documentation](https://github.com/Tab-SE/langchain-tableau)
- Review Tableau Connected Apps documentation
- Open an issue on this repository

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Acknowledgments

- [langchain-tableau](https://github.com/Tab-SE/langchain-tableau) for the Tableau integration
- [Model Context Protocol](https://modelcontextprotocol.io/) for the MCP specification
- [Anthropic](https://anthropic.com/) for the MCP tools and documentation
