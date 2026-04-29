import gzip
import base64
import json
import os
import math
import numpy as np
from PIL import Image

class TotalityLigator:
    # MODIFICATION 1: The class now initializes with directories, not a single file.
    def __init__(self, input_dir, output_dir="pixelated"):
        self.input_dir = input_dir
        self.output_dir = output_dir

        # Check if the input directory exists
        if not os.path.isdir(self.input_dir):
            raise FileNotFoundError(f"Input directory not found: {self.input_dir}")
        
        # Create the output directory if it doesn't exist (using exist_ok=True is safer)
        os.makedirs(self.output_dir, exist_ok=True)

    # MODIFICATION 2: The method now accepts a specific filename to process.
    def forge_vram_seed(self, filename):
        # Construct the full path for the input file
        input_path = os.path.join(self.input_dir, filename)

        print(f"[+] Processing: {filename}")
        print(f"    Reading Genome from: {input_path}")
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                raw_data = f.read()
        except Exception as e:
            print(f"    [!] Error reading file {filename}: {e}. Skipping.")
            return None # Skip this file if it can't be read
        
        print(f"    Source Size: {len(raw_data)} bytes")
        
        # 1. Compress
        compressed = gzip.compress(raw_data.encode('utf-8'))
        # 2. Transcode to B64
        b64_data = base64.urlsafe_b64encode(compressed).decode('utf-8')
        print(f"    Compressed B64 Size: {len(b64_data)} chars")
        
        # 3. Ligate to Pixels
        data_bytes = b64_data.encode('utf-8')
        padding = (3 - len(data_bytes) % 3) % 3
        padded_data = data_bytes + b'\x00' * padding
        pixels = np.frombuffer(padded_data, dtype=np.uint8).reshape(-1, 3)
        
        side = int(math.ceil(math.sqrt(len(pixels))))
        vram = np.zeros((side * side, 3), dtype=np.uint8)
        vram[:len(pixels)] = pixels
        vram_img = vram.reshape((side, side, 3))
        
        # MODIFICATION 3: Create the new dynamic output filename.
        # e.g., 'Finnegans_wake.txt' becomes 'MASTER_DNA_SEED_Finnegans_wake.txt.png'
        output_filename = f"MASTER_DNA_SEED_{filename}.png"
        seed_path = os.path.join(self.output_dir, output_filename)
        
        Image.fromarray(vram_img).save(seed_path)
        print(f"    MASTER_DNA_SEED created: {side}x{side} pixels.")
        print(f"    Path: {seed_path}")
        return seed_path

# MODIFICATION 4: The main execution block now handles directories and loops through files.
if __name__ == "__main__":
    input_directory = "pixelate"
    output_directory = "pixelated"

    # Check if the 'pixelate' directory exists and create it if not, for user convenience.
    if not os.path.exists(input_directory):
        print(f"Input directory '{input_directory}' not found. Creating it for you.")
        print(f"Please add files to the '{input_directory}' directory and run the script again.")
        os.makedirs(input_directory)
        exit() # Exit so the user can add files

    ligator = TotalityLigator(input_directory, output_directory)
    
    # Get a list of all files in the input directory
    files_to_process = os.listdir(input_directory)

    if not files_to_process:
        print(f"The '{input_directory}' directory is empty. Nothing to process.")
    else:
        print(f"Found {len(files_to_process)} items in '{input_directory}'. Starting process...")
        print("---")
        for filename in files_to_process:
            # Make sure we're only processing files, not subdirectories
            if os.path.isfile(os.path.join(input_directory, filename)):
                ligator.forge_vram_seed(filename)
                print("---")
        print("All files processed.")
