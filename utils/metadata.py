import json
import requests
from typing import Dict, Any
from utils.utils import http_post


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

# x = get_data_dictionary(api_key="xD-yuOXXQny3biaejIfVXg|d4DfllIyheVESOWZjBGQ9jSxZf4lFQ9L|10e58210-4b4b-4dbf-9212-6a56bca56d8f", domain="https://10ax.online.tableau.com", datasource_luid="5ae17e46-6da8-48ce-91f8-bfc7f0507f0d")
#print(x)