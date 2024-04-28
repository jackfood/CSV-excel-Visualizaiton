import sys
import os
import numpy as np
import pandas as pd
from ydata_profiling import ProfileReport

print('Generating report for Excel...')
# Get the file path from command line arguments
file_path = sys.argv[1]

# Read the Excel file
df = pd.read_excel(file_path)

# Generate the profiling report
profile = ProfileReport(df, title="Profiling Report")

# Get the directory of the input file
input_directory = os.path.dirname(file_path)

# Create the output file path in the same directory as the input file
output_file = os.path.join(input_directory, "report_xlsx.html")

# Save the report to the output file path
profile.to_file(output_file)