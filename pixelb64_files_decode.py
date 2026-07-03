import base64
import os

# Change this to the specific _b64.txt file you want to decode
INPUT_FILE = "files/example.png_b64.txt" 

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: The file '{INPUT_FILE}' was not found.")
        return

    try:
        with open(INPUT_FILE, "r") as text_file:
            # Read the lines of the file
            lines = text_file.readlines()
            
            if len(lines) < 2:
                print("Error: The file format is incorrect. It needs a filename line and a data line.")
                return

            # Line 1 is the original filename
            recovered_filename = lines[0].strip()
            # Line 2 is the Base64 string
            base64_string = lines[1].strip()

        print(f"Recovering file as: {recovered_filename}...")

        # Decode the URL-safe Base64 string
        binary_data = base64.urlsafe_b64decode(base64_string)

        # Save using the recovered filename
        with open(recovered_filename, "wb") as image_file:
            image_file.write(binary_data)

        print(f"Success! File recovered as {recovered_filename}")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
