# -*- coding: utf-8 -*-
"""
Created on Wed Jan  8 09:56:49 2025

@author: pulkit.kushwaha
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

FOLDER_NAME = "Company_revenue_v3"
INPUT_FILE = "company_cik_ticker.xlsx"
# Read and process input file
df = pd.read_excel(INPUT_FILE)
ticker_symbols = df.drop_duplicates().dropna()['ticker'].to_list()

# Find missing tickers
missing_tickers = []
for ticker in ticker_symbols:
    annual_file = os.path.join(FOLDER_NAME, f"{ticker}_annual_financial_data.xlsx")
    quarterly_file = os.path.join(FOLDER_NAME, f"{ticker}_quarterly_financial_data.xlsx")
    
    if not (os.path.exists(annual_file) and os.path.exists(quarterly_file)):
        missing_tickers.append(ticker)

print(len(missing_tickers))



# Set up WebDriver (ensure you have the correct driver installed, e.g., chromedriver)
driver = webdriver.Chrome()  # Or use Edge, Firefox, etc.

# Open the URL
url ="https://stockanalysis.com/stocks/sny/financials/?p=quarterly" 
driver.get(url)

try:
    # Locate the dropdown button using both class and title attributes
    dropdown_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[@class='controls-btn' and @title='Change number units']"))
    )
    dropdown_button.click() 
    
    # Step 2: Wait for the Dropdown Menu to Appear
    dropdown_menu = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'absolute z-40')]"))
    )

    # Step 3: Click on the "Raw" Option
    raw_option = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Raw')]"))
    )
    raw_option.click()  # Select "Raw"

    

    # Wait for the table to update (optional: sleep for a few seconds)
    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.TAG_NAME, "table"))
    )

    # Now, you can proceed to scrape the updated table data using BeautifulSoup or Selenium
    page_source = driver.page_source

finally:
    driver.quit()
"""
url ="https://stockanalysis.com/quote/otc/NPHC/financials/?p=quarterly" 
# "https://stockanalysis.com/stocks/sny/financials/"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

response = requests.get(url, headers=headers)
if response.status_code != 200:
    print("Failed to retrieve data")

"""
soup = BeautifulSoup(page_source, 'html.parser')

currency=soup.find('div', class_="hidden pb-1 text-sm text-faded lg:block")
print(currency)
# Find the financials table
tables = soup.find_all('table')
len(tables)
if not tables:
    print("No financial tables found")
    
else:
    financial_data = []
    # Extract headers
    table=tables[0]
    header_rows = table.find_all('tr')[:2]  # Extracting first two rows as headers
    header1 = [th.text.strip() for th in header_rows[0].find_all('th')]
    header2 = [th.text.strip() for th in header_rows[1].find_all('th')]

    # Create MultiIndex for column headers
    columns = pd.MultiIndex.from_tuples(zip(header1, header2))

    # Extract financial data
    financial_data = []
    for row in table.find_all('tr')[2:]:  # Skipping the first two header rows
        cols = row.find_all('td')
        if cols:
            financial_data.append([col.text.strip() for col in cols])

    # Convert to DataFrame with MultiIndex columns
    df1 = pd.DataFrame(financial_data, columns=columns)
    print(df1)

