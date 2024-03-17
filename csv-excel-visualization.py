import pandas as pd
import matplotlib.pyplot as plt
from tkinter import filedialog, messagebox, ttk, IntVar
import tkinter as tk
import numpy as np

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
        "Small": (9, 7),
        "Medium": (12, 10),
        "Large": (16, 13)
    }
    return sizes[chart_size.get()]

def update_dropdowns(data):
    global dataset
    dataset = data

    column_names = dataset.columns.tolist()
    x_axis_dropdown["values"] = column_names
    y_axis_dropdown["values"] = column_names
    chart_type_dropdown["values"] = ["Line", "Bar", "Column", "Area", "Stacked Bar", "Scatter Plot", "Dual Axes"]

def recommend_chart(event):
    if x_axis_dropdown.get() and y_axis_dropdown.get():
        x_column = x_axis_dropdown.get()
        y_column = y_axis_dropdown.get()
        x_type = dataset[x_column].dtype
        y_type = dataset[y_column].dtype
        recommendation = ""

        if np.issubdtype(x_type, np.number) and np.issubdtype(y_type, np.number):
            recommendation = "Scatter Plot"
        elif np.issubdtype(x_type, np.number) and (dataset[y_column].nunique() <= 10):
            recommendation = "Bar"
        elif (dataset[x_column].nunique() <= 10) and np.issubdtype(y_type, np.number):
            recommendation = "Bar"
        elif (dataset[x_column].nunique() <= 10) and (dataset[y_column].nunique() <= 10):
            recommendation = "Stacked Bar"
        elif np.issubdtype(x_type, np.object_) and np.issubdtype(y_type, np.object_):
            recommendation = "Scatter Plot"
        else:
            recommendation = "Scatter Plot"

        recommendation_label["text"] = f"Recommended Chart: {recommendation}"

        # Set recommendation as the selected option in the Chart Type dropdown
        chart_type_dropdown.set(recommendation)

        x_axis_label["text"] = f"X Axis ({get_data_type(x_type, x_column)}):"
        y_axis_label["text"] = f"Y Axis ({get_data_type(y_type, y_column)}):"

def get_data_type(dtype, column):
    if np.issubdtype(dtype, np.number):
        return "Number"
    elif dataset[column].nunique() <= 10:
        return "Categorical"
    else:
        return "Non-categorical"

def validate_font_size(entry_value):
    """Validate the font size entry to be numeric and between 3 and 24."""
    try:
        value = int(entry_value)
        if 3 <= value <= 24:
            return True
    except ValueError:
        pass
    
    messagebox.showwarning("Invalid Input", "Please enter a numeric value between 3 and 24.")
    return False

def recommend_chart_type(x_column, y_column):
    x_type = dataset[x_column].dtype
    y_type = dataset[y_column].dtype
    if np.issubdtype(x_type, np.number) and np.issubdtype(y_type, np.number):
        return "Scatter Plot"
    elif np.issubdtype(x_type, np.number) or np.issubdtype(y_type, np.number):
        return "Bar"
    else:
        # For two categorical variables, consider a different approach or inform the user
        return "Heatmap or Frequency Table"

def generate_visualization():
    try:
        chart_type = chart_type_dropdown.get()
        x_column = x_axis_dropdown.get()
        y_column = y_axis_dropdown.get()

        title_font_size = int(title_font_size_var.get()) if validate_font_size(title_font_size_var.get()) else 12
        tick_label_font_size = int(tick_label_font_size_var.get()) if validate_font_size(tick_label_font_size_var.get()) else 10
        tick_label_rotation = tick_label_rotation_var.get()

        plt.figure(figsize=get_chart_size())

        # Rotation setup for tick labels should be handled alongside explicit font size setting like so:
        plt.xticks(rotation=tick_label_rotation)
        plt.yticks(rotation=tick_label_rotation)  # If you want y-tick labels rotated as well

        # Correct application of tick label font size after specifying rotation
        plt.tick_params(axis='x', labelsize=tick_label_font_size)
        plt.tick_params(axis='y', labelsize=tick_label_font_size)

        if chart_type == "Line":
            plt.plot(dataset[x_column], dataset[y_column])
        elif chart_type == "Bar":
            plt.bar(dataset[x_column], dataset[y_column])
        elif chart_type == "Column":
            plt.barh(dataset[y_column], dataset[x_column])
        elif chart_type == "Area":
            plt.fill_between(dataset[x_column], dataset[y_column])
        elif chart_type == "Stacked Bar":
            crosstab = pd.crosstab(dataset[x_column], dataset[y_column])
            crosstab.plot(kind='bar', stacked=True)
        elif chart_type == "Scatter Plot":
            plt.scatter(dataset[x_column], dataset[y_column])
        elif chart_type == "Dual Axes":
            fig, ax1 = plt.subplots(figsize=get_chart_size())
            ax2 = ax1.twinx()
            ax1.plot(dataset[x_column], label=x_column)
            ax2.plot(dataset[y_column], 'r', label=y_column)
            ax1.set_xlabel(x_column, fontsize=tick_label_font_size)
            ax1.set_ylabel(y_column, fontsize=tick_label_font_size)
            ax1.tick_params(axis='x', labelsize=tick_label_font_size)
            ax1.tick_params(axis='y', labelsize=tick_label_font_size)
            ax2.tick_params(axis='y', labelsize=tick_label_font_size)

        plt.xlabel(x_column, fontsize=tick_label_font_size)
        plt.ylabel(y_column, fontsize=tick_label_font_size)
        plt.title(f"{chart_type}: {x_column} vs {y_column}", fontsize=title_font_size)

        plt.show()

    except ValueError as e:
        messagebox.showerror("Error", "Invalid font size. Please enter a number between 3 and 24.")
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
root.title("CSV/Excel Data Visualizer")

