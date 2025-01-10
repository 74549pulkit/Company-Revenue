# -*- coding: utf-8 -*-
"""
Created on Wed Jan  8 17:17:57 2025

@author: pulkit.kushwaha
"""

import os
import pandas as pd

# Folder containing financial data files
folder_path = "D:/Spyder/Company_revenue_v3"


# Initialize an empty list to store extracted data
financial_data = []

# Loop through all files in the folder
for file in os.listdir(folder_path):
    if file.endswith(".xlsx"):  # Only process Excel files for this format
        # Extract company symbol and frequency from filename
        parts = file.split("_")
        company_symbol = parts[0]
        frequency = parts[1]  # "quarterly" or "annually"

        # Read the Excel file
        file_path = os.path.join(folder_path, file)
        df = pd.read_excel(file_path)

        # Ensure required columns exist
        required_columns = {"fiscalDateEnding", "totalRevenue", "reportedCurrency"}
        if not required_columns.issubset(df.columns):
            print(f"Skipping {file} due to missing columns")
            continue

        # Extract relevant data
        for _, row in df.iterrows():
            financial_data.append({
                "Company": company_symbol,
                "Frequency": frequency,
                "Fiscal Date Ending": row["fiscalDateEnding"],
                "Total Revenue": row["totalRevenue"],
                "Reported Currency": row["reportedCurrency"]
            })

# Convert to DataFrame for better visualization
financial_df = pd.DataFrame(financial_data)

# Save the extracted data
output_file = "api_extracted_financial_data.xlsx"
financial_df.to_excel(output_file, index=False)

print(f"Financial data saved to {output_file}")
