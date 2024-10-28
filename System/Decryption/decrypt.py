import numpy as np
import cv2
import json
import sys
import firebase_admin
from firebase_admin import credentials, storage
import json
import os
from PyQt5.QtWidgets import QApplication, QMessageBox

cred = credentials.Certificate("C:/Users/Videep/OneDrive/Documents/Firebase Key/key.json")
firebase_admin.initialize_app(cred)

bucket = storage.bucket(name='mie-p-a6e9f.appspot.com')

dna={}
dna["00"]="A"
dna["01"]="T"
dna["10"]="G"
dna["11"]="C"
dna["A"]=[0,0]
dna["T"]=[0,1]
dna["G"]=[1,0]
dna["C"]=[1,1]
#DNA xor
dna["AA"]=dna["TT"]=dna["GG"]=dna["CC"]="A"
dna["AG"]=dna["GA"]=dna["TC"]=dna["CT"]="G"
dna["AC"]=dna["CA"]=dna["GT"]=dna["TG"]="C"
dna["AT"]=dna["TA"]=dna["CG"]=dna["GC"]="T"
# Maximum time point and total number of time points
tmax, N = 100, 10000

def decrypt(image, fx, fy, fz, Mk, rt):
    r, g, b = split_into_rgb_channels(image)
    benc, genc, renc = dna_encode(b, g, r)
    bs, gs, rs = scramble_new(fx, fy, fz, benc, genc, renc)
    bx, rx, gx = xor_operation_new(bs, gs, rs, Mk)
    blue, green, red = dna_decode(bx, gx, rx)
    green, red = red, green
    img = np.zeros_like(image)
    img[:, :, 0] = red
    img[:, :, 1] = green
    img[:, :, 2] = blue
    return img

def split_into_rgb_channels(image):
    red = image[:, :, 2]
    green = image[:, :, 1]
    blue = image[:, :, 0]
    return red, green, blue

def dna_encode(b, g, r):
    b = np.unpackbits(b, axis=1)
    g = np.unpackbits(g, axis=1)
    r = np.unpackbits(r, axis=1)
    m, n = b.shape
    r_enc = np.chararray((m, int(n/2)))
    g_enc = np.chararray((m, int(n/2)))
    b_enc = np.chararray((m, int(n/2)))

    for color, enc in zip((b, g, r), (b_enc, g_enc, r_enc)):
        idx = 0
        for j in range(0, m):
            for i in range(0, n, 2):
                enc[j, idx] = dna["{0}{1}".format(color[j, i], color[j, i+1])]
                idx += 1
                if i == n-2:
                    idx = 0
                    break

    b_enc = b_enc.astype(str)
    g_enc = g_enc.astype(str)
    r_enc = r_enc.astype(str)
    return b_enc, g_enc, r_enc

def scramble_new(fx, fy, fz, b, g, r):
    p, q = b.shape
    size = p * q
    bx = b.reshape(size)
    gx = g.reshape(size)
    rx = r.reshape(size)

    bx_s = b.reshape(size)
    gx_s = g.reshape(size)
    rx_s = r.reshape(size)

    bx = bx.astype(str)
    gx = gx.astype(str)
    rx = rx.astype(str)
    bx_s = bx_s.astype(str)
    gx_s = gx_s.astype(str)
    rx_s = rx_s.astype(str)

    for i in range(size):
        idx = fz[i]
        bx_s[idx] = bx[i]
    for i in range(size):
        idx = fy[i]
        gx_s[idx] = gx[i]
    for i in range(size):
        idx = fx[i]
        rx_s[idx] = rx[i]

    b_s = np.chararray((p, q))
    g_s = np.chararray((p, q))
    r_s = np.chararray((p, q))

    b_s = bx_s.reshape(p, q)
    g_s = gx_s.reshape(p, q)
    r_s = rx_s.reshape(p, q)

    return b_s, g_s, r_s

