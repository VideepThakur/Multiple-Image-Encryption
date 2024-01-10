import firebase_admin
from firebase_admin import credentials, storage

def initialize_firebase_app(credential_path):
    cred = credentials.Certificate(credential_path)
    firebase_admin.initialize_app(cred, {'storageBucket': 'image-encryption-481f6.appspot.com'})

def delete_all_files(bucket_name):
    bucket = storage.bucket(name=bucket_name)

    blobs = bucket.list_blobs()

    confirmation = input("Are you sure you want to delete all files in Firebase Storage? (Y/n): ").lower()
    if confirmation != 'y':
        print("Operation aborted.")
        return

    for blob in blobs:
        blob.delete()
        print(f"Deleted file: {blob.name}")

    print("All files deleted successfully.")

if __name__ == "__main__":
    credential_path = "C:/Users/Videep/Desktop/Multiple Image Encryption/Firebase Key/image_encryption.json"
    initialize_firebase_app(credential_path)

    bucket_name = 'image-encryption-481f6.appspot.com'  # Update with your bucket name

    delete_all_files(bucket_name)
