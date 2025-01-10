# -*- coding: utf-8 -*-
"""
Created on Wed Jan  8 16:14:26 2025

@author: pulkit.kushwaha
"""

import os
import pandas as pd

# Folder containing financial data files
folder_path = r"d:\Vscode\Company_revenue\company_revenue_v4"

# Initialize an empty list to store extracted data
financial_data = []

# Loop through all files in the folder
for file in os.listdir(folder_path):
    if file.endswith(".csv"):# or file.endswith(".xlsx"):  # Check if file is CSV or Excel
        # Extract company symbol and frequency from filename
        #file="D:/Spyder/Company_revenue_v3/TLCC_quarterly_financial_data.csv"
        parts = file.split("_")
        company_symbol = parts[0]
        frequency = parts[1]  # "quarterly" or "annually"

        # Read file based on its format
        file_path = os.path.join(folder_path, file)
        if file.endswith(".csv"):
            df = pd.read_csv(file_path, header=None)
        else:
            df = pd.read_excel(file_path)

        # Extract "Fiscal Year", "Period Ending", and "Revenue"
        fiscal_years = df.iloc[0, 1:].values.tolist()  # First row contains Fiscal Years
        period_ending = df.iloc[1, 1:].values.tolist()  # Second row contains Period Ending
        revenue_row = df[df.iloc[:, 0] == "Revenue"]
        currency_index = list(df.iloc[0, :]).index("Currency")
        if currency_index:
            if df.iloc[:,currency_index][0]=="Currency":
                currency_row = df.iloc[:,currency_index][2]
            else:
                currency_row = None
        else:
            currency_row = None
        fiscal_period_index = list(df.iloc[0, :]).index("Fiscal_Year_period")
        if fiscal_period_index:
            if df.iloc[:,fiscal_period_index][0]=="Fiscal_Year_period":
                fiscal_period = df.iloc[:,fiscal_period_index][2]
            else:
                fiscal_period = None
        else:   
            fiscal_period = None

        if not revenue_row.empty:
            revenue_values = revenue_row.iloc[:, 1:].values.flatten().tolist()
            
            # Store extracted data
            for i in range(len(fiscal_years)):  # Loop through each fiscal year column
                financial_data.append({
                    "Company": company_symbol,
                    "Frequency": frequency,
                    "Fiscal": fiscal_years[i],
                    "Period Ending": period_ending[i],
                    "Revenue": revenue_values[i] if i < len(revenue_values) else None,
                    "Currency": currency_row,
                    "Fiscal_period": fiscal_period
                })

# Convert to DataFrame for better visualization
financial_df = pd.DataFrame(financial_data)

# Save the extracted data
output_file = "Stock_analysis_extracted_financial_data.csv"

financial_df.to_csv(output_file, index=False)

print(f"Financial data saved to {output_file}")
