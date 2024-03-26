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
        self.chart_type_var = tk.StringVar(value="Auto")
        self.chart_type_button = ttk.Button(master, text="Select Chart Type", command=self.select_chart_type)
        self.chart_type_button.pack(pady=5)
        
        
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
    
    def select_chart_type(self):
        chart_type_window = tk.Toplevel(self.master)
        chart_type_window.title("Select Chart Type")
        
        chart_types = ["Auto", "Line", "Bar", "Histogram", "Pie"]
        
        for chart_type in chart_types:
            ttk.Radiobutton(chart_type_window, text=chart_type, variable=self.chart_type_var, value=chart_type).pack()
        
        ttk.Button(chart_type_window, text="OK", command=chart_type_window.destroy).pack()
    
    
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
    
        if len(selected_columns) < 1:
            tk.messagebox.showwarning("Warning", "Please select at least one column for visualization.")
            return
    
        fig, ax = plt.subplots(figsize=(int(self.chart_width.get()), int(self.chart_height.get())))
    
        if self.chart_type_var.get() == "Auto":
            if len(selected_columns) == 1:
                if self.get_data_type(self.data[selected_columns[0]]) == "Categorical":
                    self.data[selected_columns[0]].value_counts().plot(kind='bar', ax=ax)
                    ax.set_xlabel(selected_columns[0], fontsize=int(self.x_label_size.get()))
                    ax.set_ylabel("Count", fontsize=int(self.y_label_size.get()))
                    ax.set_title(f"Bar Chart of {selected_columns[0]}", fontsize=int(self.title_size.get()))
                    plt.xticks(rotation=90, fontsize=int(self.tick_label_size.get()))
                    plt.yticks(fontsize=int(self.tick_label_size.get()))
                elif self.get_data_type(self.data[selected_columns[0]]) in ["Integer", "Decimal"]:
                    self.data[selected_columns[0]].plot(kind='hist', ax=ax)
                    ax.set_xlabel(selected_columns[0], fontsize=int(self.x_label_size.get()))
                    ax.set_ylabel("Frequency", fontsize=int(self.y_label_size.get()))
                    ax.set_title(f"Histogram of {selected_columns[0]}", fontsize=int(self.title_size.get()))
                    plt.xticks(fontsize=int(self.tick_label_size.get()))
                    plt.yticks(fontsize=int(self.tick_label_size.get()))
                else:
                    ax.text(0.5, 0.5, "No suitable visualization found for the selected column.", ha="center", va="center", transform=ax.transAxes)
            elif len(selected_columns) == 2:
                if self.get_data_type(self.data[selected_columns[0]]) == "Categorical" and self.get_data_type(self.data[selected_columns[1]]) == "Categorical":
                    cross_tab = pd.crosstab(self.data[selected_columns[0]], self.data[selected_columns[1]])
                    cross_tab.plot(kind='bar', ax=ax)
                    ax.set_xlabel(selected_columns[0], fontsize=int(self.x_label_size.get()))
                    ax.set_ylabel(selected_columns[1], fontsize=int(self.y_label_size.get()))
                    ax.set_title(f"Bar Chart of {selected_columns[0]} vs {selected_columns[1]}", fontsize=int(self.title_size.get()))
                    plt.xticks(rotation=90, fontsize=int(self.tick_label_size.get()))
                    plt.yticks(fontsize=int(self.tick_label_size.get()))
                elif self.get_data_type(self.data[selected_columns[0]]) == "Categorical" and self.get_data_type(self.data[selected_columns[1]]) in ["Integer", "Decimal"]:
                    self.data.boxplot(column=selected_columns[1], by=selected_columns[0], ax=ax)
                    ax.set_xlabel(selected_columns[0], fontsize=int(self.x_label_size.get()))
                    ax.set_ylabel(selected_columns[1], fontsize=int(self.y_label_size.get()))
                    ax.set_title(f"Box Plot of {selected_columns[1]} by {selected_columns[0]}", fontsize=int(self.title_size.get()))
                    plt.xticks(rotation=90, fontsize=int(self.tick_label_size.get()))
                    plt.yticks(fontsize=int(self.tick_label_size.get()))
                elif self.get_data_type(self.data[selected_columns[0]]) in ["Integer", "Decimal"] and self.get_data_type(self.data[selected_columns[1]]) in ["Integer", "Decimal"]:
                    ax.scatter(self.data[selected_columns[0]], self.data[selected_columns[1]])
                    ax.set_xlabel(selected_columns[0], fontsize=int(self.x_label_size.get()))
                    ax.set_ylabel(selected_columns[1], fontsize=int(self.y_label_size.get()))
                    ax.set_title(f"Scatter Plot of {selected_columns[0]} vs {selected_columns[1]}", fontsize=int(self.title_size.get()))
                    plt.xticks(fontsize=int(self.tick_label_size.get()))
                    plt.yticks(fontsize=int(self.tick_label_size.get()))
                else:
                    ax.text(0.5, 0.5, "No suitable visualization found for the selected columns.", ha="center", va="center", transform=ax.transAxes)
            else:
                ax.text(0.5, 0.5, "Please select either one or two columns for visualization.", ha="center", va="center", transform=ax.transAxes)
        elif self.chart_type_var.get() == "Line":
            if len(selected_columns) == 1:
                self.data[selected_columns[0]].plot(kind='line', ax=ax)
                ax.set_xlabel("Index", fontsize=int(self.x_label_size.get()))
                ax.set_ylabel(selected_columns[0], fontsize=int(self.y_label_size.get()))
                ax.set_title(f"Line Chart of {selected_columns[0]}", fontsize=int(self.title_size.get()))
                plt.xticks(fontsize=int(self.tick_label_size.get()))
                plt.yticks(fontsize=int(self.tick_label_size.get()))
            elif len(selected_columns) == 2:
                self.data.plot(x=selected_columns[0], y=selected_columns[1], kind='line', ax=ax)
                ax.set_xlabel(selected_columns[0], fontsize=int(self.x_label_size.get()))
                ax.set_ylabel(selected_columns[1], fontsize=int(self.y_label_size.get()))
                ax.set_title(f"Line Chart of {selected_columns[1]} vs {selected_columns[0]}", fontsize=int(self.title_size.get()))
                plt.xticks(fontsize=int(self.tick_label_size.get()))
                plt.yticks(fontsize=int(self.tick_label_size.get()))
            else:
                ax.text(0.5, 0.5, "Please select either one or two columns for line chart visualization.", ha="center", va="center", transform=ax.transAxes)
        elif self.chart_type_var.get() == "Bar":
            if len(selected_columns) == 1:
                self.data[selected_columns[0]].value_counts().plot(kind='bar', ax=ax)
                ax.set_xlabel(selected_columns[0], fontsize=int(self.x_label_size.get()))
                ax.set_ylabel("Count", fontsize=int(self.y_label_size.get()))
                ax.set_title(f"Bar Chart of {selected_columns[0]}", fontsize=int(self.title_size.get()))
                plt.xticks(rotation=90, fontsize=int(self.tick_label_size.get()))
                plt.yticks(fontsize=int(self.tick_label_size.get()))
            elif len(selected_columns) == 2:
                cross_tab = pd.crosstab(self.data[selected_columns[0]], self.data[selected_columns[1]])
                cross_tab.plot(kind='bar', ax=ax)
                ax.set_xlabel(selected_columns[0], fontsize=int(self.x_label_size.get()))
                ax.set_ylabel(selected_columns[1], fontsize=int(self.y_label_size.get()))
                ax.set_title(f"Bar Chart of {selected_columns[0]} vs {selected_columns[1]}", fontsize=int(self.title_size.get()))
                plt.xticks(rotation=90, fontsize=int(self.tick_label_size.get()))
                plt.yticks(fontsize=int(self.tick_label_size.get()))
            else:
                ax.text(0.5, 0.5, "Please select either one or two columns for bar chart visualization.", ha="center", va="center", transform=ax.transAxes)
        elif self.chart_type_var.get() == "Histogram":
            if len(selected_columns) == 1:
                self.data[selected_columns[0]].plot(kind='hist', ax=ax)
                ax.set_xlabel(selected_columns[0], fontsize=int(self.x_label_size.get()))
                ax.set_ylabel("Frequency", fontsize=int(self.y_label_size.get()))
                ax.set_title(f"Histogram of {selected_columns[0]}", fontsize=int(self.title_size.get()))
                plt.xticks(fontsize=int(self.tick_label_size.get()))
                plt.yticks(fontsize=int(self.tick_label_size.get()))
            else:
                ax.text(0.5, 0.5, "Please select only one column for histogram visualization.", ha="center", va="center", transform=ax.transAxes)
        elif self.chart_type_var.get() == "Pie":
            if len(selected_columns) == 1:
                self.data[selected_columns[0]].value_counts().plot(kind='pie', ax=ax, autopct='%1.1f%%')
                ax.set_title(f"Pie Chart of {selected_columns[0]}", fontsize=int(self.title_size.get()))
                ax.legend(fontsize=int(self.tick_label_size.get()))
            else:
                ax.text(0.5, 0.5, "Please select only one column for pie chart visualization.", ha="center", va="center", transform=ax.transAxes)
    
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
