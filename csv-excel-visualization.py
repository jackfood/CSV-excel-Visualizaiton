import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import seaborn as sns
from tkinter import filedialog, messagebox, simpledialog, ttk, Listbox, MULTIPLE, IntVar, StringVar, Checkbutton, Scale, Toplevel
import tkinter as tk
import numpy as np
from scipy.stats import norm, skew, linregress
from PIL import Image, ImageTk
from dateutil.parser import parse
import itertools
import os

# GUI components
root = tk.Tk()
root.title("CSV/Excel Data Visualizer V1.5.3.0512.4")

global x_selected_fields, y_selected_fields, dataset, original_dataset, last_file_path
x_selected_fields = []
y_selected_fields = []
dataset = pd.DataFrame()
display_skew = IntVar()
display_aggression = IntVar()
original_dataset = dataset.copy()
last_file_path = None

def ask_for_histogram_customization(data):
    # Determine the default values based on the data
    data_min, data_max = data.min(), data.max()
    bin_width = 2 * (np.percentile(data, 75) - np.percentile(data, 25)) * len(data) ** (-1/3)
    default_bins = max(1, int((data_max - data_min) / bin_width))

    if enable_customization.get():
        while True:
            try:
                min_edge = simpledialog.askfloat("Histogram - Minimum Edge", f"Enter the minimum value of the range (suggested: {data_min:.2f}):", initialvalue=data_min, parent=root)
                max_edge = simpledialog.askfloat("Histogram - Maximum Edge", f"Enter the maximum value of the range (suggested: {data_max:.2f}):", initialvalue=data_max, parent=root)
                num_bins = simpledialog.askinteger("Histogram - Number of Bins", f"Enter the number of bins (suggested: {default_bins}):", initialvalue=default_bins, parent=root)

                if min_edge is None or max_edge is None or num_bins is None:
                    messagebox.showwarning("Histogram - Invalid Input", "You must provide all inputs. Using default settings.", parent=root)
                    return (False, None)

                if min_edge >= max_edge:
                    messagebox.showerror("Histogram - Error", "Minimum edge must be less than maximum edge.", parent=root)
                    continue

                if num_bins <= 0:
                    messagebox.showerror("Histogram - Error", "Number of bins must be positive.", parent=root)
                    continue

                bin_edges = np.linspace(min_edge, max_edge, num_bins + 1)
                return (True, bin_edges)

            except ValueError:
                messagebox.showerror("Histogram - Error", "Please enter valid numbers.", parent=root)
                continue

    return (False, None)

# Function to ask for bar customization
def ask_for_bar_customization():
    if enable_customization.get():
        while True:
            order = simpledialog.askstring("Bar - Sorting Order", "Enter 'asc' for ascending or 'desc' for descending:", parent=root)
            if order not in ['asc', 'desc', None]:  # Handle None for dialog cancellation
                messagebox.showerror("Error", "Invalid order. Please enter 'asc' or 'desc'.", parent=root)
                continue

            if order is None:
                return None, None  # User cancelled

            max_items = simpledialog.askinteger("Bar - Number of Items", "Enter the number of top items to display (Max is {}):".format(len(dataset)), parent=root)
            if max_items is None or max_items < 1 or max_items > len(dataset):
                messagebox.showerror("Bar - Error", "Invalid number of items. Please enter a valid number.", parent=root)
                continue

            return order, max_items
    else:
        return 'desc', min(len(dataset), 10)  # Default order and number of items

def filter_data():
    selected_indices = x_axis_listbox.curselection()
    if not selected_indices:
        messagebox.showwarning("Filter Warning", "Please select at least one field from the X-Axis listbox.")
        return

    filter_window = tk.Toplevel(root)
    filter_window.title("Filter Options")
    entries = {}

    for index in selected_indices:
        field = x_axis_listbox.get(index)
        dtype = dataset[field].dtype

        frame = ttk.LabelFrame(filter_window, text=f"Filter {field} - {dtype}")
        frame.pack(padx=10, pady=5, fill='x', expand=True)

        if dtype.kind in 'O':  # Object (treat as categorical)
            lb = Listbox(frame, selectmode=MULTIPLE, width=50, height=4, exportselection=False)
            lb.pack(side="top", fill="x", expand=True)
            for value in sorted(dataset[field].unique()):
                lb.insert(tk.END, value)
            entries[field] = lb
        elif dtype.kind in 'iuf' or dtype.kind == 'M':  # Numeric or Datetime
            current_min, current_max = dataset[field].min(), dataset[field].max()
            min_label = ttk.Label(frame, text="Min value:")
            min_label.pack(side="top")
            min_entry = ttk.Entry(frame, width=15)
            min_entry.insert(0, str(current_min))
            min_entry.pack(side="top", padx=5)

            max_label = ttk.Label(frame, text="Max value:")
            max_label.pack(side="top")
            max_entry = ttk.Entry(frame, width=15)
            max_entry.insert(0, str(current_max))
            max_entry.pack(side="top", padx=5)

            entries[field] = (min_entry, max_entry)

    def apply_filters():
        global dataset
        conditions = []
        active_filters = []

        for field, entry in entries.items():
            dtype = dataset[field].dtype
            if isinstance(entry, Listbox):  # Categorical
                selected = [entry.get(idx) for idx in entry.curselection()]
                if selected:
                    conditions.append(dataset[field].isin(selected))
                    active_filters.append(f"{field} in ({', '.join(selected)})")
            else:  # Numeric or Datetime
                min_val, max_val = float(entry[0].get()), float(entry[1].get())
                conditions.append((dataset[field] >= min_val) & (dataset[field] <= max_val))
                active_filters.append(f"{field} between {min_val} and {max_val}")

        if conditions:
            combined_condition = conditions[0]
            for cond in conditions[1:]:
                combined_condition &= cond
            dataset = dataset.loc[combined_condition]

        update_dropdowns(dataset)
        filter_label.config(text="Active Filters: " + "; ".join(active_filters) if active_filters else "No active filters")

    def reset_filters():
        if last_file_path:
            try:
                if last_file_path.endswith('.csv'):
                    dataset = pd.read_csv(last_file_path)
                else:
                    dataset = pd.read_excel(last_file_path)
                update_dropdowns(dataset)
                filter_label.config(text="No active filters")
                filter_window.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to reload file: {str(e)}")
        else:
            messagebox.showinfo("Reset Info", "No file has been loaded yet.")

    apply_button = ttk.Button(filter_window, text="Apply Filters", command=apply_filters)
    apply_button.pack(side="left", padx=5, pady=10)

    reset_button = ttk.Button(filter_window, text="Reset Filters", command=reset_filters)
    reset_button.pack(side="right", padx=5, pady=10)

