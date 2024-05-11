import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from tkinter import filedialog, messagebox, simpledialog, ttk, Listbox, MULTIPLE, IntVar, StringVar, Checkbutton
import tkinter as tk
import numpy as np
from scipy.stats import norm, skew, linregress
from PIL import Image, ImageTk
import os

# GUI components
root = tk.Tk()
root.title("CSV/Excel Data Visualizer v1.5.1.0511")

global x_selected_fields, y_selected_fields, dataset
x_selected_fields = []
y_selected_fields = []
dataset = pd.DataFrame()
display_skew = IntVar()
display_aggression = IntVar()

# Helper dialog function to ask for custom bins
def ask_for_histogram_customization(data):
    """
    Ask the user for custom histogram settings with recommended default values.
    
    Parameters:
    - data: The dataset from which to derive the default min, max, and number of bins.
    
    Returns:
    - tuple (bool, list of bin edges) if custom settings are used,
    - (False, None) if default settings should be used.
    """
    # Determine the default values based on the data
    data_min, data_max = data.min(), data.max()
    bin_width = 2 * (np.percentile(data, 75) - np.percentile(data, 25)) * len(data) ** (-1/3)
    default_bins = max(1, int((data_max - data_min) / bin_width))
    
    # Initial message to the user
    response = messagebox.askyesno(
        "Customize Histogram", 
        f"Do you want to customize the histogram range and bins?\n\n"
        f"Suggested range: {data_min:.2f} to {data_max:.2f}\n"
        f"Suggested number of bins: {default_bins}"
    )

    if response:
        while True:
            try:
                # Asking for the minimum edge with a default suggestion
                min_edge = simpledialog.askfloat(
                    "Minimum Edge", 
                    f"Enter the minimum value of the range (suggested: {data_min:.2f}):",
                    initialvalue=data_min
                )

                # Asking for the maximum edge with a default suggestion
                max_edge = simpledialog.askfloat(
                    "Maximum Edge", 
                    f"Enter the maximum value of the range (suggested: {data_max:.2f}):",
                    initialvalue=data_max
                )

                # Asking for the number of bins with a default suggestion
                num_bins = simpledialog.askinteger(
                    "Number of Bins", 
                    f"Enter the number of bins (suggested: {default_bins}):",
                    initialvalue=default_bins
                )

                # Validating the user's input
                if min_edge is None or max_edge is None or num_bins is None:
                    messagebox.showwarning("Invalid Input", "You must provide all inputs. Using default settings.")
                    return (False, None)

                if min_edge >= max_edge:
                    messagebox.showerror("Error", "Minimum edge must be less than maximum edge.")
                    continue

                if num_bins <= 0:
                    messagebox.showerror("Error", "Number of bins must be positive.")
                    continue

                # Generate the bin edges based on user input
                bin_edges = np.linspace(min_edge, max_edge, num_bins + 1)
                return (True, bin_edges)

            except ValueError:
                messagebox.showerror("Error", "Please enter valid numbers.")
                continue

    return (False, None)

def ask_for_bar_customization():
    """
    Prompt the user to customize the bar chart's sorting order and the number of top items to display.
    """
    response = messagebox.askyesno("Customize Bar Chart", "Do you want to customize the bar chart settings?")
    if response:
        order = simpledialog.askstring("Sorting Order", "Enter 'asc' for ascending or 'desc' for descending:")
        if order not in ['asc', 'desc']:
            messagebox.showerror("Error", "Invalid order. Please enter 'asc' or 'desc'.")
            return None, None

        max_items = simpledialog.askinteger("Number of Items", "Enter the number of top items to display (Max is {}):".format(len(dataset)))
        if max_items is None or max_items < 1 or max_items > len(dataset):
            messagebox.showerror("Error", "Invalid number of items. Please enter a valid number.")
            return None, None

        return order, max_items
    return None, None

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
    update_options_based_on_chart_type()

