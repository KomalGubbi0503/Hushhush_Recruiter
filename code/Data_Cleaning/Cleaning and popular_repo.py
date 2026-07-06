import pandas as pd
import os

# CONFIGURATION
INPUT_CSV_FILE = r"C:\Users\Lenovo\github_individuals_3000_4.csv"
OUTPUT_CSV_FILE = 'CLEANED_.csv'

#  LOAD THE DATASET
try:
    df = pd.read_csv(
        INPUT_CSV_FILE,
        encoding='utf-8',           # Corrected encoding to handle special characters
        on_bad_lines='skip',        # Skips malformed rows to prevent crashing
        sep=',',
        quotechar='"'
    )
    print(f"Successfully loaded '{INPUT_CSV_FILE}'.")
    print(f"Initial row count: {len(df)}")
except FileNotFoundError:
    print(f"Error: The file '{INPUT_CSV_FILE}' was not found.")
    exit()
except UnicodeDecodeError as e:
    print(f"Encoding error: {e}. Trying a different encoding.")
    # Fallback to a different encoding in case UTF-8 fails
    df = pd.read_csv(
        INPUT_CSV_FILE,
        encoding='latin-1',
        on_bad_lines='skip',
        sep=',',
        quotechar='"'
    )
    print("Successfully loaded with 'latin-1' encoding.")
except pd.errors.ParserError as e:
    print(f"Parsing error: {e}")
    exit()

#  KEEP MOST POPULAR REPO PER OWNER 
if 'owner' in df.columns and 'stars' in df.columns:
    initial_rows = len(df)
    
    # Ensure stars and forks are numeric before sorting
    df['stars'] = pd.to_numeric(df['stars'], errors='coerce')
    if 'forks' in df.columns:
        df['forks'] = pd.to_numeric(df['forks'], errors='coerce')
    
    # Fill any NaN created during coercion with a default value (e.g., 0)
    df.fillna(0, inplace=True)

    # Sort by stars and forks (descending)
    sort_columns = ['stars', 'forks'] if 'forks' in df.columns else ['stars']
    df = df.sort_values(by=sort_columns, ascending=False)

    # Drop duplicates per owner
    df = df.drop_duplicates(subset=['owner'], keep='first')

    final_rows = len(df)
    print(f"\nRemoved {initial_rows - final_rows} duplicate rows.")
    print(f"Row count after keeping most popular repo per owner: {final_rows}")
else:
    print("\nWarning: 'owner' or 'stars' column not found, skipping duplicate removal.")

#  REMOVE UNWANTED COLUMNS 
columns_to_drop = [
    'full_repository_name',
    'description',
    'latest_commit_message',
    'Unnamed: 4',
    'Unnamed: 17'
]
df.drop(columns=columns_to_drop, inplace=True, errors='ignore')
print(f"\nRemoved columns: {', '.join(columns_to_drop)}")

# DISPLAY RESULTS AND SAVE ---
print("\n--- Preview of Final Cleaned Data ---")
print(df.head())

# Save the cleaned dataframe
df.to_csv(OUTPUT_CSV_FILE, index=False)

# Print absolute path of the saved CSV
output_path = os.path.abspath(OUTPUT_CSV_FILE)
print(f"\n Cleaned data has been saved to: {output_path}")