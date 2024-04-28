import os
import tkinter as tk
from tkinter import filedialog, ttk
from autoviz import AutoViz_Class

def browse_file():
    file_path = filedialog.askopenfilename(defaultextension=".csv",
                                           filetypes=[("CSV and JSON Files", "*.csv;*.json"),
                                                      ("CSV Files", "*.csv"),
                                                      ("JSON Files", "*.json")])
    if file_path:
        file_path_var.set(file_path)

def process_file():
    file_path = file_path_var.get()
    chart_format = chart_format_var.get()
    depVar = depVar_entry.get()
    verbose = int(verbose_var.get())
    max_rows_analyzed = int(max_rows_analyzed_entry.get() or 150000)
    max_cols_analyzed = int(max_cols_analyzed_entry.get() or 30)
# Close the Tkinter window after processing the file
    window.destroy()

    AV = AutoViz_Class()
    dft = AV.AutoViz(
        file_path,
        sep=",",
        depVar=depVar,
        dfte=None,
        header=0,
        verbose=verbose,
        lowess=False,
        chart_format=chart_format,
        max_rows_analyzed=max_rows_analyzed,
        max_cols_analyzed=max_cols_analyzed,
        save_plot_dir=os.path.dirname(file_path)
    )

# Create the main window
window = tk.Tk()
window.title("AutoViz")

# Create variables to store the user input
file_path_var = tk.StringVar()
chart_format_var = tk.StringVar(value='png')
depVar_var = tk.StringVar()
verbose_var = tk.StringVar(value='2')
max_rows_analyzed_var = tk.StringVar(value='150000')
max_cols_analyzed_var = tk.StringVar(value='30')

# Create a button to browse for the file
browse_button = tk.Button(window, text="Browse", command=browse_file)
browse_button.pack(pady=10)

# Create a label and entry for the file path
file_path_label = tk.Label(window, text="File Path:")
file_path_label.pack()
file_path_entry = tk.Entry(window, textvariable=file_path_var, width=50)
file_path_entry.pack()

# Create a label and dropdown for chart format
chart_format_label = tk.Label(window, text="Chart Format:")
chart_format_label.pack()
chart_format_dropdown = ttk.Combobox(window, textvariable=chart_format_var, values=['svg', 'png', 'jpg', 'bokeh', 'server', 'html'])
chart_format_dropdown.pack()

# Create a label and entry for depVar
depVar_label = tk.Label(window, text="Target Header Field in csv:")
depVar_label.pack()
depVar_entry = tk.Entry(window, textvariable=depVar_var)
depVar_entry.pack()

# Create a label and dropdown for verbose
verbose_label = tk.Label(window, text="Verbose:")
verbose_label.pack()
verbose_dropdown = ttk.Combobox(window, textvariable=verbose_var, values=['0', '1', '2'])
verbose_dropdown.pack()

# Create a label and entry for max_rows_analyzed
max_rows_analyzed_label = tk.Label(window, text="Max Rows Analyzed:")
max_rows_analyzed_label.pack()
max_rows_analyzed_entry = tk.Entry(window, textvariable=max_rows_analyzed_var)
max_rows_analyzed_entry.pack()

# Create a label and entry for max_cols_analyzed
max_cols_analyzed_label = tk.Label(window, text="Max Columns Analyzed:")
max_cols_analyzed_label.pack()
max_cols_analyzed_entry = tk.Entry(window, textvariable=max_cols_analyzed_var)
max_cols_analyzed_entry.pack()

# Create a button to process the file
process_button = tk.Button(window, text="Process", command=process_file)
process_button.pack(pady=10)

# Run the Tkinter event loop
window.mainloop()