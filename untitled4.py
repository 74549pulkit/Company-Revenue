# -*- coding: utf-8 -*-
"""
Created on Wed Jan  8 12:21:10 2025

@author: pulkit.kushwaha
"""
import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

FOLDER_NAME = "Company_revenue_v3"
INPUT_FILE = "company_cik_ticker.xlsx"
# Read and process input file
df = pd.read_excel(INPUT_FILE)
ticker_symbols = df.drop_duplicates().dropna()['ticker'].to_list()
ticker_symbols = [str(ticker).upper() for ticker in ticker_symbols]
# Find missing tickers
missing_tickers = []
for ticker in ticker_symbols:
    annual_file = os.path.join(FOLDER_NAME, f"{ticker}_annual_financial_data.xlsx")
    quarterly_file = os.path.join(FOLDER_NAME, f"{ticker}_quarterly_financial_data.xlsx")
    
    if not (os.path.exists(annual_file) and os.path.exists(quarterly_file)):
        missing_tickers.append(ticker)

print(len(missing_tickers))



# Set up Selenium WebDriver
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in headless mode
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--window-size=1920,1080")

# Specify WebDriver path (update as needed)
service = Service("C:/Users/pulkit.kushwaha/Downloads/chromedriver-win64/chromedriver-win64/chromedriver.exe")  # Adjust the path accordingly
driver = webdriver.Chrome(service=service, options=chrome_options)

# Target URL
url = "https://stockanalysis.com/quote/otc/NPHC/financials/?p=quarterly"
driver.get(url)

try:
    # Step 1: Click the Dropdown Button
    dropdown_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[@class='controls-btn' and @title='Change number units']"))
    )
    dropdown_button.click() 

    # Step 2: Wait for Dropdown Menu
    raw_option = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Raw')]"))
    )
    raw_option.click()  # Select "Raw"

    # Step 3: Wait for the Table Update
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.TAG_NAME, "table")))

    # Step 4: Extract Updated Page Source
    page_source = driver.page_source

finally:
    # Fast shutdown
    driver.delete_all_cookies()
    driver.quit()
    #os.system("taskkill /f /im chromedriver.exe")  # Force kill if needed

# Parse with BeautifulSoup
soup = BeautifulSoup(page_source, 'html.parser')

# Find financials table
tables = soup.find_all('table')

if not tables:
    print("No financial tables found")
else:
    table = tables[0]  # First table
    rows = table.find_all('tr')

    # Extract headers (handling multi-level headers dynamically)
    headers = []
    for row in rows[:2]:  # Assuming first two rows are headers
        headers.append([th.text.strip() for th in row.find_all('th')])

    # Create MultiIndex if headers exist
    if len(headers) == 2:
        columns = pd.MultiIndex.from_tuples(zip(headers[0], headers[1]))
    else:
        columns = headers[0]

    # Extract financial data
    financial_data = []
    for row in rows[2:]:  # Skip header rows
        cols = row.find_all('td')
        if cols:
            financial_data.append([col.text.strip() for col in cols])

    # Convert to DataFrame
    df = pd.DataFrame(financial_data, columns=columns)

    # Display DataFrame
    print(df)

# Save DataFrame to CSV
df.to_csv("sc_financial_data.csv", index=False)
