import gzip
import base64
import os
import numpy as np
from PIL import Image
import math
import struct

class IronVaultPrecision:
    # The encode method is not used in this script but is kept for completeness.
    @staticmethod
    def encode(input_path, output_png="MASTER_DNA_SEED.png"):
        if not os.path.exists(input_path):
            print(f"[!] Source file {input_path} not found.")
            return

        print(f"[ENCODE] Opening Binary Source: {input_path}")
        with open(input_path, "rb") as f:
            raw_bytes = f.read()
        
        compressed = gzip.compress(raw_bytes)
        b64_str = base64.urlsafe_b64encode(compressed)
        data_len = len(b64_str)
        payload = b64_str + struct.pack(">I", data_len)
        
        padding_needed = (3 - len(payload) % 3) % 3
        padded_payload = payload + b'\x00' * padding_needed
        pixels = np.frombuffer(padded_payload, dtype=np.uint8).reshape(-1, 3)
        
        side = int(math.ceil(math.sqrt(len(pixels))))
        vram = np.zeros((side * side, 3), dtype=np.uint8)
        vram[:len(pixels)] = pixels
        
        Image.fromarray(vram.reshape((side, side, 3))).save(output_png)
        print(f"[SUCCESS] Created {output_png} ({side}x{side} px)")
        print(f"          Original Size: {len(raw_bytes)} bytes")

    # The decode method is used exactly as it is. No changes are needed here.
    @staticmethod
    def decode(png_path, output_path):
        if not os.path.exists(png_path):
            print(f"    [!] Seed file {png_path} not found.")
            return

        print(f"    Extracting Lattice from: {os.path.basename(png_path)}")
        try:
            img = Image.open(png_path).convert('RGB')
            raw_bytes = np.array(img).flatten().tobytes()
            
            clean_bytes = raw_bytes.rstrip(b'\x00')
            data_len = struct.unpack(">I", clean_bytes[-4:])[0]
            
            b64_data = clean_bytes[:data_len]
            
            compressed = base64.urlsafe_b64decode(b64_data)
            original_bytes = gzip.decompress(compressed)
            
            with open(output_path, "wb") as f:
                f.write(original_bytes)
                
            print(f"    [SUCCESS] Restored to: {output_path}")
            print(f"    Final Size: {len(original_bytes)} bytes")
            return len(original_bytes)
        except Exception as e:
            print(f"    [!] FAILED to decode {os.path.basename(png_path)}: {e}")
            return None


# --- NEW BATCH DECODING EXECUTION BLOCK ---
if __name__ == "__main__":
    input_directory = "pixelated"
    output_directory = "pixelated_done"

    # Check if the input directory exists
    if not os.path.isdir(input_directory):
        print(f"Input directory '{input_directory}' not found.")
        print("Please run the first script to generate the encoded PNG files.")
        exit()

    # Create the output directory if it doesn't exist
    os.makedirs(output_directory, exist_ok=True)
    
    vault = IronVaultPrecision()
    
    files_to_process = os.listdir(input_directory)

    if not files_to_process:
        print(f"The '{input_directory}' directory is empty. Nothing to decode.")
    else:
        print(f"--- IRON VAULT BATCH DECODER ---")
        print(f"Found {len(files_to_process)} items in '{input_directory}'. Starting restoration...")
        print("---")
        
        for png_filename in files_to_process:
            # We only want to process the specific PNGs created by the first script
            if png_filename.startswith("MASTER_DNA_SEED_") and png_filename.endswith(".png"):
                
                print(f"[+] Processing: {png_filename}")

                # --- FIX IS HERE ---
                # This is the new, robust way to extract the original filename.
                prefix = "MASTER_DNA_SEED_"
                suffix = ".png"
                
                # For Python 3.9+ you could just do:
                # original_filename = png_filename.removeprefix(prefix).removesuffix(suffix)
                
                # This manual way works on all Python 3 versions:
                temp_filename = png_filename
                if temp_filename.startswith(prefix):
                    temp_filename = temp_filename[len(prefix):]
                if temp_filename.endswith(suffix):
                    temp_filename = temp_filename[:-len(suffix)]
                original_filename = temp_filename
                # --- END OF FIX ---
                
                # Construct the full paths
                input_path = os.path.join(input_directory, png_filename)
                output_path = os.path.join(output_directory, original_filename)
                
                # Call the decode method with the correct paths
                vault.decode(input_path, output_path)
                print("---")
        
        print("All files processed.")