def update_options_based_on_chart_type():
    chart_type = chart_type_dropdown.get()
    if chart_type == "Histogram":
        skew_line_checkbutton.config(state=tk.NORMAL)
        aggression_checkbutton.config(state=tk.DISABLED)
    elif chart_type == "Scatter Plot":
        aggression_checkbutton.config(state=tk.NORMAL)
        skew_line_checkbutton.config(state=tk.DISABLED)
    else:
        aggression_checkbutton.config(state=tk.DISABLED)
        skew_line_checkbutton.config(state=tk.DISABLED)

def store_x_axis_selection():
    global x_selected_fields
    x_selected_fields = [x_axis_listbox.get(idx) for idx in x_axis_listbox.curselection()]
    x_axis_label["text"] = f"X Axis (Selected: {', '.join(x_selected_fields)}):" if x_selected_fields else "X Axis:"
    update_options_based_on_selection()

def store_y_axis_selection():
    global y_selected_fields
    y_selected_fields = [y_axis_listbox.get(idx) for idx in y_axis_listbox.curselection()]
    y_axis_label["text"] = f"Y Axis (Selected: {', '.join(y_selected_fields)}):" if y_selected_fields else "Y Axis:"
    update_options_based_on_selection()

def update_options_based_on_selection():
    if x_selected_fields and y_selected_fields and all(dataset[col].dtype.kind in 'fi' for col in x_selected_fields + y_selected_fields):
        aggression_checkbutton.config(state=tk.NORMAL)
    else:
        aggression_checkbutton.config(state=tk.DISABLED)

def recommend_chart():
    if x_selected_fields and y_selected_fields:
        recommendation = advanced_chart_recommendation(x_selected_fields, y_selected_fields, dataset)
        recommendation_label["text"] = f"Recommended Chart: {recommendation}"
        chart_type_dropdown.set(recommendation)
        update_options_based_on_chart_type()
    else:
        recommendation_label["text"] = "Select fields for X and Y axes."

def advanced_chart_recommendation(x_columns, y_columns, dataset):
    if not x_columns or not y_columns:
        return "Select appropriate data fields"

    x_dtype = dataset[x_columns[0]].dtype
    y_dtype = dataset[y_columns[0]].dtype
    x_unique_count = dataset[x_columns[0]].nunique()
    y_unique_count = dataset[y_columns[0]].nunique()
    total_entries = len(dataset)

    # Checking for single variable usage
    if len(x_columns) == 1 and x_columns == y_columns:
        if pd.api.types.is_numeric_dtype(x_dtype):
            return "Histogram"
        else:
            return "Pie Chart" if x_unique_count < 20 else "Bar"

    # Multi-variable interactions
    if len(x_columns) > 1 or len(y_columns) > 1:
        if all(dataset[col].dtype.kind in 'fi' for col in x_columns + y_columns):
            correlation = dataset[x_columns + y_columns].corr()
            # Check if high correlation exists
            if (correlation.abs() > 0.75).any().any():
                return "Line"  # Strong linear relationship
            else:
                return "Scatter Plot"  # To explore potential relationships and distributions

    # Single X, multiple Y or vice versa
    if len(x_columns) == 1 and len(y_columns) > 1:
        if pd.api.types.is_numeric_dtype(x_dtype) and all(dataset[y].dtype.kind in 'fi' for y in y_columns):
            return "Line"  # Time series or continuous relationships
        else:
            return "Stacked Bar"  # Categorical comparison across multiple Y variables

    # Categorical X, Numeric Y
    if pd.api.types.is_categorical_dtype(x_dtype) or pd.api.types.is_object_dtype(x_dtype):
        if y_unique_count <= 10:
            return "Bar"
        elif total_entries > 50:
            return "Box Plot"
        return "Bar"

    # Numeric X, Categorical Y
    if pd.api.types.is_numeric_dtype(x_dtype) and (pd.api.types.is_categorical_dtype(y_dtype) or pd.api.types.is_object_dtype(y_dtype)):
        if x_unique_count <= 10 and total_entries <= 20:
            return "Pie Chart"
        return "Line"  # To explore trends across categories

    # Default for numeric types or mixed usage
    return "Scatter Plot" if total_entries > 1000 else "Line"


