from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, WebDriverException
import time
import logging
import os
from datetime import datetime

# ------------------ CONFIG ------------------
EMPLOYER_NUMBER = "6419"
EMPLOYEE_NUMBER = "202"
PASSWORD = "0508"

CHROMEDRIVER_PATH = "C:/time_reporting/chromedriver-win64/chromedriver.exe"
LOG_FILE = os.path.join(os.path.dirname(__file__), "log_entry.txt")
# --------------------------------------------

# Setup logging
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def log_and_print(message, level="info"):
    """Helper function to log and print messages"""
    if level == "error":
        logging.error(message)
    else:
        logging.info(message)
    print(message)

# Setup Chrome options
options = Options()
options.add_argument("--start-maximized")

# Create WebDriver
try:
    service = Service(CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=options)
    log_and_print("✅ ChromeDriver started successfully.")
except WebDriverException as e:
    err_msg = str(e)
    if "This version of ChromeDriver only supports Chrome version" in err_msg:
        log_and_print("❌ ChromeDriver version mismatch detected! Please update ChromeDriver to match your Chrome version.", "error")
    else:
        log_and_print(f"❌ Failed to start ChromeDriver: {e}", "error")
    raise SystemExit("Error: Could not start ChromeDriver. Check path or Chrome version.")

try:
    driver.get("https://c.timewatch.co.il/punch/punch.php")
    time.sleep(2)
    log_and_print("🌐 Opened TimeWatch punch page.")

    try:
        driver.find_element(By.ID, "login-comp-input").send_keys(EMPLOYER_NUMBER)
        driver.find_element(By.ID, "login-name-input").send_keys(EMPLOYEE_NUMBER)
        driver.find_element(By.ID, "login-pw-input").send_keys(PASSWORD)
        log_and_print("🧾 Filled login form.")
    except NoSuchElementException as e:
        log_and_print(f"❌ Login fields not found: {e}", "error")
        raise

    try:
        driver.find_element(By.CLASS_NAME, "btn-custom").click()
        log_and_print("🔐 Clicked login button.")
    except NoSuchElementException as e:
        log_and_print(f"❌ Login button not found: {e}", "error")
        raise

    time.sleep(3)

    try:
        entry_button = driver.find_element(By.CLASS_NAME, "entry-btn")
        entry_button.click()
        log_and_print(f"✅ Clock-in successful at {datetime.now().strftime('%H:%M:%S')}.")
    except NoSuchElementException as e:
        log_and_print(f"❌ Entry button not found: {e}", "error")
        raise

    time.sleep(3)
    driver.save_screenshot("logged_in.png")
    log_and_print("📸 Screenshot saved as logged_in.png.")

except Exception as e:
    log_and_print(f"⚠️ Unexpected error occurred: {e}", "error")

finally:
    driver.quit()
    log_and_print("🧹 Browser closed.")
