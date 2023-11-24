from PIL import Image
import cv2
import numpy as np
import os
import json
import tkinter as tk
from tkinter import filedialog

ENCRYPTED_FOLDER = r'C:/Users/Videep/OneDrive\Desktop/Image Encryption/Encrypted'

'''
GLOBAL Constants
'''
# Lorenz parameters
a, b, c = 10, 2.667, 28
x0, y0, z0 = 0, 0, 0

dna = {}
dna["00"] = "A"
dna["01"] = "T"
dna["10"] = "G"
dna["11"] = "C"
dna["A"] = [0, 0]
dna["T"] = [0, 1]
dna["G"] = [1, 0]
dna["C"] = [1, 1]
# DNA xor
dna["AA"] = dna["TT"] = dna["GG"] = dna["CC"] = "A"
dna["AG"] = dna["GA"] = dna["TC"] = dna["CT"] = "G"
dna["AC"] = dna["CA"] = dna["GT"] = dna["TG"] = "C"
dna["AT"] = dna["TA"] = dna["CG"] = dna["GC"] = "T"

def load_parameters_from_file(file_path):
    with open(file_path, "r") as json_file:
        parameters = json.load(json_file)
    return parameters

def select_parameters_folder():
    root = tk.Tk()
    root.withdraw()
    folder_path = filedialog.askdirectory(title="Select Parameters Folder")
    return folder_path

def select_files():
    root = tk.Tk()
    root.withdraw()
    file_paths = filedialog.askopenfilenames(title="Select Images to Decrypt", filetypes=[("Image files", "*.jpg;*.jpeg;*.png")])
    return file_paths

def split_into_rgb_channels(image):
    red = image[:,:,2]
    green = image[:,:,1]
    blue = image[:,:,0]
    return red, green, blue

def gen_chaos_seq(m, n):
    x, y, z = x0, y0, z0
    seq_x, seq_y, seq_z = [], [], []

    for _ in range(m * n):
        x, y, z = (
            a * (y - x),
            x * (b - z) - y,
            x * y - c * z
        )

        seq_x.append(x)
        seq_y.append(y)
        seq_z.append(z)

    return seq_x, seq_y, seq_z

def xor_operation(b, g, r, mk):
    m, n = b.shape
    bx = np.chararray((m, n))
    gx = np.chararray((m, n))
    rx = np.chararray((m, n))
    b = b.astype(str)
    g = g.astype(str)
    r = r.astype(str)
    for i in range(0, m):
        for j in range(0, n):
            key = "{0}{1}".format(b[i, j], mk[i, j])
            bx[i, j] = dna[key] if key in dna else key

            key = "{0}{1}".format(g[i, j], mk[i, j])
            gx[i, j] = dna[key] if key in dna else key

            key = "{0}{1}".format(r[i, j], mk[i, j])
            rx[i, j] = dna[key] if key in dna else key

    bx = bx.astype(str)
    gx = gx.astype(str)
    rx = rx.astype(str)
    return bx, gx, rx

def sequence_indexing(x, y, z):
    n = len(x)
    fx = np.zeros((n), dtype=np.uint32)
    fy = np.zeros((n), dtype=np.uint32)
    fz = np.zeros((n), dtype=np.uint32)
    seq = sorted(x)

    for k1 in range(n):
        t = x[k1]
        k2 = np.searchsorted(seq, t)
        fx[k1] = k2

    seq = sorted(y)
    for k1 in range(n):
        t = y[k1]
        k2 = np.searchsorted(seq, t)
        fy[k1] = k2

    seq = sorted(z)
    for k1 in range(n):
        t = z[k1]
        k2 = np.searchsorted(seq, t)
        fz[k1] = k2

    return fx, fy, fz

def decompose_matrix(iname):
    image = cv2.imread(iname)  # image will contain in BGR sequence

    if image is None:
        print(f"Error: Unable to read image from {iname}")
        return None, None, None

    blue, green, red = cv2.split(image)  # image data will be split into blue, green, red channels

    B = np.asmatrix(blue)
    G = np.asmatrix(green)
    R = np.asmatrix(red)

    return B, G, R

def scramble(fx, fy, fz, b, r, g):
    p, q = b.shape
    size = p * q
    bx = b.reshape(size).astype(str)
    gx = g.reshape(size).astype(str)
    rx = r.reshape(size).astype(str)
    bx_s = np.chararray((size))
    gx_s = np.chararray((size))
    rx_s = np.chararray((size))
    for i in range(size):
        idx = fz[i]
        bx_s[i] = bx[idx]
    for i in range(size):
        idx = fy[i]
        gx_s[i] = gx[idx]
    for i in range(size):
        idx = fx[i]
        rx_s[i] = rx[idx]
    bx_s = bx_s.astype(str)
    gx_s = gx_s.astype(str)
    rx_s = rx_s.astype(str)
    b_s = np.chararray((p, q))
    g_s = np.chararray((p, q))
    r_s = np.chararray((p, q))
    b_s = bx_s.reshape(p, q)
    g_s = gx_s.reshape(p, q)
    r_s = rx_s.reshape(p, q)
    return b_s, g_s, r_s

