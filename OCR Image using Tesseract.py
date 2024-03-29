import os
from tkinter import Tk, filedialog, messagebox
from PIL import Image
import pytesseract
import piexif

# Specify the Tesseract executable path
tesseract_path = r'D:\mklink_cache\Tesseract\tesseract.exe'
pytesseract.pytesseract.tesseract_cmd = tesseract_path

def convert_to_jpg(input_path):
    if os.path.isfile(input_path):
        # Process a single file
        output_folder = os.path.dirname(input_path)
        ocr_and_save_text(input_path, output_folder)
    else:
        # Process all files in the folder
        output_folder = os.path.join(input_path, "converted_images")
        os.makedirs(output_folder, exist_ok=True)

        for filename in os.listdir(input_path):
            file_path = os.path.join(input_path, filename)

            if os.path.isfile(file_path) and any(file_path.lower().endswith(ext) for ext in ['.png', '.jpeg', '.gif', '.bmp']):
                with Image.open(file_path) as img:
                    jpg_path = os.path.join(output_folder, os.path.splitext(filename)[0] + ".jpg")
                    img.convert("RGB").save(jpg_path, "JPEG")
                    ocr_and_save_text(jpg_path, input_path)

    messagebox.showinfo("Conversion and OCR", "Conversion and OCR completed.")

def ocr_and_save_text(image_path, output_dir):
    try:
        print(f"Processing image: {image_path}")

        with Image.open(image_path) as img:
            ocr_result = pytesseract.image_to_string(img, lang='eng')

            text_file_path = os.path.join(output_dir, os.path.splitext(os.path.basename(image_path))[0] + '_ocr_result.txt')
            with open(text_file_path, 'w', encoding='utf-8') as text_file:
                text_file.write(ocr_result)
            
            print(f"OCR completed. Text saved to: {text_file_path}")

            exif_dict = piexif.load(image_path)
            exif_dict['0th'][piexif.ImageIFD.ImageDescription] = ocr_result.encode('utf-8')
            exif_bytes = piexif.dump(exif_dict)
            piexif.insert(exif_bytes, image_path)
            print(f"OCR text added to image metadata: {image_path}")

    except Exception as e:
        print(f"Error processing image {image_path}: {e}")

def select_file():
    root = Tk()
    root.withdraw()
    file_selected = filedialog.askopenfilename(title="Select Image File")
    if file_selected:
        convert_to_jpg(file_selected)

def select_folder():
    root = Tk()
    root.withdraw()
    folder_selected = filedialog.askdirectory(title="Select Folder with Image Files")
    if folder_selected:
        convert_to_jpg(folder_selected)

def main():
    root = Tk()
    root.withdraw()

    choice = messagebox.askquestion("OCR Image Processor", "Please select an option:",
                                    icon='question', type='yesnocancel',
                                    detail="Yes: Process a single file\nNo: Process a whole folder\nCancel: Exit the program")

    if choice == 'yes':
        select_file()
    elif choice == 'no':
        select_folder()
    else:
        messagebox.showinfo("OCR Image Processor", "Program terminated.")

if __name__ == "__main__":
    main()
