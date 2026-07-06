import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

#  Set the path to your file (edit this to match your system)
file_path = r"C:\Users\Lenovo\rounded_data.csv"

# Check if file exists
if not os.path.exists(file_path):
    raise FileNotFoundError(f"File not found at: {file_path}")

# Load CSV with semicolon delimiter
df = pd.read_csv(file_path)

# Show first few rows
print("Data preview:")
print(df.head(), "\n")
print("Columns:", df.columns, "\n")

# Keep only numeric columns
numeric_df = df.select_dtypes(include=["number"])

# Compute correlation matrix
corr = numeric_df.corr()

# Plot clear heatmap
plt.figure(figsize=(16, 12))  # bigger size for clarity
sns.heatmap(
    corr,
    annot=True,
    cmap="coolwarm",
    fmt=".2f",
    annot_kws={"size": 8},  # smaller numbers inside boxes
    cbar_kws={"shrink": 0.8}  # smaller color bar
)

plt.xticks(rotation=45, ha="right", fontsize=10)  # rotate x labels
plt.yticks(rotation=0, fontsize=10)              # keep y labels horizontal
plt.title("Correlation Heatmap of Repository Metrics",
          fontsize=14, weight="bold")
plt.tight_layout()


plt.show()

