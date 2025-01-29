from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os

app = FastAPI()

# Directory to store downloaded files
DOWNLOAD_DIR = "/tmp/selenium_downloads"
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

# Chrome binary & driver paths (required for Render)
CHROME_BIN_PATH = os.getenv("GOOGLE_CHROME_BIN", "/usr/bin/google-chrome")
CHROMEDRIVER_PATH = os.getenv("CHROMEDRIVER_PATH", "/usr/local/bin/chromedriver")

@app.get("/download-export")
def download_export():
    try:
        # Configure Chrome options for headless mode
        chrome_options = webdriver.ChromeOptions()
        chrome_options.binary_location = CHROME_BIN_PATH
        chrome_options.add_argument("--headless")  
        chrome_options.add_argument("--disable-gpu")  
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("prefs", {
            "download.default_directory": DOWNLOAD_DIR,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        })

        # Initialize the WebDriver
        driver = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH, options=chrome_options)
        driver.get("https://utrees.arborgold.net/AG/#/login")
        time.sleep(3)

        # Login handling
        try:
            user_name_field = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "//input[@type='text']"))
            )
            user_name_field.send_keys("Lewis")

            password_input = driver.find_element(By.XPATH, "//input[@type='password']")
            password_input.send_keys("Hammersport2024!")

            login_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Login')]")
            login_btn.click()
            print("Logging in...")
            time.sleep(5)
        except:
            print("Already logged in, skipping login step.")

        # Navigate to jobs menu
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "sidenav_link_job"))
        ).click()
        print("Navigated to jobs menu")
        time.sleep(5)

        # Open filter popup
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Filter')]"))
        ).click()
        print("Opened filter popup")
        time.sleep(3)

        # Click the 'Filter' button
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "jobsFilterButton"))
        ).click()
        print("Clicked on the filter button")
        time.sleep(5)

        # Open export popup
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Export')]"))
        ).click()
        print("Opened export popup")

        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Export')]"))
        ).click()
        print("Clicked on the Export button")

        # Wait for the file to download dynamically
        timeout = 30  # Max time to wait for the download
        start_time = time.time()

        while time.time() - start_time < timeout:
            downloaded_files = os.listdir(DOWNLOAD_DIR)
            if downloaded_files:
                latest_file = max([os.path.join(DOWNLOAD_DIR, f) for f in downloaded_files], key=os.path.getctime)
                print(f"Downloaded file: {latest_file}")
                return FileResponse(latest_file, media_type="application/octet-stream", filename=os.path.basename(latest_file))
            time.sleep(2)  # Wait before checking again

        raise HTTPException(status_code=404, detail="Download failed or took too long.")

    except Exception as e:
        import traceback
        print(f"An error occurred: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

    finally:
        driver.quit()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
