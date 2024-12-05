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
























'''
    # Load the workbook for grouping and formatting
    workbook = load_workbook(excel_filename)
    sheet = workbook.active

    # Programmatically group rows based on hierarchy depth
    def build_group(rows_list, base, depth):
        if depth == 5:
            return
        check = False
        current_ind = 0
        row_ind = 1
        for i, row in enumerate(rows_list):
            row_ind = base + i
            if row[depth + 1] == '':# Check for the first non-empty level in the hierarchy
                if check:
                    if not row_ind == current_ind + 1:
                        sheet.row_dimensions.group(start=current_ind + 1 + 1, end=row_ind - 1 + 1, outline_level=depth)
                        build_group(rows_list[current_ind + 1 : row_ind], current_ind + 1, depth + 1)
                    current_ind = row_ind
                else:
                    check = True
                    current_ind = row_ind
        if check:
            if not row_ind == current_ind:
                sheet.row_dimensions.group(start=current_ind + 1 + 1, end=row_ind + 1, outline_level=depth)

    rows_as_list = df.values.tolist()
    build_group(rows_as_list, 0, 1)
    # Auto-resize columns to fit content
    for col in sheet.columns:
        max_length = 0
        col_letter = col[0].column_letter  # Get the column letter
        for cell in col:
            try:
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))
            except:
                pass
        adjusted_width = max_length + 2
        sheet.column_dimensions[col_letter].width = adjusted_width

    # Save the final grouped and formatted Excel file
    final_excel_filename = name
    workbook.save(final_excel_filename)

    print(f"Excel file created and saved as '{final_excel_filename}'.")
'''