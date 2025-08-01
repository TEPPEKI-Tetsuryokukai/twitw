import tkinter as tk
from tkinter import ttk, messagebox
from modules.auth import AuthManager
from modules.tweet import TweetTab
import os

class TwitterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Twikit X GUI Tool")
        self.auth = AuthManager()

        self.setup_login_ui()

    def setup_login_ui(self):
        self.clear_frame()

        tk.Label(self.root, text="Email").pack()
        self.email_entry = tk.Entry(self.root)
        self.email_entry.pack()

        tk.Label(self.root, text="Password").pack()
        self.password_entry = tk.Entry(self.root, show="*")
        self.password_entry.pack()

        tk.Button(self.root, text="Login", command=self.login).pack()

    def login(self):
        email = self.email_entry.get()
        password = self.password_entry.get()
        try:
            self.auth.login(email, password)
            messagebox.showinfo("Login", f"Logged in as {self.auth.username}")
            self.setup_main_ui()
        except Exception as e:
            messagebox.showerror("Login Failed", str(e))

    def setup_main_ui(self):
        self.clear_frame()
        label = tk.Label(self.root, text=f"Welcome, {self.auth.username}!", font=("Arial", 14))
        label.pack(pady=10)

        tab_control = ttk.Notebook(self.root)
        tweet_tab = ttk.Frame(tab_control)
        tab_control.add(tweet_tab, text='投稿')
        tab_control.pack(expand=1, fill='both')

        TweetTab(tweet_tab, self.auth.client)

    def clear_frame(self):
        for widget in self.root.winfo_children():
            widget.destroy()

if __name__ == '__main__':
    root = tk.Tk()
    app = TwitterApp(root)
    root.mainloop()
