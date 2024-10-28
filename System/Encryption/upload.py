import firebase_admin
from firebase_admin import credentials, storage
import os
import sys

def initialize_firebase_app(credential_path):
    cred = credentials.Certificate(credential_path)
    firebase_admin.initialize_app(cred, {'storageBucket': 'mie-p-a6e9f.appspot.com'})

def upload_to_firebase(json_file_path, output_path, bucket_name):
    bucket = storage.bucket(name=bucket_name)
    blob = bucket.blob(os.path.basename(json_file_path))

    blob.upload_from_filename(json_file_path)

    print(f"Uploaded {json_file_path} to Firebase Storage.")

    os.remove(json_file_path)

if __name__ == "__main__":
    if len(sys.argv) > 2:
        #The JSON file path and output path are command-line arguments
        json_file_path = sys.argv[1]
        output_path = sys.argv[2]

        credential_path = "C:/Users/Videep/OneDrive/Documents/Firebase Key/key.json"
        initialize_firebase_app(credential_path)

        bucket_name = 'mie-p-a6e9f.appspot.com' 

        upload_to_firebase(json_file_path, output_path, bucket_name)
    else:
        print("Please provide the JSON file path and output path as command-line arguments.")
