from __future__ import unicode_literals
import os
import webbrowser
from PyQt5 import QtWidgets, QtCore
import youtube_dl
from PyQt5.QtWidgets import QMainWindow, QMessageBox
from app.models.downloadvideothread import DownloadVideoThread
from app.models.github_api import GithubApi
from app.models.info_thread import Info_Thread
from app.models.sync_files_thread import SyncFilesThread


class MainWindow(QMainWindow):
    """
    Mainwindow where currently all interactions taking place

    """

    quality_info_items = []
    url = None
    files = []

    def __init__(self):
        """
        Initialize our object fields
        setting default values for the widgets and checks for updates at start

        """
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.completed_downloads_listWidget = self.findChild(QtWidgets.QListWidget, "completed_downloads_listWidget")
        self.current_download_label = self.findChild(QtWidgets.QLabel, "current_download_label")
        self.download_speed_label = self.findChild(QtWidgets.QLabel, "download_speed_label")
        self.download_size_label = self.findChild(QtWidgets.QLabel, "download_size_label")
        self.download_pushButton = self.findChild(QtWidgets.QPushButton, "download_pushButton")
        self.progressBar = self.findChild(QtWidgets.QProgressBar, "progressBar")
        self.quality_comboBox = self.findChild(QtWidgets.QComboBox, "quality_comboBox")
        self.video_url_lineEdit = self.findChild(QtWidgets.QLineEdit, "video_url_lineEdit")
        self.video_url_lineEdit.textChanged.connect(self.video_url_lineEdit_finished)
        self.download_pushButton.clicked.connect(self.download_pushButton_clicked)
        self.info_thread = Info_Thread()
        self.info_thread.add_quality_item.connect(self.add_quality_item)
        self.info_thread.finished.connect(self.info_thread_finished)
        self.sync_files_thread = SyncFilesThread()
        self.sync_files_thread.files.connect(self.sync_files)
        self.download_video_thread = DownloadVideoThread()
        self.download_video_thread.download_progress.connect(self.download_progress)
        self.download_video_thread.finished.connect(self.download_finished)
        self.progressBar.setValue(0)
        self.download_pushButton.setEnabled(False)
        self.completed_downloads_listWidget.itemDoubleClicked.connect(self.list_item_clicked)
        self.crawl_files()
        self.update_completed_download_list()
        self.github_api = GithubApi()
        if self.github_api.update_available() is True:
            QMessageBox.information(self, "Update verfügbar",
                                    "Es ist eine neue Version verfügbar: {0} <a href='{1}'>Zum Download</a>".format(
                                        self.github_api.last_release, self.github_api.release_url))
        self.sync_files_thread.start()

    def setupUi(self, MainWindow):
        """
        Initialize our widgets for the mainwindow

        :param MainWindow: the mainwindow
        :type MainWindow: MainWindow
        :return: None
        :rtype: None
        """
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1095, 738)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(10, 20, 301, 17))
        self.label.setObjectName("label")
        self.video_url_lineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.video_url_lineEdit.setGeometry(QtCore.QRect(10, 40, 461, 25))
        self.video_url_lineEdit.setObjectName("video_url_lineEdit")
        self.download_pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.download_pushButton.setGeometry(QtCore.QRect(10, 650, 151, 25))
        self.download_pushButton.setObjectName("download_pushButton")
        self.quality_comboBox = QtWidgets.QComboBox(self.centralwidget)
        self.quality_comboBox.setGeometry(QtCore.QRect(70, 80, 161, 25))
        self.quality_comboBox.setObjectName("quality_comboBox")
        self.progressBar = QtWidgets.QProgressBar(self.centralwidget)
        self.progressBar.setGeometry(QtCore.QRect(10, 600, 461, 23))
        self.progressBar.setProperty("value", 24)
        self.progressBar.setObjectName("progressBar")
        self.completed_downloads_listWidget = QtWidgets.QListWidget(self.centralwidget)
        self.completed_downloads_listWidget.setGeometry(QtCore.QRect(10, 140, 1061, 411))
        self.completed_downloads_listWidget.setObjectName("completed_downloads_listWidget")
        self.current_download_label = QtWidgets.QLabel(self.centralwidget)
        self.current_download_label.setGeometry(QtCore.QRect(10, 570, 1051, 17))
        self.current_download_label.setObjectName("current_download_label")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(10, 80, 61, 20))
        self.label_2.setObjectName("label_2")
        self.current_download_label_2 = QtWidgets.QLabel(self.centralwidget)
        self.current_download_label_2.setGeometry(QtCore.QRect(10, 120, 1051, 17))
        self.current_download_label_2.setObjectName("current_download_label_2")
        self.download_speed_label = QtWidgets.QLabel(self.centralwidget)
        self.download_speed_label.setGeometry(QtCore.QRect(480, 600, 101, 17))
        self.download_speed_label.setObjectName("download_speed_label")
        self.download_size_label = QtWidgets.QLabel(self.centralwidget)
        self.download_size_label.setGeometry(QtCore.QRect(570, 600, 101, 17))
        self.download_size_label.setObjectName("download_size_label")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1095, 22))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "PyQt_YTDownloader"))
        self.label.setText(_translate("MainWindow", "Video-URL"))
        self.download_pushButton.setText(_translate("MainWindow", "Download"))
        self.current_download_label.setText(_translate("MainWindow", ""))
        self.label_2.setText(_translate("MainWindow", "Qualität"))
        self.current_download_label_2.setText(_translate("MainWindow", "Videos:"))
        self.download_speed_label.setText(_translate("MainWindow", ""))
        self.download_size_label.setText(_translate("MainWindow", ""))

    def crawl_files(self):
        if os.path.isdir(os.curdir + '/PyQt_YTDownloader_Videos') is False:
            os.mkdir(os.curdir + '/PyQt_YTDownloader_Videos')

        self.files.clear()
        for entry in os.scandir(os.curdir + '/PyQt_YTDownloader_Videos'):
            self.files.append(entry)

    def sync_files(self, file_list):
        length_difference = len(self.files) != len(file_list)
        file_changed = len(list(set(self.files) - set(file_list))) > 0

        if length_difference or file_changed:
            self.crawl_files()
            self.update_completed_download_list()

    def download_progress(self, progress_dict):
        """
        Managaging the download progress for us.
        It set the label and progressbar values.

        :param progress: the progress dictionary
        :type progress: dict
        :return: None
        :rtype: None
        """
        if "_percent_str" in progress_dict:
            percent = progress_dict["_percent_str"]
            percent_int = float(percent.replace("%", ""))
            self.progressBar.setValue(percent_int)
            progress_string = "Aktuell: {0}".format(progress_dict["filename"])
            self.current_download_label.setText(progress_string)
            self.download_speed_label.setText(progress_dict["_speed_str"])
            self.download_size_label.setText(progress_dict["_total_bytes_str"])

    def update_completed_download_list(self):
        """
        scans the PyQt_YTDownloader directory for videos and appends it to our listwidget

        :return: None
        :rtype: None
        """

        self.completed_downloads_listWidget.clear()

        for entry in self.files:
            if entry.is_file():
                list_item = QtWidgets.QListWidgetItem()
                list_item.setText(entry.name)
                list_item.setToolTip("Klicken um zu Datei zu springen")
                self.completed_downloads_listWidget.addItem(list_item)

    def list_item_clicked(self, item):
        """
        gets fired when a list item is doubled clicked
        opens the explorer in the pyTDownload directory

        :param item: The QListWidgetItem
        :type item: QtWidgets.QListWidgetItem
        :return: None
        :rtype: None
        """
        webbrowser.open('file://' + os.path.abspath('./PyQt_YTDownloader_Videos/'))

    def download_finished(self):
        """
        Fires when the download has finished

        :return: None
        :rtype: None
        """
        self.update_completed_download_list()
        self.current_download_label.setText("Download abgeschlossen")

    def info_thread_finished(self):
        """
        Fires when the info thread has finished

        :return: None
        :rtype: None
        """
        self.quality_info_items = list(dict.fromkeys(self.quality_info_items))
        self.quality_info_items.sort()
        for info_tuple in self.quality_info_items:
            self.quality_comboBox.addItem(info_tuple[0], userData=info_tuple[1])
        self.download_pushButton.setEnabled(True)
        self.current_download_label.setText("")

    def add_quality_item(self, string, user_data):
        """
        Adds a quality item to our list

        :param string: the text for the combobox item
        :type string: string
        :param user_data: the id of the quality format
        :type user_data: string
        :return: None
        :rtype: None
        """
        self.quality_info_items.append((string, user_data))

    def video_url_lineEdit_finished(self):
        """
        fetches meta information of the video

        :return: None
        :rtype: None
        """
        url = youtube_dl.utils.url_or_none(self.video_url_lineEdit.text())
        if url is not None:
            self.url = url
            self.info_thread.url = self.url
            self.info_thread.start()
            self.current_download_label.setText("Hole Video Informationen...")
            self.download_pushButton.setEnabled(False)

    def download_pushButton_clicked(self):
        """
        resets the progressbar value
        sets the quality format for the video
        sets the youtube url

        :return: None
        :rtype: None
        """
        if self.url is not None:
            self.progressBar.setValue(0)
            self.download_video_thread.format = self.quality_comboBox.currentData()
            self.download_video_thread.url = self.url

            if self.quality_comboBox.currentData() == "tiny":
                self.download_video_thread.audio_only = True
            self.download_video_thread.start()
