import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from tkinter import filedialog, messagebox, ttk, Listbox, MULTIPLE, IntVar
import tkinter as tk
import numpy as np
from PIL import Image, ImageTk
import os

global x_selected_fields, y_selected_fields, dataset
x_selected_fields = []
y_selected_fields = []
dataset = pd.DataFrame()

def load_file():
    file_path = filedialog.askopenfilename(filetypes=[("CSV and Excel Files", "*.csv;*.xlsx")])
    if file_path:
        try:
            if file_path.endswith(".csv"):
                data = pd.read_csv(file_path)
            else:
                data = pd.read_excel(file_path)
            update_dropdowns(data)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file: {str(e)}")

def get_chart_size():
    sizes = {
        "Small": (8, 6),
        "Medium": (12, 8),
        "Large": (16, 12)
    }
    return sizes[chart_size.get()]

def update_dropdowns(data):
    global dataset
    dataset = data
    column_names = dataset.columns.tolist()
    x_axis_listbox.delete(0, tk.END)
    y_axis_listbox.delete(0, tk.END)
    for col in column_names:
        x_axis_listbox.insert(tk.END, col)
        y_axis_listbox.insert(tk.END, col)
    chart_type_dropdown["values"] = ["Line", "Bar", "Column", "Area", "Stacked Bar", "Scatter Plot", "Dual Axes", "Histogram", "Box Plot", "Pie Chart"]

def store_x_axis_selection():
    global x_selected_fields
    x_selected_fields = [x_axis_listbox.get(idx) for idx in x_axis_listbox.curselection()]
    x_axis_label["text"] = f"X Axis (Selected: {', '.join(x_selected_fields)}):" if x_selected_fields else "X Axis:"

def store_y_axis_selection():
    global y_selected_fields
    y_selected_fields = [y_axis_listbox.get(idx) for idx in y_axis_listbox.curselection()]
    y_axis_label["text"] = f"Y Axis (Selected: {', '.join(y_selected_fields)}):" if y_selected_fields else "Y Axis:"

def recommend_chart():
    if x_selected_fields and y_selected_fields:
        recommendation = advanced_chart_recommendation(x_selected_fields, y_selected_fields, dataset)
        recommendation_label["text"] = f"Recommended Chart: {recommendation}"
        chart_type_dropdown.set(recommendation)
    else:
        recommendation_label["text"] = "Select fields for X and Y axes."

def advanced_chart_recommendation(x_columns, y_columns, dataset):
    if not x_columns or not y_columns:
        return "Select appropriate data fields"

    x_dtype = dataset[x_columns[0]].dtype
    y_dtype = dataset[y_columns[0]].dtype
    x_unique_count = dataset[x_columns[0]].nunique()
    y_unique_count = dataset[y_columns[0]].nunique()

    if len(x_columns) > 1 or len(y_columns) > 1:
        return "Line"
    if pd.api.types.is_numeric_dtype(x_dtype) and pd.api.types.is_numeric_dtype(y_dtype):
        if len(dataset) > 1000:
            return "Scatter Plot"
        return "Line"
    elif pd.api.types.is_categorical_dtype(x_dtype) or pd.api.types.is_object_dtype(x_dtype):
        if y_unique_count <= 10:
            return "Bar"
        return "Box Plot" if len(dataset) > 50 else "Bar"
    elif pd.api.types.is_categorical_dtype(y_dtype) or pd.api.types.is_object_dtype(y_dtype):
        if x_unique_count <= 10 and len(dataset) <= 20:
            return "Pie Chart"
        return "Bar"
    return "Scatter Plot"

