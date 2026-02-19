import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import threading
import queue
import time
from datetime import datetime

# =========================
# Password hashing (built-in)
# =========================
import hashlib
import secrets

def hash_password(password: str, salt: str | None = None) -> str:
    """
    Returns a string like: "salt$hash"
    Uses SHA-256 for simplicity (good enough for class projects).
    For production: use bcrypt/argon2.
    """
    if salt is None:
        salt = secrets.token_hex(16)
    digest = hashlib.sha256((salt + password).encode("utf-8")).hexdigest()
    return f"{salt}${digest}"

def verify_password(stored: str, password: str) -> bool:
    """
    stored: "salt$hash"
    """
    try:
        salt, _ = stored.split("$", 1)
    except ValueError:
        return False
    return hash_password(password, salt) == stored


# Sensor backend (your motion.py supports Mac fake mode + Pi real mode)
from motion import start_motion_system, detect_mail_once


# =========================
# User storage (users.json)
# =========================
class UserData:
    def __init__(self, filename='users.json'):
        self.filename = filename
        self.users = self.load_users()

    def load_users(self):
        """
        Supports two formats:
        OLD: {"alice": "15551234567"}
        NEW: {"alice": {"phone": "15551234567", "password": "salt$hash"}}
        """
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as f:
                    data = json.load(f)

                # --- Auto-upgrade old format to new format ---
                if isinstance(data, dict):
                    upgraded = {}
                    changed = False
                    for username, value in data.items():
                        if isinstance(value, str):
                            # old format: phone string only
                            upgraded[username] = {"phone": value, "password": ""}
                            changed = True
                        elif isinstance(value, dict):
                            upgraded[username] = {
                                "phone": value.get("phone", ""),
                                "password": value.get("password", "")
                            }
                        else:
                            upgraded[username] = {"phone": "", "password": ""}

                    if changed:
                        # write upgraded structure back to disk
                        self.users = upgraded
                        self.save_users()
                    return upgraded

            except Exception:
                return {}
        return {}

    def save_users(self):
        with open(self.filename, 'w') as f:
            json.dump(self.users, f, indent=4)

    # ---------- NEW/CHANGED ----------
    def add_user(self, username, phone_number, password_plain: str):
        self.users[username] = {
            "phone": phone_number,
            "password": hash_password(password_plain)
        }
        self.save_users()

    # ---------- NEW ----------
    def user_exists(self, username):
        return username in self.users

    def get_phone(self, username):
        user = self.users.get(username)
        if isinstance(user, dict):
            return user.get("phone")
        return None

    # ---------- NEW ----------
    def verify_login(self, username, password_plain: str) -> bool:
        user = self.users.get(username)
        if not isinstance(user, dict):
            return False
        stored = user.get("password", "")
        if not stored:
            # user exists but no password set (from old format upgrade)
            return False
        return verify_password(stored, password_plain)

    # ---------- NEW ----------
    def set_password(self, username, password_plain: str):
        if username in self.users and isinstance(self.users[username], dict):
            self.users[username]["password"] = hash_password(password_plain)
            self.save_users()

    # ---------- NEW/CHANGED ----------
    def update_phone(self, username, phone_number):
        if username in self.users and isinstance(self.users[username], dict):
            self.users[username]["phone"] = phone_number
            self.save_users()


# =========================
# Mail history storage
# =========================
HISTORY_FILE = "mail_history.json"


def load_mail_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
        except Exception:
            pass
    return []


def save_mail_history(history_list):
    try:
        with open(HISTORY_FILE, "w") as f:
            json.dump(history_list, f, indent=2)
    except Exception:
        pass


