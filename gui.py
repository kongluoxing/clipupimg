# coding: utf-8
#
# Copyright 2014, Kong Luoxing<kong.luoxing@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys
from PyQt4 import QtGui
from PyQt4 import QtCore
from PIL import ImageGrab

from clipupimg import ClipupImageQiniu
from clipupimg import HOTKEY

app = QtGui.QApplication(sys.argv)
cliper = ClipupImageQiniu()


class ImageWidget(QtGui.QMainWindow):
    def __init__(self):
        super(ImageWidget, self).__init__()
        self.layout = QtGui.QLayout()
        self.gv = QtGui.QGraphicsView()

        self.initUI()

    def initUI(self):
        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('Clipboard Viewer')
        self.setWindowIcon(QtGui.QIcon('icon.ico'))
        self.setAttribute(QtCore.Qt.WA_QuitOnClose, False)

    def grab_from_clipboard(self):
        image = QtGui.QImage(ImageGrab.grabclipboard())
        self.layout.addWidget(self.gv)


    def show_content(self):
        self.grab_from_clipboard()
        self.setVisible(True)

iw = ImageWidget()


class TrayWidget(QtGui.QSystemTrayIcon):
    def __init__(self):
        super(TrayWidget, self).__init__()

        self.clipboard = QtGui.QApplication.clipboard(app)

        # menu
        self.quit_action = QtGui.QAction('&Quit', None)
        self.quit_action.triggered.connect(sys.exit)
        self.upload_action = QtGui.QAction('&Upload', None)
        self.upload_action.triggered.connect(cliper.clipup)
        self.show_action = QtGui.QAction('&Show', None)
        self.show_action.triggered.connect(self.on_show_action)
        self.test_action = QtGui.QAction('&Test', None)
        self.test_action.triggered.connect(self.on_test_action)

        tray_icon_menu = QtGui.QMenu()
        tray_icon_menu.addAction(self.upload_action)
        tray_icon_menu.addAction(self.show_action)
        tray_icon_menu.addAction(self.quit_action)
        tray_icon_menu.addAction(self.test_action)

        # tray icon
        icon = QtGui.QIcon('icon.ico')
        self.setIcon(icon)
        self.setVisible(True)
        self.setContextMenu(tray_icon_menu)
        self.setToolTip('Upload clipboard image to qiniu')

        # when finished, show a message
        # self.connect(self, QtCore.SIGNAL('finished'), self.show_finished)
        cliper.finished.connect(self.show_finished)

        # global hotkey
        hotkey = QtGui.QKeySequence(HOTKEY)
        self.upload_action.setShortcut(hotkey)

        # click icon to upload
        self.activated.connect(self.on_double_clicked)

    def on_test_action(self):


    def on_double_clicked(self, reason):
        if reason == self.DoubleClick:
            cliper.clipup()

    def show_finished(self, url):
        self.showMessage('Success', 'Upload finished: ' + url)

    def on_show_action(self):
        iw.show_content()


tw = TrayWidget()


class QtExceptionHandler(QtCore.QObject):
    # show all exception
    error_signal = QtCore.pyqtSignal()

    def __init__(self):
        super(QtExceptionHandler, self).__init__()

    def handle(self, exctype, value, traceback):
        tw.showMessage('Warning', str(value), icon=QtGui.QSystemTrayIcon.Warning)
        sys.__excepthook__(exctype, value, traceback)


exception_handler = QtExceptionHandler()
sys.excepthook = exception_handler.handle

if __name__ == '__main__':
    app.exec_()