def dna_decode(b, g, r):
    m, n = b.shape
    r_dec = np.zeros((m, int(n * 2)), dtype=np.uint8)
    g_dec = np.zeros((m, int(n * 2)), dtype=np.uint8)
    b_dec = np.zeros((m, int(n * 2)), dtype=np.uint8)
    for color, dec in zip((b, g, r), (b_dec, g_dec, r_dec)):
        for j in range(0, m):
            for i in range(0, n):
                key = str(color[j, i])
                if key in dna:
                    dec[j, 2 * i] = dna[key][0]
                    dec[j, 2 * i + 1] = dna[key][1]
                else:
                    print(f"Key Error: '{key}' not found in dna dictionary.")
                    # You can handle this error as per your requirements
    b_dec = (np.packbits(b_dec, axis=-1))[:, :n]  # Trim the decoded matrix to the original size
    g_dec = (np.packbits(g_dec, axis=-1))[:, :n]
    r_dec = (np.packbits(r_dec, axis=-1))[:, :n]
    return b_dec, g_dec, r_dec

def recover_image(b, g, r, iname):
    img = cv2.imread(iname)
    if img.shape[:2] != b.shape:
        print("Error: Decoded matrix size does not match the original image size.")
        return None
    
    img[:, :, 2] = r
    img[:, :, 1] = g
    img[:, :, 0] = b
    file_name, file_extension = os.path.splitext(os.path.basename(iname))
    decrypted_file_path = os.path.join(ENCRYPTED_FOLDER, f"{file_name}_decrypted{file_extension}")
    cv2.imwrite(decrypted_file_path, img)
    print(f"Saved decrypted image as {decrypted_file_path}")
    return img

def decryption_process(file_name, parameters):
    key = parameters["key"]
    fx = np.array(parameters["fx"])
    fy = np.array(parameters["fy"])
    fz = np.array(parameters["fz"])
    Mk_e = np.array(parameters["Mk_e"])
    counter = parameters["counter"]

    blue, green, red = decompose_matrix(file_name)

    if blue is None or green is None or red is None:
        print("Error: Decomposition failed. Check the image file.")
        return
    
    print(f"Blue shape: {blue.shape}, Green shape: {green.shape}, Red shape: {red.shape}")

    blue_e, green_e, red_e = xor_operation(blue, green, red, Mk_e)
    x, y, z = gen_chaos_seq(blue.shape[0], blue.shape[1])
    fx, fy, fz = sequence_indexing(x, y, z)
    blue_scrambled, green_scrambled, red_scrambled = scramble(fx, fy, fz, blue_e, red_e, green_e)
    b, g, r = dna_decode(blue_scrambled, green_scrambled, red_scrambled)
    img = recover_image(b, g, r, file_name)
    print(f"Image decrypted: {file_name} in Thread {counter}")

def decrypt_and_reverse_operations(file_name, key, fx, fy, fz, Mk_e):
    blue, green, red = decompose_matrix(file_name)
    blue_e, green_e, red_e = xor_operation(blue, green, red, Mk_e)
    x, y, z = gen_chaos_seq(blue.shape[0], blue.shape[1])
    fx, fy, fz = sequence_indexing(x, y, z)
    blue_scrambled, green_scrambled, red_scrambled = scramble(fx, fy, fz, blue_e, red_e, green_e)
    b, g, r = dna_decode(blue_scrambled, green_scrambled, red_scrambled)
    return b, g, r

def decryption_process(file_name, parameters):
    key = parameters["key"]
    fx = np.array(parameters["fx"])
    fy = np.array(parameters["fy"])
    fz = np.array(parameters["fz"])
    Mk_e = np.array(parameters["Mk_e"])
    counter = parameters["counter"]

    blue, green, red = decompose_matrix(file_name)

    if blue is None or green is None or red is None:
        print("Error: Decomposition failed. Check the image file.")
        return
    
    print(f"Blue shape: {blue.shape}, Green shape: {green.shape}, Red shape: {red.shape}")

    blue_e, green_e, red_e = xor_operation(blue, green, red, Mk_e)
    x, y, z = gen_chaos_seq(blue.shape[0], blue.shape[1])
    fx, fy, fz = sequence_indexing(x, y, z)
    blue_scrambled, green_scrambled, red_scrambled = scramble(fx, fy, fz, blue_e, red_e, green_e)
    b, g, r = dna_decode(blue_scrambled, green_scrambled, red_scrambled)
    img = recover_image(b, g, r, file_name)
    print(f"Image decrypted: {file_name} in Thread {counter}")

if __name__ == "__main__":
    # Load parameters from data.json
    parameters_folder = select_parameters_folder()
    file_paths = select_files()

    for counter, file_path in enumerate(file_paths):
        # Fetch parameters based on the image name
        file_name, _ = os.path.splitext(os.path.basename(file_path))
        parameters_file_path = os.path.join(parameters_folder, f"{file_name}_parameters.json")

        if not os.path.exists(parameters_file_path):
            print(f"Error: Parameters file not found for {file_name}. Skipping decryption.")
            continue

        parameters = load_parameters_from_file(parameters_file_path)

        # Perform decryption for each selected image
        parameters["counter"] = counter
        decryption_process(file_path, parameters)

