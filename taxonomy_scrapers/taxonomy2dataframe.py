import pandas as pd
import json


def flatten_taxonomy(taxonomy, parent_hierarchy=""):
    """
    Recursively flattens the taxonomy into a list of rows for the DataFrame.

    Args:
        taxonomy (list): A list of category nodes (JSON structure).
        parent_hierarchy (str): The hierarchy of parent nodes up to this point.

    Returns:
        list: A list of rows, where each row is a dictionary with `hierarchy`, `name`, and `description`.
    """
    rows = []
    for node in taxonomy:
        # Build the current node's hierarchy
        current_hierarchy = f"{parent_hierarchy} > {node['name']}".strip(" > ")

        # Add the current node as a row
        rows.append({
            "hierarchy": current_hierarchy,
            "name": node["name"],
            "description": ""  # Initially empty
        })

        # Recursively process subcategories, if they exist
        if "subcategories" in node and isinstance(node["subcategories"], list):
            rows.extend(flatten_taxonomy(node["subcategories"], current_hierarchy))

    return rows


def taxonomy_to_dataframe(taxonomy_json):
    """
    Converts a taxonomy JSON structure into a pandas DataFrame.

    Args:
        taxonomy_json (list): The top-level array from the taxonomy JSON file.

    Returns:
        pandas.DataFrame: A DataFrame with columns `hierarchy`, `name`, and `description`.
    """
    rows = flatten_taxonomy(taxonomy_json)
    return pd.DataFrame(rows)

if __name__ == "__main__":
    # Example usage
    taxonomy_json_path = 'surplex_taxonomy/taxonomy.json'  # Path to your taxonomy JSON file

    # Load the taxonomy JSON
    with open(taxonomy_json_path, 'r') as f:
        taxonomy_json = json.load(f)

    # Convert to DataFrame
    taxonomy_df = taxonomy_to_dataframe(taxonomy_json)

    # Display the DataFrame
    taxonomy_df.head(20)

    # Save to CSV (if needed)
    taxonomy_df.to_csv("flattened_taxonomy.csv", index=False)
