import tkinter as tk
from tkinter import messagebox

#Function for home. page. 
def go_to_home():
    user_name = ent_name.get()
    user_id = ent_user_id.get()
    user_password = ent_password.get()

    # Validation
    if not user_name or not user_id or not user_password:
        messagebox.showwarning("Missing Info", "Please fill in all fields.")
        return

    if not all(x.isalpha() or x.isspace() for x in user_name):
        messagebox.showerror("Invalid Name", "Name must contain letters only.")
        return

    if not user_id.isdigit() or len(user_id) != 10:
        messagebox.showerror("Invalid Number", "User Number must be 10 digits.")
        return

    # Switch to Home Page
    login_frame.pack_forget()
    home_frame.pack(fill="both", expand=True)


def hover_on(e):
    btn_login["bg"] = "#0052cc"

def hover_off(e):
    btn_login["bg"] = "#0066ff"


# MAIN WINDOW 
window = tk.Tk()
window.title("SmartMailbox System")
window.geometry("900x600")
window.configure(bg="#e6f0ff")
#window.resizable(False, False)

# LOGIN FRAME 
login_frame = tk.Frame(window, bg="white", bd=0, relief="ridge")
login_frame.place(relx=0.5, rely=0.5, anchor="center", width=400, height=450)

tk.Label(
    login_frame,
    text="SmartMailbox",
    font=("Helvetica", 24, "bold"),
    bg="white",
    fg="#003366"
).pack(pady=(30, 10))

tk.Label(
    login_frame,
    text="Login to your account",
    font=("Helvetica", 12),
    bg="white",
    fg="gray"
).pack(pady=(0, 20))


# Name
tk.Label(login_frame, text="User Name", bg="white").pack(anchor="w", padx=40)
ent_name = tk.Entry(login_frame, font=("Arial", 12), bd=2, relief="groove")
ent_name.pack(padx=40, pady=5, fill="x")

# User ID
tk.Label(login_frame, text="User Number", bg="white").pack(anchor="w", padx=40)
ent_user_id = tk.Entry(login_frame, font=("Arial", 12), bd=2, relief="groove")
ent_user_id.pack(padx=40, pady=5, fill="x")

# Password
tk.Label(login_frame, text="Password", bg="white").pack(anchor="w", padx=40)
ent_password = tk.Entry(login_frame, show="*", font=("Arial", 12), bd=2, relief="groove")
ent_password.pack(padx=40, pady=5, fill="x")

# Login Button
btn_login = tk.Button(
    login_frame,
    text="Login",
    command=go_to_home,
    font=("Helvetica", 12, "bold"),
    bg="#0066ff",
    fg="white",
    activebackground="#0052cc",
    activeforeground="white",
    relief="flat",
    pady=10
)
btn_login.pack(pady=30, padx=40, fill="x")

btn_login.bind("<Enter>", hover_on)
btn_login.bind("<Leave>", hover_off)


# HOME FRAME 
home_frame = tk.Frame(window, bg="#f2f7ff")

tk.Label(
    home_frame,
    text="📬 Welcome to SmartMailbox!",
    font=("Helvetica", 24, "bold"),
    bg="#f2f7ff",
    fg="#003366"
).pack(pady=80)

tk.Label(
    home_frame,
    text="You are successfully logged in.",
    font=("Helvetica", 14),
    bg="#f2f7ff"
).pack()

window.mainloop()
