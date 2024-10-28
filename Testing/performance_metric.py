'''
UACI (User Authentication Code Initialization):

The value 0.3674611747264862 is likely a measure of the effectiveness or error rate of a particular authentication or 
encryption process. A lower value is generally desirable, indicating better accuracy in user authentication.


NPCR (National Physical Cryptographic Resource):

The value 0.9960759106213651 is likely a measure of the percentage change in pixels between the original and encrypted 
images. In NPCR, a value close to 1 indicates that the encrypted image has a high similarity to the original, which is 
generally desirable.
'''

import numpy as np
from PIL import Image

def calculate_uaci(original, encrypted):
    # Convert images to numpy arrays
    original_array = np.array(original, dtype=np.float32)
    encrypted_array = np.array(encrypted, dtype=np.float32)

    # Calculate UACI
    uaci = np.sum(np.abs(original_array - encrypted_array)) / np.sum(original_array + encrypted_array)

    return uaci

def calculate_npcr(original, encrypted):
    # Convert images to numpy arrays
    original_array = np.array(original)
    encrypted_array = np.array(encrypted)

    # Calculate NPCR
    npcr = np.sum(original_array != encrypted_array) / (original_array.size * 1.0)

    return npcr


original_image = Image.open("C:/Users/Videep/Desktop/MIE/Testing/original.png")
encrypted_image = Image.open("C:/Users/Videep/Desktop/MIE/Testing/encrypted.png")


if original_image.size != encrypted_image.size:
    raise ValueError("Original and encrypted images must have the same dimensions.")


uaci_value = calculate_uaci(original_image, encrypted_image)
print(f"UACI: {uaci_value}")


npcr_value = calculate_npcr(original_image, encrypted_image)
print(f"NPCR: {npcr_value}")
