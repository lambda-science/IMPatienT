import tkinter as tk
from tkinter import filedialog
from PIL import ImageTk, Image
from tkinter import ttk
import random

root = tk.Tk()
root.resizable(width=True, height=True)
root.title("Histo-annotation")
root.geometry('800x800')
def openfn():
    filename = filedialog.askopenfilename(title='open')
    return filename

def open_img():
    x = openfn()
    img = Image.open(x)
    img = img.resize((400, 400), Image.ANTIALIAS)
    img = ImageTk.PhotoImage(img)
    panel = tk.Label(root, image=img)
    panel.image = img
    panel.grid(row=1,column=0)

btn = tk.Button(root, text='Ouvrir l\'image', command=open_img).grid(row=0,column=0)

a = tk.Label(root ,text = "Prénom Patient").grid(row = 0,column = 1)
b = tk.Label(root ,text = "Nom Patient").grid(row = 1,column = 1)
c = tk.Label(root ,text = "ID Patient").grid(row = 2,column = 1)
d = tk.Label(root ,text = "Nom expert").grid(row = 3,column = 1)
a1 = tk.Entry(root).grid(row = 0,column = 2)
b1 = tk.Entry(root).grid(row = 1,column = 2)
c1 = tk.Entry(root).grid(row = 2,column = 2)
d1 = tk.Entry(root).grid(row = 3,column = 2)

root.mainloop()