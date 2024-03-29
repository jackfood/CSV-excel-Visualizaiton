import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from tkinter import filedialog, messagebox, ttk, IntVar
import tkinter as tk
import numpy as np
from PIL import Image, ImageTk
import os

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
           messagebox.showerror("Error", str(e))

def get_label_size():
   return int(label_size.get())

def get_chart_size():
   sizes = {
       "Small": (8, 6),
       "Medium": (10, 8),
       "Large": (20, 16)
   }
   return sizes[chart_size.get()]

def update_dropdowns(data):
   global dataset
   dataset = data

   column_names = dataset.columns.tolist()
   x_axis_dropdown["values"] = column_names
   y_axis_dropdown["values"] = column_names
   chart_type_dropdown["values"] = ["Line", "Bar", "Column", "Area", "Stacked Bar", "Scatter Plot", "Dual Axes", "Histogram"]

def recommend_chart(event):
   if x_axis_dropdown.get() and y_axis_dropdown.get():
       x_column = x_axis_dropdown.get()
       y_column = y_axis_dropdown.get()
       recommendation = recommend_chart_type(dataset, x_column, y_column)
       recommendation_label["text"] = f"Recommended Chart: {recommendation}"
       chart_type_dropdown.set(recommendation)
       x_axis_label["text"] = f"X Axis ({get_data_type(dataset[x_column].dtype, x_column)}):"
       y_axis_label["text"] = f"Y Axis ({get_data_type(dataset[y_column].dtype, y_column)}):"

def get_data_type(dtype, column):
   if np.issubdtype(dtype, np.number):
       return "Number"
   elif dataset[column].nunique() <= 10:
       return "Categorical"
   else:
       return "Non-categorical"

def advanced_chart_recommendation(x_column, y_column, dataset):
   x_dtype = dataset[x_column].dtype
   y_dtype = dataset[y_column].dtype
   x_unique_count = dataset[x_column].nunique()
   y_unique_count = dataset[y_column].nunique()
   dataset_length = len(dataset)
   
   # Check for numeric data types
   if pd.api.types.is_numeric_dtype(x_dtype) and pd.api.types.is_numeric_dtype(y_dtype):
       if dataset_length > 1000:
           return "Scatter Plot"
       else:
           return "Line"
   # Adjust check for categorical data types using the recommended approach
   elif isinstance(x_dtype, pd.CategoricalDtype) or pd.api.types.is_object_dtype(x_dtype):
       if y_unique_count <= 10:
           return "Bar"
       else:
           if dataset_length > 50:
               return "Box Plot"
           else:
               return "Bar"
   # Adjust check for categorical data types for y_dtype as well
   elif isinstance(y_dtype, pd.CategoricalDtype) or pd.api.types.is_object_dtype(y_dtype):
       if x_unique_count <= 10:
           return "Pie Chart" if dataset_length <= 20 else "Bar"
       else:
           return "Histogram"
   else:
       return "Scatter Plot"

