import customtkinter as ctk
import subprocess
import os
from tkinter import messagebox

# ---------- CONFIG ----------
LOGIN_SCRIPT = r"C:\00\00_PyA\time_reporting\time_login_entry_alert.py"
LOGOUT_SCRIPT = r"C:\00\00_PyA\time_reporting\time_login_exit_alert.py"

# ---------- FUNCTION ----------
def run_script(script_path, action_name):
    """Run external Python script."""
    if not os.path.exists(script_path):
        messagebox.showerror("Error", f"Script not found:\n{script_path}")
        return

    try:
        subprocess.Popen(["python", script_path], shell=True)
        messagebox.showinfo("Success", f"{action_name} triggered successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to run {action_name.lower()}:\n{e}")

# ---------- UI SETUP ----------
ctk.set_appearance_mode("System")  # Options: "System", "Dark", "Light"
ctk.set_default_color_theme("blue")  # You can try "green", "dark-blue" etc.

root = ctk.CTk()
root.title("⏱️ Time Reporting Control")
root.geometry("400x300")
root.resizable(False, False)

# ---------- LAYOUT ----------
frame = ctk.CTkFrame(master=root, corner_radius=15)
frame.pack(padx=20, pady=20, fill="both", expand=True)

title_label = ctk.CTkLabel(frame, text="Time Reporting Control", font=ctk.CTkFont(size=20, weight="bold"))
title_label.pack(pady=(20, 10))

subtitle_label = ctk.CTkLabel(frame, text="Manage your work sessions", font=ctk.CTkFont(size=14))
subtitle_label.pack(pady=(0, 20))

# Buttons
btn_login = ctk.CTkButton(
    frame, text="Login", width=200, height=45, fg_color="#2E8B57", hover_color="#3CB371",
    font=ctk.CTkFont(size=16, weight="bold"),
    command=lambda: run_script(LOGIN_SCRIPT, "Login")
)
btn_login.pack(pady=10)

btn_logout = ctk.CTkButton(
    frame, text="Logout", width=200, height=45, fg_color="#B22222", hover_color="#CD5C5C",
    font=ctk.CTkFont(size=16, weight="bold"),
    command=lambda: run_script(LOGOUT_SCRIPT, "Logout")
)
btn_logout.pack(pady=10)

# Exit button
btn_exit = ctk.CTkButton(
    frame, text="Exit", width=100, height=35, fg_color="#444", hover_color="#666",
    command=root.destroy
)
btn_exit.pack(pady=(20, 10))

# ---------- START ----------
root.mainloop()