# =========================
# App
# =========================
class LoginApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SmartMailbox System")
        self.root.geometry("900x600")

        # Center window
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

        self.user_data = UserData()
        self.current_user = None

        # Mail notification state
        self.sensor_queue = queue.Queue()
        self.mail_history = []
        self.sensor_thread_started = False
        self.last_trigger_time = 0
        self.COOLDOWN = 60  # seconds

        self.show_login_screen()

    # ---------- UI helpers ----------
    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    # ---------- Login/Register screen ----------
    def show_login_screen(self):
        self.clear_window()

        self.sensor_thread_started = False  # prevent double thread when logging in/out
        self.current_user = None

        container = tk.Frame(self.root)
        container.pack(expand=True)

        title_label = tk.Label(container, text="Login / Register", font=("Arial", 18, "bold"))
        title_label.pack(pady=20)

        # username
        username_frame = tk.Frame(container)
        username_frame.pack(pady=10)
        tk.Label(username_frame, text="Username:").pack(side=tk.LEFT, padx=5)
        self.username_entry = tk.Entry(username_frame, width=30)
        self.username_entry.pack(side=tk.LEFT)

        # phone number
        phone_frame = tk.Frame(container)
        phone_frame.pack(pady=10)
        tk.Label(phone_frame, text="Phone Number:").pack(side=tk.LEFT, padx=5)
        self.phone_entry = tk.Entry(phone_frame, width=30)
        self.phone_entry.pack(side=tk.LEFT)

        # ---------- NEW: password ----------
        pass_frame = tk.Frame(container)
        pass_frame.pack(pady=10)
        tk.Label(pass_frame, text="Password:").pack(side=tk.LEFT, padx=5)
        self.password_entry = tk.Entry(pass_frame, width=30, show="*")
        self.password_entry.pack(side=tk.LEFT)

        # Optional: show/hide checkbox
        self.show_pass_var = tk.BooleanVar(value=False)

        def toggle_password():
            self.password_entry.config(show="" if self.show_pass_var.get() else "*")

        tk.Checkbutton(container, text="Show password", variable=self.show_pass_var,
                       command=toggle_password).pack()

        # buttons
        button_frame = tk.Frame(container)
        button_frame.pack(pady=20)

        login_btn = tk.Button(button_frame, text="Login",
                              command=self.login,
                              bg="lightgreen",
                              width=12)
        login_btn.pack(side=tk.LEFT, padx=10)

        register_btn = tk.Button(button_frame, text="Register",
                                 command=self.register,
                                 bg="lightblue",
                                 width=12)
        register_btn.pack(side=tk.LEFT, padx=10)

        self.status_label = tk.Label(container, text="", fg="red")
        self.status_label.pack(pady=5)

    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()  # NEW

        if not username:
            self.status_label.config(text="need a username")
            return

        if not password:
            self.status_label.config(text="need a password")
            return

        if self.user_data.user_exists(username):
            # NEW: verify password
            if self.user_data.verify_login(username, password):
                self.current_user = username
                self.show_dashboard()
            else:
                # If user was upgraded from old format and has no password
                user = self.user_data.users.get(username, {})
                if isinstance(user, dict) and not user.get("password"):
                    self.status_label.config(text="password not set for this user (re-register or set password)")
                else:
                    self.status_label.config(text="wrong password")
        else:
            self.status_label.config(text="user not found")

    def register(self):
        username = self.username_entry.get().strip()
        phone = self.phone_entry.get().strip()
        password = self.password_entry.get().strip()  # NEW

        if not username:
            self.status_label.config(text="need a username")
            return

        if not phone:
            self.status_label.config(text="need a phone number")
            return

        clean_phone = phone.replace(" ", "").replace("-", "").replace("+", "")
        if not clean_phone.isdigit():
            self.status_label.config(text="phone should be numbers")
            return

        # NEW: require password
        if not password:
            self.status_label.config(text="need a password")
            return
        if len(password) < 4:
            self.status_label.config(text="password too short (min 4 chars)")
            return

        if self.user_data.user_exists(username):
            self.status_label.config(text="username already exists")
            return

        # CHANGED: add_user now stores password hash
        self.user_data.add_user(username, phone, password)
        self.current_user = username

        messagebox.showinfo("Success", f"user '{username}' registered!")
        self.show_dashboard()

    # ---------- Dashboard (phone + notifications) ----------
    def show_dashboard(self):
        self.clear_window()

        # Top bar
        top = tk.Frame(self.root)
        top.pack(fill="x", padx=20, pady=15)

        tk.Label(top, text=f"📬 SmartMailbox Dashboard", font=("Arial", 18, "bold")).pack(side="left")
        tk.Button(top, text="Logout", command=self.logout, bg="salmon", width=12).pack(side="right")

        # User info row
        info = tk.Frame(self.root)
        info.pack(fill="x", padx=20, pady=10)

        tk.Label(info, text=f"Welcome, {self.current_user}!", font=("Arial", 14)).pack(side="left")

        current_phone = self.user_data.get_phone(self.current_user) or "(none)"
        tk.Label(info, text=f"Phone: {current_phone}", fg="blue", font=("Arial", 12)).pack(side="right")

        # Update phone row
        update = tk.Frame(self.root)
        update.pack(fill="x", padx=20, pady=10)

        tk.Label(update, text="New phone:").pack(side="left", padx=5)
        self.new_phone_entry = tk.Entry(update, width=25)
        self.new_phone_entry.pack(side="left", padx=5)
        tk.Button(update, text="Update", command=self.update_phone, bg="orange").pack(side="left", padx=5)

        self.main_status_label = tk.Label(self.root, text="", fg="green")
        self.main_status_label.pack(pady=(0, 10))

        # Latest mail label
        self.latest_var = tk.StringVar(value="Latest: (none)")
        tk.Label(self.root, textvariable=self.latest_var, font=("Arial", 12)).pack(anchor="w", padx=22, pady=(10, 5))

        # Notification table
        table_frame = tk.Frame(self.root)
        table_frame.pack(fill="both", expand=True, padx=20, pady=10)

        columns = ("time", "weight", "status")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=12)
        self.tree.heading("time", text="Date & Time")
        self.tree.heading("weight", text="Weight")
        self.tree.heading("status", text="Status")

        self.tree.column("time", width=330, anchor="w")
        self.tree.column("weight", width=120, anchor="center")
        self.tree.column("status", width=150, anchor="center")

        scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        # Buttons row
        btn_row = tk.Frame(self.root)
        btn_row.pack(fill="x", padx=20, pady=(0, 20))

        tk.Button(btn_row, text="Delete Selected", command=self.delete_selected,
                  bg="#ff4444", fg="white", relief="flat", padx=12, pady=8).pack(side="left")

        tk.Button(btn_row, text="Clear All", command=self.clear_all,
                  bg="#888888", fg="white", relief="flat", padx=12, pady=8).pack(side="left", padx=10)

        tk.Label(btn_row, text="Newest notifications appear at the top.",
                 fg="#555555").pack(side="right")

        # Load and show mail history
        self.mail_history = load_mail_history()
        self.refresh_tree_from_history()

        # Start sensors AFTER login/dashboard shows
        self.start_sensors_once()
        self.update_gui_from_queue()

    def update_phone(self):
        new_phone = self.new_phone_entry.get().strip()

        if not new_phone:
            self.main_status_label.config(text="enter a new number")
            return

        clean_new = new_phone.replace(" ", "").replace("-", "").replace("+", "")
        if not clean_new.isdigit():
            self.main_status_label.config(text="phone should be numbers")
            return

        # CHANGED: use update_phone instead of add_user
        self.user_data.update_phone(self.current_user, new_phone)
        self.new_phone_entry.delete(0, tk.END)
        self.main_status_label.config(text="phone updated!")

    def logout(self):
        self.show_login_screen()

    # ---------- Mail notifications ----------
    def start_sensors_once(self):
        if self.sensor_thread_started:
            return
        self.sensor_thread_started = True

        t = threading.Thread(target=self.monitor_sensors_background, daemon=True)
        t.start()

    def monitor_sensors_background(self):
        # On Pi: calibrates, on Mac: does nothing
        start_motion_system()

        while True:
            mail_detected, weight_value, motion_bool = detect_mail_once(weight_threshold=2.0)
            now = time.time()

            if mail_detected and (now - self.last_trigger_time) > self.COOLDOWN:
                self.last_trigger_time = now
                ts = datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")
                event = {"ts": ts, "weight": float(weight_value)}
                self.sensor_queue.put(event)

            time.sleep(0.2)

    def update_gui_from_queue(self):
        # Only update if we are on dashboard (tree exists)
        if hasattr(self, "tree"):
            while not self.sensor_queue.empty():
                event = self.sensor_queue.get()
                self.add_notification(event)
                self.latest_var.set(f'Latest: {event["ts"]}  |  {event["weight"]:.2f} g')

        self.root.after(300, self.update_gui_from_queue)

    def add_notification(self, event):
        self.mail_history.insert(0, event)
        save_mail_history(self.mail_history)
        self.tree.insert("", 0, values=(event["ts"], f'{event["weight"]:.2f} g', "Mail Arrived"))

    def refresh_tree_from_history(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for ev in self.mail_history:
            self.tree.insert("", "end", values=(ev["ts"], f'{ev["weight"]:.2f} g', "Mail Arrived"))
        if self.mail_history:
            self.latest_var.set(f'Latest: {self.mail_history[0]["ts"]}  |  {self.mail_history[0]["weight"]:.2f} g')
        else:
            self.latest_var.set("Latest: (none)")

    def delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Delete", "Select a notification to delete.")
            return

        for item_id in selected:
            ts, weight_str, status = self.tree.item(item_id, "values")
            self.tree.delete(item_id)

            try:
                w = float(weight_str.replace(" g", ""))
            except Exception:
                w = None

            for i, ev in enumerate(self.mail_history):
                if ev.get("ts") == ts and (w is None or abs(ev.get("weight", 0) - w) < 1e-6):
                    self.mail_history.pop(i)
                    break

        save_mail_history(self.mail_history)
        self.refresh_tree_from_history()

    def clear_all(self):
        if not self.mail_history and not self.tree.get_children():
            return
        if messagebox.askyesno("Clear All", "Delete all notifications?"):
            self.mail_history.clear()
            save_mail_history(self.mail_history)
            self.refresh_tree_from_history()


def main():
    root = tk.Tk()
    app = LoginApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