def generate_visualization():
    try:
        if not x_selected_fields or not y_selected_fields:
            messagebox.showerror("Error", "Select at least one field for both X and Y axes.")
            return

        title_font_size = int(title_font_size_var.get())
        x_tick_label_font_size = int(x_axis_font_size_var.get())
        y_tick_label_font_size = int(y_axis_font_size_var.get())
        x_tick_label_rotation = x_tick_label_rotation_var.get()
        y_tick_label_rotation = y_tick_label_rotation_var.get()

        chart_types = ["Line", "Bar", "Column", "Area", "Stacked Bar", "Scatter Plot", "Dual Axes", "Histogram", "Box Plot", "Pie Chart"]
        
        for chart_type in chart_types:
            fig, ax = plt.subplots(figsize=get_chart_size())
            if use_seaborn.get():
                sns.set(style="whitegrid")

            try:
                plot_data = dataset[list(set(x_selected_fields + y_selected_fields))]
                if chart_type in ["Bar", "Column"]:
                    if use_seaborn.get():
                        sns.barplot(data=plot_data, x=x_selected_fields[0], y=y_selected_fields[0], ax=ax, orient='v' if chart_type == "Bar" else 'h')
                    else:
                        ax.bar(plot_data[x_selected_fields[0]], plot_data[y_selected_fields[0]], color='skyblue') if chart_type == "Bar" else ax.barh(plot_data[x_selected_fields[0]], plot_data[y_selected_fields[0]], color='skyblue')
                elif chart_type == "Area":
                    ax.fill_between(range(len(plot_data)), plot_data[y_selected_fields[0]], color='skyblue', alpha=0.3)
                elif chart_type == "Stacked Bar":
                    crosstab = pd.crosstab(plot_data[x_selected_fields[0]], plot_data[y_selected_fields[0]])
                    crosstab.plot(kind='bar', stacked=True, ax=ax)
                elif chart_type == "Scatter Plot":
                    sns.scatterplot(data=plot_data, x=x_selected_fields[0], y=y_selected_fields[0], ax=ax) if use_seaborn.get() else ax.scatter(plot_data[x_selected_fields[0]], plot_data[y_selected_fields[0]])
                elif chart_type == "Line":
                    for y_col in y_selected_fields:
                        sns.lineplot(data=plot_data, x=x_selected_fields[0], y=y_col, ax=ax) if use_seaborn.get() else ax.plot(plot_data[x_selected_fields[0]], plot_data[y_col], label=y_col)
                    ax.legend()
                elif chart_type == "Histogram":
                    sns.histplot(data=plot_data, x=x_selected_fields[0], ax=ax) if use_seaborn.get() else ax.hist(plot_data[x_selected_fields[0]], bins=10)
                elif chart_type == "Dual Axes":
                    ax2 = ax.twinx()
                    ax.plot(plot_data[x_selected_fields[0]], label=x_selected_fields[0], color='skyblue')
                    ax2.plot(plot_data[y_selected_fields[0]], label=y_selected_fields[0], color='darkorange')
                    ax2.set_ylabel(", ".join(y_selected_fields), fontsize=y_tick_label_font_size)
                elif chart_type == "Box Plot":
                    sns.boxplot(data=plot_data, x=x_selected_fields[0], y=y_selected_fields[0], ax=ax) if use_seaborn.get() else ax.boxplot([plot_data[x_selected_fields[0]], plot_data[y_selected_fields[0]]])
                elif chart_type == "Pie Chart":
                    plot_data[y_selected_fields[0]].value_counts().plot.pie(ax=ax, autopct='%1.1f%%')

                ax.set_xlabel(", ".join(x_selected_fields), fontsize=x_tick_label_font_size)
                ax.set_ylabel(", ".join(y_selected_fields), fontsize=y_tick_label_font_size)
                ax.set_title(f"{chart_type}: {', '.join(x_selected_fields)} vs {', '.join(y_selected_fields)}", fontsize=title_font_size)
                ax.tick_params(axis='x', labelsize=x_tick_label_font_size, rotation=x_tick_label_rotation)
                ax.tick_params(axis='y', labelsize=y_tick_label_font_size, rotation=y_tick_label_rotation)
                plt.tight_layout()
                plt.show()

            except Exception as e:
                print(f"Error generating {chart_type} chart: {str(e)}")

    except Exception as e:
        messagebox.showerror("Error", f"Visualization failed: {str(e)}")

def clear_selections():
    global x_selected_fields, y_selected_fields
    x_axis_listbox.selection_clear(0, tk.END)
    y_axis_listbox.selection_clear(0, tk.END)
    x_selected_fields = []
    y_selected_fields = []
    chart_type_dropdown.set("")
    x_axis_label["text"] = "X Axis:"
    y_axis_label["text"] = "Y Axis:"
    recommendation_label["text"] = ""

# GUI components
root = tk.Tk()
root.title("CSV/Excel Data Visualizer v1.3")

frame = ttk.Frame(root, padding="10")
frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
load_button = ttk.Button(frame, text="Load File", command=load_file)
load_button.grid(column=0, row=0, padx=10, pady=10)

use_seaborn = tk.BooleanVar()
use_seaborn.set(False)
seaborn_label = ttk.Label(frame, text="Use Seaborn:")
seaborn_label.grid(column=0, row=1, padx=10, pady=10)
seaborn_radio_button = ttk.Radiobutton(frame, text="Yes", variable=use_seaborn, value=True)
seaborn_radio_button.grid(column=1, row=1, padx=10, pady=10)
matplotlib_radio_button = ttk.Radiobutton(frame, text="No", variable=use_seaborn, value=False)
matplotlib_radio_button.grid(column=2, row=1, padx=10, pady=10)

x_axis_label = ttk.Label(frame, text="X Axis:")
x_axis_label.grid(column=0, row=2, padx=10, pady=10)
x_axis_listbox = Listbox(frame, selectmode=MULTIPLE, width=30, height=5)
x_axis_listbox.grid(column=1, row=2, padx=10, pady=10)

store_x_button = ttk.Button(frame, text="Store X-Axis Selection", command=store_x_axis_selection)
store_x_button.grid(column=2, row=2, padx=10, pady=10)

y_axis_label = ttk.Label(frame, text="Y Axis:")
y_axis_label.grid(column=0, row=3, padx=10, pady=10)
y_axis_listbox = Listbox(frame, selectmode=MULTIPLE, width=30, height=5)
y_axis_listbox.grid(column=1, row=3, padx=10, pady=10)

