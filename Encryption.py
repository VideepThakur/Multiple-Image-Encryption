from PIL import Image #used for image data in line 6
import tkinter as tk #for dialog boxes 324
from tkinter import filedialog
import hashlib 
import textwrap #used for breaking hexadecimal key into small parts
import cv2 #decomposing into blue green red
import numpy as np
from scipy.integrate import odeint  #for chaotic sequences
import matplotlib.pyplot as plt 
from bisect import bisect_left as bsearch #indexing sequences generated from chaotic data
import threading
import os
import json

ENCRYPTED_FOLDER = r'C:/Users/Videep/OneDrive/Desktop/Image Encryption/Encrypted'

# Lorenz paramters
a, b, c = 10, 2.667, 28
x0, y0, z0 = 0, 0, 0
tmax, N = 100, 10000 #max time point for generating chaotic sequence,no of points used in integeration of lorenz equations

def lorenz(X, t, a, b, c):
    x, y, z = X
    x_dot = -a*(x - y)
    y_dot = c*x - y - x*z
    z_dot = -b*z + x*y
    return x_dot, y_dot, z_dot

def split_into_rgb_channels(image):
  red = image[:,:,2]
  green = image[:,:,1]
  blue = image[:,:,0]
  return red, green, blue

def image_selector():                           
    path = "NULL"
    root = tk.Tk()
    root.withdraw()                            
    path = filedialog.askopenfilename()         
    if path!="NULL":
        print("Image loaded!") 
    else:
        print("Error Image not loaded!")
    return path

def securekey (iname):
    img = Image.open(iname)                     #creating a image object
    m, n = img.size                             #width and height
    print("pixels: {0}  width: {2} height: {1} ".format(m*n, m, n))
    pix = img.load()                            #we will get pixel data        
    plainimage = list()                         #storing rgb values of each pixel                  
    for y in range(n):                          #height
        for x in range(m):                      #width
            for k in range(0,3):                #rgb channels
                plainimage.append(pix[x,y][k])  #for every pixel rgb values are retrieved 
    key = hashlib.sha256()                      #hashfunction                   
    key.update(bytearray(plainimage))           #rgb values are updated in plainimage       
    return key.hexdigest() ,m ,n                #hexadecimal key 

def update_lorentz (key):
    key_bin = bin(int(key, 16))[2:].zfill(256)  #converts hexadecimal to binary
    k={}                                        
    key_32_parts=textwrap.wrap(key_bin, 8)  #break into 32 parts each 8 size   
    num=1
    for i in key_32_parts:
        k["k{0}".format(num)]=i  
        num = num + 1
    t1 = t2 = t3 = 0
    for i in range (1,12): #xor of t1 with first 11 parts k1 to k11
        t1=t1^int(k["k{0}".format(i)],2)  
    for i in range (12,23):
        t2=t2^int(k["k{0}".format(i)],2)
    for i in range (23,33):
        t3=t3^int(k["k{0}".format(i)],2)   
    global x0 ,y0, z0
    x0=x0 + t1/256            
    y0=y0 + t2/256            
    z0=z0 + t3/256            

def decompose_matrix(iname):
    image = cv2.imread(iname)#image will contain in bgr sequence
    blue,green,red = split_into_rgb_channels(image) #image data will be splitted into blue green red channels
    for values, channel in zip((red, green, blue), (2,1,0)):
        img = np.zeros((values.shape[0], values.shape[1]), dtype = np.uint8)#empty block img will be created with the size same as the channel being processed
        img[:,:] = (values)
        if channel == 0:
            B = np.asmatrix(img)
        elif channel == 1:
            G = np.asmatrix(img)
        else:
            R = np.asmatrix(img)
    return B,G,R

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
dna["AT"]=dna["TA"]=dna["CG"]=dna["GC"]="T"
dna["AC"]=dna["CA"]=dna["GT"]=dna["TG"]="C"
dna["AG"]=dna["GA"]=dna["TC"]=dna["CT"]="G"

def dna_encode(b,g,r):
    
    b = np.unpackbits(b,axis=1)#converts pixel to binary
    g = np.unpackbits(g,axis=1)
    r = np.unpackbits(r,axis=1)
    m,n = b.shape
    r_enc= np.chararray((m,int(n/2)))# these contain a c t g values of corresponding binary 
    g_enc= np.chararray((m,int(n/2)))
    b_enc= np.chararray((m,int(n/2)))
    
    for color,enc in zip((b,g,r),(b_enc,g_enc,r_enc)):
        idx=0
        for j in range(0,m):
            for i in range(0,n,2):
                enc[j,idx]=dna["{0}{1}".format(color[j,i],color[j,i+1])]
                idx+=1
                if (i==n-2):
                    idx=0
                    break
    
    b_enc=b_enc.astype(str)
    g_enc=g_enc.astype(str)
    r_enc=r_enc.astype(str)
    return b_enc,g_enc,r_enc

