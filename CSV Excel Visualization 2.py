import tkinter as tk
from tkinter import filedialog, ttk, messagebox, simpledialog
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

root = tk.Tk()
root.title("Data Visualizer")
root.geometry("800x600")

df = None
selected_fields = []  # Store selected fields globally
chart_type = tk.StringVar()

def load_file():
    global df
    file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx;*.xls"), ("CSV files", "*.csv")])
    if file_path:
        try:
            if file_path.lower().endswith('.csv'):
                df = pd.read_csv(file_path)
            elif file_path.lower().endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file_path)
            update_listbox()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file: {e}")

def update_listbox():
    listbox_fields.delete(0, tk.END)
    for column in df.columns:
        listbox_fields.insert(tk.END, column)

def infer_data_type(col):
    if pd.api.types.is_numeric_dtype(df[col]):
        if pd.api.types.is_integer_dtype(df[col]):
            return 'Integer'
        elif pd.api.types.is_float_dtype(df[col]):
            return 'Decimal'
    elif pd.api.types.is_categorical_dtype(df[col]) or df[col].nunique() < len(df[col]) / 2:
        return 'Categorical'
    elif pd.api.types.is_string_dtype(df[col]):
        return 'String'
    elif pd.api.types.is_datetime64_any_dtype(df[col]):
        return 'DateTime'
    else:
        return 'Unknown'

def suggest_chart(data_types):
    if len(data_types) == 1:
        dt = data_types[0]
        if dt in ['Integer', 'Decimal']:
            return ['Histogram', 'Boxplot']
        elif dt == 'Categorical':
            return ['Barplot', 'Countplot']
        elif dt == 'DateTime':
            return ['Time Series Plot']
        else:
            return ['Countplot']
    
    elif len(data_types) == 2:
        dt1, dt2 = data_types
        if dt1 in ['Integer', 'Decimal'] and dt2 in ['Integer', 'Decimal']:
            return ['Scatterplot', 'Lineplot']
        elif (dt1 == 'Categorical' and dt2 in ['Integer', 'Decimal']) or (dt2 == 'Categorical' and dt1 in ['Integer', 'Decimal']):
            return ['Boxplot', 'Violin Plot', 'Barplot']
        elif dt1 == 'Categorical' and dt2 == 'Categorical':
            return ['Heatmap', 'Stacked Bar Chart']
        elif 'DateTime' in data_types:
            return ['Time Series Plot']
        else:
            return ['Scatterplot']
    
    elif len(data_types) == 3:
        if all(dt in ['Integer', 'Decimal'] for dt in data_types):
            return ['3D Scatter Plot']
        else:
            return ['Pairplot', 'Facet Grid']
    
    elif len(data_types) >= 4:
        return ['Pairplot', 'Parallel Coordinates']
    
    return ['Please select 1-4 fields']

def on_field_select(event):
    global selected_fields
    selected_indices = listbox_fields.curselection()
    selected_fields = [listbox_fields.get(i) for i in selected_indices]
    if not selected_fields:
        return
    data_types = [infer_data_type(field) for field in selected_fields]
    data_types_label.config(text="Data Types: " + ", ".join(data_types))
    update_chart_options(suggest_chart(data_types))

def update_chart_options(chart_options):
    for widget in frame_chart_options.winfo_children():
        widget.destroy()
    for chart_name in chart_options:
        b = tk.Radiobutton(frame_chart_options, text=chart_name, variable=chart_type, value=chart_name, indicatoron=False)
        b.pack(side='left', padx=5, pady=5)

def show_customization_options():
    if edit_options_var.get():
        title = simpledialog.askstring("Input", "Enter chart title:", parent=root)
        xlabel = simpledialog.askstring("Input", "Enter x-axis label:", parent=root)
        ylabel = simpledialog.askstring("Input", "Enter y-axis label:", parent=root)
        fontsize = simpledialog.askinteger("Input", "Enter font size (e.g., 10):", parent=root)
        return title, xlabel, ylabel, fontsize
    return None, None, None, None

