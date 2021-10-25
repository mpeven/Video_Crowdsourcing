import os
from pathlib import Path
from tkinter import Tk, filedialog

def folder_select_dialogue():
    """ Use system GUI to select a folder """
    root = Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    return filedialog.askdirectory()

def save_text(file, text):
    """ Save text to a file, overwriting existing file """
    if os.path.exists(file):
        os.remove(file)
    Path(os.path.dirname(file)).mkdir(parents=True, exist_ok=True)
    with open(file, "w") as f:
        f.write(text)