def plot_bar(ax, plot_data):
    if len(x_selected_fields) != 1 or len(y_selected_fields) != 1:
        messagebox.showerror("Error", "Bar plot requires exactly one X field and one Y field.")
        return

    # Ensure y-axis data is numeric
    if not pd.api.types.is_numeric_dtype(plot_data[y_selected_fields[0]]):
        messagebox.showerror("Error", "Y-axis data must be numeric (int or float) for bar plots.")
        return

    try:
        # Aggregating data by the X field
        # Change 'mean' to 'sum', 'max', 'min', or any other appropriate aggregation
        aggregated_data = plot_data.groupby(x_selected_fields[0], as_index=False)[y_selected_fields[0]].mean()

        # Ask for customization
        order, max_items = ask_for_bar_customization()
        if order and max_items:
            aggregated_data = aggregated_data.nlargest(max_items, y_selected_fields[0]) if order == 'desc' else aggregated_data.nsmallest(max_items, y_selected_fields[0])
        
        x = aggregated_data[x_selected_fields[0]]
        y = aggregated_data[y_selected_fields[0]]
        bar_width = 0.8

        # Convert x values to strings for labeling purposes
        x = x.astype(str)

        if use_seaborn.get():
            sns.barplot(data=aggregated_data, x=x_selected_fields[0], y=y_selected_fields[0], ax=ax, color='lightblue', orient='v')
        else:
            ax.bar(x, y, width=bar_width, color='lightblue')

        ax.set_xticks(range(len(x)))
        ax.set_xticklabels(x, rotation=x_tick_label_rotation_var.get(), fontsize=int(x_axis_font_size_var.get()))

    except Exception as e:
        messagebox.showerror("Error", f"Failed to plot bar chart: {str(e)}")

def plot_area(ax, plot_data):
    if len(x_selected_fields) != 1:
        messagebox.showerror("Error", "Area plot requires exactly one X field and multiple Y fields.")
        return
    for y_col in y_selected_fields:
        ax.fill_between(plot_data[x_selected_fields[0]], plot_data[y_col], alpha=0.3, label=y_col, color='#66c2a5')
    ax.legend()

def plot_stacked_bar(ax, plot_data):
    if len(x_selected_fields) != 1:
        messagebox.showerror("Error", "Stacked Bar plot requires exactly one X field and multiple Y fields.")
        return
    if not y_selected_fields:
        messagebox.showerror("Error", "Stacked Bar plot requires at least one Y field.")
        return

    # Preparing the data for plotting
    crosstab_data = plot_data.groupby(x_selected_fields[0])[y_selected_fields].sum()

    if use_seaborn.get():
        # Seaborn doesn't support stacked bars directly, use Matplotlib's functionality
        bottom = np.zeros(len(crosstab_data))
        palette = sns.color_palette("husl", len(y_selected_fields))  # Get a color palette from Seaborn
        for idx, col in enumerate(y_selected_fields):
            ax.bar(crosstab_data.index, crosstab_data[col], bottom=bottom, label=col, color=palette[idx])
            bottom += crosstab_data[col].values  # Update the bottom position for the next bar
    else:
        # Directly use Matplotlib's stacked bar functionality
        crosstab_data.plot(kind='bar', stacked=True, ax=ax, color=sns.color_palette("husl", len(y_selected_fields)))

    ax.set_xticks(range(len(crosstab_data.index)))
    ax.set_xticklabels(crosstab_data.index, rotation=x_tick_label_rotation_var.get(), fontsize=int(x_axis_font_size_var.get()))
    ax.set_xlabel(x_selected_fields[0], fontsize=int(x_axis_font_size_var.get()))
    ax.set_ylabel("Sum of Values", fontsize=int(y_axis_font_size_var.get()))
    ax.legend(title="Categories")

