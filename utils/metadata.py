import json
import requests
from typing import Dict, Any
from utils.utils import http_post


def get_datasources_query():
    query = f"""
    query Datasources {{
      publishedDatasources {{
        name
        description
        luid
      }}
    }}
    """

    return query

def get_datasource_query(luid):
    query = f"""
    query Datasources {{
      publishedDatasources(filter: {{ luid: "{luid}" }}) {{
        name
        description
        owner {{
          name
        }}
        fields {{
          name
          description
          isHidden
        }}
      }}
    }}
    """

    return query


async def get_data_dictionary_async(api_key: str, domain: str, datasource_luid: str) -> Dict[str, Any]:
    """
    Asynchronously queries the Tableau Metadata API to get a data dictionary for the specified datasource.

    Args:
        api_key (str): The API key for authentication.
        domain (str): The Tableau domain.
        datasource_luid (str): The LUID of the Tableau datasource.

    Returns:
        Dict[str, Any]: The data dictionary from the metadata API.
    """
    full_url = f"{domain}/api/metadata/graphql"
    query = get_datasource_query(datasource_luid)

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'X-Tableau-Auth': api_key
    }
    print("Request Headers:", headers)

    payload = { "query": query }
    response = await http_post(endpoint=full_url, headers=headers, payload=payload)
    if response['status'] == 200:
        return response['data']
    else:
        error_message = (
            f"Failed to query metadata API. "
            f"Status code: {response['status']}. Response: {response['data']}"
        )
        raise RuntimeError(error_message)

def get_datasources(api_key: str, domain: str) -> Dict[str, Any]:
    """
    Queries the Tableau Metadata API to get a data dictionary for the datasources' luid.
    Args:
        api_key (str): The API key for authentication.
        domain (str): The Tableau domain.
    Returns:
        Dict[str, Any]: The data dictionary from the metadata API.
    """

    full_url = f"{domain}/api/metadata/graphql"
    query = get_datasources_query()

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'X-Tableau-Auth': api_key
    }
    print("Request Headers:", headers)

    payload = { "query": query }
    response = requests.post(full_url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()

def get_data_dictionary(api_key: str, domain: str, datasource_luid: str) -> Dict[str, Any]:
    """
    Queries the Tableau Metadata API to get a data dictionary for the specified datasource.
    Args:
        api_key (str): The API key for authentication.
        domain (str): The Tableau domain.
        datasource_luid (str): The LUID of the Tableau datasource.
    Returns:
        Dict[str, Any]: The data dictionary from the metadata API.
    """

    full_url = f"{domain}/api/metadata/graphql"
    query = get_datasource_query(datasource_luid)

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'X-Tableau-Auth': api_key
    }
    print("Request Headers:", headers)

    payload = { "query": query }
    response = requests.post(full_url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()