def load_file():
    global last_file_path, dataset  # Include dataset if you modify it globally
    file_path = filedialog.askopenfilename(filetypes=[("CSV and Excel Files", "*.csv;*.xlsx")])
    if file_path:
        last_file_path = file_path  # Update last_file_path
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
    """Update listboxes with new data after loading or applying filters."""
    global dataset
    dataset = data

    # Retrieve current selections to reapply after updating the list
    selected_x_indices = list(x_axis_listbox.curselection())
    selected_y_indices = list(y_axis_listbox.curselection())
    selected_x_values = [x_axis_listbox.get(i) for i in selected_x_indices]
    selected_y_values = [y_axis_listbox.get(i) for i in selected_y_indices]

    x_axis_listbox.delete(0, tk.END)
    y_axis_listbox.delete(0, tk.END)

    if dataset.empty:
        # Notify the user that the dataset is empty after filtering
        messagebox.showinfo("Update", "The dataset is empty after filtering.")
        x_axis_listbox.config(state='disabled')
        y_axis_listbox.config(state='disabled')
    else:
        x_axis_listbox.config(state='normal')
        y_axis_listbox.config(state='normal')
        new_x_indices = []
        new_y_indices = []
        for idx, column in enumerate(data.columns):
            x_axis_listbox.insert(tk.END, column)
            y_axis_listbox.insert(tk.END, column)
            if column in selected_x_values:
                new_x_indices.append(idx)
            if column in selected_y_values:
                new_y_indices.append(idx)

        # Reapply previous selections if still relevant
        for idx in new_x_indices:
            x_axis_listbox.selection_set(idx)
        for idx in new_y_indices:
            y_axis_listbox.selection_set(idx)

def generate_dashboard_and_save():
    try:
        # Create the figure
        fig = plt.figure(figsize=(20, 15))
        gs = GridSpec(3, 3, figure=fig)

        # List of subplots to use
        subplots = []
        subplot_titles = []
        failed_charts = []

        # Create subplots for each type of chart without causing errors
        def safe_plot(ax, plot_func, plot_data, title):
            try:
                plot_func(ax, plot_data)
                ax.set_title(title)
                subplots.append(ax)
                subplot_titles.append(title)
            except Exception:
                failed_charts.append(title)

        plot_data = dataset[list(set(x_selected_fields + y_selected_fields))]

        # Line Plot
        if "Line" in chart_type_dropdown["values"]:
            safe_plot(fig.add_subplot(gs[0, 0]), plot_line, plot_data, "Line Plot")

        # Bar Chart
        if "Bar" in chart_type_dropdown["values"]:
            safe_plot(fig.add_subplot(gs[0, 1]), plot_bar, plot_data, "Bar Chart")

        # Column Chart
        if "Column" in chart_type_dropdown["values"]:
            safe_plot(fig.add_subplot(gs[0, 2]), plot_column, plot_data, "Column Chart")

        # Stacked Bar Chart
        if "Stacked Bar" in chart_type_dropdown["values"]:
            safe_plot(fig.add_subplot(gs[1, 0]), plot_stacked_bar, plot_data, "Stacked Bar Chart")

        # Scatter Plot
        if "Scatter Plot" in chart_type_dropdown["values"]:
            safe_plot(fig.add_subplot(gs[1, 1]), plot_scatter, plot_data, "Scatter Plot")

        # Dual Axes Plot
        if "Dual Axes" in chart_type_dropdown["values"]:
            safe_plot(fig.add_subplot(gs[1, 2]), plot_dual_axes, plot_data, "Dual Axes Plot")

        # Histogram
        if "Histogram" in chart_type_dropdown["values"]:
            safe_plot(fig.add_subplot(gs[2, 0]), plot_histogram, plot_data, "Histogram")

        # Box Plot
        if "Box Plot" in chart_type_dropdown["values"]:
            safe_plot(fig.add_subplot(gs[2, 1]), plot_box, plot_data, "Box Plot")

        # Pie Chart
        if "Pie Chart" in chart_type_dropdown["values"]:
            safe_plot(fig.add_subplot(gs[2, 2]), plot_pie, plot_data, "Pie Chart")

        # Adjust layout and save the dashboard
        if subplots:
            plt.tight_layout()

            # Ask user where to save the dashboard
            file_path = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
                title="Save Dashboard as PNG"
            )
            if file_path:
                fig.savefig(file_path, dpi=300)
                success_message = f"Dashboard saved successfully at {file_path}"
                if failed_charts:
                    success_message += f"\n\nThe following charts could not be generated:\n" + "\n".join(failed_charts)
            plt.close(fig)

    except Exception as e:
        return

