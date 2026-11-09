# TimeWatch Time Reporting Automation

This project automates clock-in and clock-out actions for a TimeWatch-based time reporting system using Python, Selenium, and Chrome/ChromeDriver. It includes a simple desktop UI, a daily scheduler, and helper scripts that trigger entry/exit actions automatically.

## Overview

The repository contains a small Windows-focused workflow for:

- logging into the TimeWatch website,
- recording a work session start,
- recording a work session end,
- capturing screenshots,
- emailing success or failure notifications,
- scheduling the actions automatically during the day.

## Project structure

```text
.
├── entry.bat                  # Runs the entry script manually
├── exit.bat                   # Runs the exit script manually
├── refresh.ico                # App icon used by the UI
├── time_login_entry_alert.py   # Logs in and triggers the entry action
├── time_login_exit_alert.py    # Logs in and triggers the exit action
├── time_login_scheduler.py     # Daily scheduler that triggers login/logout at set times
├── time_report_ui.py           # GUI to trigger entry/exit actions manually
├── README.md                  # Project documentation
└── .gitignore                 # Git ignore rules
```

## Main scripts

### `time_login_entry_alert.py`
Runs a Selenium browser session against the TimeWatch punch page, logs in with configured credentials, clicks the entry button, saves a screenshot, and sends an email result alert.

### `time_login_exit_alert.py`
Same flow as the entry script, but clicks the exit button and records a logout event.

### `time_login_scheduler.py`
Continuously checks the current time and creates a daily schedule. It calculates a random login time within a time window and then schedules a logout based on the configured delay.

### `time_report_ui.py`
Provides a simple custom tkinter desktop interface with Login and Logout buttons for manual execution.

### `entry.bat` and `exit.bat`
Windows batch wrappers for running the related Python scripts directly.

## Prerequisites

- Windows 10 or Windows 11
- Python 3.9+
- Google Chrome installed
- ChromeDriver compatible with the installed Chrome version
- Access to the TimeWatch site used by your workplace

## Dependencies

Install the required Python packages:

```bash
pip install selenium requests customtkinter
```

If ChromeDriver is not already installed or is mismatched, the scripts can download a matching version automatically. However, the capability depends on network access and the browser version being readable from the local machine.

## Configuration

Before using the scripts, update the configuration values in the following files:

- `time_login_entry_alert.py`
- `time_login_exit_alert.py`

Look for the configuration block near the top of each file and update:

- employer number
- employee number
- password

Email settings are read from environment variables by both alert scripts:

| Variable | Required | Default / purpose |
|---|---:|---|
| `TIMEWATCH_SENDER_EMAIL` | Yes | SMTP account used to send alerts |
| `TIMEWATCH_SENDER_PASSWORD` | Yes | SMTP password or provider app password |
| `TIMEWATCH_RECIPIENT_EMAIL` | Yes | Address that receives alerts |
| `TIMEWATCH_SMTP_SERVER` | No | SMTP host; defaults to `smtp.gmail.com` |
| `TIMEWATCH_SMTP_PORT` | No | SMTP port; defaults to `587` (STARTTLS) |

For Gmail, use an app password if the account requires one; a regular account
password may not be accepted. Configure these values in Windows Environment
Variables before starting the script, GUI, or scheduler. Restart already-running
processes after changing environment variables so they inherit the new settings.
The scripts log missing settings and SMTP delivery errors to `log_entry.txt` or
`log_exit.txt`; successful delivery is also recorded there.

Do not commit or share real credentials in a public repository. If an SMTP
password was previously stored in source code or committed, revoke it and create
a replacement before configuring the environment variables.

## Usage

### Run the GUI manually

```bash
python time_report_ui.py
```

This opens a small Time Reporting Control window with Login and Logout actions.

### Run the entry script directly

```bash
python time_login_entry_alert.py
```

### Run the exit script directly

```bash
python time_login_exit_alert.py
```

### Run the scheduler

```bash
python time_login_scheduler.py
```

The scheduler runs continuously in the background and triggers the login/logout automation based on the saved daily schedule.

### Run via batch files on Windows

```bat
entry.bat
```

```bat
exit.bat
```

## Behavior notes

- The scheduler creates a fresh daily schedule when the date changes.
- The login time is randomized within the configured morning window.
- The logout time is computed relative to the login event and the configured delay.
- Each script captures a screenshot and logs activity to a text log file in the project folder.
- Success and error notifications are sent by email when configured.

## Files created during runtime

The scripts may generate files such as:

- `time_login_scheduler.log`
- `time_login_scheduler_state.txt`
- `logged_in.png`
- `logged_out.png`
- `log_entry.txt`
- `log_exit.txt`
- browser-related ChromeDriver folders under a `chromedriver` directory

## Security and operational notes

- This project uses hard-coded credentials and SMTP credentials in the source files.
- For production or shared environments, move secrets to environment variables or a secure configuration file.
- The scripts are designed for a personal Windows workstation workflow and rely on a specific website structure.
- Any website changes may require updating selectors such as `By.ID`, `By.CLASS_NAME`, and button names.

## Limitations

- Windows-specific assumptions are hard-coded.
- ChromeDriver version matching is performed automatically but still depends on the browser being installed and accessible.
- The project does not include automated tests.
- The selectors may break if the TimeWatch site changes its HTML.

## License

No explicit license file is included in this repository. Please check with the repository owner before redistributing or reusing this project in another environment.
