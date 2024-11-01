import sys
import subprocess
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QFileDialog, QLineEdit, QLabel, QDialog
from PyQt5.QtGui import QMovie
from PyQt5.QtCore import QObject, QThread, pyqtSignal, QTimer
from PyQt5.uic import loadUi
import json
import os
import time

class PasswordDialog(QDialog):
    def __init__(self, image_name, parent=None):
        super().__init__(parent)
        self.image_name = image_name
        self.setWindowTitle(f"Enter Password for {image_name}")
        self.setGeometry(100, 100, 400, 150)
        self.label = QLabel(f"Enter password for {image_name}:", self)
        self.password_edit = QLineEdit(self)
        self.ok_button = QPushButton('OK', self)
        self.cancel_button = QPushButton('Cancel', self)
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        self.setStyleSheet("QDialog { background-color: #f5f5f5; }"
                           "QLabel { font-size: 14px; }"
                           "QLineEdit { background-color: #ffffff; font-size: 14px; border: 1px solid #dcdcdc; padding: 3px; }"
                           "QPushButton { background-color: #4CAF50; color: white; border: none; padding: 5px 10px; font-size: 14px; }"
                           "QPushButton:hover { background-color: #45a049; }")
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.password_edit)
        layout.addWidget(self.ok_button)
        layout.addWidget(self.cancel_button)
        self.setLayout(layout)

    def get_password(self):
        return self.password_edit.text()

class Worker(QObject):
    show_tick = pyqtSignal()

    def __init__(self):
        super().__init__()

    def run(self):
        while True:
            if os.path.exists('System/Frontend/signal_hide_label.txt'):
                self.show_tick.emit()
                os.remove('System/Frontend/signal_hide_label.txt')
            time.sleep(1)

class ImageEncryptionApp(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi('System/Frontend/load_ui.ui', self)

        encrypt_button = self.findChild(QPushButton, 'encrypt')
        encrypt_button.clicked.connect(self.show_folder_dialog)

        decrypt_button = self.findChild(QPushButton, 'decrypt')
        decrypt_button.clicked.connect(self.run_decrypt_window)

        self.passwords_array = []

        self.gif_label = self.findChild(QLabel, 'gif')
        if self.gif_label:
            self.hide_gif_label()

        self.tick = self.findChild(QLabel, 'tick')
        if self.tick:
            self.hide_tick()

        self.worker = Worker()
        self.worker_thread = QThread()

        self.worker.moveToThread(self.worker_thread)
        self.worker.show_tick.connect(self.load_and_display_tick)
        self.worker_thread.started.connect(self.worker.run)
        self.worker_thread.start()

        self.encryption_process = None
        self.decryption_process = None
        self.tick_movie = None

    def show_folder_dialog(self):
        folder_path = QFileDialog.getExistingDirectory(self, 'Select Folder Containing Images')

        if folder_path:
            image_files = [f for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
            for image_file in image_files:
                password = self.get_password(image_file)
                if password:
                    self.passwords_array.append((image_file, password))

            passwords_json = json.dumps(self.passwords_array)

            # Update the paths to encr.py and upload.py
            encr_path = os.path.join('System', 'Encryption', 'encr.py')
            upload_path = os.path.join('System', 'Encryption', 'upload.py')

            self.encryption_process = subprocess.Popen(['python', encr_path, folder_path, passwords_json])

            # Show giphy.gif while encr.py is running
            self.load_and_display_gif()

            # Check for encryption process completion periodically
            QTimer.singleShot(1000, self.check_encryption_completion)

    def check_encryption_completion(self):
        if self.encryption_process and self.encryption_process.poll() is not None:
            # Encryption process has completed
            self.hide_gif_label()
        else:
            # Encryption process is still running, check again after 1 second
            QTimer.singleShot(1000, self.check_encryption_completion)

    def load_and_display_gif(self):
        if self.gif_label:
            self.gif_label.show()
            movie = QMovie('System/Frontend/giphy.gif')
            self.gif_label.setMovie(movie)
            movie.start()

    def hide_gif_label(self):
        if self.gif_label:
            self.gif_label.hide()

            # Show and play tick.gif for 2 times
            self.load_and_display_tick()

    def load_and_display_tick(self):
        if self.tick:
            self.tick.show()
            self.tick_movie = QMovie('System/Frontend/tick.gif')
            self.tick.setMovie(self.tick_movie)
            self.tick_movie.start()

    def hide_tick(self):
        if self.tick_movie:
            self.tick_movie.stop()
            self.tick_movie.deleteLater()
            self.tick_movie = None
            self.tick.hide()

    def run_decrypt_window(self):
        self.hide_tick()
        self.hide_gif_label()

        # Update the path to decryptwindow.py
        # decrypt_path = os.path.join('System', 'Decryption', 'decryptwindow.py')
        decrypt_path = "C:/Projects/MIE/System/Decryption/decryptwindow.py"
        self.decryption_process = subprocess.Popen(['python', decrypt_path])

        # Show giphy.gif while decryptwindow.py is running
        self.load_and_display_gif()

        # Check for decryption process completion periodically
        QTimer.singleShot(1000, self.check_decryption_completion)

    def check_decryption_completion(self):
        if self.decryption_process and self.decryption_process.poll() is not None:
            # Decryption process has completed
            self.hide_gif_label()
            # Show and play tick.gif for 10 seconds
            self.load_and_display_tick()
            QTimer.singleShot(10000, self.hide_tick)
        else:
            # Decryption process is still running, check again after 1 second
            QTimer.singleShot(1000, self.check_decryption_completion)

    def get_password(self, image_file):
        password_dialog = PasswordDialog(image_file, self)
        result = password_dialog.exec_()
        if result == QDialog.Accepted:
            return password_dialog.get_password()
        else:
            return None

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ImageEncryptionApp()
    window.showMaximized()
    sys.exit(app.exec_())
