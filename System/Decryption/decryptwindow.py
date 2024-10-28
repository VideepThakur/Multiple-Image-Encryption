import sys
import subprocess
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel, QLineEdit, QFileDialog

class ImageEncryptionWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Image Decryption")
        self.setGeometry(100, 100, 400, 200)

        layout = QVBoxLayout()

        self.label = QLabel("Select Encrypted Image:")
        layout.addWidget(self.label)

        self.button = QPushButton("Browse")
        self.button.clicked.connect(self.get_image_path)
        layout.addWidget(self.button)

        self.setStyleSheet("QDialog { background-color: #f5f5f5; }"
                           "QLabel { font-size: 14px; }"
                           "QLineEdit { background-color: #ffffff; font-size: 14px; border: 1px solid #dcdcdc; padding: 3px; }"
                           "QPushButton { background-color: #4CAF50; color: white; border: none; padding: 5px 10px; font-size: 14px; }"
                           "QPushButton:hover { background-color: #45a049; }")

        self.password_label = QLabel("Enter Password:")
        layout.addWidget(self.password_label)

        self.password_edit = QLineEdit()
        layout.addWidget(self.password_edit)

        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.retrieve_password)
        layout.addWidget(self.ok_button)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def get_image_path(self):
        options = QFileDialog.Options()
        encrypted_image_path, _ = QFileDialog.getOpenFileName(self, "Select Encrypted Image", "", "Images (*.png *.jpg *.jpeg *.bmp *.gif)", options=options)
        if encrypted_image_path:
            print("Selected Encrypted Image Path:", encrypted_image_path)
            self.encrypted_image_path = encrypted_image_path

    def retrieve_password(self):
        password = self.password_edit.text()
        print("Entered Password:", password)
        if hasattr(self, 'encrypted_image_path'):
            print("Password and Image Path:", password, self.encrypted_image_path)
            self.run_decryption_script(password, self.encrypted_image_path)
        else:
            print("Please select an encrypted image first.")

    def run_decryption_script(self, password, image_path):
        decrypt_script_path = "C:/Projects/MIE/System/Decryption/decrypt.py"
        try:
            subprocess.run(["python", decrypt_script_path, password, image_path], check=True)
        except subprocess.CalledProcessError as e:
            print("Error running decryption script:", e)
        else:
            print("Decryption script executed successfully.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageEncryptionWindow()
    window.show()
    sys.exit(app.exec_())