def update_aggression_options_based_on_chart_type():
    chart_type = chart_type_dropdown.get()

    # Enable/Disable value display options
    if chart_type in ["Bar", "Column", "Line", "Stacked Bar", "Histogram"]:
        display_values_checkbutton.config(state=tk.NORMAL)
        value_label_font_size_label.config(state=tk.NORMAL)
        value_label_font_size_entry.config(state=tk.NORMAL)
    else:
        display_values_checkbutton.config(state=tk.DISABLED)
        value_label_font_size_label.config(state=tk.DISABLED)
        value_label_font_size_entry.config(state=tk.DISABLED)

    # Enable/Disable skew/aggression lines
    if chart_type == "Histogram":
        skew_line_checkbutton.config(state=tk.NORMAL)
        aggression_checkbutton.config(state=tk.DISABLED)
    elif chart_type == "Scatter Plot":
        aggression_checkbutton.config(state=tk.NORMAL)
        skew_line_checkbutton.config(state=tk.DISABLED)
    else:
        aggression_checkbutton.config(state=tk.DISABLED)
        skew_line_checkbutton.config(state=tk.DISABLED)

    # Enable/Disable aggregation method dropdown
    if chart_type == "Line":
        aggregation_method_dropdown.config(state=tk.NORMAL)
    else:
        aggregation_method_dropdown.config(state=tk.DISABLED)

def display_values_on_bars(ax, bars, font_size=4):
    for bar in bars:
        if isinstance(bar, plt.Line2D):
            for x, y in zip(bar.get_xdata(), bar.get_ydata()):
                ax.text(x, y, f'{y:.2f}', ha='center', va='bottom', fontsize=font_size)
        else:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2.0, height, f'{height:.2f}', ha='center', va='bottom', fontsize=font_size)

def store_x_axis_selection():
    global x_selected_fields
    x_selected_fields = [x_axis_listbox.get(idx) for idx in x_axis_listbox.curselection()]
    x_axis_label["text"] = f"X Axis (Selected: {', '.join(x_selected_fields)}):" if x_selected_fields else "X Axis:"
    update_aggression_options_based_on_selection()

def store_y_axis_selection():
    global y_selected_fields
    y_selected_fields = [y_axis_listbox.get(idx) for idx in y_axis_listbox.curselection()]
    y_axis_label["text"] = f"Y Axis (Selected: {', '.join(y_selected_fields)}):" if y_selected_fields else "Y Axis:"
    update_aggression_options_based_on_selection()

def update_aggression_options_based_on_selection():
    if x_selected_fields and y_selected_fields and all(dataset[col].dtype.kind in 'fi' for col in x_selected_fields + y_selected_fields):
        aggression_checkbutton.config(state=tk.NORMAL)
    else:
        aggression_checkbutton.config(state=tk.DISABLED)

def recommend_chart():
    if x_selected_fields and y_selected_fields:
        recommendation = advanced_chart_recommendation(x_selected_fields, y_selected_fields, dataset)
        recommendation_label["text"] = f"Recommended Chart: {recommendation}"
        chart_type_dropdown.set(recommendation)
        update_aggression_options_based_on_chart_type()
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


def aggregate_data(data, x_col, y_col, aggregation_method):
    if aggregation_method == 'mean':
        aggregated_data = data.groupby(x_col)[y_col].mean().reset_index()
    elif aggregation_method == 'sum':
        aggregated_data = data.groupby(x_col)[y_col].sum().reset_index()
    elif aggregation_method == 'max':
        aggregated_data = data.groupby(x_col)[y_col].max().reset_index()
    elif aggregation_method == 'min':
        aggregated_data = data.groupby(x_col)[y_col].min().reset_index()
    else:
        raise ValueError(f"Unsupported aggregation method: {aggregation_method}")
    return aggregated_data


def plot_line(ax, plot_data):
    if len(x_selected_fields) != 1 or not y_selected_fields:
        messagebox.showerror("Line - Error", "Line plot requires exactly one X field and at least one Y field.")
        return

    x_col = x_selected_fields[0]
    aggregation_method = aggregation_method_var.get()

    # Define a color palette or a list of colors
    colors = ['#66c2a5', '#fc8d62', '#8da0cb', '#e78ac3', '#a6d854', '#ffd92f', '#e5c494', '#b3b3b3']

    for y_col, color in zip(y_selected_fields, itertools.cycle(colors)):
        aggregated_data = aggregate_data(plot_data, x_col, y_col, aggregation_method)

        if use_seaborn.get():
            line = sns.lineplot(data=aggregated_data, x=x_col, y=y_col, ax=ax, color=color, marker='o', markersize=5)
        else:
            line, = ax.plot(aggregated_data[x_col], aggregated_data[y_col], label=y_col, color=color, marker='o', markersize=5)

        if display_values.get():
            font_size = int(value_label_font_size_var.get())
            for i, v in enumerate(aggregated_data[y_col]):
                ax.text(aggregated_data[x_col][i], v, f"{v:.2f}", fontsize=font_size, ha='center', va='bottom')

    # Set x-axis labels only for the actual data points
    x_labels = aggregated_data[x_col].unique()
    ax.set_xticks(x_labels)
    ax.set_xticklabels(x_labels)

    ax.legend()


