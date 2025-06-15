import tkinter as tk
from tkinter import filedialog


def saveFileDialog(fileTypes):
    root = tk.Tk()
    root.withdraw()

    filePath = filedialog.asksaveasfilename(
        defaultextension=fileTypes[0][1], filetypes=fileTypes
    )

    return filePath


def loadFileDialog(fileTypes):
    root = tk.Tk()
    root.withdraw()

    filePath = filedialog.askopenfilename(
        defaultextension=fileTypes[0][1], filetypes=fileTypes
    )

    return filePath


def loadDirectoryDialog():
    root = tk.Tk()
    root.withdraw()

    dirPath = filedialog.askdirectory()

    return dirPath
