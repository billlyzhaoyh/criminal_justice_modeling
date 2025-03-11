"""Process tables aiming to work with overview-tables-September-2024.ods as the latest published version in Mar 2025"""

import json
import os

import pandas as pd

OUTPUT_DIR = "./data/cjsq/processed"
# Ensure the output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)


def extract_meta_data_from_contents(ods_file):
    # Extract meta data from contents sheet
    contents_sheet = pd.read_excel(ods_file, sheet_name="Contents", engine="odf")
    # Extract the mapping between sheet names and their descriptions
    mapping = dict(
        zip(
            contents_sheet.iloc[3:, 0].str.strip().str.lower(),
            contents_sheet.iloc[3:, 1],
        )
    )
    return mapping


def extract_all_relevant_tabs_as_csv(ods_file):
    # Read all sheets from the ODS file using the odf engine
    sheets = pd.read_excel(ods_file, sheet_name=None, engine="odf")

    output_dir_for_file = os.path.join(
        OUTPUT_DIR, os.path.basename(ods_file).split(".")[0]
    )
    os.makedirs(output_dir_for_file, exist_ok=True)

    # Define sheet names to exclude (case-insensitive)
    exclude_sheets = {"cover", "contents", "notes"}

    # Process each sheet
    saved_files = []
    for sheet_name, df in sheets.items():
        # Skip sheets that are in the exclusion list (ignoring case and whitespace)
        if sheet_name.strip().lower() in exclude_sheets:
            continue

        # Attempt to find a valid header row by checking row indices 3 (4th row) and 4 (5th row)
        header_row = None
        for i in [2, 3, 4]:
            if (
                i < len(df) and df.iloc[i].notna().sum() > 2
            ):  # Ensure enough valid entries
                header_row = i
                break

        if header_row is None:
            print(
                f"Could not determine a header row for sheet: {sheet_name}. Skipping this sheet."
            )
            continue

        # Set the discovered header row as the columns and drop rows before and including it
        df.columns = df.iloc[header_row]
        df = df.iloc[header_row + 1 :].reset_index(drop=True)

        # Generate a safe filename from the sheet name and save the CSV
        safe_sheet_name = sheet_name.replace(" ", "_").lower()
        csv_path = os.path.join(output_dir_for_file, f"{safe_sheet_name}.csv")
        df.to_csv(csv_path, index=False)
        saved_files.append(csv_path)
    return saved_files


if __name__ == "__main__":
    ods_file_path = "./data/cjsq/raw/overview-tables-September-2024.ods"
    meta_data = extract_meta_data_from_contents(ods_file_path)
    saved_files = extract_all_relevant_tabs_as_csv(ods_file_path)
    # mesh the two together
    file_explaination_dict = dict()
    for file in saved_files:
        sheet_name = os.path.basename(file).split(".")[0]
        file_explaination_dict[file] = meta_data[sheet_name]
    output_dir_for_file = os.path.join(
        OUTPUT_DIR, os.path.basename(ods_file_path).split(".")[0]
    )
    with open(os.path.join(output_dir_for_file, "file_explaination.json"), "w") as f:
        f.write(json.dumps(file_explaination_dict, indent=4))
