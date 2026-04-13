import tkinter as tk
from tkinter import ttk

root = tk.Tk()
notebook = ttk.Notebook(root)
notebook.pack(fill='both', expand=True)

frame1 = ttk.Frame(notebook)
notebook.add(frame1, text='Tab 1')

# Add a boolean var for master checkbox
vars = []
for i in range(5):
    var = tk.BooleanVar(value=True)
    vars.append(var)
    ttk.Checkbutton(frame1, text=f"Video {i+1}", variable=var).pack()

root.update()
notebook.select(frame1)
# root.mainloop()
