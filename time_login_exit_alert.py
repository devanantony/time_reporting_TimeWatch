import requests
import zipfile
import io
import shutil
import subprocess
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, WebDriverException
import time
import logging
import os
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

# ------------------ CONFIG ------------------
EMPLOYER_NUMBER = "6419"
EMPLOYEE_NUMBER = "202"
PASSWORD = "0508"

CHROMEDRIVER_DIR = "C:/00/00_PyA/time_reporting/chromedriver-win64/"
CHROMEDRIVER_PATH = os.path.join(CHROMEDRIVER_DIR, "chromedriver.exe")

LOG_FILE = os.path.join(os.path.dirname(__file__), "log_exit.txt")
SCREENSHOT_PATH = os.path.join(os.path.dirname(__file__), "logged_out.png")

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "devan.antony@gmail.com"
SENDER_PASSWORD = "tcbtqlwojhwrqdvi"
RECIPIENT_EMAIL = "devanantony@yahoo.com.sg"
# --------------------------------------------
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ---------------- AUTO UPDATE CHROMEDRIVER ------------------
def get_installed_chrome_version():
    """Reads installed Chrome version from registry"""
    try:
        output = subprocess.check_output(
            r'reg query "HKEY_CURRENT_USER\Software\Google\Chrome\BLBeacon" /v version',
            shell=True, text=True)
        version = output.split("REG_SZ")[-1].strip()
        return version
    except Exception:
        return None

def download_latest_matching_chromedriver(chrome_version):
    """Download ChromeDriver that matches installed Chrome"""
    major_version = chrome_version.split(".")[0]
    print(f"🔍 Installed Chrome version: {chrome_version}")
    print(f"🔍 Fetching ChromeDriver for major version: {major_version}")

    # Google Chrome for Testing API
    url = "https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json"

    try:
        data = requests.get(url).json()
        stable = data["channels"]["Stable"]["downloads"]["chromedriver"]

        # Pick Windows version
        for item in stable:
            if "win64" in item["platform"]:
                driver_url = item["url"]
                break

        print(f"⬇️ Downloading ChromeDriver from: {driver_url}")

        zip_content = requests.get(driver_url).content
        with zipfile.ZipFile(io.BytesIO(zip_content)) as z:
            # Clear old directory
            if os.path.exists(CHROMEDRIVER_DIR):
                shutil.rmtree(CHROMEDRIVER_DIR)
            os.makedirs(CHROMEDRIVER_DIR)

            z.extractall(CHROMEDRIVER_DIR)

        print("✅ ChromeDriver updated successfully.")
        return True

    except Exception as e:
        print(f"❌ Failed to download ChromeDriver: {e}")
        return False

# ------------------------------------------------------------
def send_email_alert(subject, message, attachments=None):
    try:
        msg = MIMEMultipart()
        msg["From"] = SENDER_EMAIL
        msg["To"] = RECIPIENT_EMAIL
        msg["Subject"] = subject
        msg.attach(MIMEText(message, "plain"))

        if attachments:
            for file_path in attachments:
                if os.path.exists(file_path):
                    with open(file_path, "rb") as f:
                        part = MIMEBase("application", "octet-stream")
                        part.set_payload(f.read())
                    encoders.encode_base64(part)
                    part.add_header(
                        "Content-Disposition",
                        f"attachment; filename={os.path.basename(file_path)}"
                    )
                    msg.attach(part)

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
    except Exception as e:
        print(f"❌ Email sending failed: {e}")

def log_and_print(message, level="info", alert=False, success=False):
    if level == "error":
        logging.error(message)
        print(message)
        if alert:
            send_email_alert("⚠️ TimeWatch Exit Script Failure", message, attachments=[LOG_FILE])
    elif success:
        logging.info(message)
        print(message)
        send_email_alert("✅ TimeWatch Exit Successful", message, attachments=[SCREENSHOT_PATH, LOG_FILE])
    else:
        logging.info(message)
        print(message)

# ------------------ START DRIVER ------------------
def start_driver_with_auto_update():
    options = Options()
    options.add_argument("--start-maximized")

    try:
        service = Service(CHROMEDRIVER_PATH)
        return webdriver.Chrome(service=service, options=options)

    except WebDriverException as e:
        if "only supports Chrome version" in str(e):
            print("⚠️ ChromeDriver version mismatch detected.")
            chrome_version = get_installed_chrome_version()

            if chrome_version:
                if download_latest_matching_chromedriver(chrome_version):
                    print("🔁 Retrying driver start...")
                    service = Service(CHROMEDRIVER_PATH)
                    return webdriver.Chrome(service=service, options=options)

        raise e

# ------------------ MAIN SCRIPT ------------------
try:
    driver = start_driver_with_auto_update()
    log_and_print("✅ ChromeDriver started successfully.")

    driver.get("https://c.timewatch.co.il/punch/punch.php")
    time.sleep(2)
    log_and_print("🌐 Opened TimeWatch punch page.")

    driver.find_element(By.ID, "login-comp-input").send_keys(EMPLOYER_NUMBER)
    driver.find_element(By.ID, "login-name-input").send_keys(EMPLOYEE_NUMBER)
    driver.find_element(By.ID, "login-pw-input").send_keys(PASSWORD)
    log_and_print("🧾 Filled login form.")

    driver.find_element(By.CLASS_NAME, "btn-custom").click()
    log_and_print("🔐 Clicked login button.")

    time.sleep(3)

    exit_button = driver.find_element(By.CLASS_NAME, "exit-btn")
    exit_button.click()

    time.sleep(3)
    driver.save_screenshot(SCREENSHOT_PATH)

    success_msg = f"✅ Clock-out successful at {datetime.now().strftime('%H:%M:%S')}."
    log_and_print(success_msg, success=True)

except Exception as e:
    log_and_print(f"⚠️ Unexpected error occurred: {e}", "error", alert=True)

finally:
    try:
        driver.quit()
    except:
        pass
    log_and_print("🧹 Browser closed.")