def key_matrix_encode(key,b):    
    #encoded key matrix
    b = np.unpackbits(b,axis=1)
    m,n = b.shape
    key_bin = bin(int(key, 16))[2:].zfill(256)
    Mk = np.zeros((m,n),dtype=np.uint8)
    x=0
    for j in range(0,m):
            for i in range(0,n):
                Mk[j,i]=key_bin[x%256]
                x+=1
    
    Mk_enc=np.chararray((m,int(n/2)))
    idx=0
    for j in range(0,m):
        for i in range(0,n,2):
            if idx==(n/2):
                idx=0
            Mk_enc[j,idx]=dna["{0}{1}".format(Mk[j,i],Mk[j,i+1])]
            idx+=1
    Mk_enc=Mk_enc.astype(str)
    return Mk_enc

def xor_operation(b,g,r,mk):
    m,n = b.shape
    bx=np.chararray((m,n))
    gx=np.chararray((m,n))
    rx=np.chararray((m,n))
    b=b.astype(str)
    g=g.astype(str)
    r=r.astype(str)
    for i in range(0,m):
        for j in range (0,n):
            bx[i,j] = dna["{0}{1}".format(b[i,j],mk[i,j])]
            gx[i,j] = dna["{0}{1}".format(g[i,j],mk[i,j])]
            rx[i,j] = dna["{0}{1}".format(r[i,j],mk[i,j])]
         
    bx=bx.astype(str)
    gx=gx.astype(str)
    rx=rx.astype(str)
    return bx,gx,rx 

def gen_chaos_seq(m,n):
    global x0,y0,z0,a,b,c,N
    N=m*n*4
    x= np.array((m,n*4))
    y= np.array((m,n*4))
    z= np.array((m,n*4))
    t = np.linspace(0, tmax, N)
    f = odeint(lorenz, (x0, y0, z0), t, args=(a, b, c))
    x, y, z = f.T
    x=x[:(N)]
    y=y[:(N)]
    z=z[:(N)]
    return x,y,z

def plot(x,y,z):
    fig = plt.figure()
    ax = fig.gca(projection='3d')
    s = 100
    c = np.linspace(0,1,N)
    for i in range(0,N-s,s):
        ax.plot(x[i:i+s+1], y[i:i+s+1], z[i:i+s+1], color=(1-c[i],c[i],1), alpha=0.4)
    ax.set_axis_off()
    plt.show()

def sequence_indexing(x,y,z):
    n=len(x)
    fx=np.zeros((n),dtype=np.uint32)
    fy=np.zeros((n),dtype=np.uint32)
    fz=np.zeros((n),dtype=np.uint32)
    seq=sorted(x)
    for k1 in range(0,n):
            t = x[k1]
            k2 = bsearch(seq, t)
            fx[k1]=k2
    seq=sorted(y)
    for k1 in range(0,n):
            t = y[k1]
            k2 = bsearch(seq, t)
            fy[k1]=k2
    seq=sorted(z)
    for k1 in range(0,n):
            t = z[k1]
            k2 = bsearch(seq, t)
            fz[k1]=k2
    return fx,fy,fz
        
def scramble(fx,fy,fz,b,r,g):
    p,q=b.shape
    size = p*q
    bx=b.reshape(size).astype(str)
    gx=g.reshape(size).astype(str)
    rx=r.reshape(size).astype(str)
    bx_s=np.chararray((size))
    gx_s=np.chararray((size))
    rx_s=np.chararray((size))

    for i in range(size):
            idx = fz[i]
            bx_s[i] = bx[idx]
    for i in range(size):
            idx = fy[i]
            gx_s[i] = gx[idx]
    for i in range(size):
            idx = fx[i]
            rx_s[i] = rx[idx]     
    bx_s=bx_s.astype(str)
    gx_s=gx_s.astype(str)
    rx_s=rx_s.astype(str)
    
    b_s=np.chararray((p,q))
    g_s=np.chararray((p,q))
    r_s=np.chararray((p,q))

    b_s=bx_s.reshape(p,q)
    g_s=gx_s.reshape(p,q)
    r_s=rx_s.reshape(p,q)
    return b_s,g_s,r_s

