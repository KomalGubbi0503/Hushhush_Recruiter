import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
import os

def classify_candidates(input_csv, output_csv):
   
    try:
        #  Load the data from the CSV file
        print(" Loading data ")
        df = pd.read_csv(input_csv)
        print("Data loaded successfully.")

        #  Separate numerical and string columns
        print("\n Separating numerical and string columns")
        numerical_df = df.select_dtypes(include=np.number).dropna()
        string_df = df.select_dtypes(exclude=np.number)

        # Check for numerical features to ensure the algorithm has data to work with
        if numerical_df.empty:
            print("Error: No numerical features found for clustering.")
            return

        print("Numerical features separated.")

        # Perform K-Means Clustering on numerical data with 2 clusters ( I want two clusters beacuse I am classifying candidates as good or bad)
        print("\n Running K-Means with 2 clusters")
        kmeans = KMeans(n_clusters=2, random_state=42, n_init=10)
        kmeans.fit(numerical_df)
        df['cluster_label'] = kmeans.labels_
        print("K-Means clustering completed.")

        #  Evaluate the model (using Silhouette Score)
        print("\n Evaluating the clustering model")
        silhouette_avg = silhouette_score(numerical_df, df['cluster_label'])
        print(f"Silhouette Score: {silhouette_avg:.3f}")
        
        # Count the number of candidates in each cluster
        print("\n Counting candidates in each cluster")
        cluster_counts = df['cluster_label'].value_counts().sort_index()
        print(cluster_counts)

        # Combine all columns and save the final result
        print("\n Combining columns and saving final CSV ")
        final_df = pd.concat([df[string_df.columns], df[numerical_df.columns], df['cluster_label']], axis=1)
        final_df.to_csv(output_csv, index=False)
        print(f"Final data with cluster names saved to '{output_csv}'.")

        # Plot the PCA scatter plot
        print("\n Plotting PCA scatter plot ")
        pca = PCA(n_components=2, random_state=42)
        pca_features = pca.fit_transform(numerical_df)
        
        plt.figure(figsize=(10, 8))
        scatter = plt.scatter(pca_features[:, 0], pca_features[:, 1], c=df['cluster_label'], cmap='viridis', s=50)
        plt.title('K-Means Clusters in PCA Space')
        plt.xlabel('Principal Component 1')
        plt.ylabel('Principal Component 2')
        plt.legend(handles=scatter.legend_elements()[0], labels=['Cluster 0', 'Cluster 1'])
        plt.grid(True)
        plt.show()
        print("PCA plot displayed successfully.")

    except FileNotFoundError:
        print(f"Error: The file '{input_csv}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")


input_file = r"C:\Users\Lenovo\processed_data.csv"
output_file = 'classified_candidates_1.csv'

classify_candidates(input_file, output_file)