def plot_bar(ax, plot_data):
    if len(x_selected_fields) != 1 or len(y_selected_fields) != 1:
        messagebox.showerror("Bar - Error", "Bar plot requires exactly one X field and one Y field.")
        return

    # Ensure Y-axis data is numeric
    try:
        plot_data[y_selected_fields[0]] = pd.to_numeric(plot_data[y_selected_fields[0]], errors='coerce')
        if plot_data[y_selected_fields[0]].isnull().any():
            messagebox.showerror("Bar - Error", "Non-numeric data found in Y-axis field after conversion attempt.")
            return

        # Drop rows where Y data could not be converted and resulted in NaN
        plot_data = plot_data.dropna(subset=[y_selected_fields[0]])

        # Group by X field and calculate mean for Y field
        aggregated_data = plot_data.groupby(x_selected_fields[0])[y_selected_fields[0]].mean().reset_index()

        # Customize order and number of items if enabled
        order, max_items = ask_for_bar_customization()
        if order is None:  # Handle case where customization is not done
            messagebox.showinfo("Bar - Info", "Using default settings for sorting and item count.")
            order, max_items = 'desc', min(len(aggregated_data), 10)  # Default settings

        if order == 'desc':
            aggregated_data = aggregated_data.nlargest(max_items, y_selected_fields[0])
        else:
            aggregated_data = aggregated_data.nsmallest(max_items, y_selected_fields[0])

        x = aggregated_data[x_selected_fields[0]].astype(str)
        y = aggregated_data[y_selected_fields[0]]
        bar_width = 0.8

        if use_seaborn.get():
            bars = sns.barplot(data=aggregated_data, x=x_selected_fields[0], y=y_selected_fields[0], ax=ax, color='lightblue', orient='v')
        else:
            bars = ax.bar(x, y, width=bar_width, color='lightblue')

        ax.set_xticks(range(len(x)))
        ax.set_xticklabels(x, rotation=x_tick_label_rotation_var.get(), fontsize=int(x_axis_font_size_var.get()))

        if display_values.get():
            font_size = int(value_label_font_size_var.get())
            display_values_on_bars(ax, bars, font_size=font_size)

    except Exception as e:
        messagebox.showerror("Error", f"Failed to plot bar chart: {str(e)}")

def plot_area(ax, plot_data):
    if len(x_selected_fields) != 1:
        messagebox.showerror("Area - Error", "Area plot requires exactly one X field and multiple Y fields.")
        return
    for y_col in y_selected_fields:
        ax.fill_between(plot_data[x_selected_fields[0]], plot_data[y_col], alpha=0.3, label=y_col, color='#66c2a5')
    ax.legend()

def plot_stacked_bar(ax, plot_data):
    if len(x_selected_fields) != 1:
        messagebox.showerror("Stacked - Error", "Stacked Bar plot requires exactly one X field.")
        return
    if not y_selected_fields:
        messagebox.showerror("Stacked - Error", "Stacked Bar plot requires at least one Y field.")
        return

    # Check if Y fields are numeric
    if not all(pd.api.types.is_numeric_dtype(plot_data[col]) for col in y_selected_fields):
        messagebox.showerror("Stacked - Error", "All Y fields must be numeric for stacked bar plots.")
        return

    # Preparing the data for plotting
    crosstab_data = plot_data.groupby(x_selected_fields[0])[y_selected_fields].sum()
    crosstab_data.fillna(0, inplace=True)  # Replace NaN with 0 for stacking

    bottom = np.zeros(len(crosstab_data))

    if use_seaborn.get():
        # Use Matplotlib directly as Seaborn doesn't support stacked bars
        palette = sns.color_palette("husl", len(y_selected_fields))
        bars = []
        for idx, col in enumerate(y_selected_fields):
            bar = ax.bar(crosstab_data.index, crosstab_data[col], bottom=bottom, label=col, color=palette[idx])
            bars.append(bar)
            bottom += crosstab_data[col].values
    else:
        # Directly use Matplotlib's stacked bar functionality
        palette = sns.color_palette("husl", len(y_selected_fields))
        bars = []
        bottom = np.zeros(len(crosstab_data))
        for idx, col in enumerate(y_selected_fields):
            bar = ax.bar(crosstab_data.index, crosstab_data[col], bottom=bottom, label=col, color=palette[idx])
            bars.append(bar)
            bottom += crosstab_data[col].values

    ax.set_xticks(range(len(crosstab_data.index)))
    ax.set_xticklabels(crosstab_data.index, rotation=x_tick_label_rotation_var.get(), fontsize=int(x_axis_font_size_var.get()))
    ax.set_xlabel(x_selected_fields[0], fontsize=int(x_axis_font_size_var.get()))
    ax.set_ylabel("Sum of Values", fontsize=int(y_axis_font_size_var.get()))
    ax.legend(title="Categories")

    # Display values on bars if enabled
    if display_values.get():
        font_size = int(value_label_font_size_var.get())
        for bar_group in bars:
            for rect in bar_group:
                height = rect.get_height()
                if height > 0:
                    ax.text(
                        rect.get_x() + rect.get_width() / 2,
                        rect.get_y() + height,
                        f'{int(height)}',
                        ha='center',
                        va='bottom',
                        fontsize=font_size
                    )