def dna_decode(b,g,r):
    m,n = b.shape
    r_dec= np.ndarray((m,int(n*2)),dtype=np.uint8)
    g_dec= np.ndarray((m,int(n*2)),dtype=np.uint8)
    b_dec= np.ndarray((m,int(n*2)),dtype=np.uint8)
    for color,dec in zip((b,g,r),(b_dec,g_dec,r_dec)):
        for j in range(0,m):
            for i in range(0,n):
                dec[j,2*i]=dna["{0}".format(color[j,i])][0]
                dec[j,2*i+1]=dna["{0}".format(color[j,i])][1]
    b_dec=(np.packbits(b_dec,axis=-1))
    g_dec=(np.packbits(g_dec,axis=-1))
    r_dec=(np.packbits(r_dec,axis=-1))
    return b_dec,g_dec,r_dec

def recover_image(b, g, r, iname, counter):
    img = cv2.imread(iname)
    img[:,:,2] = r
    img[:,:,1] = g
    img[:,:,0] = b
     # Extract the filename and extension from the original image path
    file_name, file_extension = os.path.splitext(os.path.basename(iname))
    
    # Create the folder for encrypted images if it doesn't exist
    os.makedirs(ENCRYPTED_FOLDER, exist_ok=True)
    
    # Save the encrypted image with the original filename
    encrypted_file_path = os.path.join(ENCRYPTED_FOLDER, f"{file_name}_encrypted{file_extension}")
    cv2.imwrite(encrypted_file_path, img)
    
    print(f"Saved encrypted image as {encrypted_file_path}")
    return img    

def process_image(file_path, counter):    
    key, m, n = securekey(file_path)
    update_lorentz(key)
    blue, green, red = decompose_matrix(file_path)
    blue_e, green_e, red_e = dna_encode(blue, green, red)
    Mk_e = key_matrix_encode(key, blue)
    blue_final, green_final, red_final = xor_operation(blue_e, green_e, red_e, Mk_e)
    x, y, z = gen_chaos_seq(m, n)
    fx, fy, fz = sequence_indexing(x, y, z)
    blue_scrambled, green_scrambled, red_scrambled = scramble(fx, fy, fz, blue_final, red_final, green_final)
    b, g, r = dna_decode(blue_scrambled, green_scrambled, red_scrambled)
    img = recover_image(b, g, r, file_path, counter)
    print(f"Image encrypted in Thread {counter}")
    save_parameters_for_decryption(file_path, key, fx, fy, fz, Mk_e, counter)

    return img

def process_images_in_folder(folder_path):
    threads = []
    counter = 0
    for file_name in os.listdir(folder_path): #for iterating
        file_path = os.path.join(folder_path, file_name) #creating full path for each image
        if os.path.isfile(file_path) and file_name.lower().endswith(('.jpg', '.jpeg', '.png')):
            thread = threading.Thread(target=process_image, args=(file_path, counter))
            threads.append(thread)
            counter += 1
    
    for thread in threads:
        thread.start() #starting all threads
    
    for thread in threads:
        thread.join() #wait for all threads to complete

def select_folder():
    root = tk.Tk() #creating a tkinter window
    root.withdraw() #creating a pop-up dialog box
    folder_path = filedialog.askdirectory(title="Select Folder")
    return folder_path

def save_parameters_for_decryption(file_path, key, fx, fy, fz, Mk_e, counter):
    parameters = {
        "file_path": file_path,
        "key": key,
        "fx": fx.tolist(),
        "fy": fy.tolist(),
        "fz": fz.tolist(),
        "Mk_e": Mk_e.tolist(),
        "counter": counter
    }

    # Extract the filename and extension from the original image path
    file_name, _ = os.path.splitext(os.path.basename(file_path))

    # Create a folder to store individual parameter files if it doesn't exist
    parameters_folder = "parameters"
    os.makedirs(parameters_folder, exist_ok=True)

    # Save the parameters to a separate JSON file for each image
    json_filename = os.path.join(parameters_folder, f"{file_name}_parameters.json")
    with open(json_filename, "w") as json_file:
        json.dump(parameters, json_file)

    print(f"Saved parameters for decryption as {json_filename}")

if __name__ == "__main__": #to check whether main is running or not
    folder_path = select_folder()
    process_images_in_folder(folder_path)