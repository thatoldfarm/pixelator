import base64
import os

# The folder to scan
SOURCE_FOLDER = "files"

def encode_png_to_b64(input_path, output_path, original_filename):
    """Encodes file and saves filename + data into the text file."""
    try:
        with open(input_path, "rb") as image_file:
            binary_data = image_file.read()
            encoded_bytes = base64.urlsafe_b64encode(binary_data)
            base64_string = encoded_bytes.decode('utf-8')

        with open(output_path, "w") as text_file:
            # LINE 1: The original filename
            # LINE 2: The actual Base64 data
            text_file.write(f"{original_filename}\n{base64_string}")
        
        return True
    except Exception as e:
        print(f"  Failed to encode {input_path}: {e}")
        return False

def main():
    if not os.path.exists(SOURCE_FOLDER):
        print(f"Error: The folder '{SOURCE_FOLDER}' was not found.")
        return

    print(f"Scanning '{SOURCE_FOLDER}' for PNGs...")
    files_processed = 0

    for root, dirs, files in os.walk(SOURCE_FOLDER):
        for filename in files:
            if filename.lower().endswith(".png"):
                input_path = os.path.join(root, filename)
                output_filename = f"{filename}_b64.txt"
                output_path = os.path.join(root, output_filename)
                
                print(f"Encoding: {input_path} ...", end=" ")
                if encode_png_to_b64(input_path, output_path, filename):
                    print("Done!")
                    files_processed += 1

    print(f"\nSuccess! Processed {files_processed} files.")

if __name__ == "__main__":
    main()