def generate_visualization():
   try:
       chart_type = chart_type_dropdown.get()
       x_column = x_axis_dropdown.get()
       y_column = y_axis_dropdown.get()

       title_font_size = int(title_font_size_var.get())
       tick_label_font_size = int(tick_label_font_size_var.get())
       tick_label_rotation = tick_label_rotation_var.get()

       fig, ax = plt.subplots(figsize=get_chart_size())  # Explicit figure and axes creation

       if use_seaborn.get():
           sns.set(style="whitegrid")

       if chart_type == "Bar" or chart_type == "Column":
           if use_seaborn.get():
               if chart_type == "Bar":
                   sns.barplot(x=x_column, y=y_column, data=dataset, ax=ax)
               else:  # Column
                   sns.barplot(x=y_column, y=x_column, data=dataset, ax=ax, orient='h')
           else:
               if chart_type == "Bar":
                   ax.bar(dataset[x_column], dataset[y_column], color='skyblue')
               else:  # Column
                   ax.barh(dataset[x_column], dataset[y_column], color='skyblue')
           ax.set_xlabel(x_column, fontsize=tick_label_font_size)
           ax.set_ylabel(y_column, fontsize=tick_label_font_size)
       elif chart_type == "Area":
           ax.fill_between(range(len(dataset[x_column])), dataset[y_column])
           ax.set_xlabel(x_column, fontsize=tick_label_font_size)
           ax.set_ylabel(y_column, fontsize=tick_label_font_size)
       elif chart_type == "Stacked Bar":
           crosstab = pd.crosstab(dataset[x_column], dataset[y_column])
           if use_seaborn.get():
               sns.barplot(x=x_column, y=y_column, data=dataset, ax=ax)
           else:
               crosstab.plot(kind='bar', stacked=True, ax=ax)
       elif chart_type == "Scatter Plot":
           if use_seaborn.get():
               sns.scatterplot(x=x_column, y=y_column, data=dataset, ax=ax)
           else:
               ax.scatter(dataset[x_column], dataset[y_column])
           ax.set_xlabel(x_column, fontsize=tick_label_font_size)
           ax.set_ylabel(y_column, fontsize=tick_label_font_size)
       elif chart_type == "Line":
           if use_seaborn.get():
               sns.lineplot(x=x_column, y=y_column, data=dataset, ax=ax)
           else:
               ax.plot(dataset[x_column], dataset[y_column])
           ax.set_xlabel(x_column, fontsize=tick_label_font_size)
           ax.set_ylabel(y_column, fontsize=tick_label_font_size)
       elif chart_type == "Histogram":
           if use_seaborn.get():
               sns.histplot(data=dataset, x=x_column, ax=ax)
           else:
               ax.hist(dataset[x_column], bins=10)
           ax.set_xlabel(x_column, fontsize=tick_label_font_size)
           ax.set_ylabel('Frequency', fontsize=tick_label_font_size)
       elif chart_type == "Dual Axes":
           ax2 = ax.twinx()
           ax.plot(dataset[x_column], label=x_column, color='skyblue')
           ax2.plot(dataset[y_column], label=y_column, color='darkorange')
           ax.set_xlabel(x_column, fontsize=tick_label_font_size)
           ax.set_ylabel(x_column, fontsize=tick_label_font_size)
           ax2.set_ylabel(y_column, fontsize=tick_label_font_size)
           ax.tick_params(axis='x', labelsize=tick_label_font_size, rotation=tick_label_rotation)
           ax.tick_params(axis='y', labelsize=tick_label_font_size)
           ax2.tick_params(axis='y', labelsize=tick_label_font_size)

       ax.set_title(f"{chart_type}: {x_column} vs {y_column}", fontsize=title_font_size)

       plt.show()

   except Exception as e:
       messagebox.showerror("Error", str(e))

def clear_selections():
   x_axis_dropdown.set("")
   y_axis_dropdown.set("")
   chart_type_dropdown.set("")
   x_axis_label["text"] = "X Axis:"
   y_axis_label["text"] = "Y Axis:"
   recommendation_label["text"] = ""

root = tk.Tk()
root.title("CSV/Excel Data Visualizer 1.03")

frame = ttk.Frame(root, padding="10")
frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
load_button = ttk.Button(frame, text="Load File", command=load_file)
load_button.grid(column=0, row=0, padx=10, pady=10)

# Add radio buttons for selecting seaborn or matplotlib
use_seaborn = tk.BooleanVar()
use_seaborn.set(False)  # Default to matplotlib
seaborn_label = ttk.Label(frame, text="Use Seaborn:")
seaborn_label.grid(column=0, row=1, padx=10, pady=10)
seaborn_radio_button = ttk.Radiobutton(frame, text="Seaborn", variable=use_seaborn, value=True)
seaborn_radio_button.grid(column=1, row=1, padx=10, pady=10)
matplotlib_radio_button = ttk.Radiobutton(frame, text="Matplotlib", variable=use_seaborn, value=False)
matplotlib_radio_button.grid(column=2, row=1, padx=10, pady=10)

