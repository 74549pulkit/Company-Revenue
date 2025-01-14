# -*- coding: utf-8 -*-
"""
Multithreaded Stock Financial Data Scraper
Created on Wed Jan 8 12:21:10 2025
@author: pulkit.kushwaha

An enhanced web scraper for extracting financial data from stockanalysis.com
with improved error handling, structure, and parallel processing.
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
from urllib.parse import urlparse, parse_qs
from concurrent.futures import ThreadPoolExecutor
from queue import Queue
import threading
import time

class FinancialDataScraper:
    def __init__(self, chromedriver_path, input_file, output_folder, max_workers=5):
        """Initialize the scraper with configuration parameters."""
        self.chromedriver_path = chromedriver_path
        self.input_file = input_file
        self.output_folder = output_folder
        self.max_workers = max_workers
        self.chrome_options = self.configure_chrome_options()
        self.lock = threading.Lock()
        
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
        df = pd.read_csv(self.input_file)
        
        # Filter out rows with missing values in 'Symbol' or 'Link', and remove duplicates
        df_cleaned = df.dropna(subset=['Symbol', 'Link']).drop_duplicates(subset=['Symbol', 'Link'])
        ticker_symbols = df_cleaned[['Symbol', 'Link']].values.tolist()
        
        missing_tickers_link = []
        for ticker, link in ticker_symbols:
            annual_excel = os.path.join(self.output_folder, f"{ticker}_annual_financial_data.xlsx")
            quarterly_excel = os.path.join(self.output_folder, f"{ticker}_quarterly_financial_data.xlsx")
            
            annual_csv = os.path.join(self.output_folder, f"{ticker}_annual_financial_data.csv")
            quarterly_csv = os.path.join(self.output_folder, f"{ticker}_quarterly_financial_data.csv")
            
            if not ((os.path.exists(annual_excel) or os.path.exists(annual_csv)) and
                    (os.path.exists(quarterly_excel) or os.path.exists(quarterly_csv))):
                missing_tickers_link.append(link)
        
        with self.lock:
            print(f"Found {len(missing_tickers_link)} missing tickers")
        return missing_tickers_link

    def _attempt_scrape(self, driver, url, ticker):
        """Attempt to scrape data from a specific URL."""
        try:
            driver.get(url)
            with self.lock:
                print(f"Accessing {url} for {ticker}...")

            if "quarterly" in url:
                parsed_url = urlparse(driver.current_url)
                query_params = parse_qs(parsed_url.query)
                if 'p' not in query_params or query_params['p'][0].lower() != 'quarterly':
                    quarterly_button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, "//ul[contains(@class, 'navmenu submenu')]//button[text()='Quarterly']"))
                    )
                    quarterly_button.click()
                    WebDriverWait(driver, 10).until(
                        lambda driver: 'quarterly' in driver.current_url.lower()
                    )

            dropdown_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@class='controls-btn' and @title='Change number units']"))
            )
            dropdown_button.click()
            
            dropdown_menu = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'absolute z-40')]"))
            )

            raw_option = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Raw')]"))
            )
            raw_option.click()
            
            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.TAG_NAME, "table")))
            
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            table = soup.find('table')
            element = soup.find('div', class_="hidden pb-1 text-sm text-faded lg:block")
            
            currency = "N/A"
            fiscal_year = "N/A"
            if element:
                currency_fiscal = element.text.split('.')
                if currency_fiscal:
                    currency = currency_fiscal[0].strip()
                if len(currency_fiscal) > 1:
                    fiscal_year = currency_fiscal[1].strip()
            
            if table:
                return self._process_table_data(table, currency, fiscal_year)
            return None
            
        except (TimeoutException, WebDriverException) as e:
            with self.lock:
                print(f"Error accessing {url} for {ticker}: {str(e)}")
            return None

    def process_ticker(self, link):
        """Process a single ticker with both quarterly and annual data."""
        ticker = link.split('/')[-2].upper()
        driver = None
        try:
            service = Service(self.chromedriver_path)
            driver = webdriver.Chrome(service=service, options=self.chrome_options)
            
            # Scrape quarterly data
            quarterly_data = self.scrape_financial_data(link, 'quarterly', driver)
            if quarterly_data is not None:
                self.save_data(quarterly_data, ticker, 'quarterly')
            
            # Scrape annual data
            annual_data = self.scrape_financial_data(link, 'annual', driver)
            if annual_data is not None:
                self.save_data(annual_data, ticker, 'annual')
                
        except Exception as e:
            with self.lock:
                print(f"Failed to process ticker {ticker}: {str(e)}")
        finally:
            if driver:
                driver.quit()
    
    def scrape_financial_data(self, link, report_type='quarterly', driver=None):
        """Scrape financial data for a specific ticker."""
        ticker = link.split('/')[-2].upper()
        url = f"{link}financials/?p={report_type}"
        
        try:
            data = self._attempt_scrape(driver, url, ticker)
            if data is None:
                raise ValueError(f"No financial table found for {ticker}")
            return data
            
        except Exception as e:
            with self.lock:
                print(f"Failed to scrape {ticker}: {str(e)}")
            return None
    
    def _process_table_data(self, table, currency, fiscal_year):
        """Process the scraped table and convert to DataFrame."""
        rows = table.find_all('tr')
        headers = []
        for row in rows[:2]:
            headers.append([th.text.strip() for th in row.find_all('th')])
        
        columns = (pd.MultiIndex.from_tuples(zip(headers[0], headers[1])) 
                  if len(headers) == 2 else headers[0])
        
        data = []
        for row in rows[2:]:
            cols = row.find_all('td')
            if cols:
                data.append([col.text.strip() for col in cols])
                
        table_df = pd.DataFrame(data, columns=columns)
        table_df['Currency'] = currency
        table_df['Fiscal_Year_period'] = fiscal_year
        return table_df
    
    def save_data(self, df, ticker, report_type):
        """Save the DataFrame to a file."""
        filename = os.path.join(self.output_folder, f"{ticker}_{report_type}_financial_data.csv")
        df.to_csv(filename, index=False)
        with self.lock:
            print(f"Saved data to {filename}")

def main():
    # Configuration
    CHROMEDRIVER_PATH = r"C:/Users/pulkit.kushwaha/Downloads/chromedriver-win64/chromedriver-win64/chromedriver.exe"
    INPUT_FILE = r"D:\Vscode\Company_revenue\Data\stock_analysis_screener_OTC_USA.csv"
    OUTPUT_FOLDER = r"D:\Vscode\Company_revenue\company_revenue_otc_usa"
    MAX_WORKERS = 5
    
    # Create output directory if it doesn't exist
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    
    # Initialize scraper
    scraper = FinancialDataScraper(CHROMEDRIVER_PATH, INPUT_FILE, OUTPUT_FOLDER, MAX_WORKERS)
    
    # Get missing tickers
    missing_tickers_link = scraper.get_missing_tickers()
    
    # Process tickers using ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        executor.map(scraper.process_ticker, missing_tickers_link)

if __name__ == "__main__":
    main()