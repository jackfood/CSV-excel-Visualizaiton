# CSV/Excel Data Visualizer

This project is a Python-based data visualization tool that allows users to load CSV or Excel files, select columns for the X and Y axes, choose a chart type, and customize various chart properties. The tool provides a user-friendly graphical interface built with Tkinter and utilizes popular data analysis and visualization libraries such as Pandas and Matplotlib.

## Features

- Load CSV and Excel files
- Select columns for the X and Y axes
- Choose from various chart types:
  - Line
  - Bar
  - Column
  - Area
  - Stacked Bar
  - Scatter Plot
  - Dual Axes
- Customize chart properties:
  - Title font size
  - Tick label font size
  - Chart size (Small, Medium, Large)
  - X-axis tick label rotation (45°, 90°, 180°)
- Automatic chart type recommendation based on selected columns
- Clear selections for starting a new visualization

## Requirements

- Python 3.x
- Pandas
- Matplotlib
- Tkinter
- NumPy

## Installation

1. Clone the repository:

```
git clone https://github.com/your-username/csv-excel-data-visualizer.git
```

2. Install the required dependencies:

```
pip install pandas matplotlib tkinter numpy
```

## Usage

1. Run the script:

```
python data_visualizer.py
```

2. Click the "Load File" button to select a CSV or Excel file.

3. Choose the desired columns for the X and Y axes from the dropdown menus.

4. Select a chart type from the dropdown menu or use the automatically recommended chart type.

5. Customize the chart properties:
   - Enter the desired title font size (default: 14)
   - Enter the desired tick label font size (default: 8)
   - Select the chart size (Small, Medium, Large)
   - Choose the X-axis tick label rotation (45°, 90°, 180°)

6. Click the "Visualize" button to generate the visualization.

7. To start a new visualization, click the "Clear" button to reset the selections.

## Example

Here's an example of how to use the CSV/Excel Data Visualizer:

1. Load a CSV file containing sales data with columns: "Month", "Product", and "Revenue".

2. Select "Month" for the X-axis and "Revenue" for the Y-axis.

3. The tool automatically recommends a "Bar" chart based on the selected columns.

4. Customize the chart properties as desired (e.g., set the title font size to 16 and the chart size to Large).

5. Click "Visualize" to generate a bar chart showing the revenue for each month.

6. To create a new visualization, click "Clear" and repeat the process with different selections.

## Contributing

Contributions are welcome! If you find any issues or have suggestions for improvements, please open an issue or submit a pull request.

## License

This project is licensed under the [MIT License](LICENSE).

## Acknowledgements

- [Pandas](https://pandas.pydata.org/)
- [Matplotlib](https://matplotlib.org/)
- [Tkinter](https://docs.python.org/3/library/tkinter.html)
- [NumPy](https://numpy.org/)

Feel free to customize the README file based on your specific project details and requirements.
