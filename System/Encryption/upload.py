import firebase_admin
from firebase_admin import credentials, storage
import os
import sys

def initialize_firebase_app(credential_path):
    cred = credentials.Certificate(credential_path)
    firebase_admin.initialize_app(cred, {'storageBucket': 'image-encryption-481f6.appspot.com'})

def upload_to_firebase(json_file_path, output_path, bucket_name):
    bucket = storage.bucket(name=bucket_name)
    blob = bucket.blob(os.path.basename(json_file_path))

    # Upload the JSON file to Firebase Storage
    blob.upload_from_filename(json_file_path)

    print(f"Uploaded {json_file_path} to Firebase Storage.")

    # Permanently delete the JSON file
    os.remove(json_file_path)

if __name__ == "__main__":
    # Modify the main block in upload.py
    if len(sys.argv) > 2:
        # The JSON file path and output path are passed as command-line arguments
        json_file_path = sys.argv[1]
        output_path = sys.argv[2]

        # Use the provided details
        credential_path = "C:/Users/Videep/OneDrive/Documents/image_encryption.json"
        initialize_firebase_app(credential_path)

        bucket_name = 'image-encryption-481f6.appspot.com' 

        upload_to_firebase(json_file_path, output_path, bucket_name)
    else:
        print("Please provide the JSON file path and output path as command-line arguments.")
