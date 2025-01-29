from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
import time
import os
import logging

# Initialize logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# FastAPI app initialization
app = FastAPI()

# Directory to save downloaded files
DOWNLOAD_DIR = "/tmp/selenium_downloads"
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

@app.get("/download-export")
async def download_export():
    logger.info("Starting the export download process.")
    
    # Setup Chrome options
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.add_experimental_option("prefs", {
        "download.default_directory": DOWNLOAD_DIR,
        "download.prompt_for_download": False,
        "safebrowsing.enabled": True
    })

    try:
        # Initialize WebDriver
        logger.debug("Initializing WebDriver with ChromeService.")
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)

        # Navigate to the login page
        logger.debug("Navigating to the login page.")
        driver.get("https://utrees.arborgold.net/AG/#/login")
        time.sleep(3)

        # Log in process
        logger.debug("Entering username and password.")
        user_name_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@type='text']"))
        )
        user_name_field.send_keys("Lewis")

        password_input = driver.find_element(By.XPATH, "//input[@type='password']")
        password_input.send_keys("Hammersport2024!")

        login_btn = driver.find_element(By.XPATH, "//button[contains(text(),'Login')]")
        login_btn.click()
        time.sleep(5)

        # Open job menu
        logger.debug("Navigating to the job menu.")
        job_menu = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "sidenav_link_job"))
        )
        job_menu.click()
        time.sleep(5)

        # Apply filter
        logger.debug("Clicking the filter button.")
        job_filter = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Filter')]"))
        )
        job_filter.click()
        time.sleep(3)

        # Selecting period filter option
        logger.debug("Selecting period dropdown option.")
        period_dropdown = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//span[contains(text(),'Last Month')]"))
        )
        period_dropdown.click()

        filter_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "jobsFilterButton"))
        )
        filter_button.click()
        time.sleep(5)

        # Open export popup and select export
        logger.debug("Opening export popup and selecting export option.")
        open_export_popup = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Export')]"))
        )
        open_export_popup.click()

        export_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//li/span[contains(text(),'Export')]"))
        )
        export_btn.click()

        # Wait for download to complete
        logger.debug("Waiting for the download to complete.")
        time.sleep(20)

        # Check if files have been downloaded
        downloaded_files = os.listdir(DOWNLOAD_DIR)
        if not downloaded_files:
            logger.error("No files were downloaded.")
            raise HTTPException(status_code=404, detail="No files downloaded.")

        # Get the latest downloaded file
        latest_file = max([os.path.join(DOWNLOAD_DIR, f) for f in downloaded_files], key=os.path.getctime)
        logger.debug(f"Downloaded file: {latest_file}")

        # Return the file response
        return FileResponse(latest_file, media_type="application/octet-stream", filename=os.path.basename(latest_file))

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return {"error": str(e)}

    finally:
        # Clean up the WebDriver
        logger.debug("Closing the WebDriver.")
        driver.quit()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