frame = ttk.Frame(root, padding="10")
frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
load_button = ttk.Button(frame, text="Load File", command=load_file)
load_button.grid(column=0, row=0, padx=10, pady=10)

x_axis_label = ttk.Label(frame, text="X Axis:")
x_axis_label.grid(column=0, row=1, padx=10, pady=10)
x_axis_dropdown = ttk.Combobox(frame)
x_axis_dropdown.grid(column=1, row=1, padx=10, pady=10)
x_axis_dropdown.bind("<<ComboboxSelected>>", recommend_chart)

y_axis_label = ttk.Label(frame, text="Y Axis:")
y_axis_label.grid(column=0, row=2, padx=10, pady=10)
y_axis_dropdown = ttk.Combobox(frame)
y_axis_dropdown.grid(column=1, row=2, padx=10, pady=10)
y_axis_dropdown.bind("<<ComboboxSelected>>", recommend_chart)

chart_type_label = ttk.Label(frame, text="Chart Type:")
chart_type_label.grid(column=0, row=3, padx=10, pady=10)
chart_type_dropdown = ttk.Combobox(frame)
chart_type_dropdown.grid(column=1, row=3, padx=10, pady=10)

# Entry for title/header font size
title_font_size_label = ttk.Label(frame, text="Title Font Size:")
title_font_size_label.grid(column=0, row=4, padx=10, pady=10)
title_font_size_var = tk.StringVar()
title_font_size_var.set("14")  # Set the default text to 14
title_font_size_entry = ttk.Entry(frame, textvariable=title_font_size_var)
title_font_size_entry.grid(column=1, row=4, padx=10, pady=10)

# Entry for tick label font size
tick_label_font_size_label = ttk.Label(frame, text="Tick Label Font Size:")
tick_label_font_size_label.grid(column=0, row=5, padx=10, pady=10)
tick_label_font_size_var = tk.StringVar()
tick_label_font_size_var.set("8")  # Set the default text to 8
tick_label_font_size_entry = ttk.Entry(frame, textvariable=tick_label_font_size_var)
tick_label_font_size_entry.grid(column=1, row=5, padx=10, pady=10)

# Correcting the row for chart size radio buttons
chart_size_label = ttk.Label(frame, text="Chart Size:")
chart_size_label.grid(column=0, row=6, padx=10, pady=10)
chart_size = tk.StringVar()  # Use StringVar for string-based selections
chart_size.set("Large")  # Default chart size
chart_size_radio1 = ttk.Radiobutton(frame, text="Small", variable=chart_size, value="Small")
chart_size_radio1.grid(column=1, row=6, padx=5, pady=5)
chart_size_radio2 = ttk.Radiobutton(frame, text="Medium", variable=chart_size, value="Medium")
chart_size_radio2.grid(column=2, row=6, padx=5, pady=5)
chart_size_radio3 = ttk.Radiobutton(frame, text="Large", variable=chart_size, value="Large")
chart_size_radio3.grid(column=3, row=6, padx=5, pady=5)

# Adjusted positions for the visualize and clear buttons, and the recommendation label
visualize_button = ttk.Button(frame, text="Visualize", command=generate_visualization)
visualize_button.grid(column=0, row=7, padx=10, pady=10)  # Moved to row=7

clear_button = ttk.Button(frame, text="Clear", command=clear_selections)
clear_button.grid(column=1, row=7, padx=10, pady=10)  # Moved to row=7

recommendation_label = ttk.Label(frame, text="")
recommendation_label.grid(row=9, columnspan=4, pady=10)  # Adjusted to new row

# Adding radio buttons for X-axis tick label rotation selection in your Tkinter GUI setup
tick_label_rotation_var = IntVar()
tick_label_rotation_var.set(45)  # Default rotation set to 45°

tick_label_rotation_label = ttk.Label(frame, text="X-Axis Tick Label Rotation:")
tick_label_rotation_label.grid(column=0, row=8, padx=10, pady=10)
radio_45 = ttk.Radiobutton(frame, text="45°", variable=tick_label_rotation_var, value=45)
radio_45.grid(column=1, row=8, padx=5, pady=5)
radio_90 = ttk.Radiobutton(frame, text="90°", variable=tick_label_rotation_var, value=90)
radio_90.grid(column=2, row=8, padx=5, pady=5)
radio_0 = ttk.Radiobutton(frame, text="0°", variable=tick_label_rotation_var, value=0)
radio_0.grid(column=3, row=8, padx=5, pady=5)

# Your Tkinter GUI main loop
root.mainloop()
