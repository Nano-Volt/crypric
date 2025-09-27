import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import tkinter.font as tkfont

# --- Syntax Highlighting Rules ---
KEYWORDS = ["fn", "loop", "print", "return", "if", "else", "while", "break", "continue"]
TYPES = ["int", "string", "bool"]

def highlight(event=None):
    text.tag_remove("keyword", "1.0", "end")
    text.tag_remove("type", "1.0", "end")
    text.tag_remove("string", "1.0", "end")
    text.tag_remove("number", "1.0", "end")
    text.tag_remove("comment", "1.0", "end")

    # Keywords
    for keyword in KEYWORDS:
        start = "1.0"
        while True:
            start = text.search(rf"\y{keyword}\y", start, stopindex="end", regexp=True)
            if not start:
                break
            end = f"{start}+{len(keyword)}c"
            text.tag_add("keyword", start, end)
            start = end

    # Types
    for typ in TYPES:
        start = "1.0"
        while True:
            start = text.search(rf"\y{typ}\y", start, stopindex="end", regexp=True)
            if not start:
                break
            end = f"{start}+{len(typ)}c"
            text.tag_add("type", start, end)
            start = end

    # Strings
    start = "1.0"
    while True:
        start = text.search(r'"', start, stopindex="end")
        if not start:
            break
        end = text.search(r'"', f"{start}+1c", stopindex="end")
        if not end:
            break
        end = f"{end}+1c"
        text.tag_add("string", start, end)
        start = end

    # Numbers
    start = "1.0"
    while True:
        start = text.search(r"\b[0-9]+\b", start, stopindex="end", regexp=True)
        if not start:
            break
        end = f"{start}+{len(text.get(start, start+' word'))}c"
        text.tag_add("number", start, end)
        start = end

    # Comments (// ...)
    start = "1.0"
    while True:
        start = text.search("//", start, stopindex="end")
        if not start:
            break
        end = f"{start} lineend"
        text.tag_add("comment", start, end)
        start = end

# --- File Ops ---
def open_file():
    path = filedialog.askopenfilename(filetypes=[("Cryptic files", "*.cryp"), ("All files", "*.*")])
    if path:
        with open(path, "r") as f:
            text.delete("1.0", "end")
            text.insert("1.0", f.read())
        root.title(f"Cryptic IDE - {path}")

def save_file():
    path = filedialog.asksaveasfilename(defaultextension=".cryp",
                                        filetypes=[("Cryptic files", "*.cryp"), ("All files", "*.*")])
    if path:
        with open(path, "w") as f:
            f.write(text.get("1.0", "end-1c"))
        root.title(f"Cryptic IDE - {path}")

def run_file():
    code = text.get("1.0", "end-1c")
    # For now just show code, later hook to compiler
    messagebox.showinfo("Run Cryptic", f"Running code:\n\n{code}")

# --- GUI Setup ---
root = tk.Tk()
root.title("Cryptic IDE")
root.geometry("800x600")

# Dark theme colors
bg_color = "#1e1e1e"
fg_color = "#d4d4d4"

# Text area
text = scrolledtext.ScrolledText(root, wrap="word", undo=True, font=("Consolas", 12),
                                 background=bg_color, foreground=fg_color,
                                 insertbackground="white", selectbackground="#555555")
text.pack(fill="both", expand=True)

# Syntax tags
text.tag_configure("keyword", foreground="#569CD6", font=("Consolas", 12, "bold"))
text.tag_configure("type", foreground="#4EC9B0")
text.tag_configure("string", foreground="#CE9178")
text.tag_configure("number", foreground="#B5CEA8")

# Fix italic comments
comment_font = tkfont.Font(family="Consolas", size=12, slant="italic")
text.tag_configure("comment", foreground="#6A9955", font=comment_font)

# Bind highlight on typing
text.bind("<KeyRelease>", highlight)

# Menu
menu = tk.Menu(root)
root.config(menu=menu)

file_menu = tk.Menu(menu, tearoff=0)
menu.add_cascade(label="File", menu=file_menu)
file_menu.add_command(label="Open", command=open_file)
file_menu.add_command(label="Save", command=save_file)
file_menu.add_separator()
file_menu.add_command(label="Exit", command=root.quit)

run_menu = tk.Menu(menu, tearoff=0)
menu.add_cascade(label="Run", menu=run_menu)
run_menu.add_command(label="Run Code", command=run_file)

root.mainloop()
