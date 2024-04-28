import os
import tkinter as tk
from tkinter import filedialog

def browse_file():
    file_path = filedialog.askopenfilename(defaultextension=".xlsx",
                                           filetypes=[("Excel and CSV Files", "*.xlsx;*.xls;*.csv"),
                                                      ("Excel Files", "*.xlsx;*.xls"),
                                                      ("CSV Files", "*.csv")])
    if file_path:
        window.destroy()  # Close the Tkinter window
        process_file(file_path)

def process_file(file_path):
    _, file_extension = os.path.splitext(file_path)

    if file_extension == '.xlsx' or file_extension == '.xls':
        os.system(f"python report_xlsx.py {file_path}")
    elif file_extension == '.csv':
        os.system(f"python report_csv.py {file_path}")
    else:
        print("Unsupported file format. Please provide an Excel (.xlsx or .xls) or CSV (.csv) file.")

# Create the main window
window = tk.Tk()
window.title("File Processing")

# Create a button to browse for the file
browse_button = tk.Button(window, text="Browse", command=browse_file)
browse_button.pack(pady=10)

# Run the Tkinter event loop
window.mainloop()