def generate_visualization():
    if not selected_fields or not 1 <= len(selected_fields) <= 4:
        messagebox.showwarning("Warning", "Please select 1-4 fields for comparison.")
        return

    selected_chart_type = chart_type.get()
    if not selected_chart_type:
        messagebox.showwarning("Warning", "Please select a valid chart type.")
        return

    title, xlabel, ylabel, fontsize = show_customization_options()
    
    plt.figure()
    if fontsize:
        sns.set(font_scale=fontsize/10)

    try:
        if selected_chart_type == 'Histogram':
            sns.histplot(df[selected_fields[0]], kde=True)
        elif selected_chart_type == 'Boxplot':
            sns.boxplot(data=df[selected_fields])
        elif selected_chart_type == 'Barplot':
            sns.barplot(x=selected_fields[0], y=selected_fields[1], data=df)
        elif selected_chart_type == 'Countplot':
            sns.countplot(x=df[selected_fields[0]])
        elif selected_chart_type == 'Scatterplot':
            sns.scatterplot(x=selected_fields[0], y=selected_fields[1], data=df)
        elif selected_chart_type == 'Lineplot':
            sns.lineplot(x=selected_fields[0], y=selected_fields[1], data=df)
        elif selected_chart_type == 'Violin Plot':
            sns.violinplot(x=selected_fields[0], y=selected_fields[1], data=df)
        elif selected_chart_type == 'Heatmap':
            cross_tab = pd.crosstab(df[selected_fields[0]], df[selected_fields[1]])
            sns.heatmap(cross_tab)
        elif selected_chart_type == '3D Scatter Plot':
            from mpl_toolkits.mplot3d import Axes3D
            ax = plt.figure().add_subplot(projection='3d')
            ax.scatter(df[selected_fields[0]], df[selected_fields[1]], df[selected_fields[2]])
        elif selected_chart_type == 'Time Series Plot':
            plt.plot(df[selected_fields[0]], df[selected_fields[1]])
        elif selected_chart_type == 'Pairplot':
            sns.pairplot(df[selected_fields])
        elif selected_chart_type == 'Facet Grid':
            g = sns.FacetGrid(df, col=selected_fields[2])
            g.map(plt.scatter, selected_fields[0], selected_fields[1])
        elif selected_chart_type == 'Parallel Coordinates':
            from pandas.plotting import parallel_coordinates
            parallel_coordinates(df[selected_fields], class_column=selected_fields[0])
        elif selected_chart_type == 'Stacked Bar Chart':
            cross_tab = pd.crosstab(df[selected_fields[0]], df[selected_fields[1]])
            cross_tab.plot(kind='bar', stacked=True)
        else:
            sns.scatterplot(x=selected_fields[0], y=selected_fields[1], data=df)
    except Exception as e:
        messagebox.showerror("Error", f"Error generating visualization: {e}")
        return

    if title:
        plt.title(title)
    if xlabel:
        plt.xlabel(xlabel)
    if ylabel:
        plt.ylabel(ylabel)

    plt.show()

# GUI Layout
frame_top = tk.Frame(root)
frame_top.pack(fill='x', padx=10, pady=5)

frame_middle = tk.Frame(root)
frame_middle.pack(fill='both', expand=True, padx=10, pady=5)

frame_chart_options = tk.Frame(frame_middle)
frame_chart_options.pack(side='top', pady=10)

frame_bottom = tk.Frame(root)
frame_bottom.pack(fill='x', padx=10, pady=5)

load_button = tk.Button(frame_top, text="Load File", command=load_file)
load_button.pack(side='left')

data_types_label = tk.Label(frame_top, text="Data Types: ")
data_types_label.pack(side='left', padx=10)

edit_options_var = tk.BooleanVar()
edit_options_checkbox = ttk.Checkbutton(frame_top, text="Enable Editing", variable=edit_options_var)
edit_options_checkbox.pack(side='right')

listbox_fields = tk.Listbox(frame_middle, selectmode='extended')
listbox_fields.pack(side='left', fill='both', expand=True)
listbox_fields.bind('<<ListboxSelect>>', on_field_select)

scrollbar = ttk.Scrollbar(frame_middle, orient='vertical', command=listbox_fields.yview)
scrollbar.pack(side='left', fill='y')
listbox_fields.config(yscrollcommand=scrollbar.set)

visualize_button = tk.Button(frame_bottom, text="Generate Visualization", command=generate_visualization)
visualize_button.pack(side='right', padx=10)

root.mainloop()