def plot_scatter(ax, plot_data):
    # Ensure the columns are numeric and handle NaN values
    if plot_data[x_selected_fields[0]].dtype.kind not in 'fi' or plot_data[y_selected_fields[0]].dtype.kind not in 'fi':
        messagebox.showerror("Scatter Error", "Scatter plot requires numeric data types for both axes.")
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
    if len(x_selected_fields) != 1 or len(y_selected_fields) != 2:
        messagebox.showerror("Error", "Dual Axes plot requires exactly one X field and two Y fields.")
        return

    x_field = x_selected_fields[0]
    y_field1 = y_selected_fields[0]
    y_field2 = y_selected_fields[1]

    color1 = '#66c2a5'
    color2 = '#fc8d62'

    if use_seaborn.get():
        sns.lineplot(x=x_field, y=y_field1, data=plot_data, ax=ax, color=color1, label=f"{y_field1} (left axis)")
        ax2 = ax.twinx()
        sns.lineplot(x=x_field, y=y_field2, data=plot_data, ax=ax2, color=color2, label=f"{y_field2} (right axis)")
    else:
        ax.plot(plot_data[x_field], plot_data[y_field1], color=color1, label=f"{y_field1} (left axis)")
        ax.set_xlabel(x_field, fontsize=int(x_axis_font_size_var.get()))
        ax.set_ylabel(y_field1, fontsize=int(y_axis_font_size_var.get()))

        ax2 = ax.twinx()
        ax2.plot(plot_data[x_field], plot_data[y_field2], color=color2, label=f"{y_field2} (right axis)")
        ax2.set_ylabel(y_field2, fontsize=int(y_axis_font_size_var.get()))

    lines, labels = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax2.legend(lines + lines2, labels + labels2, loc='upper right')

    ax.figure.tight_layout()

def plot_histogram(ax, plot_data):
    # Check if a single field is selected
    if len(x_selected_fields) != 1:
        messagebox.showerror("Histogram - Error", "Histogram requires exactly one field to be selected for the X axis.")
        return

    data = plot_data[x_selected_fields[0]]

    # Check if the selected data is numeric
    if not pd.api.types.is_numeric_dtype(data):
        messagebox.showerror("Histogram - Error", "Histogram requires numerical data. Please select a numeric field.")
        return

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

    # Display values on bars if enabled
    if display_values.get():
        font_size = int(value_label_font_size_var.get())
        for count, rect in zip(counts, patches):
            height = rect.get_height()
            ax.text(rect.get_x() + rect.get_width() / 2, height, f'{int(height)}', ha='center', va='bottom', fontsize=font_size)

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

def plot_pie(ax, plot_data):
    if not x_selected_fields or len(x_selected_fields) != 1:
        messagebox.showerror("Pie - Error", "Pie Chart requires exactly one field selected for the X Axis.")
        return

    x_field = x_selected_fields[0]
    if pd.api.types.is_numeric_dtype(plot_data[x_field]):
        messagebox.showerror("Error", "Pie Chart requires categorical data, not numeric data.")
        return

    try:
        category_counts = plot_data[x_field].value_counts()
    except KeyError:
        messagebox.showerror("Pie - Error", f"Field '{x_field}' not found in data.")
        return

    colors = ['#66c2a5', '#fc8d62', '#8da0cb', '#e78ac3', '#a6d854', '#ffd92f', '#e5c494', '#b3b3b3']
    wedges, texts, autotexts = ax.pie(category_counts, autopct='%1.1f%%', startangle=90, colors=colors[:len(category_counts)],
                                      wedgeprops=dict(width=0.3, edgecolor='black', linewidth=1.5))
    
    ax.set_ylabel('')
    ax.set_title(f"Pie Chart: {x_field}", fontsize=14)
    ax.axis('equal')
    ax.legend(wedges, category_counts.index, title=x_field, loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))

    for text in autotexts:
        text.set_color('black')
        text.set_fontsize(10)
        text.set_weight('bold')
    for text in texts:
        text.set_fontsize(10)

