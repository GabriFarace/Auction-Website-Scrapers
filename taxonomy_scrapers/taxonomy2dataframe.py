import pandas as pd
import json
import re


pattern = r"\(\d+\)"
number_at_end_pattern = r"\d+$"

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
        node['name'] = re.sub(pattern, '', re.sub(number_at_end_pattern,'' ,node["name"])).replace("\n", '').replace('""', '').lower()
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
        if "sub_categories" in node and isinstance(node["sub_categories"], list):
            rows.extend(flatten_taxonomy(node["sub_categories"], current_hierarchy))

    return rows


def taxonomy_to_dataframe(taxonomy_json, taxonomy_path):
    """
    Converts a taxonomy JSON structure into a pandas DataFrame.

    Args:
        taxonomy_json (list): The top-level array from the taxonomy JSON file.

    Returns:
        pandas.DataFrame: A DataFrame with columns `hierarchy`, `name`, and `description`.
    """
    rows = flatten_taxonomy(taxonomy_json)
    print(f"The number of elements for the {taxonomy_path} is : {len(rows)}")
    return pd.DataFrame(rows)


def convert_taxonomy(taxonomy_json_path):

    # Load the taxonomy JSON
    with open(taxonomy_json_path, 'r') as f:
        taxonomy_json = json.load(f)

    # Convert to DataFrame
    taxonomy_df = taxonomy_to_dataframe(taxonomy_json[1:-1], taxonomy_json_path)

    # Save to CSV (if needed)
    taxonomy_df.to_csv(taxonomy_json_path.split(".")[0] + ".csv", index=False)

if __name__ == "__main__":
    convert_taxonomy("UNSPSC_taxonomy/taxonomy.json")
    '''convert_taxonomy("surplex_taxonomy/taxonomy.json")
    convert_taxonomy("ritchie_bros_taxonomy/taxonomy.json")
    convert_taxonomy("plant_and_equipment_taxonomy/taxonomy.json")
    convert_taxonomy("machinio_taxonomy/taxonomy.json")
    convert_taxonomy("machinery_zone_taxonomy/taxonomy.json")
    convert_taxonomy("machinery_trader_taxonomy/taxonomy.json")
    convert_taxonomy("machinery_trader_taxonomy/tractor_house_taxonomy/taxonomy.json")
    convert_taxonomy("machinery_marketplace_taxonomy/taxonomy.json")
    convert_taxonomy("gov_deals_taxonomy/taxonomy.json")
    convert_taxonomy("exapro_taxonomy/taxonomy.json")
    convert_taxonomy("bid_on_equipment_taxonomy/taxonomy.json")'''