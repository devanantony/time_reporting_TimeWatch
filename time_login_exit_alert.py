import requests
import zipfile
import io
import shutil
import subprocess
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
import time
import logging
import os
import sys
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

def safe_print(message):
    """Print safely when running with a console, including Unicode messages."""
    if sys.stdout is None:
        return
    try:
        print(message)
    except UnicodeEncodeError:
        encoding = getattr(sys.stdout, "encoding", None) or "utf-8"
        try:
            safe_message = str(message).encode(encoding, errors="replace").decode(
                encoding, errors="replace"
            )
            print(safe_message)
        except Exception:
            pass


# Use UTF-8 for redirected output where streams are available.
for _stream in (sys.stdout, sys.stderr):
    if _stream is not None and hasattr(_stream, "reconfigure"):
        try:
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except (OSError, ValueError):
            pass


# ================== CONFIG ==================
EMPLOYER_NUMBER = "6419"
EMPLOYEE_NUMBER = "202"
PASSWORD = "0508"

BASE_DIR = os.path.dirname(__file__)
CHROMEDRIVER_DIR = os.path.join(BASE_DIR, "chromedriver")
CHROMEDRIVER_PATH = os.path.join(
    CHROMEDRIVER_DIR, "chromedriver-win64", "chromedriver.exe"
)

LOG_FILE = os.path.join(BASE_DIR, "log_exit.txt")
SCREENSHOT_PATH = os.path.join(BASE_DIR, "logged_out.png")

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "devan.antony@gmail.com"
SENDER_PASSWORD = "tcbtqlwojhwrqdvi"
RECIPIENT_EMAIL = "devanantony@yahoo.com.sg"
# ============================================
logging.basicConfig(
    filename=LOG_FILE,
    encoding="utf-8",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ========== CHROME VERSION ==========
def get_installed_chrome_version():
    try:
        output = subprocess.check_output(
            r'reg query "HKEY_CURRENT_USER\Software\Google\Chrome\BLBeacon" /v version',
            shell=True, text=True
        )
        return output.split("REG_SZ")[-1].strip()
    except Exception:
        return None

# ========== DOWNLOAD MATCHING CHROMEDRIVER ==========
def download_matching_chromedriver(chrome_version):
    major = chrome_version.split(".")[0]
    safe_print(f"🔍 Installed Chrome version: {chrome_version}")
    safe_print(f"🔍 Fetching ChromeDriver for major version: {major}")

    url = "https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json"

    try:
        versions = requests.get(url, timeout=15).json()["versions"]

        match = next(
            v for v in reversed(versions)
            if v["version"].startswith(major + ".")
        )

        driver_url = next(
            d["url"] for d in match["downloads"]["chromedriver"]
            if d["platform"] == "win64"
        )

        safe_print(f"⬇️ Downloading ChromeDriver from:\n{driver_url}")

        zip_data = requests.get(driver_url, timeout=30).content

        if os.path.exists(CHROMEDRIVER_DIR):
            shutil.rmtree(CHROMEDRIVER_DIR)
        os.makedirs(CHROMEDRIVER_DIR)

        with zipfile.ZipFile(io.BytesIO(zip_data)) as z:
            z.extractall(CHROMEDRIVER_DIR)

        return True

    except Exception as e:
        safe_print(f"❌ ChromeDriver download failed: {e}")
        return False

# ========== EMAIL ==========
def send_email_alert(subject, message, attachments=None):
    try:
        msg = MIMEMultipart()
        msg["From"] = SENDER_EMAIL
        msg["To"] = RECIPIENT_EMAIL
        msg["Subject"] = subject
        msg.attach(MIMEText(message, "plain"))

        for file_path in attachments or []:
            if os.path.exists(file_path):
                with open(file_path, "rb") as f:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header(
                    "Content-Disposition",
                    f'attachment; filename="{os.path.basename(file_path)}"'
                )
                msg.attach(part)

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)

    except Exception as e:
        safe_print(f"❌ Email failed: {e}")

def log_and_print(message, error=False, success=False):
    safe_print(message)
    if error:
        logging.error(message)
        send_email_alert("⚠️ TimeWatch Script Error", message, [LOG_FILE])
    else:
        logging.info(message)
        if success:
            send_email_alert(
                "✅ TimeWatch Exit Successful",
                message,
                [SCREENSHOT_PATH, LOG_FILE]
            )

# ========== START DRIVER ==========
def start_driver():
    options = Options()
    options.add_argument("--start-maximized")

    try:
        return webdriver.Chrome(
            service=Service(CHROMEDRIVER_PATH),
            options=options
        )

    except WebDriverException:
        safe_print("⚠️ ChromeDriver mismatch detected")

        chrome_version = get_installed_chrome_version()
        logging.info(f"Installed Chrome: {chrome_version}")
        if not chrome_version:
            raise RuntimeError("❌ Could not detect Chrome version")

        if not download_matching_chromedriver(chrome_version):
            raise RuntimeError("❌ ChromeDriver update failed")

        safe_print("🔁 Retrying ChromeDriver startup...")
        return webdriver.Chrome(
            service=Service(CHROMEDRIVER_PATH),
            options=options
        )

# ================== MAIN ==================
driver = None

try:
    driver = start_driver()
    log_and_print("✅ ChromeDriver started")

    driver.get("https://c.timewatch.co.il/punch/punch.php")
    time.sleep(2)

    driver.find_element(By.ID, "login-comp-input").send_keys(EMPLOYER_NUMBER)
    driver.find_element(By.ID, "login-name-input").send_keys(EMPLOYEE_NUMBER)
    driver.find_element(By.ID, "login-pw-input").send_keys(PASSWORD)
    driver.find_element(By.CLASS_NAME, "btn-custom").click()

    time.sleep(3)
    driver.find_element(By.CLASS_NAME, "exit-btn").click()
    time.sleep(3)

    driver.save_screenshot(SCREENSHOT_PATH)

    log_and_print(
        f"✅ Clock-out successful at {datetime.now().strftime('%H:%M:%S')}",
        success=True
    )

except Exception as e:
    log_and_print(f"❌ Script failed: {e}", error=True)

finally:
    if driver:
        driver.quit()
    log_and_print("🧹 Browser closed")
