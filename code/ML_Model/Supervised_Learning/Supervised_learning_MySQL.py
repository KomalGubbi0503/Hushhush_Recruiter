import pandas as pd
import numpy as np
import mysql.connector
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
import joblib 
import os

# Configure your MySQL database credentials here 
DB_HOST = "localhost"
DB_USER = "YourUsername"
DB_PASSWORD = "YourPassword"
DB_NAME = "candidatesdb"
TABLE_NAME = "good_candidates"
PICKLE_FILE_NAME = "logistic_model.pkl" 

def save_to_mysql(df_to_save, table_name):
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = conn.cursor()
        print(f"\n--- Connected to MySQL database '{DB_NAME}' ---")

        # Clean column names
        df_to_save.columns = df_to_save.columns.str.strip()
        df_to_save.columns = df_to_save.columns.str.replace(' ', '_')
        print("DataFrame column names have been cleaned.")

        # Dynamic CREATE TABLE statement
        columns_sql = ", ".join([f"`{col}` VARCHAR(255)" if df_to_save[col].dtype == 'object'
                                 else f"`{col}` DOUBLE"
                                 for col in df_to_save.columns])
        create_table_query = f"CREATE TABLE IF NOT EXISTS `{table_name}` ({columns_sql})"
        cursor.execute(create_table_query)
        print(f"Table '{table_name}' created or already exists.")

        # Dynamic INSERT statement
        insert_query = f"INSERT INTO `{table_name}` ({', '.join([f'`{col}`' for col in df_to_save.columns])}) VALUES ({', '.join(['%s'] * len(df_to_save.columns))})"
        
        # Prepare the data for insertion
        records = [tuple(row) for row in df_to_save.values]
        
        # Insert all records at once
        cursor.executemany(insert_query, records)
        conn.commit()
        print(f"Successfully inserted {len(df_to_save)} records into '{table_name}'.")

    except mysql.connector.Error as err:
        print(f"Error connecting to MySQL: {err}")
        return False
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()
            print("MySQL connection closed.")
    return True


def run_supervised_classification(input_csv):
    try:
        # Load the data from the CSV file
        print(" Loading data")
        df = pd.read_csv(input_csv)
        print("Data loaded successfully.")

        # Prepare the data for Logistic Regression
        print("\n Preparing data for model training")
        numerical_cols = df.select_dtypes(include=np.number).columns
        feature_cols = [col for col in numerical_cols if col != 'cluster_label']
        X = df[feature_cols]
        y = df['cluster_label']
        
        # Split data into training and testing sets (for evaluation)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Train the Logistic Regression model
        print("\n Training the Logistic Regression model")
        model = LogisticRegression(random_state=42)
        model.fit(X_train, y_train)
        print("Model training completed.")
        
        # Save the trained model to a pickle file ---
        joblib.dump(model, PICKLE_FILE_NAME)
        print(f"Trained model saved to {PICKLE_FILE_NAME}")
       

        # Make predictions and filter for "good" candidates
        print("\n Predicting and filtering for good candidates")
        df['predicted_label'] = model.predict(X)
        good_candidates = df[df['predicted_label'] == 1].copy()
        print(f"Found {len(good_candidates)} good candidates.")

        # Save the filtered DataFrame to the MySQL database
        if not good_candidates.empty:
            print("\n Saving good candidates to MySQL")
            success = save_to_mysql(good_candidates, TABLE_NAME)
            if success:
                print("Operation completed successfully.")
            else:
                print("Operation failed.")
        else:
            print("No good candidates found to save.")

    except FileNotFoundError:
        print(f"Error: The file '{input_csv}' was not found. Please ensure it's in the correct directory.")
    except KeyError:
        print("Error: The CSV file must contain a 'cluster_label' column for the target variable.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# Call the main function
input_file = r"C:\Users\Lenovo\split_data_part1.csv"
run_supervised_classification(input_file)