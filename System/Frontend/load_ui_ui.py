# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets, QtMultimedia, QtMultimediaWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1904, 844)
        font = QtGui.QFont()
        font.setFamily("Arial Black")
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        MainWindow.setFont(font)
        MainWindow.setStyleSheet("background-color:black;")
        MainWindow.setAnimated(True)
        
        # Add QVideoWidget for video playback
        self.videoWidget = QtMultimediaWidgets.QVideoWidget(MainWindow)
        self.videoWidget.setGeometry(QtCore.QRect(0, 0, 1904, 844))
        self.videoWidget.setObjectName("videoWidget")
        MainWindow.setCentralWidget(self.videoWidget)
        
        # Create media player
        self.mediaPlayer = QtMultimedia.QMediaPlayer(MainWindow)
        self.mediaPlayer.setVideoOutput(self.videoWidget)
        
        # Load video file (bg.mp4 in this case)
        videoFile = QtCore.QUrl.fromLocalFile("Background/bg.mp4")
        self.mediaPlayer.setMedia(QtMultimedia.QMediaContent(videoFile))
        
        # Start video playback
        self.mediaPlayer.play()
        error = self.mediaPlayer.error()
        if error != QtMultimedia.QMediaPlayer.NoError:
            print(f"Error: {self.mediaPlayer.errorString()}")
        
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.encrypt = QtWidgets.QPushButton(self.centralwidget)
        self.encrypt.setGeometry(QtCore.QRect(640, 310, 221, 61))
        font = QtGui.QFont()
        font.setFamily("Arial Black")
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.encrypt.setFont(font)
        self.encrypt.setStyleSheet("background-color:black;\n"
"border:3px solid white;\n"
"color:white;\n"
"")
        self.encrypt.setObjectName("encrypt")
        
        self.decrypt = QtWidgets.QPushButton(self.centralwidget)
        self.decrypt.setGeometry(QtCore.QRect(1000, 310, 221, 61))
        font = QtGui.QFont()
        font.setFamily("Arial Black")
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.decrypt.setFont(font)
        self.decrypt.setStyleSheet("background-color:black;\n"
"border:3px solid white;\n"
"color:white;\n"
"")
        self.decrypt.setObjectName("decrypt")
        
        self.gif = QtWidgets.QLabel(self.centralwidget)
        self.gif.setGeometry(QtCore.QRect(690, 390, 521, 211))
        self.gif.setText("")
        self.gif.setObjectName("gif")
        
        self.tick = QtWidgets.QLabel(self.centralwidget)
        self.tick.setGeometry(QtCore.QRect(530, 400, 691, 261))
        self.tick.setText("")
        self.tick.setObjectName("tick")
        
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1904, 26))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.encrypt.setText(_translate("MainWindow", "Encrypt"))
        self.decrypt.setText(_translate("MainWindow", "Decrypt"))

# Main application
if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
