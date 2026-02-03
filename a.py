import tkinter as tk
from tkinter import messagebox
import json
import os

class UserData:
    """Handles user data storage and retrieval"""
    def __init__(self, filename='users.json'):
        self.filename = filename
        self.users = self.load_users()
    
    def load_users(self):
        """Load user data from JSON file"""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return {}
        return {}
    
    def save_users(self):
        """Save user data to JSON file"""
        with open(self.filename, 'w') as f:
            json.dump(self.users, f, indent=4)
    
    def add_user(self, username, phone_number):
        """Add or update a user"""
        self.users[username] = phone_number
        self.save_users()
    
    def get_phone(self, username):
        """Get phone number for a user"""
        return self.users.get(username)

class LoginApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Raspberry Pi User System")
        self.root.geometry("400x300")
        
        # Center the window on screen
        self.root.eval('tk::PlaceWindow . center')
        
        self.user_data = UserData()
        self.current_user = None
        
        self.show_login_screen()
    
    def clear_window(self):
        """Clear all widgets from the window"""
        for widget in self.root.winfo_children():
            widget.destroy()
    
    def show_login_screen(self):
        """Display the login/registration screen"""
        self.clear_window()
        
        # Title
        title_label = tk.Label(self.root, text="User Login", font=("Arial", 16, "bold"))
        title_label.pack(pady=20)
        
        # Username
        username_frame = tk.Frame(self.root)
        username_frame.pack(pady=10)
        tk.Label(username_frame, text="Username:", font=("Arial", 12)).pack(side=tk.LEFT, padx=5)
        self.username_entry = tk.Entry(username_frame, font=("Arial", 12), width=20)
        self.username_entry.pack(side=tk.LEFT)
        
        # Phone Number (for new registration)
        phone_frame = tk.Frame(self.root)
        phone_frame.pack(pady=10)
        tk.Label(phone_frame, text="Phone Number:", font=("Arial", 12)).pack(side=tk.LEFT, padx=5)
        self.phone_entry = tk.Entry(phone_frame, font=("Arial", 12), width=20)
        self.phone_entry.pack(side=tk.LEFT)
        
        # Buttons Frame
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=20)
        
        # Login Button
        login_btn = tk.Button(button_frame, text="Login", 
                             command=self.login, 
                             bg="#4CAF50", fg="white",
                             font=("Arial", 12), 
                             width=10, height=1)
        login_btn.pack(side=tk.LEFT, padx=10)
        
        # Register Button
        register_btn = tk.Button(button_frame, text="Register", 
                                command=self.register, 
                                bg="#2196F3", fg="white",
                                font=("Arial", 12), 
                                width=10, height=1)
        register_btn.pack(side=tk.LEFT, padx=10)
        
        # Status Label
        self.status_label = tk.Label(self.root, text="", fg="red", font=("Arial", 10))
        self.status_label.pack(pady=10)
    
    def login(self):
        """Handle login attempt"""
        username = self.username_entry.get().strip()
        
        if not username:
            self.status_label.config(text="Please enter a username")
            return
        
        if username in self.user_data.users:
            self.current_user = username
            self.show_main_menu()
        else:
            self.status_label.config(text="User not found. Please register first.")
    
    def register(self):
        """Handle user registration"""
        username = self.username_entry.get().strip()
        phone = self.phone_entry.get().strip()
        
        if not username:
            self.status_label.config(text="Please enter a username")
            return
        
        if not phone:
            self.status_label.config(text="Please enter a phone number")
            return
        
        # Simple phone validation
        if not phone.replace(" ", "").replace("-", "").replace("+", "").isdigit():
            self.status_label.config(text="Please enter a valid phone number")
            return
        
        if username in self.user_data.users:
            self.status_label.config(text="Username already exists. Please login.")
            return
        
        self.user_data.add_user(username, phone)
        self.current_user = username
        messagebox.showinfo("Success", f"User '{username}' registered successfully!")
        self.show_main_menu()
    
    def show_main_menu(self):
        """Display the main menu screen"""
        self.clear_window()
        
        # Welcome Message
        welcome_label = tk.Label(self.root, 
                                text=f"Welcome, {self.current_user}!",
                                font=("Arial", 18, "bold"))
        welcome_label.pack(pady=20)
        
        # Current Phone Number Display
        phone_frame = tk.Frame(self.root)
        phone_frame.pack(pady=20)
        
        tk.Label(phone_frame, 
                text="Current Phone Number:", 
                font=("Arial", 12)).pack(side=tk.LEFT, padx=5)
        
        self.current_phone_var = tk.StringVar(value=self.user_data.get_phone(self.current_user))
        phone_label = tk.Label(phone_frame, 
                              textvariable=self.current_phone_var,
                              font=("Arial", 12, "bold"),
                              fg="blue")
        phone_label.pack(side=tk.LEFT, padx=5)
        
        # Update Phone Section
        update_frame = tk.Frame(self.root)
        update_frame.pack(pady=20)
        
        tk.Label(update_frame, text="New Phone Number:", font=("Arial", 12)).pack(side=tk.LEFT, padx=5)
        self.new_phone_entry = tk.Entry(update_frame, font=("Arial", 12), width=20)
        self.new_phone_entry.pack(side=tk.LEFT, padx=5)
        
        update_btn = tk.Button(update_frame, text="Update", 
                              command=self.update_phone,
                              bg="#FF9800", fg="white",
                              font=("Arial", 10))
        update_btn.pack(side=tk.LEFT, padx=5)
        
        # Logout Button
        logout_btn = tk.Button(self.root, text="Logout", 
                              command=self.logout,
                              bg="#f44336", fg="white",
                              font=("Arial", 12),
                              width=10, height=1)
        logout_btn.pack(pady=20)
        
        # Status Label for Main Menu
        self.main_status_label = tk.Label(self.root, text="", fg="green", font=("Arial", 10))
        self.main_status_label.pack(pady=10)
    
    def update_phone(self):
        """Update the phone number for current user"""
        new_phone = self.new_phone_entry.get().strip()
        
        if not new_phone:
            self.main_status_label.config(text="Please enter a new phone number")
            return
        
        # Simple phone validation
        if not new_phone.replace(" ", "").replace("-", "").replace("+", "").isdigit():
            self.main_status_label.config(text="Please enter a valid phone number")
            return
        
        # Update phone number
        self.user_data.add_user(self.current_user, new_phone)
        self.current_phone_var.set(new_phone)
        self.new_phone_entry.delete(0, tk.END)
        self.main_status_label.config(text="Phone number updated successfully!")
    
    def logout(self):
        """Logout and return to login screen"""
        self.current_user = None
        self.show_login_screen()

def main():
    root = tk.Tk()
    app = LoginApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
