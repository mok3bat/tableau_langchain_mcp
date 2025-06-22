# tools.py (with async version)

import os
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta, timezone
from utils.auth import jwt_connected_app
from utils.metadata import get_data_dictionary
from utils.vizql_data_service import query_vds, query_vds_metadata
from utils.simple_datasource_qa import (
    get_headlessbi_data,
    get_values,
    augment_datasource_metadata
)
from mcp.server.fastmcp import FastMCP
import json

mcp = FastMCP(cors=True)  # FastMCP instance to register 
app = mcp._app  # <-- temporarily using internal _app if available

class EnvManager:
    @staticmethod
    def get(key: str) -> str:
        """
        Get an environment variable, or raise an error if missing.
        
        Args:
            key (str): The name of the environment variable.
        
        Returns:
            str: The value of the environment variable.
        
        Raises:
            ValueError: If the variable is not found.
        """
        val = os.getenv(key)
        if val is None:
            raise ValueError(f"Missing environment variable: {key}")
        return val

    @staticmethod
    def get_list(key: str) -> list[str]:
        val = EnvManager.get(key)
        try:
            # Try to parse as JSON list
            parsed = json.loads(val)
            if isinstance(parsed, list):
                return parsed
        except json.JSONDecodeError:
            pass

        # Fallback to comma-separated string
        return [item.strip() for item in val.split(",")]

class TokenManager:
    _token: Optional[str] = None
    _expiry: Optional[datetime] = None

    @classmethod
    def get_token(cls) -> Optional[str]:
        if cls._token and cls._expiry and cls._expiry > datetime.now(timezone.utc) + timedelta(minutes=3):
            return cls._token # Valid for more than 3 minutes
        return None

    @classmethod
    def set_token(cls, token: str, expires_in_minutes: int = 120):
        cls._token = token
        cls._expiry = datetime.now(timezone.utc) + timedelta(minutes=expires_in_minutes)

    @classmethod
    def get_or_refresh(cls) -> str:
        token = cls.get_token()
        if token:
            print("[Auth] Using cached token.")
            return token

        print("[Auth] Token missing or expiring soon. Re-authenticating...")
        auth_response = tableau_auth_tool()
        token = auth_response["credentials"]["token"]
        cls.set_token(token, expires_in_minutes=120)
        return token


@mcp.tool()
def say_hi_world() -> str:
    """
    Returns a simple greeting.
    """
    return "Hi World! MCP is working."

# As we added Token Manager class, we can remove auth tool as it will be called from the get_data_dictionary_tool.
#@mcp.tool()
def tableau_auth_tool() -> Dict[str, Any]:
    """
    Authenticates to Tableau using JWT credentials from environment variables.
    """

    scopes = EnvManager.get_list("JWT_SCOPES")
    return jwt_connected_app(
        tableau_domain=EnvManager.get("TABLEAU_DOMAIN"),
        tableau_site=EnvManager.get("TABLEAU_SITE"),
        tableau_api=EnvManager.get("TABLEAU_API"),
        tableau_user=EnvManager.get("TABLEAU_USER"),
        jwt_client_id=EnvManager.get("TABLEAU_JWT_CLIENT_ID"),
        jwt_secret_id=EnvManager.get("TABLEAU_JWT_SECRET_ID"),
        jwt_secret=EnvManager.get("TABLEAU_JWT_SECRET"),
        scopes=scopes
    )


@mcp.tool()
def get_data_dictionary_tool(datasource_luid: str) -> Dict[str, Any]:
    """
    Queries Tableau's Metadata API to get a data dictionary of a published datasource.

    Args:
        datasource_luid (str): LUID of the Tableau published datasource

    Returns:
        Dict[str, Any]: Dictionary with datasource name, description, owner, and visible fields.
    """

    #Checks token cache and uses it if valid. Otherwise re-authenticates to get a fresh token.
    token = TokenManager.get_or_refresh()
    tableau_domain=EnvManager.get("TABLEAU_DOMAIN")

    return get_data_dictionary(api_key=token, domain=tableau_domain, datasource_luid=datasource_luid)

@mcp.tool()
def query_vds_metadata_tool(datasource_luid: str) -> Dict[str, Any]:
    """
    Authenticates with Tableau and retrieves metadata from VizQL Data Service for the given datasource.

    Args:
        datasource_luid (str): LUID of the Tableau datasource

    Returns:
        Dict[str, Any]: Metadata response from VDS
    """
    token = TokenManager.get_or_refresh()
    domain = EnvManager.get("TABLEAU_DOMAIN")

    return query_vds_metadata(api_key=token, datasource_luid=datasource_luid, url=domain)

@mcp.tool()
def query_vds_tool(datasource_luid: str, query: Dict[str, Any]) -> Dict[str, Any]:
    """
    Authenticates with Tableau and runs a data query via VizQL Data Service.

    Args:
        datasource_luid (str): LUID of the Tableau datasource
        query (Dict): The query to run against the datasource

    Returns:
        Dict[str, Any]: Query result
    """
    token = TokenManager.get_or_refresh()
    domain = EnvManager.get("TABLEAU_DOMAIN")

    return query_vds(api_key=token, datasource_luid=datasource_luid, url=domain, query=query)

@mcp.tool()
def get_headlessbi_data_tool(payload: Dict[str, Any], datasource_luid: str) -> str:
    """
    Queries Tableau using a JSON string payload and returns results as markdown.

    Args:
        payload (str): A JSON-formatted string containing the query.
        datasource_luid (str): The LUID of the Tableau datasource.

    Returns:
        str: Markdown table of query results.
    """
    token = TokenManager.get_or_refresh()
    domain = EnvManager.get("TABLEAU_DOMAIN")
    return get_headlessbi_data(payload=payload, url=domain, api_key=token, datasource_luid=datasource_luid)

@mcp.tool()
def get_values_tool(datasource_luid: str, caption: str) -> list:
    """
    Retrieves sample values (max 4) for a given field caption from a datasource.

    Args:
        datasource_luid (str): The LUID of the datasource.
        caption (str): The field caption (label) to look up.

    Returns:
        list: Up to 4 sample values.
    """
    token = TokenManager.get_or_refresh()
    domain = EnvManager.get("TABLEAU_DOMAIN")
    return get_values(api_key=token, url=domain, datasource_luid=datasource_luid, caption=caption)

@mcp.tool()
def augment_datasource_metadata_tool(
    task: str,
    datasource_luid: str,
    prompt: Dict[str, Any],
    previous_errors: Optional[str] = None,
    previous_vds_payload: Optional[str] = None
) -> Dict[str, Any]:
    """
    Gathers all metadata and augments it into a prompt dictionary.

    Args:
        task (str): Task description to be inserted.
        datasource_luid (str): Tableau datasource LUID.
        prompt (Dict[str, str]): Initial prompt to be augmented.
        previous_errors (Optional[str]): Previous error message.
        previous_vds_payload (Optional[str]): Previous failed VDS query (JSON).

    Returns:
        Dict[str, Any]: Prompt with metadata, dictionary, and optional debug info.
    """
    token = TokenManager.get_or_refresh()
    domain = EnvManager.get("TABLEAU_DOMAIN")
    return augment_datasource_metadata(
        task=task,
        api_key=token,
        url=domain,
        datasource_luid=datasource_luid,
        prompt=prompt,
        previous_errors=previous_errors,
        previous_vds_payload=previous_vds_payload
    )
