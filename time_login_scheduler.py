import os
import sys
import time
import random
import logging
import subprocess
from datetime import datetime, timedelta, time as dt_time
from pathlib import Path

# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent

LOGIN_SCRIPT = BASE_DIR / "time_login_entry_alert.py"
LOGOUT_SCRIPT = BASE_DIR / "time_login_exit_alert.py"

LOG_FILE = BASE_DIR / "time_login_scheduler.log"
STATE_FILE = BASE_DIR / "time_login_scheduler_state.txt"

CHECK_INTERVAL = 10  # seconds

START_TIME = dt_time(7, 0)
END_TIME = dt_time(8, 0)
EXIT_DELAY_HOURS = 9

# --------------------------------------------------
# LOGGING
# --------------------------------------------------
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# --------------------------------------------------
# STATE MANAGEMENT
# --------------------------------------------------
def load_state():
    if STATE_FILE.exists():
        try:
            import json
            with open(STATE_FILE, "r") as f:
                return json.load(f)
        except Exception:
            logging.exception("Could not read state file")

    return {}

def save_state(state):
    import json
    temp_file = STATE_FILE.with_suffix(".tmp")

    with open(temp_file, "w") as f:
        json.dump(state, f, indent=4)

    os.replace(temp_file, STATE_FILE)

# --------------------------------------------------
# SCRIPT EXECUTION
# --------------------------------------------------
def execute_script(script_path, event_name, state):
    if not script_path.exists():
        logging.error("%s script not found: %s", event_name, script_path)
        return False

    try:
        logging.info("TRIGGERING %s: %s", event_name, script_path.name)

        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=str(BASE_DIR),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace"
        )

        logging.info(
            "%s completed with exit code %s",
            event_name,
            result.returncode
        )

        if result.stdout:
            logging.info("%s stdout: %s", event_name, result.stdout.strip())

        if result.stderr:
            logging.error("%s stderr: %s", event_name, result.stderr.strip())

        return result.returncode == 0

    except Exception:
        logging.exception("Failed to execute %s", event_name)
        return False

# --------------------------------------------------
# MAIN SCHEDULER
# --------------------------------------------------
def main():
    logging.info("Time login scheduler started")

    last_weekend_log_date = None

    while True:
        now = datetime.now()

        # Monday=0 ... Friday=4, Saturday=5, Sunday=6.
        # Keep the scheduler alive, but do not create or execute schedules
        # on weekends. This also protects against a Friday-started process
        # that remains running through Saturday and Sunday.
        if now.weekday() >= 5:
            weekend_date = now.date().isoformat()
            if last_weekend_log_date != weekend_date:
                logging.info(
                    "Weekend detected (%s). Login/logout scheduling is disabled.",
                    now.strftime("%A %Y-%m-%d")
                )
                last_weekend_log_date = weekend_date

            time.sleep(CHECK_INTERVAL)
            continue

        today = now.date().isoformat()

        state = load_state()

        # New day: create a fresh schedule
        if state.get("date") != today:
            random_minutes = random.randint(0, 60)

            login_time = datetime.combine(
                now.date(), START_TIME
            ) + timedelta(minutes=random_minutes)

            logout_time = login_time + timedelta(hours=EXIT_DELAY_HOURS)

            state = {
                "date": today,
                "login_time": login_time.isoformat(),
                "logout_time": logout_time.isoformat(),
                "login_done": False,
                "logout_done": False,
                "pending_exit_logged": False
            }
            save_state(state)

            logging.info(
                "New schedule: Login=%s | Logout=%s",
                login_time,
                logout_time
            )

        login_time = datetime.fromisoformat(state["login_time"])
        logout_time = datetime.fromisoformat(state["logout_time"])
        if (
            state.get("login_done")
            and not state.get("logout_done")
            and not state.get("pending_exit_logged", False)
        ):
            logging.info(
                "PENDING EXIT | Expected logout time: %s",
                logout_time.strftime("%Y-%m-%d %H:%M:%S")
            )
            state["pending_exit_logged"] = True
            save_state(state)

        # LOGIN TRIGGER
        if not state.get("login_done") and now >= login_time:
            state["login_done"] = True
            save_state(state)

            login_success = execute_script(
                LOGIN_SCRIPT, "LOGIN ENTRY", state
            )

            if login_success:
                logging.info(
                    "LOGIN ENTRY SUCCESSFUL | Next expected EXIT: %s",
                    logout_time.strftime("%Y-%m-%d %H:%M:%S")
                )
            else:
                logging.error(
                    "LOGIN ENTRY FAILED | Expected EXIT remains scheduled for: %s",
                    logout_time.strftime("%Y-%m-%d %H:%M:%S")
                )

        # LOGOUT TRIGGER
        if (
            state.get("login_done")
            and not state.get("logout_done")
            and now >= logout_time
        ):
            state["logout_done"] = True
            save_state(state)

            execute_script(
                LOGOUT_SCRIPT, "LOGIN EXIT", state
            )

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.info("Scheduler stopped manually")
