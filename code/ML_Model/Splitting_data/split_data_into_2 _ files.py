import pandas as pd

def split_csv_sheet(input_file, output_prefix, part1_ratio=0.8, part2_ratio=0.2):

    # Reading files from csv
    try:
        df = pd.read_csv(input_file)
        print(f"Successfully read {input_file} with {len(df)} rows.")
    except FileNotFoundError:
        print(f"Error: The file '{input_file}' was not found.")
        return

    # Shuffle the DataFrame to ensure random distribution of rows
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)

    # Calculate the number of rows for each part
    total_rows = len(df)
    part1_rows = int(total_rows * part1_ratio)
    
    # The last part gets the remaining rows to ensure no data is lost
    part2_rows = total_rows - part1_rows

    print(f"Splitting into {part1_rows} rows (Part 1) and {part2_rows} rows (Part 2).")

    # Split the Data
    df_part1 = df.iloc[:part1_rows]
    df_part2 = df.iloc[part1_rows:]

    # Save the files
    try:
        df_part1.to_csv(f"{output_prefix}_part1.csv", index=False)
        df_part2.to_csv(f"{output_prefix}_part2.csv", index=False)
        print("Successfully saved the two parts.")
    except Exception as e:
        print(f"An error occurred while saving the files: {e}")


input_file_name = r"C:\Users\Lenovo\classified_candidates.csv"
output_file_prefix = 'split_data'

# Main Fuction
split_csv_sheet(input_file_name, output_file_prefix)