def plot_column(ax, plot_data):
    if len(x_selected_fields) != 1 or len(y_selected_fields) != 1:
        messagebox.showerror("ColumnBar - Error", "Column plot requires exactly one X field and one Y field.")
        return

    # Ensure y-axis data is numeric
    if not pd.api.types.is_numeric_dtype(plot_data[y_selected_fields[0]]):
        messagebox.showerror("ColumnBar - Error", "Y-axis data must be numeric (int or float) for column plots.")
        return

    try:
        # Convert X and Y fields to numeric types, handling non-convertible data by coercion
        plot_data[x_selected_fields[0]] = pd.to_numeric(plot_data[x_selected_fields[0]], errors='coerce')
        plot_data[y_selected_fields[0]] = pd.to_numeric(plot_data[y_selected_fields[0]], errors='coerce')

        # Check if conversion was successful; NaNs indicate failed conversion
        if plot_data[x_selected_fields[0]].isnull().any() or plot_data[y_selected_fields[0]].isnull().any():
            messagebox.showerror("ColumnBar - Error", "Non-numeric data found in fields after conversion attempt.")
            return

        # Remove rows with NaN values resulting from 'coerce'
        plot_data = plot_data.dropna(subset=[x_selected_fields[0], y_selected_fields[0]])

        # Aggregating data by the X field
        aggregated_data = plot_data.groupby(x_selected_fields[0], as_index=False)[y_selected_fields[0]].mean()
        order, max_items = ask_for_bar_customization()
        if order is None or max_items is None:
            messagebox.showwarning("ColumnBar - Warning", "Sorting order or max items not specified.")
            return
        
        if order and max_items:
            aggregated_data = aggregated_data.nlargest(max_items, y_selected_fields[0]) if order == 'desc' else aggregated_data.nsmallest(max_items, y_selected_fields[0])

        x = aggregated_data[x_selected_fields[0]].astype(str)
        y = aggregated_data[y_selected_fields[0]]

        if use_seaborn.get():
            bars = sns.barplot(data=aggregated_data, x=y_selected_fields[0], y=x_selected_fields[0], ax=ax, color='lightblue', orient='h')
        else:
            bars = ax.barh(x, y, color='lightblue')

        ax.set_yticks(range(len(x)))
        ax.set_yticklabels(x, rotation=y_tick_label_rotation_var.get(), fontsize=int(y_axis_font_size_var.get()))

        if display_values.get():
            font_size = int(value_label_font_size_var.get())
            display_values_on_bars(ax, bars, font_size=font_size)

    except Exception as e:
        messagebox.showerror("ColumnBar - Error", f"Failed to plot column chart: {str(e)}")

def analyze_data_types(selected_fields):
    if not selected_fields:
        return None
    data_types = dataset[selected_fields].dtypes
    if all(dtype.kind in 'fi' for dtype in data_types):  # Check if all are float or int
        return 'numeric'
    elif all(dtype.kind in 'O' or dtype.name == 'category' for dtype in data_types):  # Check if all are object or category
        return 'categorical'
    else:
        return 'mixed'

def check_chart_suitability():
    x_type = analyze_data_types(x_selected_fields)
    y_type = analyze_data_types(y_selected_fields)

    chart_type = chart_type_dropdown.get()
    if not x_type or not y_type:
        # If no fields are selected yet, return without prompt
        return
    
    chart_requirements = {
        "Line": ("numeric", "numeric"),
        "Bar": ("categorical", "numeric"),
        "Column": ("categorical", "numeric"),
        "Area": ("numeric", "numeric"),
        "Stacked Bar": ("categorical", "numeric"),
        "Scatter Plot": ("numeric", "numeric"),
        "Dual Axes": ("numeric", "numeric"),
        "Histogram": ("numeric", None),
        "Box Plot": (None, "numeric"),
        "Pie Chart": ("categorical", None)
    }
    
    required_x, required_y = chart_requirements.get(chart_type, (None, None))

    messages = []
    if required_x and required_x != x_type:
        messages.append(f"X axis should be {required_x} for a {chart_type}.")
    if required_y and required_y != y_type:
        messages.append(f"Y axis should be {required_y} for a {chart_type}.")

    if messages:
        messagebox.showwarning("Chart Type Suitability", " ".join(messages))
    else:
        messagebox.showinfo("Chart Type Suitability", f"{chart_type} is suitable for the selected data types.")


def generate_visualization():
    chart_type_errors = {}
    chart_type = chart_type_dropdown.get()

    # Initial checks for field selections based on the type of chart
    if chart_type in ["Histogram", "Pie Chart", "Box Plot"]:
        if len(x_selected_fields) != 1:
            messagebox.showerror("Generating - Error", f"Select only one field for the {chart_type}.")
            return
    else:
        if not x_selected_fields or (chart_type != "Pie Chart" and not y_selected_fields):
            messagebox.showerror("Generating - Error", "Select at least one field for both X and Y axes.")
            return

    # Setup general plot parameters
    title_font_size = int(title_font_size_var.get())
    x_tick_label_font_size = int(x_axis_font_size_var.get())
    y_tick_label_font_size = int(y_axis_font_size_var.get())
    x_tick_label_rotation = x_tick_label_rotation_var.get()
    y_tick_label_rotation = y_tick_label_rotation_var.get()

    generate_all = generate_all_var.get()
    chart_types = ["Histogram", "Line", "Bar", "Column", "Area", "Stacked Bar", "Scatter Plot", "Dual Axes", "Box Plot", "Pie Chart"] if generate_all else [chart_type]

    for chart_type in chart_types:
        try:
            fig, ax = plt.subplots(figsize=get_chart_size())
            if use_seaborn.get():
                sns.set(style="whitegrid")

            plot_data = dataset[list(set(x_selected_fields + y_selected_fields))]

            # Dictionary mapping chart types to their respective plotting functions
            chart_functions = {
                "Pie Chart": plot_pie,
                "Bar": plot_bar,
                "Column": plot_column,
                "Area": plot_area,
                "Stacked Bar": plot_stacked_bar,
                "Scatter Plot": plot_scatter,
                "Dual Axes": plot_dual_axes,
                "Histogram": plot_histogram,
                "Box Plot": plot_box,
                "Line": plot_line
            }

            chart_function = chart_functions.get(chart_type)
            if chart_function:
                chart_function(ax, plot_data)

            ax.set_xlabel(", ".join(x_selected_fields), fontsize=x_tick_label_font_size)
            ax.set_ylabel(", ".join(y_selected_fields), fontsize=y_tick_label_font_size)
            ax.set_title(f"{chart_type}: {', '.join(x_selected_fields)} vs {', '.join(y_selected_fields)}", fontsize=title_font_size)
            ax.tick_params(axis='x', labelsize=x_tick_label_font_size, rotation=x_tick_label_rotation)
            ax.tick_params(axis='y', labelsize=y_tick_label_font_size, rotation=y_tick_label_rotation)

            plt.tight_layout()
            plt.show()

        except Exception as e:
            chart_type_errors[chart_type] = str(e)

    if chart_type_errors:
        error_message = "Visualizations failed - chart types:\n" + "\n".join(f"{k}: {v}" for k, v in chart_type_errors.items())
        messagebox.showerror("Visualization Errors", error_message)

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
load_button.grid(column=0, row=0, padx=10, pady=1)

