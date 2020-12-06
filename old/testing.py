import tkinter as tk
from tkinter import ttk
class ScrollableFrame(ttk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

if __name__ == "__main__":
    

    root = tk.Tk()
    frame = ScrollableFrame(root)
    feature = open("config_ontology", "r")
    feature_list = [line.strip() for line in feature.readlines()]
    for j in range(len(feature_list)):
        tk.Label(frame.scrollable_frame ,text = feature_list[j]).grid(row = j,column = 0)

        vals = [0, 1]
        etiqs = ['Absent', 'Présent']
        varGr = tk.StringVar()
        varGr.set(vals[0])
        for i in range(2):
            b = tk.Radiobutton(frame.scrollable_frame, variable=varGr, text=etiqs[i], value=vals[i])
            b.grid(row=j, column=i+1)
    frame.pack(fill=tk.BOTH)
    root.mainloop()