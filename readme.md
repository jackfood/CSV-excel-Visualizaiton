# Image OCR Converter**
This project is a Python script designed to convert various image formats such as PNG, JPEG, GIF, and BMP to JPG format while performing Optical Character Recognition (OCR) using Tesseract. It saves the OCR results as text files and embeds them into the image metadata. The script utilizes libraries such as Pillow, pytesseract, and piexif for image processing and OCR.

**Features**
Convert images to JPG format
Perform OCR using Tesseract
Save OCR text as separate files
Embed OCR text into image metadata
Installation
Install Python 3.x from python.org.
Install Tesseract OCR Engine from here.
Install required Python packages:
bash
```
pip install pillow pytesseract piexif
```
**Usage**
Run the script.
Select a folder containing image files.
Converted images and OCR text files will be saved in a subfolder named converted_images.
Example
Suppose you have a folder named input_images containing various image files like .png, .jpeg, .gif, .bmp, etc. After running the script, a folder named converted_images will be created inside the input_images directory. The converted images in JPG format and their OCR text files will be saved in this folder.

```
input_images/
    ├── converted_images/
    │   ├── image1.jpg
    │   ├── image1_ocr_result.txt
    │   ├── image2.jpg
    │   ├── image2_ocr_result.txt
    │   ├── image3.jpg
    │   ├── image3_ocr_result.txt
    │   └── ...
    ├── image1.png
    ├── image2.jpg
    ├── image3.gif
    └── ...
```
Additionally, the OCR text will be embedded into the image metadata.

**Notes**
Ensure Tesseract is properly installed and its executable path is correctly set in the script (tesseract_path variable).
This script supports common image formats like PNG, JPEG, GIF, and BMP. You can extend the supported formats by modifying the code.


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
git clone https://github.com/jackfood/csv-excel-data-visualizer.git
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