def xor_operation_new(b, g, r, mk):
    m, n = b.shape
    bx = np.chararray((m, n))
    gx = np.chararray((m, n))
    rx = np.chararray((m, n))
    b = b.astype(str)
    g = g.astype(str)
    r = r.astype(str)
    for i in range(0, m):
        for j in range(0, n):
            bx[i, j] = dna["{0}{1}".format(b[i, j], mk[i, j])]
            gx[i, j] = dna["{0}{1}".format(g[i, j], mk[i, j])]
            rx[i, j] = dna["{0}{1}".format(r[i, j], mk[i, j])]

    bx = bx.astype(str)
    gx = gx.astype(str)
    rx = rx.astype(str)
    return bx, gx, rx

def dna_decode(b, g, r):
    m, n = b.shape
    r_dec = np.ndarray((m, int(n*2)), dtype=np.uint8)
    g_dec = np.ndarray((m, int(n*2)), dtype=np.uint8)
    b_dec = np.ndarray((m, int(n*2)), dtype=np.uint8)
    for color, dec in zip((b, g, r), (b_dec, g_dec, r_dec)):
        for j in range(0, m):
            for i in range(0, n):
                dec[j, 2*i] = dna["{0}".format(color[j, i])][0]
                dec[j, 2*i+1] = dna["{0}".format(color[j, i])][1]
    b_dec = np.packbits(b_dec, axis=-1)
    g_dec = np.packbits(g_dec, axis=-1)
    r_dec = np.packbits(r_dec, axis=-1)
    return b_dec, g_dec, r_dec

def load_encryption_info(json_file):
    with open(json_file, 'r') as f:
        data = json.load(f)
        fx = np.array(data['fx'])
        fy = np.array(data['fy'])
        fz = np.array(data['fz'])
        Mk_e = np.array(data['Mk_e'])
        red = np.array(data['red'])

    return fx, fy, fz, Mk_e, red

def download_file_from_storage(file_name, destination_path):
    blob = bucket.blob(file_name)
    if not blob.exists():
        return False

    blob.download_to_filename(destination_path)
    print(f"File downloaded to {destination_path}")
    return True

def decrypt_image(image_path, json_file, output_folder):
    image = cv2.imread(image_path)
    fx, fy, fz, Mk_e, red = load_encryption_info(json_file)
    
    decrypted_image = decrypt(image, fx, fy, fz, Mk_e, red)

    original_filename, _ = os.path.splitext(os.path.basename(image_path))
    os.makedirs(output_folder, exist_ok=True)

    decrypted_image_path = os.path.join(output_folder, f"{original_filename}.jpg")
    
    if not np.all(decrypted_image == 0):
        cv2.imwrite(decrypted_image_path, decrypted_image)
        print(f"Decrypted image saved to: {decrypted_image_path}")
    else:
        print("Decryption failed. The decrypted image is empty.")
    
    #removing the password.json file from Firebase
    password_file = f"{original_filename}.json"
    delete_file_from_storage(password_file)

def delete_file_from_storage(file_name):
    blob = bucket.blob(file_name)
    if blob.exists():
        blob.delete()
        print(f"{file_name} deleted from Firebase storage.")
    else:
        print(f"{file_name} does not exist in Firebase storage.")

if __name__ == "__main__":
    if len(sys.argv) > 2:
        password = sys.argv[1]
        image_path = sys.argv[2]
        output_folder = "C:/Projects/MIE/Decrypted Images"
        password_file = f"{password}.json"
        
        if download_file_from_storage(password_file, "parameters.json"):
            decrypt_image(image_path, "parameters.json", output_folder)
            os.remove("parameters.json")
            with open('signal_hidea_label.txt', 'w') as signal_file:
                signal_file.write('hide_label')
            with open('completed.txt', 'w') as signal_file:
                signal_file.write('completed')
            delete_file_from_storage(password_file)
        else:
            app = QApplication(sys.argv)
            msg = QMessageBox()
            msg.setWindowTitle("Invalid Password")
            msg.setText("The password provided is invalid.")
            msg.setIcon(QMessageBox.Warning)
            msg.exec_()
            sys.exit(0)