filter_label = ttk.Label(frame, text="")
filter_label.grid(column=1, row=1, padx=10, pady=1)

filter_button = ttk.Button(frame, text="Filter", command=filter_data)
filter_button.grid(column=2, row=1, padx=10, pady=1)

use_seaborn = tk.BooleanVar()
use_seaborn.set(False)
seaborn_label = ttk.Label(frame, text="Use Seaborn:")
seaborn_label.grid(column=0, row=2, padx=10, pady=1)
seaborn_radio_button = ttk.Radiobutton(frame, text="Yes", variable=use_seaborn, value=True)
seaborn_radio_button.grid(column=1, row=2, padx=10, pady=1)
matplotlib_radio_button = ttk.Radiobutton(frame, text="No", variable=use_seaborn, value=False)
matplotlib_radio_button.grid(column=2, row=2, padx=10, pady=1)

x_axis_label = ttk.Label(frame, text="X Axis Field:")
x_axis_label.grid(column=0, row=3, padx=10, pady=10)
x_axis_listbox = Listbox(frame, selectmode=MULTIPLE, width=30, height=5)
x_axis_listbox.grid(column=1, row=3, padx=10, pady=10)

store_x_button = ttk.Button(frame, text="Store X-Axis Selection", command=store_x_axis_selection)
store_x_button.grid(column=2, row=3, padx=10, pady=10)

y_axis_label = ttk.Label(frame, text="Y Axis Field:")
y_axis_label.grid(column=0, row=4, padx=10, pady=10)
y_axis_listbox = Listbox(frame, selectmode=MULTIPLE, width=30, height=5)
y_axis_listbox.grid(column=1, row=4, padx=10, pady=10)

store_y_button = ttk.Button(frame, text="Store Y-Axis Selection", command=store_y_axis_selection)
store_y_button.grid(column=2, row=4, padx=10, pady=10)

chart_type_label = ttk.Label(frame, text="Chart Type:")
chart_type_label.grid(column=0, row=5, padx=10, pady=10)
chart_type_dropdown = ttk.Combobox(frame)
chart_type_dropdown.grid(column=1, row=5, padx=10, pady=10)
chart_type_dropdown["values"] = ["Line", "Bar", "Column", "Area", "Stacked Bar", "Scatter Plot", "Dual Axes", "Histogram", "Box Plot", "Pie Chart"]
chart_type_dropdown.bind("<<ComboboxSelected>>", lambda event: [check_chart_suitability(), update_aggression_options_based_on_chart_type()])

title_font_size_label = ttk.Label(frame, text="Title Font Size:")
title_font_size_label.grid(column=0, row=6, padx=10, pady=1)
title_font_size_var = tk.StringVar()
title_font_size_var.set("14")
title_font_size_entry = ttk.Entry(frame, textvariable=title_font_size_var)
title_font_size_entry.grid(column=1, row=6, padx=10, pady=1)

x_axis_font_size_label = ttk.Label(frame, text="X-Axis Font Size:")
x_axis_font_size_label.grid(column=0, row=7, padx=10, pady=1)
x_axis_font_size_var = tk.StringVar()
x_axis_font_size_var.set("10")
x_axis_font_size_entry = ttk.Entry(frame, textvariable=x_axis_font_size_var)
x_axis_font_size_entry.grid(column=1, row=7, padx=10, pady=1)

y_axis_font_size_label = ttk.Label(frame, text="Y-Axis Font Size:")
y_axis_font_size_label.grid(column=0, row=8, padx=10, pady=1)
y_axis_font_size_var = tk.StringVar()
y_axis_font_size_var.set("10")
y_axis_font_size_entry = ttk.Entry(frame, textvariable=y_axis_font_size_var)
y_axis_font_size_entry.grid(column=1, row=8, padx=10, pady=1)

# Font size input for the value labels
value_label_font_size_var = tk.StringVar(value="7")
value_label_font_size_label = ttk.Label(frame, text="Bar / Line Count Label Size:")
value_label_font_size_entry = ttk.Entry(frame, textvariable=value_label_font_size_var, width=5)
value_label_font_size_label.grid(column=0, row=9, padx=10, pady=1)
value_label_font_size_entry.grid(column=1, row=9, padx=10, pady=1)

