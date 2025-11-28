import pandas as pd
"""
    Class used to remove duplicates from the occupations.csv file.
    The duplicates are identified based on the 'uri' column.
    The cleaned file is saved as occupations_cleaned.csv with headers.
"""
def clean_occupations_csv(input_file, output_file):
    # 1. Define column names in the correct order
    column_names = [
        'occupation',
        'uri',
        'description',
        'essential_skills',
        'essential_knowledge',
        'optional_skills',
        'optional_knowledge'
    ]

    print(f"Reading file {input_file}...")

    # 2. Read the CSV without a header (because the current file doesn't have one)
    try:
        df = pd.read_csv(input_file, header=None, names=column_names)
    except FileNotFoundError:
        print(f"Error: The file '{input_file}' was not found.")
        return

    original_count = len(df)
    print(f"Total rows read: {original_count}")

    # 3. Remove duplicates based on the 'uri' column
    # keep='first' keeps the first occurrence and drops subsequent ones
    df_cleaned = df.drop_duplicates(subset=['uri'], keep='first')

    final_count = len(df_cleaned)
    duplicates_removed = original_count - final_count

    print(f"Duplicates removed: {duplicates_removed}")
    print(f"Unique rows remaining: {final_count}")

    # 4. Save the new cleaned file with headers
    print(f"Saving cleaned file to {output_file}...")
    df_cleaned.to_csv(output_file, index=False)
    print("Done! The file is ready.")


# Execute cleanup
if __name__ == "__main__":
    clean_occupations_csv('occupations.csv', 'occupations_cleaned.csv')