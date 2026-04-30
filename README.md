# pixelator
A method to encode and decode files to and from PNG files.

# NOTE:

The latest version of the script is the 'pixelator-standalone-full.py' and 'pixelator-standalone-auto.py' scripts. Both of which handle adding metadata to the PNG and handle batch processing.

---

#### How the Encoding Works

The encoding process is a multi-stage pipeline that transforms raw file data into a visual image. 

**1. Reading the Raw Data**
```python
with open(input_path, 'r', encoding='utf-8') as f:
    raw_data = f.read()
```

The script begins by reading the entire content of the source file into memory as a string. (Note: The second script correctly uses binary mode `rb`, which is better for non-text files. This first script was designed for text).

**2. Compression (Gzip)**

```python
compressed = gzip.compress(raw_data.encode('utf-8'))
```

*   **What:** The raw data is compressed using the Gzip algorithm, the same one used for `.gz` files.

*   **Why:** Most files contain repetitive patterns. Compression significantly reduces the amount of data we need to store. A smaller data size results in a smaller final PNG image. This is a **lossless** compression, meaning no information is lost.

**3. Transcoding (Base64)**

```python
b64_data = base64.urlsafe_b64encode(compressed).decode('utf-8')
```

*   **What:** The compressed binary data is encoded using Base64. This transforms the raw bytes (which can have any value from 0 to 255) into a string composed of only "safe" ASCII characters (A-Z, a-z, 0-9, '-', '_').

*   **Why:** This is a crucial step. We need to represent our data as RGB pixel values, where each color channel (Red, Green, Blue) is a byte. Base64 ensures that our data stream is clean and predictable, without any problematic control characters that could interfere with the process.

**4. Ligation to Pixels (The Visual Step)**
This is where the data becomes an image.

```python
# Convert the B64 string back into bytes
data_bytes = b64_data.encode('utf-8')

# Ensure the total number of bytes is a multiple of 3 (for RGB)
padding = (3 - len(data_bytes) % 3) % 3
padded_data = data_bytes + b'\x00' * padding

# Treat the byte stream as a list of [R,G,B] pixel values
pixels = np.frombuffer(padded_data, dtype=np.uint8).reshape(-1, 3)
```

*   A pixel is composed of 3 bytes: one for Red, one for Green, and one for Blue.
*   The script takes the long stream of Base64 bytes and groups them into chunks of three.
*   If the data stream isn't perfectly divisible by 3, it adds one or two null bytes (`\x00`, which corresponds to black) as padding to make it divisible.

**5. Arranging Pixels in a Square**
```python
# Calculate the side length for a square image
side = int(math.ceil(math.sqrt(len(pixels))))

# Create a blank (black) square canvas of the required size
vram = np.zeros((side * side, 3), dtype=np.uint8)

# "Paint" our data pixels onto the canvas
vram[:len(pixels)] = pixels

# Reshape the 1D pixel list into a 2D image
vram_img = vram.reshape((side, side, 3))
```

*   **What:** To create an image, we need to arrange the pixels in a 2D grid. The most efficient shape is a square.

*   **Why:** The script calculates the smallest possible square that can hold all of our data pixels (`math.sqrt`). If our data doesn't perfectly fill the square, the remaining space is left as black pixels (`np.zeros`). This is why you often see a black border or section at the bottom-right of the generated images.

**6. Saving the Final Image**

```python
Image.fromarray(vram_img).save(seed_path)
```
Finally, the 2D array of RGB pixel values is saved as a PNG file. PNG is used because it is a **lossless** image format, which is essential. Using a lossy format like JPEG would corrupt the data and make perfect reconstruction impossible.

---

### Part 2: The Decoder

#### How the Decoding Works

The decoding process is the exact reverse of encoding, with one very clever trick to ensure 100% accuracy. The `IronVaultPrecision` version of the script introduced a "Precision Anchor" to solve a key problem.

**The Problem:** The encoder pads the data with null bytes to make it fit into RGB triplets and pads the image with black pixels to make it a perfect square. When decoding, how do we know where the *real* data ends and the padding begins?

**The Solution (The "Precision Anchor"):** The `IronVaultPrecision` encoder appends the **length of the Base64 string** as a 4-byte number to the end of the payload before converting it to pixels. This acts as a map for the decoder.

Let's trace the decoding process for `MASTER_DNA_SEED_my_data.json.png`:

**1. Extracting the Original Filename**

```python
original_filename = png_filename[18:-4]
```

The script first "parses" the PNG filename to figure out what the original file should be called. It strips the prefix (`MASTER_DNA_SEED_`) and the suffix (`.png`).

**2. Reading the Image Data**

```python
img = Image.open(png_path).convert('RGB')
raw_bytes = np.array(img).flatten().tobytes()
```

The script opens the PNG image and "flattens" it from a 2D grid of pixels back into a single, continuous 1D stream of bytes (R, G, B, R, G, B, ...).

**3. Finding the Precision Anchor**

```python
clean_bytes = raw_bytes.rstrip(b'\x00')
data_len = struct.unpack(">I", clean_bytes[-4:])[0]
```

This is the magic step.
*   First, it strips all trailing null bytes (`\x00`) from the stream. This removes the black pixels used to pad the square image.
*   Now, the *very last 4 bytes* of the remaining data are the length anchor we stored during encoding.
*   `struct.unpack` reads these 4 bytes and converts them back into an integer (`data_len`). We now know the *exact* length of the original Base64 data.

**4. Slicing the Exact Data**

```python
b64_data = clean_bytes[:data_len]
```

Using the length we just recovered, the script slices the byte stream. This gives us the pure Base64 data, discarding any extra padding bytes that were added to make the stream divisible by three.

**5. Reversing Transcoding (Base64)**

```python
compressed = base64.urlsafe_b64decode(b64_data)
```

The Base64 data is decoded back into the compressed binary data.

**6. Reversing Compression (Gzip)**

```python
original_bytes = gzip.decompress(compressed)
```

The compressed data is decompressed, yielding the final, bit-perfect bytes of the original file.

**7. Writing the Final File**

```python
with open(output_path, "wb") as f:
    f.write(original_bytes)
```

The script writes these restored bytes to a new file in the `pixelated_done` directory, using the original filename it extracted in the first step. The process is complete.

---
---

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/thatoldfarm/pixelator/blob/main/LICENSE) file for details.