def plot_scatter(ax, plot_data):
    # Ensure the columns are numeric and handle NaN values
    if plot_data[x_selected_fields[0]].dtype.kind not in 'fi' or plot_data[y_selected_fields[0]].dtype.kind not in 'fi':
        messagebox.showerror("Error", "Scatter plot requires numeric data types for both axes.")
        return

    # Drop NaN values from the data used in the scatter plot to avoid errors in calculations
    plot_data = plot_data.dropna(subset=[x_selected_fields[0], y_selected_fields[0]])

    # Plotting the scatter plot
    if use_seaborn.get():
        sns.scatterplot(data=plot_data, x=x_selected_fields[0], y=y_selected_fields[0], ax=ax, color='#66c2a5')
    else:
        ax.scatter(plot_data[x_selected_fields[0]], plot_data[y_selected_fields[0]], color='#66c2a5')

    # Checking if the aggression line should be displayed
    if display_aggression.get():
        try:
            x_data = plot_data[x_selected_fields[0]].astype(float)
            y_data = plot_data[y_selected_fields[0]].astype(float)
            slope, intercept, r_value, p_value, std_err = linregress(x_data, y_data)
            ax.plot(x_data, intercept + slope * x_data, color="lightpink", label=f'Aggression Line: y={intercept:.2f}+{slope:.2f}x')

            textstr = f'Slope: {slope:.2f}, R-squared: {r_value**2:.2f}'
            props = dict(boxstyle='round', facecolor='white', alpha=0.5)
            ax.text(0.95, 0.05, textstr, transform=ax.transAxes, fontsize=8, verticalalignment='bottom', horizontalalignment='right', bbox=props)
            ax.legend()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to compute aggression line: {str(e)}")

    ax.legend()


def plot_dual_axes(ax, plot_data):
    if len(x_selected_fields) != 1 or len(y_selected_fields) != 1:
        messagebox.showerror("Error", "Dual Axes plot requires exactly one X field and one Y field.")
        return
    ax2 = ax.twinx()
    ax.plot(plot_data[x_selected_fields[0]], plot_data[y_selected_fields[0]], label=x_selected_fields[0], color='#66c2a5')
    ax2.plot(plot_data[y_selected_fields[0]], label=y_selected_fields[0], color='#fc8d62')
    ax2.set_ylabel(", ".join(y_selected_fields), fontsize=int(y_axis_font_size_var.get()))
    ax.legend()

def plot_histogram(ax, plot_data):
    data = plot_data[x_selected_fields[0]]

    # Use the improved dialog function with data to get user preferences
    use_custom_bins, custom_bins = ask_for_histogram_customization(data)

    if use_custom_bins:
        # Plot histogram with the custom bins provided by the user
        counts, bins, patches = ax.hist(data, bins=custom_bins, color='lightblue', edgecolor='black', alpha=0.7)
    else:
        # Automatic bins - Freedman-Diaconis rule as a fallback
        q25, q75 = np.percentile(data, [25, 75])
        bin_width = 2 * (q75 - q25) * len(data) ** (-1/3)
        if bin_width == 0:
            bin_width = 2.7 * np.std(data) / (len(data) ** (1/3))

        bin_count = int((data.max() - data.min()) / bin_width)
        counts, bins, patches = ax.hist(data, bins=bin_count, color='lightblue', edgecolor='black', alpha=0.7)

    # Setting labels and titles
    ax.set_xlabel(", ".join(x_selected_fields), fontsize=12)
    ax.set_ylabel("Frequency", fontsize=12)
    ax.set_title(f"Histogram: {', '.join(x_selected_fields)}", fontsize=14)

    # Skewness information
    mean_value = np.mean(data)
    std_dev = np.std(data)
    skew_value = skew(data)

    if display_skew.get():
        skew_text = f"Mean: {mean_value:.2f}, Std Dev: {std_dev:.2f}, Skew: {skew_value:.2f}"
        props = dict(boxstyle='round', facecolor='white', alpha=0.8)
        ax.text(0.95, 0.95, skew_text, transform=ax.transAxes, fontsize=10, verticalalignment='top', horizontalalignment='right', bbox=props)

        x = np.linspace(min(bins), max(bins), 400)
        scale_factor = len(data) * np.diff(bins[:2])[0]
        y_skew = norm.pdf(x, mean_value, std_dev) * scale_factor

        skew_adjustment = skew_value * (x - mean_value)**3 / (3 * std_dev**3)
        y_skew += skew_adjustment

        ax.plot(x, y_skew, color='lightpink', linestyle='--', linewidth=2, label='Skewness Line')
        ax.legend()

    ax.grid(axis='y', linestyle='--', alpha=0.7)

