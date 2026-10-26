
import pandas as pd

# Load the CSV using a compatible encoding
df = pd.read_csv(
    "superstore_dataset2011-2015.csv",
    encoding="latin1"
)

# Display first five rows
print("\nFirst 5 rows:")
print(df.head())

# Display column names
print("\nColumn names:")
print(df.columns.tolist())

# Display number of rows and columns
print("\nDataset shape:")
print(df.shape)

# Display dataset information
print("\nDataset information:")
df.info()

# Check missing values
print("\nMissing values:")
print(df.isnull().sum())

