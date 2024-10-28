# Image Encryption and Decryption with Firebase

## Overview
This project is designed for encrypting and decrypting images using DNA-based encoding techniques. The encrypted data, along with necessary parameters, is uploaded to Firebase Storage for secure storage. Users can later retrieve and decrypt the images using a password-protected process.

## Features
- **Image Encryption**: Encrypts images using a custom DNA-based encoding scheme.
- **Image Decryption**: Decrypts images using parameters stored in Firebase.
- **Firebase Integration**: Uploads and retrieves files securely using Firebase Storage.
- **User-friendly Interface**: Utilizes PyQt5 to provide a graphical interface for error notifications.

## Technologies Used
- Python
- OpenCV (for image processing)
- NumPy (for numerical operations)
- Firebase Admin SDK (for interacting with Firebase Storage)
- PyQt5 (for GUI dialogs)

## Prerequisites
- Python 3.x
- Required Python packages:
  - `numpy`
  - `opencv-python`
  - `firebase-admin`
  - `PyQt5`
  
You can install the required packages using pip:
```bash
pip install numpy opencv-python firebase-admin PyQt5