x_axis_label = ttk.Label(frame, text="X Axis:")
x_axis_label.grid(column=0, row=2, padx=10, pady=10)
x_axis_dropdown = ttk.Combobox(frame)
x_axis_dropdown.grid(column=1, row=2, padx=10, pady=10)
x_axis_dropdown.bind("<<ComboboxSelected>>", recommend_chart)

y_axis_label = ttk.Label(frame, text="Y Axis:")
y_axis_label.grid(column=0, row=3, padx=10, pady=10)
y_axis_dropdown = ttk.Combobox(frame)
y_axis_dropdown.grid(column=1, row=3, padx=10, pady=10)
y_axis_dropdown.bind("<<ComboboxSelected>>", recommend_chart)

chart_type_label = ttk.Label(frame, text="Chart Type:")
chart_type_label.grid(column=0, row=4, padx=10, pady=10)
chart_type_dropdown = ttk.Combobox(frame)
chart_type_dropdown.grid(column=1, row=4, padx=10, pady=10)

# Entry for title/header font size
title_font_size_label = ttk.Label(frame, text="Title Font Size:")
title_font_size_label.grid(column=0, row=5, padx=10, pady=10)
title_font_size_var = tk.StringVar()
title_font_size_var.set("14")  # Set the default text to 14
title_font_size_entry = ttk.Entry(frame, textvariable=title_font_size_var)
title_font_size_entry.grid(column=1, row=5, padx=10, pady=10)

# Entry for tick label font size
tick_label_font_size_label = ttk.Label(frame, text="Tick Label Font Size:")
tick_label_font_size_label.grid(column=0, row=6, padx=10, pady=10)
tick_label_font_size_var = tk.StringVar()
tick_label_font_size_var.set("8")  # Set the default text to 8
tick_label_font_size_entry = ttk.Entry(frame, textvariable=tick_label_font_size_var)
tick_label_font_size_entry.grid(column=1, row=6, padx=10, pady=10)

# Chart size radio buttons
chart_size_label = ttk.Label(frame, text="Chart Size:")
chart_size_label.grid(column=0, row=7, padx=10, pady=10)
chart_size = tk.StringVar()  # Use StringVar for string-based selections
chart_size.set("Large")  # Default chart size
chart_size_radio1 = ttk.Radiobutton(frame, text="Small", variable=chart_size, value="Small")
chart_size_radio1.grid(column=1, row=7, padx=5, pady=5)
chart_size_radio2 = ttk.Radiobutton(frame, text="Medium", variable=chart_size, value="Medium")
chart_size_radio2.grid(column=2, row=7, padx=5, pady=5)
chart_size_radio3 = ttk.Radiobutton(frame, text="Large", variable=chart_size, value="Large")
chart_size_radio3.grid(column=3, row=7, padx=5, pady=5)

# Buttons and recommendation label
visualize_button = ttk.Button(frame, text="Visualize", command=generate_visualization)
visualize_button.grid(column=0, row=8, padx=10, pady=10)

clear_button = ttk.Button(frame, text="Clear", command=clear_selections)
clear_button.grid(column=1, row=8, padx=10, pady=10)

recommendation_label = ttk.Label(frame, text="")
recommendation_label.grid(row=10, columnspan=4, pady=10)

# Adding radio buttons for X-axis tick label rotation selection
tick_label_rotation_var = IntVar()
tick_label_rotation_var.set(45)  # Default rotation set to 45°

tick_label_rotation_label = ttk.Label(frame, text="X-Axis Tick Label Rotation:")
tick_label_rotation_label.grid(column=0, row=9, padx=10, pady=10)
radio_45 = ttk.Radiobutton(frame, text="45°", variable=tick_label_rotation_var, value=45)
radio_45.grid(column=1, row=9, padx=5, pady=5)
radio_90 = ttk.Radiobutton(frame, text="90°", variable=tick_label_rotation_var, value=90)
radio_90.grid(column=2, row=9, padx=5, pady=5)
radio_0 = ttk.Radiobutton(frame, text="0°", variable=tick_label_rotation_var, value=0)
radio_0.grid(column=3, row=9, padx=5, pady=5)

# Your Tkinter GUI main loop
root.mainloop()
