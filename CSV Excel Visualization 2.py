import pandas as pd
import numpy as np
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinterdnd2 import DND_FILES, TkinterDnD
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os

class DataVisualizerGUI:
    def __init__(self, master):
        self.master = master
        master.title("Data Visualizer")
        
        self.frame = ttk.Frame(master)
        self.frame.pack(fill=tk.BOTH, expand=True)
        
        self.file_entry = ttk.Entry(self.frame, width=50)
        self.file_entry.pack(side=tk.LEFT, padx=5, pady=5)
        self.file_entry.drop_target_register(DND_FILES)
        self.file_entry.dnd_bind("<<Drop>>", self.drop_file)
        
        self.browse_button = ttk.Button(self.frame, text="Browse", command=self.browse_file)
        self.browse_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.data_preview = None
        
        self.chart_width = tk.StringVar(value="6")
        self.chart_height = tk.StringVar(value="4")
        self.tick_label_size = tk.StringVar(value="10")
        self.title_size = tk.StringVar(value="12")
        self.x_label_size = tk.StringVar(value="10")
        self.y_label_size = tk.StringVar(value="10")
        
        self.customization_frame = ttk.Frame(master)
        self.customization_frame.pack(pady=10)
        
        ttk.Label(self.customization_frame, text="Chart Width:").grid(row=0, column=0, sticky=tk.E)
        ttk.Entry(self.customization_frame, textvariable=self.chart_width, width=5).grid(row=0, column=1)
        
        ttk.Label(self.customization_frame, text="Chart Height:").grid(row=1, column=0, sticky=tk.E)
        ttk.Entry(self.customization_frame, textvariable=self.chart_height, width=5).grid(row=1, column=1)
        
        ttk.Label(self.customization_frame, text="Tick Label Size:").grid(row=2, column=0, sticky=tk.E)
        ttk.Entry(self.customization_frame, textvariable=self.tick_label_size, width=5).grid(row=2, column=1)
        
        ttk.Label(self.customization_frame, text="Title Size:").grid(row=3, column=0, sticky=tk.E)
        ttk.Entry(self.customization_frame, textvariable=self.title_size, width=5).grid(row=3, column=1)
        
        ttk.Label(self.customization_frame, text="X-Label Size:").grid(row=4, column=0, sticky=tk.E)
        ttk.Entry(self.customization_frame, textvariable=self.x_label_size, width=5).grid(row=4, column=1)
        
        ttk.Label(self.customization_frame, text="Y-Label Size:").grid(row=5, column=0, sticky=tk.E)
        ttk.Entry(self.customization_frame, textvariable=self.y_label_size, width=5).grid(row=5, column=1)
        
        self.column_selection_frame = ttk.Frame(master)
        self.column_selection_frame.pack(pady=10)
        
        ttk.Label(self.column_selection_frame, text="Select Columns:").pack()
        
        self.selected_columns = []
        self.column_listbox = tk.Listbox(self.column_selection_frame, selectmode=tk.MULTIPLE)
        self.column_listbox.pack()
        
        self.visualize_button = ttk.Button(master, text="Visualize", command=self.visualize_data)
        self.visualize_button.pack(pady=5)
        
    def drop_file(self, event):
        file_path = event.data
        if "{" in file_path or "}" in file_path:
            file_path = file_path.replace("{", "").replace("}", "")
        file_path = file_path.strip()
        self.file_entry.delete(0, tk.END)
        self.file_entry.insert(0, file_path)
        self.load_data(file_path)
        
    def browse_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx;*.xls"), ("CSV files", "*.csv")])
        if file_path:
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, file_path)
            self.load_data(file_path)
        
    def load_data(self, file_path):
        try:
            if file_path.endswith(".xlsx") or file_path.endswith(".xls"):
                xlsx = pd.ExcelFile(file_path)
                sheet_names = xlsx.sheet_names
                if len(sheet_names) > 1:
                    self.select_sheet(xlsx, sheet_names)
                else:
                    self.data = pd.read_excel(xlsx, sheet_name=sheet_names[0])
            elif file_path.endswith(".csv"):
                self.data = pd.read_csv(file_path)
            else:
                raise ValueError("Unsupported file format")
        except Exception as e:
            print(f"Error loading file: {str(e)}")
            return 
        
        if self.data_preview:
            self.data_preview.destroy()
        
        self.data_preview = ttk.Frame(self.master)
        self.data_preview.pack(side=tk.RIGHT, padx=10, pady=10)
        
        preview_label = ttk.Label(self.data_preview, text="Data Preview")
        preview_label.pack()
        
        preview_table = ttk.Treeview(self.data_preview, show="headings")
        preview_table.pack()
        
        columns = list(self.data.columns)
        preview_table["columns"] = columns
        
        for col in columns:
            preview_table.heading(col, text=col)
            preview_table.column(col, width=100)
        
        for _, row in self.data.head().iterrows():
            preview_table.insert("", tk.END, values=list(row))
        
        self.column_listbox.delete(0, tk.END)
        for col in columns:
            self.column_listbox.insert(tk.END, col)
    
    def select_sheet(self, xlsx, sheet_names):
        sheet_window = tk.Toplevel(self.master)
        sheet_window.title("Select Sheet")
        
        sheet_var = tk.StringVar(value=sheet_names[0])
        
        ttk.Label(sheet_window, text="Select a sheet:").pack()
        
        for sheet in sheet_names:
            ttk.Radiobutton(sheet_window, text=sheet, variable=sheet_var, value=sheet).pack()
        
        ttk.Button(sheet_window, text="OK", command=lambda: self.load_sheet(xlsx, sheet_var.get(), sheet_window)).pack()
        
    def load_sheet(self, xlsx, sheet_name, sheet_window):
        self.data = pd.read_excel(xlsx, sheet_name=sheet_name)
        sheet_window.destroy()
        
        if self.data_preview:
            self.data_preview.destroy()
        
        self.data_preview = ttk.Frame(self.master)
        self.data_preview.pack(side=tk.RIGHT, padx=10, pady=10)
        
        preview_label = ttk.Label(self.data_preview, text="Data Preview")
        preview_label.pack()
        
        preview_table = ttk.Treeview(self.data_preview, show="headings")
        preview_table.pack()
        
        columns = list(self.data.columns)
        preview_table["columns"] = columns
        
        for col in columns:
            preview_table.heading(col, text=col)
            preview_table.column(col, width=100)
        
        for _, row in self.data.head().iterrows():
            preview_table.insert("", tk.END, values=list(row))
        
        self.column_listbox.delete(0, tk.END)
        for col in columns:
            self.column_listbox.insert(tk.END, col)
    
        
    def visualize_data(self):
        selected_columns = [self.column_listbox.get(idx) for idx in self.column_listbox.curselection()]
        
        if len(selected_columns) < 2:
            tk.messagebox.showwarning("Warning", "Please select at least two columns for visualization.")
            return
        
        fig, ax = plt.subplots(figsize=(int(self.chart_width.get()), int(self.chart_height.get())))
        
        for i in range(len(selected_columns) - 1):
            field1 = selected_columns[i]
            field2 = selected_columns[i + 1]
            
            if self.get_data_type(self.data[field1]) == "Categorical" and self.get_data_type(self.data[field2]) == "Categorical":
                cross_tab = pd.crosstab(self.data[field1], self.data[field2])
                ax.imshow(cross_tab, cmap="YlGn", aspect="auto")
                ax.set_xticks(range(len(cross_tab.columns)))
                ax.set_xticklabels(cross_tab.columns, rotation=90, fontsize=int(self.tick_label_size.get()))
                ax.set_yticks(range(len(cross_tab.index)))
                ax.set_yticklabels(cross_tab.index, fontsize=int(self.tick_label_size.get()))
                for i in range(len(cross_tab.index)):
                    for j in range(len(cross_tab.columns)):
                        ax.text(j, i, cross_tab.iloc[i, j], ha="center", va="center", color="black")
                ax.set_title(f"{field1} vs {field2}", fontsize=int(self.title_size.get()))
            
            elif self.get_data_type(self.data[field1]) == "Categorical" and self.get_data_type(self.data[field2]) in ["Integer", "Decimal"]:
                self.data.boxplot(column=field2, by=field1, ax=ax)
                ax.set_title(f"{field2} by {field1}", fontsize=int(self.title_size.get()))
                ax.set_xlabel(field1, fontsize=int(self.x_label_size.get()))
                ax.set_ylabel(field2, fontsize=int(self.y_label_size.get()))
                plt.xticks(rotation=90, fontsize=int(self.tick_label_size.get()))
                plt.yticks(fontsize=int(self.tick_label_size.get()))
            
            elif self.get_data_type(self.data[field1]) in ["Integer", "Decimal"] and self.get_data_type(self.data[field2]) in ["Integer", "Decimal"]:
                ax.scatter(self.data[field1], self.data[field2])
                ax.set_xlabel(field1, fontsize=int(self.x_label_size.get()))
                ax.set_ylabel(field2, fontsize=int(self.y_label_size.get()))
                ax.set_title(f"{field1} vs {field2}", fontsize=int(self.title_size.get()))
                plt.xticks(fontsize=int(self.tick_label_size.get()))
                plt.yticks(fontsize=int(self.tick_label_size.get()))
            
            elif self.get_data_type(self.data[field1]) == "Datetime" and self.get_data_type(self.data[field2]) in ["Integer", "Decimal"]:
                self.data = self.data.sort_values(by=field1)
                ax.plot(self.data[field1], self.data[field2])
                ax.set_xlabel(field1, fontsize=int(self.x_label_size.get()))
                ax.set_ylabel(field2, fontsize=int(self.y_label_size.get()))
                ax.set_title(f"{field2} over {field1}", fontsize=int(self.title_size.get()))
                plt.xticks(rotation=45, fontsize=int(self.tick_label_size.get()))
                plt.yticks(fontsize=int(self.tick_label_size.get()))
            
            else:
                ax.text(0.5, 0.5, "No suitable visualization found for the selected fields.", ha="center", va="center", transform=ax.transAxes)
        
        fig.tight_layout()
        
        visualization_window = tk.Toplevel(self.master)
        visualization_window.title("Data Visualization")
        
        canvas = FigureCanvasTkAgg(fig, master=visualization_window)
        canvas.draw()
        canvas.get_tk_widget().pack()
        
    def get_data_type(self, column):
        if column.dtype == object:
            if column.nunique() == len(column):
                return "Non-Categorical (Unique)"
            else:
                return "Categorical"
        elif np.issubdtype(column.dtype, np.integer):
            return "Integer"
        elif np.issubdtype(column.dtype, np.floating):
            return "Decimal"
        elif np.issubdtype(column.dtype, np.datetime64):
            return "Datetime"
        else:
            return str(column.dtype)

root = TkinterDnD.Tk()
gui = DataVisualizerGUI(root)
root.mainloop()