def plot_box(ax, plot_data):
    if len(x_selected_fields) != 1 or len(y_selected_fields) != 1:
        ax.clear()
        ax.text(0.5, 0.5, "Box plot requires exactly one X field and one Y field.", ha='center', va='center')
        return

    x_field = x_selected_fields[0]
    y_field = y_selected_fields[0]

    if x_field not in plot_data.columns or y_field not in plot_data.columns:
        ax.clear()
        ax.text(0.5, 0.5, f"Selected fields ({x_field}, {y_field}) not found in the dataset.", ha='center', va='center')
        return

    if not np.issubdtype(plot_data[y_field].dtype, np.number):
        ax.clear()
        ax.text(0.5, 0.5, f"Y field ({y_field}) must be numeric for box plot.", ha='center', va='center')
        return

    if use_seaborn.get():
        if plot_data[x_field].nunique() > 1:
            try:
                sns.boxplot(data=plot_data, x=x_field, y=y_field, ax=ax)
            except ValueError as e:
                ax.clear()
                ax.text(0.5, 0.5, str(e), ha='center', va='center')
        else:
            try:
                sns.boxplot(data=plot_data, y=y_field, ax=ax)
            except ValueError as e:
                ax.clear()
                ax.text(0.5, 0.5, str(e), ha='center', va='center')
    else:
        if plot_data[x_field].nunique() > 1:
            grouped_data = [group[y_field].values for _, group in plot_data.groupby(x_field)]
            labels = plot_data[x_field].unique()
            ax.boxplot(grouped_data, labels=labels)
        else:
            ax.boxplot([plot_data[y_field].values], labels=[x_field])

def plot_pie(ax, plot_data, x_selected_fields, y_selected_fields):
    # Check if the selected fields lists are initialized and have the correct length
    if not x_selected_fields or len(x_selected_fields) != 1:
        messagebox.showerror("Error", "Pie Chart requires exactly one field selected for X Axis.")
        return
    
    if not y_selected_fields or len(y_selected_fields) == 0:
        messagebox.showerror("Error", "No field selected for Y Axis.")
        return

    # Check if the selected field contains appropriate data for a pie chart (non-numeric and categorical)
    if pd.api.types.is_numeric_dtype(plot_data[y_selected_fields[0]]):
        messagebox.showerror("Error", "Pie Chart requires categorical data, not numeric data.")
        return

    # Calculate the value counts of the categories which will determine the size of each pie slice
    try:
        category_counts = plot_data[y_selected_fields[0]].value_counts()
    except KeyError:
        messagebox.showerror("Error", f"Field '{y_selected_fields[0]}' not found in data.")
        return

    # Plot the pie chart using the counts
    category_counts.plot.pie(ax=ax, autopct='%1.1f%%', startangle=90, colors=['#66c2a5', '#fc8d62', '#8da0cb', '#e78ac3'])

    # Additional aesthetics for clarity
    ax.set_ylabel('')  # Pie charts do not need a y-axis label
    ax.set_title(f"Pie Chart: {y_selected_fields[0]}", fontsize=14)

    # Ensure no chart legend overlaps
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.


def plot_line(ax, plot_data):
    if len(x_selected_fields) != 1 or not y_selected_fields:
        messagebox.showerror("Error", "Line plot requires exactly one X field and at least one Y field.")
        return
    for y_col in y_selected_fields:
        if use_seaborn.get():
            sns.lineplot(data=plot_data, x=x_selected_fields[0], y=y_col, ax=ax, color='#66c2a5')
        else:
            ax.plot(plot_data[x_selected_fields[0]], plot_data[y_col], label=y_col, color='#66c2a5')
    ax.legend()


