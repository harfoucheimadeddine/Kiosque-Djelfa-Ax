import tkinter as tk

root = tk.Tk()
root.title("كشك الجلفة - أكسا")

label = tk.Label(root, text="مرحباً بك في كشك الجلفة - أكسا", font=("Arial", 20))
label.pack(pady=50)

root.geometry("500x300")
root.mainloop()
