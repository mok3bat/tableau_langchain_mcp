import os
import json
import re
import logging
from typing import Any, Dict, Optional
from dotenv import load_dotenv

from utils.vizql_data_service import query_vds, query_vds_metadata
from utils.utils import json_to_markdown_table
from utils.metadata import get_data_dictionary


def get_headlessbi_data(payload: Dict[str, Any], url: str, api_key: str, datasource_luid: str) -> str:
    
    try:
        headlessbi_data = query_vds(
            api_key=api_key,
            datasource_luid=datasource_luid,
            url=url,
            query=payload  # Already a parsed dict
        )

        if not headlessbi_data or 'data' not in headlessbi_data:
            raise ValueError("Invalid or empty response from query_vds")

        markdown_table = json_to_markdown_table(headlessbi_data['data'])
        return markdown_table

    except ValueError as ve:
        logging.error(f"Value error in get_headlessbi_data: {str(ve)}")
        raise

    except Exception as e:
        logging.error(f"Unexpected error in get_headlessbi_data: {str(e)}")
        raise RuntimeError(f"An unexpected error occurred: {str(e)}")


def get_payload(output):
    try:
        parsed_output = output.split('JSON_payload')[1]
    except IndexError:
        raise ValueError("'JSON_payload' not found in the output")

    match = re.search(r'{.*}', parsed_output, re.DOTALL)
    if match:
        json_string = match.group(0)
        try:
            payload = json.loads(json_string)
            return payload
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON format in the payload")
    else:
        raise ValueError("No JSON payload found in the parsed output")


def get_values(api_key: str, url: str, datasource_luid: str, caption: str):
    column_values = {'fields': [{'fieldCaption': caption}]}
    output = query_vds(
        api_key=api_key,
        datasource_luid=datasource_luid,
        url=url,
        query=column_values
    )
    if output is None:
        return None
    sample_values = [list(item.values())[0] for item in output['data']][:4]
    return sample_values


def augment_datasource_metadata(
    task: str,
    api_key: str,
    url: str,
    datasource_luid: str,
    prompt: Dict[str, Any],
    previous_errors: Optional[str] = None,
    previous_vds_payload: Optional[str] = None
):
    """
    Augment datasource metadata with additional information and format as JSON.

    This function retrieves the data dictionary and sample field values for a given
    datasource, adds them to the provided prompt dictionary, and includes any previous
    errors or queries for debugging purposes.

    Args:
        api_key (str): The API key for authentication.
        url (str): The base URL for the API endpoints.
        datasource_luid (str): The unique identifier of the datasource.
        prompt (Dict[str, str]): Initial prompt dictionary to be augmented.
        previous_errors (Optional[str]): Any errors from previous function calls. Defaults to None.
        previous_vds_payload (Optional[str]): The query that caused errors in previous calls. Defaults to None.

    Returns:
        str: A JSON string containing the augmented prompt dictionary with datasource metadata.

    Note:
        This function relies on external functions `get_data_dictionary` and `query_vds_metadata`
        to retrieve the necessary datasource information.
    """
    # insert the user input as a task
    prompt['task'] = task

    # get dictionary for the data source from the Metadata API
    data_dictionary = get_data_dictionary(
        api_key=api_key,
        domain=url,
        datasource_luid=datasource_luid
    )

    # Step 1: Extract fields
    try:
        published = data_dictionary["data"]["publishedDatasources"]
        if not published:
            raise ValueError("No published datasources found")

        fields = published[0].get("fields", [])
        # insert data dictionary from Tableau's Data Catalog
        prompt['data_dictionary'] = fields

        # Step 2: Remove 'fields' key from the original dictionary
        published[0].pop("fields", None)
        # insert data source name, description and owner into 'meta' key
        prompt['meta'] = data_dictionary

    except (KeyError, IndexError, TypeError) as e:
        raise ValueError("Failed to extract and clean up fields from data_dictionary") from e 

    #  get sample values for fields from VDS metadata endpoint
    datasource_metadata = query_vds_metadata(
        api_key=api_key,
        url=url,
        datasource_luid=datasource_luid
    )

    for field in datasource_metadata['data']:
        del field['fieldName']
        del field['logicalTableId']

    # insert the data model with sample values from Tableau's VDS metadata API
    prompt['data_model'] = datasource_metadata['data']

    # include previous error and query to debug in current run
    if previous_errors:
        prompt['previous_call_error'] = previous_errors
    if previous_vds_payload:
        prompt['previous_vds_payload'] = previous_vds_payload

    return prompt


def prepare_prompt_inputs(data: dict, user_string: str) -> dict:
    """
    Prepare inputs for the prompt template with explicit, safe mapping.

    Args:
        data (dict): Raw data from VizQL query
        user_input (str): Original user query

    Returns:
        dict: Mapped inputs for PromptTemplate
    """

    return {
        "vds_query": data.get('query', 'no query'),
        "data_source_name": data.get('data_source_name', 'no name'),
        "data_source_description": data.get('data_source_description', 'no description'),
        "data_source_maintainer": data.get('data_source_maintainer', 'no maintainer'),
        "data_table": data.get('data_table', 'no data'),
        "user_input": user_string
    }
