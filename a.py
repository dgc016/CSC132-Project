import tkinter as tk
import json
import os

class UserData:
    def __init__(self, filename='users.json'):
        self.filename = filename
        self.users = self.load_users()
    
    def load_users(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_users(self):
        with open(self.filename, 'w') as f:
            json.dump(self.users, f, indent=4)
    
    def add_user(self, username, phone_number):
        self.users[username] = phone_number
        self.save_users()
    
    def get_phone(self, username):
        return self.users.get(username)

class LoginApp:
    def __init__(self, root):
        self.root = root
        self.root.title("User System")
        self.root.geometry("400x350")
        
        # center window
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
        self.user_data = UserData()
        self.current_user = None
        
        self.show_login_screen()
    
    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()
    
    def show_login_screen(self):
        self.clear_window()
        
        title_label = tk.Label(self.root, text="Login / Register", font=("Arial", 16))
        title_label.pack(pady=20)
        
        # username
        username_frame = tk.Frame(self.root)
        username_frame.pack(pady=10)
        tk.Label(username_frame, text="Username:").pack(side=tk.LEFT, padx=5)
        self.username_entry = tk.Entry(username_frame, width=25)
        self.username_entry.pack(side=tk.LEFT)
        
        # phone number
        phone_frame = tk.Frame(self.root)
        phone_frame.pack(pady=10)
        tk.Label(phone_frame, text="Phone Number:").pack(side=tk.LEFT, padx=5)
        self.phone_entry = tk.Entry(phone_frame, width=25)
        self.phone_entry.pack(side=tk.LEFT)
        
        # buttons
        button_frame = tk.Frame(self.root)
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
        
        self.status_label = tk.Label(self.root, text="", fg="red")
        self.status_label.pack(pady=5)
    
    def login(self):
        username = self.username_entry.get().strip()
        
        if not username:
            self.status_label.config(text="need a username")
            return
        
        if username in self.user_data.users:
            self.current_user = username
            self.show_main_menu()
        else:
            self.status_label.config(text="user not found")
    
    def register(self):
        username = self.username_entry.get().strip()
        phone = self.phone_entry.get().strip()
        
        if not username:
            self.status_label.config(text="need a username")
            return
        
        if not phone:
            self.status_label.config(text="need a phone number")
            return
        
        # check phone number
        clean_phone = phone.replace(" ", "").replace("-", "").replace("+", "")
        if not clean_phone.isdigit():
            self.status_label.config(text="phone should be numbers")
            return
        
        if username in self.user_data.users:
            self.status_label.config(text="username already exists")
            return
        
        self.user_data.add_user(username, phone)
        self.current_user = username
        
        # show success popup
        popup = tk.Toplevel(self.root)
        popup.title("Success")
        popup.geometry("250x100")
        label = tk.Label(popup, text=f"user '{username}' registered!")
        label.pack(pady=20)
        ok_btn = tk.Button(popup, text="OK", command=popup.destroy)
        ok_btn.pack()
        
        self.show_main_menu()
    
    def show_main_menu(self):
        self.clear_window()
        
        welcome_label = tk.Label(self.root, 
                                text=f"welcome, {self.current_user}!",
                                font=("Arial", 16))
        welcome_label.pack(pady=20)
        
        # current phone display
        phone_frame = tk.Frame(self.root)
        phone_frame.pack(pady=15)
        
        tk.Label(phone_frame, text="your phone:").pack(side=tk.LEFT, padx=5)
        
        current_phone = self.user_data.get_phone(self.current_user)
        self.phone_label = tk.Label(phone_frame, text=current_phone, fg="blue")
        self.phone_label.pack(side=tk.LEFT, padx=5)
        
        # update phone section
        update_frame = tk.Frame(self.root)
        update_frame.pack(pady=20)
        
        tk.Label(update_frame, text="new phone:").pack(side=tk.LEFT, padx=5)
        self.new_phone_entry = tk.Entry(update_frame, width=25)
        self.new_phone_entry.pack(side=tk.LEFT, padx=5)
        
        update_btn = tk.Button(update_frame, text="Update", 
                              command=self.update_phone,
                              bg="orange")
        update_btn.pack(side=tk.LEFT, padx=5)
        
        # logout button
        logout_btn = tk.Button(self.root, text="Logout", 
                              command=self.logout,
                              bg="salmon",
                              width=15)
        logout_btn.pack(pady=30)
        
        self.main_status_label = tk.Label(self.root, text="", fg="green")
        self.main_status_label.pack(pady=5)
    
    def update_phone(self):
        new_phone = self.new_phone_entry.get().strip()
        
        if not new_phone:
            self.main_status_label.config(text="enter a new number")
            return
        
        # check phone number
        clean_new = new_phone.replace(" ", "").replace("-", "").replace("+", "")
        if not clean_new.isdigit():
            self.main_status_label.config(text="phone should be numbers")
            return
        
        self.user_data.add_user(self.current_user, new_phone)
        self.phone_label.config(text=new_phone)
        self.new_phone_entry.delete(0, tk.END)
        self.main_status_label.config(text="phone updated!")
    
    def logout(self):
        self.current_user = None
        self.show_login_screen()

def main():
    root = tk.Tk()
    app = LoginApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
