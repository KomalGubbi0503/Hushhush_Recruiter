import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix
import os
import time  

def run_logistic_regression(input_csv, output_csv):
    
    try:
        #  Load the data from the CSV file
        print("Loading data")
        df = pd.read_csv(input_csv)
        print("Data loaded successfully.")

        #  Prepare the data for Logistic Regression
        print("\n Preparing data for model training ")
        
        # Features (X): All numerical columns except 'cluster_label'
        numerical_cols = df.select_dtypes(include=np.number).columns
        feature_cols = [col for col in numerical_cols if col != 'cluster_label']
        X = df[feature_cols]
        
        # Target tables from K-Means
        y = df['cluster_label']
        
        # Split data into training and testing sets (80/20 split)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        print(f"Data split into {len(X_train)} training samples and {len(X_test)} testing samples.")

        #  Train the Logistic Regression model
        print("\n  Training the Logistic Regression model")
        
        # Start the timer
        start_time = time.time()
        
        model = LogisticRegression(random_state=42)
        model.fit(X_train, y_train)
        
        # Stop the timer and calculate the elapsed time
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        print("Model training completed.")
        print(f"Training took {elapsed_time:.4f} seconds.")

        #  Make predictions and evaluate the model
        print("\n Making predictions and evaluating the model")
        y_pred = model.predict(X_test)
        
        # Calculate evaluation metrics
        accuracy = accuracy_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)
        
        print(f"Accuracy Score: {accuracy:.2f}")
        print(f"F1 Score: {f1:.2f}")

        #  Print the Confusion Matrix
        print("\nConfusion Matrix:")
        cm = confusion_matrix(y_test, y_pred)
        print(cm)
        
        #  Predict for all candidates and filter for "good" ones
        print("\n Predicting for all candidates and filtering for good candidates ")
        df['predicted_label'] = model.predict(X)
        
        # Filter the DataFrame to keep only rows where the predicted label is 1 (I wanted only good candidates to dispalyed)
        good_candidates = df[df['predicted_label'] == 1].copy()
        print(f"Found {len(good_candidates)} good candidates.")
        
        #  Save the filtered DataFrame to a new CSV file
        print(f"\n Saving filtered data to '{output_file}'")
        good_candidates.to_csv(output_csv, index=False)
        print("Good candidates saved successfully.")

    except FileNotFoundError:
        print(f"Error: The file '{input_csv}' was not found. Please ensure it's in the same directory as this script.")
    except KeyError:
        print("Error: The CSV file must contain a 'cluster_label' column for the target variable.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


input_file = r"C:\Users\Lenovo\split_data_part1.csv"
output_file = 'good_candidates_only_5.csv'
run_logistic_regression(input_file, output_file)