def generate_visualization():
    try:
        chart_type = chart_type_dropdown.get()
        if chart_type in ["Histogram", "Pie Chart", "Box Plot"]:
            if len(x_selected_fields) != 1:
                messagebox.showerror("Error", f"Select only one field for the {chart_type}.")
                return
        else:
            if not x_selected_fields or (chart_type != "Pie Chart" and not y_selected_fields):
                messagebox.showerror("Error", "Select at least one field for both X and Y axes.")
                return

        title_font_size = int(title_font_size_var.get())
        x_tick_label_font_size = int(x_axis_font_size_var.get())
        y_tick_label_font_size = int(y_axis_font_size_var.get())
        x_tick_label_rotation = x_tick_label_rotation_var.get()
        y_tick_label_rotation = y_tick_label_rotation_var.get()

        light_colors = ['#66c2a5', '#fc8d62', '#8da0cb', '#e78ac3', '#a6d854', '#ffd92f', '#e5c494', '#b3b3b3']

        generate_all = generate_all_var.get()

        if generate_all:
            chart_types = ["Line", "Bar", "Column", "Area", "Stacked Bar", "Scatter Plot", "Dual Axes", "Histogram", "Box Plot", "Pie Chart"]
        else:
            chart_types = [chart_type]

        for chart_type in chart_types:
            fig, ax = plt.subplots(figsize=get_chart_size())
            if use_seaborn.get():
                sns.set(style="whitegrid")

            plot_data = dataset[list(set(x_selected_fields + y_selected_fields))]

            if chart_type == "Pie Chart":
                plot_pie(ax, plot_data, x_selected_fields, y_selected_fields)  # Ensure x_selected_fields and y_selected_fields are passed
            elif chart_type == "Bar":
                plot_bar(ax, plot_data)
            elif chart_type == "Column":
                plot_column(ax, plot_data)
            elif chart_type == "Area":
                plot_area(ax, plot_data)
            elif chart_type == "Stacked Bar":
                plot_stacked_bar(ax, plot_data)
            elif chart_type == "Scatter Plot":
                plot_scatter(ax, plot_data)
            elif chart_type == "Dual Axes":
                plot_dual_axes(ax, plot_data)
            elif chart_type == "Histogram":
                plot_histogram(ax, plot_data)
            elif chart_type == "Box Plot":
                plot_box(ax, plot_data)
            elif chart_type == "Line":
                plot_line(ax, plot_data)

            ax.set_xlabel(", ".join(x_selected_fields), fontsize=x_tick_label_font_size)
            ax.set_ylabel(", ".join(y_selected_fields), fontsize=y_tick_label_font_size)
            ax.set_title(f"{chart_type}: {', '.join(x_selected_fields)} vs {', '.join(y_selected_fields)}", fontsize=title_font_size)
            ax.tick_params(axis='x', labelsize=x_tick_label_font_size, rotation=x_tick_label_rotation)
            ax.tick_params(axis='y', labelsize=y_tick_label_font_size, rotation=y_tick_label_rotation)

            plt.tight_layout()
            plt.show()

    except Exception as e:
        messagebox.showerror("Error", f"Visualization failed: {str(e)}")

    # Untick and disable checkboxes
    display_aggression.set(0)
    aggression_checkbutton.config(state=tk.DISABLED)

    display_skew.set(0)
    skew_line_checkbutton.config(state=tk.DISABLED)

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
chart_type_dropdown.bind("<<ComboboxSelected>>", lambda event: update_options_based_on_chart_type())

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

generate_all_var = tk.BooleanVar()
generate_all_checkbutton = Checkbutton(frame, text="Generate All Charts", variable=generate_all_var)
generate_all_checkbutton.grid(column=0, row=13, padx=10, pady=10)

# Checkbox for Display Aggression Line in Scatter Plot
display_aggression = IntVar()
aggression_checkbutton = Checkbutton(frame, text="Display Aggression Line", variable=display_aggression)
aggression_checkbutton.grid(column=1, row=13, padx=10, pady=10)

# Checkbox for Display Skew Line in Histogram
display_skew = IntVar()
skew_line_checkbutton = Checkbutton(frame, text="Display Skew Line", variable=display_skew)
skew_line_checkbutton.grid(column=2, row=13, padx=10, pady=10)

# Initial state setup for these options
aggression_checkbutton.config(state=tk.DISABLED)
skew_line_checkbutton.config(state=tk.DISABLED)

root.mainloop()
