# -*- coding: utf-8 -*-
"""
Created on Mon Jan 13 11:57:27 2025

@author: pulkit.kushwaha
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
from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException
import time
from selenium.webdriver.common.keys import Keys
import threading
import re

class PopupHandler:
    def __init__(self, driver, check_interval=1):
        """
        Initialize popup handler with background monitoring
        
        Args:
            driver: Selenium WebDriver instance
            check_interval: How often to check for popup (in seconds)
        """
        self.driver = driver
        self.check_interval = check_interval
        self.is_running = False
        self.monitor_thread = None

    def close_popup(self):
        """Attempts to close the popup if it exists"""
        try:
            popup = self.driver.find_element(By.CSS_SELECTOR, 'div[aria-modal="true"]')
            close_button = popup.find_element(By.CSS_SELECTOR, 'button[aria-label="Close"]')
            close_button.click()
            print("Newsletter popup closed successfully")
            time.sleep(0.5)  # Short wait to ensure popup is gone
        except NoSuchElementException:
            pass  # No popup found, continue silently
        except Exception as e:
            print(f"Error closing popup: {str(e)}")

    def monitor_popups(self):
        """Background process to continuously monitor for popups"""
        while self.is_running:
            self.close_popup()
            time.sleep(self.check_interval)

    def start(self):
        """Start background popup monitoring"""
        self.is_running = True
        self.monitor_thread = threading.Thread(target=self.monitor_popups)
        self.monitor_thread.daemon = True  # Thread will stop when main program exits
        self.monitor_thread.start()
        print("Popup monitoring started")

    def stop(self):
        """Stop background popup monitoring"""
        self.is_running = False
        if self.monitor_thread:
            self.monitor_thread.join()
        print("Popup monitoring stopped")

def main():
    CHROMEDRIVER_PATH = "C:/Users/pulkit.kushwaha/Downloads/chromedriver-win64/chromedriver-win64/chromedriver.exe"

    options = Options()
    #options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-dev-shm-usage")

    url = "https://stockanalysis.com/stocks/screener/"
    service = Service(CHROMEDRIVER_PATH)

    try:
        driver = webdriver.Chrome(service=service, options=options)
        
        # Initialize and start popup handler
        popup_handler = PopupHandler(driver)
        popup_handler.start()
        
        driver.get(url)
        
        country_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[@class='controls-btn' and .//div[text()='US']]")))
        country_button.click()
        time.sleep(2)

        xp="/html/body/div/div[1]/div[2]/main/div[1]/div[2]/div[1]/div[2]/div/div[2]/button[2]"
        # click on dropdown
        dropdown_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, xp))) #"//button[@class='dd' and text()='US OTC']")))
        dropdown_button.click()
        time.sleep(5)

        add_filter_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[.//div[text()='Add Filters']]"))
        )
        add_filter_button.click()
        print("Clicked on 'Add Filters' button.")
        """
        # Wait for the page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "sector"))
        )
        """
        # Select the "Sector" filter
        sector_checkbox = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//label[contains(text(),'Sector')]"))
        )
        sector_checkbox.click()
        
        # Select the "Industry" filter
        industry_checkbox = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//label[contains(text(),'Industry')]"))
        )
        industry_checkbox.click()
        time.sleep(1)
        
        
        
        # Select the "Sector" dropdown and choose "Healthcare"
        button = driver.find_element(By.XPATH, "//div[contains(text(),'Sector')]/following-sibling::div//div[contains(@class, 'relative inline-block text-left')]//button[contains(@class, 'controls-btn')]")
        button.click()  # Click the button
        wait = WebDriverWait(driver, 10)
       
        sector_healthcare_checkbox = wait.until(EC.element_to_be_clickable((By.XPATH, "//label[contains(text(),'Healthcare')]")))
        sector_healthcare_checkbox.click()
        time.sleep(10)
        
        # Select the "Industry" dropdown and choose biotechnology options
        industry_dropdown = driver.find_element(By.XPATH, "//div[contains(text(),'Industry')]/following-sibling::div//div[contains(@class, 'relative inline-block text-left')]//button[contains(@class, 'controls-btn')]")
        industry_dropdown.click()  # Open the dropdown
        time.sleep(10)
        
        # Select both options in the Industry dropdown Biotechnology
        industry_biotech = driver.find_element(By.XPATH, "//label[contains(text(),'Biotechnology')]")
        industry_biotech.click()
        time.sleep(10)
        
        industry_drug_manufacturers = driver.find_element(By.XPATH, "//label[contains(text(),'Drug Manufacturers - Specialty & Generic')]")
        industry_drug_manufacturers.click()
       
        time.sleep(20)  # Wait for the page to load

        # Find the table element
        table = driver.find_element(By.ID, 'main-table')

        # Initialize an empty list to store the rows
        table_data = []

        current_page = 1
        table_id='main-table'
        wait_time=10

        try:
            # Get total number of pages
            page_info = WebDriverWait(driver, wait_time).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div.rows-wrap span.whitespace-nowrap'))
            )
            match = re.search(r'Page \d+ of (\d+)', page_info.text)
            total_pages = int(match.group(1)) if match else 1
            
            while current_page <= total_pages:
                # Wait for table to be present
                table = WebDriverWait(driver, wait_time).until(
                    EC.presence_of_element_located((By.ID, table_id))
                )
                
                # Extract headers
                rows = table.find_elements(By.TAG_NAME, 'tr')
                headers = [header.text for header in rows[0].find_elements(By.TAG_NAME, 'th')]
                
                # Add "Link" as a new header column if it's not already present
                if "Link" not in headers:
                    headers.append("Link")

                # Extract data from each row
                for row in rows[1:]:
                    columns = row.find_elements(By.TAG_NAME, 'td')
                    row_data = {}
                    for i, column in enumerate(columns):
                        row_data[headers[i]] = column.text
                    # Add the link to the row data
                    # Extract URL from the first column (the link)
                    link_element = columns[0].find_element(By.TAG_NAME, 'a')
                    if link_element:
                        row_data["Link"] = link_element.get_attribute('href')
                    table_data.append(row_data)
                
                print(f"Processed page {current_page} of {total_pages}")
                
                if current_page < total_pages:
                    # Scroll to bottom of page
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(2)  # Short pause to allow scroll to complete
                    
                    # Click next page button
                    next_button = WebDriverWait(driver, wait_time).until(
                        EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Next')]"))
                    )
                    next_button.click()
                    
                    # Wait for table to refresh
                    time.sleep(2)
                
                current_page += 1
                
        except TimeoutException:
            print(f"Timeout while processing page {current_page}")
        except NoSuchElementException as e:
            print(f"Element not found: {str(e)}")
        except Exception as e:
            print(f"An error occurred: {str(e)}")

        # Save the extracted data to a CSV file
        pd.DataFrame(table_data).to_csv("C:/Users/pulkit.kushwaha/Downloads/stock_analysis_screener_OTC_USA.csv", index=False)

    finally:
        # Stop the popup handler before quitting
        popup_handler.stop()
        driver.quit()

if __name__ == "__main__":
    main()