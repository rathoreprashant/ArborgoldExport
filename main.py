from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import os

app = FastAPI()

DOWNLOAD_DIR = "/tmp/selenium_downloads"
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

@app.get("/download-export")
async def download_export():
    chrome_options = webdriver.ChromeOptions()
    
    # Path to the Google Chrome binary (ensure it's installed in the environment)
    chrome_options.binary_location = "/usr/bin/google-chrome-stable"  # Specify the path to Chrome binary

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

    # Initialize the Chrome WebDriver with the specified options
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    try:
        # Navigate to the login page
        driver.get("https://utrees.arborgold.net/AG/#/login")
        time.sleep(3)

        # Locate the username field and input data
        user_name_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@type='text']"))
        )
        user_name_field.send_keys("Lewis")

        # Locate the password field and input data
        password_input = driver.find_element(By.XPATH, "//input[@type='password']")
        password_input.send_keys("Hammersport2024!")

        # Locate and click the login button
        login_btn = driver.find_element(By.XPATH, "//button[contains(text(),'Login')]")
        login_btn.click()
        time.sleep(5)

        # Click the job menu
        job_menu = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "sidenav_link_job"))
        )
        job_menu.click()
        time.sleep(5)

        # Click the filter button to open the filter options
        job_filter = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Filter')]"))
        )
        job_filter.click()
        time.sleep(3)

        # Select the "Last Month" period in the filter
        period_dropdown = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//span[contains(text(),'Last Month')]"))
        )
        period_dropdown.click()

        # Click the filter button to apply the filter
        filter_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "jobsFilterButton"))
        )
        filter_button.click()
        time.sleep(5)

        # Open the export popup
        open_export_popup = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Export')]"))
        )
        open_export_popup.click()

        # Click the export option
        export_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//li/span[contains(text(),'Export')]"))
        )
        export_btn.click()

        # Wait for the download to complete
        time.sleep(20)

        # List the files in the download directory and return the latest one
        downloaded_files = os.listdir(DOWNLOAD_DIR)
        if not downloaded_files:
            raise HTTPException(status_code=404, detail="No files downloaded.")

        latest_file = max([os.path.join(DOWNLOAD_DIR, f) for f in downloaded_files], key=os.path.getctime)

        return FileResponse(latest_file, media_type="application/octet-stream", filename=os.path.basename(latest_file))

    except Exception as e:
        return {"error": str(e)}

    finally:
        driver.quit()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
