import os
from tkinter import Tk, filedialog
from PIL import Image
import pytesseract
import piexif

# Specify the Tesseract executable path
tesseract_path = r'D:\mklink_cache\Tesseract\tesseract.exe'
pytesseract.pytesseract.tesseract_cmd = tesseract_path

def convert_to_jpg(input_folder):
    # Create an output folder for the JPG images
    output_folder = os.path.join(input_folder, "converted_images")
    os.makedirs(output_folder, exist_ok=True)

    # Iterate through all files in the input folder
    for filename in os.listdir(input_folder):
        input_path = os.path.join(input_folder, filename)

        # Check if the file is an image (you may want to extend this check)
        if os.path.isfile(input_path) and any(input_path.lower().endswith(ext) for ext in ['.png', '.jpeg', '.gif', '.bmp']):
            # Open and convert the image to JPG format
            with Image.open(input_path) as img:
                jpg_path = os.path.join(output_folder, os.path.splitext(filename)[0] + ".jpg")
                img.convert("RGB").save(jpg_path, "JPEG")

                # Perform OCR and save text
                ocr_and_save_text(jpg_path, input_folder)

    print("Conversion and OCR completed. JPG images and OCR text saved in:", output_folder)

def ocr_and_save_text(image_path, output_dir):
    try:
        print(f"Processing image: {image_path}")

        # Open the image
        with Image.open(image_path) as img:
            # Perform OCR using Tesseract
            ocr_result = pytesseract.image_to_string(img, lang='eng')

            # Save OCR result as a UTF-8 text file in the same directory as the image directory
            text_file_path = os.path.join(output_dir, os.path.splitext(os.path.basename(image_path))[0] + '_ocr_result.txt')
            with open(text_file_path, 'w', encoding='utf-8') as text_file:
                text_file.write(ocr_result)
            
            print(f"OCR completed. Text saved to: {text_file_path}")

            # Add OCR text to image metadata
            exif_dict = piexif.load(image_path)
            exif_dict['0th'][piexif.ImageIFD.ImageDescription] = ocr_result.encode('utf-8')
            exif_bytes = piexif.dump(exif_dict)
            piexif.insert(exif_bytes, image_path)
            print(f"OCR text added to image metadata: {image_path}")

    except Exception as e:
        print(f"Error processing image {image_path}: {e}")

def select_folder():
    # Create a Tkinter root window (it won't be shown)
    root = Tk()
    root.withdraw()

    # Ask the user to select a folder containing image files
    folder_selected = filedialog.askdirectory(title="Select Folder with Image Files")

    # Check if the user selected a folder
    if folder_selected:
        convert_to_jpg(folder_selected)

if __name__ == "__main__":
    select_folder()
