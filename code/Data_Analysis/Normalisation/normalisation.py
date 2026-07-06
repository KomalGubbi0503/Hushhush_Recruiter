import pandas as pd
from sklearn.preprocessing import PowerTransformer, MinMaxScaler
import numpy as np

def normalize_and_save_data(input_csv, output_csv):
   
    try:
        # Read the CSV file into a pandas DataFrame
        print(f" Reading data from '{input_csv}'")
        df = pd.read_csv(input_csv)
        print("Data read successfully.")

        # Store the original column order
        original_columns = df.columns.tolist()

        #  Separate numerical and non-numerical columns
        print("\n Separating numerical and string columns ")
        # Select all columns with a numerical data type
        numerical_df = df.select_dtypes(include=np.number)
        # Select all columns with a non-numerical data type 
        string_df = df.select_dtypes(exclude=np.number)
        
        # Check if there are any numerical features to normalize
        if numerical_df.empty:
            print("No numerical features found to normalize. Saving original data as is.")
            df.to_csv(output_csv, index=False)
            return

        #  Normalize ALL numerical features
        print("\n Normalizing numerical features")
        
        # Initialize the PowerTransformer
        pt = PowerTransformer()
        
        # Fit and transform the numerical data
        X_transformed_pt = pt.fit_transform(numerical_df)
        print("Numerical data has been transformed using PowerTransformer.")

        # Initialize MinMaxScaler
        scaler = MinMaxScaler()
        
        # Fit and transform the already transformed data to a [0, 1] range
        X_final_scaled = scaler.fit_transform(X_transformed_pt)
        print("Numerical data has been scaled to a [0, 1] range.")

        # Convert the processed NumPy array back to a DataFrame with column names
        normalized_numerical_df = pd.DataFrame(X_final_scaled, columns=numerical_df.columns)

        # Combine the normalized numerical columns with the original string columns
        # This will create a new DataFrame with the normalized numerical columns and the untouched string columns.
        print("\n Combining processed and original columns")
        final_df = pd.concat([normalized_numerical_df, string_df], axis=1)
        
        # Re-order the columns to match the original DataFrame
        final_df = final_df.reindex(columns=original_columns)

        # Save the final combined DataFrame to a new CSV file
        print(f"\n--- Step 6: Saving the final DataFrame to '{output_csv}' ---")
        final_df.to_csv(output_csv, index=False)
        print("Final processed data saved successfully.")

    except FileNotFoundError:
        print(f"Error: The file '{input_csv}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")


input_file_name = r"C:\Users\Lenovo\Downloads\rounded_data.csv"
output_file_name = 'processed_data.csv'

normalize_and_save_data(input_file_name, output_file_name)