x_tick_label_rotation_label = ttk.Label(frame, text="X-Axis Tick Label Rotation:")
x_tick_label_rotation_label.grid(column=0, row=10, padx=10, pady=1)
x_tick_label_rotation_var = tk.IntVar()
x_tick_label_rotation_var.set(45)
x_radio_0 = ttk.Radiobutton(frame, text="0", variable=x_tick_label_rotation_var, value=0)
x_radio_0.grid(column=1, row=10, padx=5, pady=1)
x_radio_45 = ttk.Radiobutton(frame, text="45", variable=x_tick_label_rotation_var, value=45)
x_radio_45.grid(column=2, row=10, padx=5, pady=1)
x_radio_90 = ttk.Radiobutton(frame, text="90", variable=x_tick_label_rotation_var, value=90)
x_radio_90.grid(column=3, row=10, padx=5, pady=1)

y_tick_label_rotation_label = ttk.Label(frame, text="Y-Axis Tick Label Rotation:")
y_tick_label_rotation_label.grid(column=0, row=11, padx=10, pady=1)
y_tick_label_rotation_var = tk.IntVar()
y_tick_label_rotation_var.set(0)
y_radio_0 = ttk.Radiobutton(frame, text="0", variable=y_tick_label_rotation_var, value=0)
y_radio_0.grid(column=1, row=11, padx=5, pady=1)
y_radio_45 = ttk.Radiobutton(frame, text="45", variable=y_tick_label_rotation_var, value=45)
y_radio_45.grid(column=2, row=11, padx=5, pady=1)
y_radio_90 = ttk.Radiobutton(frame, text="90", variable=y_tick_label_rotation_var, value=90)
y_radio_90.grid(column=3, row=11, padx=5, pady=1)

chart_size_label = ttk.Label(frame, text="Chart Size:")
chart_size_label.grid(column=0, row=12, padx=10, pady=1)
chart_size = tk.StringVar()
chart_size.set("Medium")
chart_size_radio1 = ttk.Radiobutton(frame, text="Small", variable=chart_size, value="Small")
chart_size_radio1.grid(column=1, row=12, padx=5, pady=1)
chart_size_radio2 = ttk.Radiobutton(frame, text="Medium", variable=chart_size, value="Medium")
chart_size_radio2.grid(column=2, row=12, padx=5, pady=1)
chart_size_radio3 = ttk.Radiobutton(frame, text="Large", variable=chart_size, value="Large")
chart_size_radio3.grid(column=3, row=12, padx=5, pady=1)

recommendation_button = ttk.Button(frame, text="Update Recommendation", command=recommend_chart)
recommendation_button.grid(column=0, row=13, padx=10, pady=1)

visualize_button = ttk.Button(frame, text="Visualize", command=generate_visualization)
visualize_button.grid(column=1, row=13, padx=5, pady=1)

# Add the button for saving the dashboard
dashboard_button = ttk.Button(frame, text="Generate Dashboard", command=generate_dashboard_and_save)
dashboard_button.grid(column=2, row=13, pady=5, padx=1)

clear_button = ttk.Button(frame, text="Clear Selection", command=clear_selections)
clear_button.grid(column=1, row=14, padx=5, pady=1)

recommendation_label = ttk.Label(frame, text="")
recommendation_label.grid(row=14, column=0, padx=10, pady=1)

generate_all_var = tk.BooleanVar()
generate_all_checkbutton = tk.Checkbutton(frame, text="Generate All Charts", variable=generate_all_var)
generate_all_checkbutton.grid(column=0, row=15, padx=10, pady=1)

# Checkbox for Display Aggression Line in Scatter Plot
display_aggression = tk.IntVar()
aggression_checkbutton = tk.Checkbutton(frame, text="Display Aggression Line", variable=display_aggression)
aggression_checkbutton.grid(column=1, row=15, padx=10, pady=1)

# Checkbox for Display Skew Line in Histogram
display_skew = tk.IntVar()
skew_line_checkbutton = tk.Checkbutton(frame, text="Display Skew Line", variable=display_skew)
skew_line_checkbutton.grid(column=2, row=15, padx=10, pady=1)

# Checkbox for displaying values on bars/lines
display_values = tk.IntVar(value=0)
display_values_checkbutton = tk.Checkbutton(frame, text="Display Values", variable=display_values)
display_values_checkbutton.grid(column=0, row=16, padx=10, pady=1)

# Checkbox for customization option
enable_customization = tk.IntVar()
customization_checkbutton = tk.Checkbutton(frame, text="Enable Customization", variable=enable_customization)
customization_checkbutton.grid(column=1, row=16, padx=10, pady=1)

# Create a variable to store the selected aggregation method
aggregation_method_var = tk.StringVar(value='mean')

# Create a dropdown menu for selecting the aggregation method
aggregation_method_dropdown = ttk.Combobox(frame, textvariable=aggregation_method_var, state='readonly')
aggregation_method_dropdown['values'] = ['mean', 'sum', 'max', 'min']
aggregation_method_dropdown.grid(column=2, row=16, padx=10, pady=1)

# Initial state setup for these options
aggression_checkbutton.config(state=tk.DISABLED)
skew_line_checkbutton.config(state=tk.DISABLED)

root.mainloop()
