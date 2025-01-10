# -*- coding: utf-8 -*-
"""
Created on Thu Jan  9 11:40:51 2025

@author: pulkit.kushwaha
"""

import pandas as pd

# Load the data
cik_file = "D:/Spyder/company_cik_ticker.xlsx"
cik_df = pd.read_excel(cik_file)

fin_excel = "D:/Vscode/Company_revenue/Stock_analysis_extracted_financial_data.csv"
excel_df = pd.read_csv(fin_excel)

# Merge the dataframes on the specified columns
merged_df = pd.merge(cik_df, excel_df, left_on='ticker', right_on='Company', how='inner')

# Display the merged dataframe
print(merged_df)

# Save the merged dataframe to a new Excel file if needed
output_file = "Stock_analysis_merged_financial_data.xlsx"
merged_df.to_excel(output_file, index=False)
print(f"Merged dataframe saved to {output_file}")
