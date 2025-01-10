

# -*- coding: utf-8 -*-
"""
Stock Financial Data Scraper
Created on Wed Jan 8 12:21:10 2025
@author: pulkit.kushwaha

An enhanced web scraper for extracting financial data from stockanalysis.com
with improved error handling and structure.
"""

import os
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

class FinancialDataScraper:
    def __init__(self, chromedriver_path, input_file, output_folder):
        """Initialize the scraper with configuration parameters."""
        self.chromedriver_path = chromedriver_path
        self.input_file = input_file
        self.output_folder = output_folder
        self.chrome_options = self.configure_chrome_options()
        
    @staticmethod
    def configure_chrome_options():
        """Configure Chrome WebDriver options."""
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-dev-shm-usage")
        return options
    
    def get_missing_tickers(self):
        """Identify tickers with missing financial data."""
        df = pd.read_excel(self.input_file)
        ticker_symbols = df.drop_duplicates().dropna()['ticker'].to_list()
        
        missing_tickers = []
        for ticker in ticker_symbols:
            annual_file = os.path.join(self.output_folder, f"{ticker}_annual_financial_data.xlsx")
            quarterly_file = os.path.join(self.output_folder, f"{ticker}_quarterly_financial_data.xlsx")
            
            if not (os.path.exists(annual_file) and os.path.exists(quarterly_file)):
                missing_tickers.append(ticker)
                
        print(f"Found {len(missing_tickers)} missing tickers")
        return missing_tickers
    
    def scrape_financial_data(self, ticker, report_type='quarterly'):
        """
        Scrape financial data for a specific ticker.
        
        Args:
            ticker (str): Stock ticker symbol
            report_type (str): Either 'quarterly' or 'annual'
            
        Returns:
            pandas.DataFrame: Scraped financial data
        """
        url1= f"https://stockanalysis.com/stocks/{ticker}/financials/?p={report_type}"
        url2 = f"https://stockanalysis.com/quote/otc/{ticker}/financials/?p={report_type}"
        driver = None
        
        try:
            service = Service(self.chromedriver_path)
            driver = webdriver.Chrome(service=service, options=self.chrome_options)
            driver.get(url)
            
           
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
            raw_option.click()  #
            
            # Wait for table update
            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.TAG_NAME, "table")))
            
            # Parse the page
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            table = soup.find('table')
            
            if not table:
                raise ValueError("No financial table found on the page")
            
            # Extract and process table data
            return self._process_table_data(table)
            
        except TimeoutException as e:
            print(f"Timeout while scraping {ticker}: {str(e)}")
            raise
        except WebDriverException as e:
            print(f"WebDriver error for {ticker}: {str(e)}")
            raise
        except Exception as e:
            print(f"Unexpected error scraping {ticker}: {str(e)}")
            raise
        finally:
            if driver:
                driver.quit()
    
    def _process_table_data(self, table):
        """Process the scraped table and convert to DataFrame."""
        
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
                
        return df
    
    def save_data(self, df, ticker, report_type):
        """Save the DataFrame to a file."""
        filename = os.path.join(self.output_folder, f"{ticker}_{report_type}_financial_data.csv")
        df.to_csv(filename, index=False)
        print(f"Saved data to {filename}")

def main():
    # Configuration
    CHROMEDRIVER_PATH = "C:/Users/pulkit.kushwaha/Downloads/chromedriver-win64/chromedriver-win64/chromedriver.exe"
    INPUT_FILE = "company_cik_ticker.xlsx"
    OUTPUT_FOLDER = "Company_revenue_v3"
    
    # Create output directory if it doesn't exist
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    
    # Initialize scraper
    scraper = FinancialDataScraper(CHROMEDRIVER_PATH, INPUT_FILE, OUTPUT_FOLDER)
    
    # Get missing tickers
    missing_tickers = scraper.get_missing_tickers()
    missing_tickers=missing_tickers[:5]
    # Process each missing ticker
    for ticker in missing_tickers:
        try:
            print(f"Processing ticker: {ticker}")
            
            # Scrape quarterly data
            quarterly_data = scraper.scrape_financial_data(ticker, 'quarterly')
            scraper.save_data(quarterly_data, ticker, 'quarterly')
            
            # Scrape annual data
            annual_data = scraper.scrape_financial_data(ticker, 'annual')
            scraper.save_data(annual_data, ticker, 'annual')
            
        except Exception as e:
            print(f"Failed to process ticker {ticker}: {str(e)}")
            continue

if __name__ == "__main__":
    main()