store_y_button = ttk.Button(frame, text="Store Y-Axis Selection", command=store_y_axis_selection)
store_y_button.grid(column=2, row=3, padx=10, pady=10)

chart_type_label = ttk.Label(frame, text="Chart Type:")
chart_type_label.grid(column=0, row=4, padx=10, pady=10)
chart_type_dropdown = ttk.Combobox(frame)
chart_type_dropdown.grid(column=1, row=4, padx=10, pady=10)

title_font_size_label = ttk.Label(frame, text="Title Font Size:")
title_font_size_label.grid(column=0, row=5, padx=10, pady=10)
title_font_size_var = tk.StringVar()
title_font_size_var.set("14")
title_font_size_entry = ttk.Entry(frame, textvariable=title_font_size_var)
title_font_size_entry.grid(column=1, row=5, padx=10, pady=10)

x_axis_font_size_label = ttk.Label(frame, text="X-Axis Font Size:")
x_axis_font_size_label.grid(column=0, row=6, padx=10, pady=10)
x_axis_font_size_var = tk.StringVar()
x_axis_font_size_var.set("10")
x_axis_font_size_entry = ttk.Entry(frame, textvariable=x_axis_font_size_var)
x_axis_font_size_entry.grid(column=1, row=6, padx=10, pady=10)

y_axis_font_size_label = ttk.Label(frame, text="Y-Axis Font Size:")
y_axis_font_size_label.grid(column=0, row=7, padx=10, pady=10)
y_axis_font_size_var = tk.StringVar()
y_axis_font_size_var.set("10")
y_axis_font_size_entry = ttk.Entry(frame, textvariable=y_axis_font_size_var)
y_axis_font_size_entry.grid(column=1, row=7, padx=10, pady=10)

x_tick_label_rotation_label = ttk.Label(frame, text="X-Axis Tick Label Rotation:")
x_tick_label_rotation_label.grid(column=0, row=8, padx=10, pady=10)
x_tick_label_rotation_var = IntVar()
x_tick_label_rotation_var.set(45)
x_radio_0 = ttk.Radiobutton(frame, text="0", variable=x_tick_label_rotation_var, value=0)
x_radio_0.grid(column=1, row=8, padx=5, pady=5)
x_radio_45 = ttk.Radiobutton(frame, text="45", variable=x_tick_label_rotation_var, value=45)
x_radio_45.grid(column=2, row=8, padx=5, pady=5)
x_radio_90 = ttk.Radiobutton(frame, text="90", variable=x_tick_label_rotation_var, value=90)
x_radio_90.grid(column=3, row=8, padx=5, pady=5)

y_tick_label_rotation_label = ttk.Label(frame, text="Y-Axis Tick Label Rotation:")
y_tick_label_rotation_label.grid(column=0, row=9, padx=10, pady=10)
y_tick_label_rotation_var = IntVar()
y_tick_label_rotation_var.set(0)
y_radio_0 = ttk.Radiobutton(frame, text="0", variable=y_tick_label_rotation_var, value=0)
y_radio_0.grid(column=1, row=9, padx=5, pady=5)
y_radio_45 = ttk.Radiobutton(frame, text="45", variable=y_tick_label_rotation_var, value=45)
y_radio_45.grid(column=2, row=9, padx=5, pady=5)
y_radio_90 = ttk.Radiobutton(frame, text="90", variable=y_tick_label_rotation_var, value=90)
y_radio_90.grid(column=3, row=9, padx=5, pady=5)

chart_size_label = ttk.Label(frame, text="Chart Size:")
chart_size_label.grid(column=0, row=10, padx=10, pady=10)
chart_size = tk.StringVar()
chart_size.set("Medium")
chart_size_radio1 = ttk.Radiobutton(frame, text="Small", variable=chart_size, value="Small")
chart_size_radio1.grid(column=1, row=10, padx=5, pady=5)
chart_size_radio2 = ttk.Radiobutton(frame, text="Medium", variable=chart_size, value="Medium")
chart_size_radio2.grid(column=2, row=10, padx=5, pady=5)
chart_size_radio3 = ttk.Radiobutton(frame, text="Large", variable=chart_size, value="Large")
chart_size_radio3.grid(column=3, row=10, padx=5, pady=5)

recommendation_button = ttk.Button(frame, text="Update Recommendation", command=recommend_chart)
recommendation_button.grid(column=0, row=11, padx=10, pady=10)

visualize_button = ttk.Button(frame, text="Visualize", command=generate_visualization)
visualize_button.grid(column=1, row=11, padx=10, pady=10)

clear_button = ttk.Button(frame, text="Clear Selection", command=clear_selections)
clear_button.grid(column=2, row=11, padx=10, pady=10)

recommendation_label = ttk.Label(frame, text="")
recommendation_label.grid(row=12, column=0, columnspan=4, padx=10, pady=10)

root.mainloop()
