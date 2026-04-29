import gzip
import base64
import os
import numpy as np
from PIL import Image
import math
import struct
import json
import hashlib

class IronVaultUltimate:
    def __init__(self):
        self.prefix = "MASTER_DNA_SEED_"
        self.output_ext = ".png"

    def _calculate_checksum(self, data):
        """Generates a SHA-256 hash of the data."""
        return hashlib.sha256(data).hexdigest()

    def encode_batch(self, input_dir="pixelate", output_dir="pixelated"):
        os.makedirs(output_dir, exist_ok=True)
        if not os.path.exists(input_dir):
            os.makedirs(input_dir)
            print(f"[*] Created {input_dir}/. Please add files there and restart.")
            return

        files = [f for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f))]
        
        for filename in files:
            input_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, f"{self.prefix}{filename}{self.output_ext}")
            
            print(f"[ENCODE] Processing: {filename}")
            
            # 1. Read Raw Binary
            with open(input_path, "rb") as f:
                raw_data = f.read()

            # 2. Generate Checksum & Metadata
            checksum = self._calculate_checksum(raw_data)
            metadata = {
                "filename": filename,
                "checksum": checksum,
                "size": len(raw_data)
            }
            metadata_json = json.dumps(metadata).encode('utf-8')
            
            # 3. Compress Data
            compressed_data = gzip.compress(raw_data)

            # 4. Construct Binary Package: 
            # [4 bytes Header Len] + [Metadata JSON] + [Compressed Data]
            header_len = struct.pack(">I", len(metadata_json))
            payload = header_len + metadata_json + compressed_data
            
            # 5. Base64 & Length Anchor
            b64_str = base64.urlsafe_b64encode(payload)
            final_data = b64_str + struct.pack(">I", len(b64_str))

            # 6. Map to Pixels
            padding = (3 - len(final_data) % 3) % 3
            padded_data = final_data + b'\x00' * padding
            pixels = np.frombuffer(padded_data, dtype=np.uint8).reshape(-1, 3)
            
            side = int(math.ceil(math.sqrt(len(pixels))))
            vram = np.zeros((side * side, 3), dtype=np.uint8)
            vram[:len(pixels)] = pixels
            
            Image.fromarray(vram.reshape((side, side, 3))).save(output_path)
            print(f"    [SUCCESS] Checksum: {checksum[:10]}... (Verified)")

    def decode_batch(self, input_dir="pixelated", output_dir="pixelated_done"):
        os.makedirs(output_dir, exist_ok=True)
        if not os.path.exists(input_dir):
            print(f"[!] {input_dir} not found.")
            return

        files = [f for f in os.listdir(input_dir) if f.endswith(self.output_ext)]

        for png_file in files:
            print(f"[DECODE] Analyzing: {png_file}")
            img_path = os.path.join(input_dir, png_file)
            
            try:
                # 1. Extract Pixels
                img = Image.open(img_path).convert('RGB')
                raw_bytes = np.array(img).flatten().tobytes()
                
                # 2. Find Length Anchor
                clean_bytes = raw_bytes.rstrip(b'\x00')
                total_b64_len = struct.unpack(">I", clean_bytes[-4:])[0]
                
                # 3. Decode B64
                b64_payload = clean_bytes[:total_b64_len]
                binary_blob = base64.urlsafe_b64decode(b64_payload)
                
                # 4. Parse Metadata Header
                header_len = struct.unpack(">I", binary_blob[:4])[0]
                metadata_json = binary_blob[4:4+header_len]
                metadata = json.loads(metadata_json.decode('utf-8'))
                
                # 5. Decompress Data
                compressed_data = binary_blob[4+header_len:]
                restored_data = gzip.decompress(compressed_data)
                
                # 6. Checksum Verification
                new_checksum = self._calculate_checksum(restored_data)
                if new_checksum == metadata['checksum']:
                    status = "BIT-PERFECT VERIFIED"
                else:
                    status = "!!! CHECKSUM MISMATCH (CORRUPT) !!!"

                # 7. Save to original filename
                output_path = os.path.join(output_dir, metadata['filename'])
                with open(output_path, "wb") as f:
                    f.write(restored_data)
                
                print(f"    [RESULT] {metadata['filename']} | {status}")
                
            except Exception as e:
                print(f"    [!] Error processing {png_file}: {e}")

if __name__ == "__main__":
    vault = IronVaultUltimate()
    
    print("--- 1. RUNNING ENCODER ---")
    vault.encode_batch("pixelate", "pixelated")
    
    print("\n--- 2. RUNNING DECODER ---")
    vault.decode_batch("pixelated", "pixelated_done")
