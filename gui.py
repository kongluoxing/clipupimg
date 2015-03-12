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
import os
from PyQt4 import QtGui
from PyQt4 import QtCore

from clipupimg import HOTKEY, PROMPT
from clipupimg import ClipupImageQiniu
from clipupimg import _cur_path

app = QtGui.QApplication(sys.argv)
clipper = ClipupImageQiniu()


class ImageViewer(QtGui.QFrame):
    def __init__(self):
        """
        show uploaded image

        """
        super(ImageViewer, self).__init__()
        self.clipboard = QtGui.QApplication.clipboard()
        self.image_path = None

        self.initUI()

    def initUI(self):
        # centerize
        screen = QtGui.QDesktopWidget().screenGeometry()
        self.resize(300, 200)
        size = self.geometry()
        self.move((screen.width()-size.width())/2, (screen.height()-size.height())/2)

        self.setWindowTitle('Clipboard Viewer')
        self.setWindowIcon(QtGui.QIcon('icon.ico'))
        self.setAttribute(QtCore.Qt.WA_QuitOnClose, False)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        # layout
        layout = QtGui.QGridLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # show image
        self.label = QtGui.QLabel()
        self.label.setFrameStyle(QtGui.QFrame.Panel)
        self.label.setAutoFillBackground(True)
        self.label.setBackgroundRole(QtGui.QPalette.ToolTipBase)
        self.setLayout(layout)

        self.label = QtGui.QLabel()
        layout.addWidget(self.label)

    def show_content(self):
        if self.image_path:
            image = QtGui.QImage(self.image_path)
            pixmap = QtGui.QPixmap(image)
            self.label.setPixmap(pixmap)
            self.setVisible(True)

image_viewer = ImageViewer()


class TrayWidget(QtGui.QSystemTrayIcon):
    def __init__(self):
        """
        tray icon and menus

        """
        super(TrayWidget, self).__init__()

        self.clipboard = QtGui.QApplication.clipboard()

        # menu
        self.quit_action = QtGui.QAction('&Quit', None)
        self.quit_action.triggered.connect(sys.exit)
        self.upload_action = QtGui.QAction('&Upload', None)
        self.upload_action.triggered.connect(clipper.clipup)
        self.show_action = QtGui.QAction('&Show', None)
        self.show_action.triggered.connect(self.on_show_action)

        tray_icon_menu = QtGui.QMenu()
        tray_icon_menu.addAction(self.upload_action)
        tray_icon_menu.addAction(self.show_action)
        tray_icon_menu.addAction(self.quit_action)

        # tray icon
        icon = QtGui.QIcon(_cur_path + os.sep + 'icon.ico')
        self.setIcon(icon)
        self.setVisible(True)
        self.setContextMenu(tray_icon_menu)
        self.setToolTip('Upload clipboard image to qiniu')

        # when finished, show a message
        # self.connect(self, QtCore.SIGNAL('finished'), self.show_finished)
        clipper.finished.connect(self.on_finished)

        # hotkey
        hotkey = QtGui.QKeySequence(HOTKEY)
        self.upload_action.setShortcut(hotkey)

        # click icon to upload
        self.activated.connect(self.on_double_clicked)

    def on_test_action(self):
        content = self.clipboard.text()
        if not content:
            content = self.clipboard.image()

        label = QtGui.QLabel()
        pixmap = QtGui.QPixmap(content)
        label.setPixmap(pixmap)
        label.show()

    def on_double_clicked(self, reason):
        if reason == self.DoubleClick:
            if PROMPT == 'false':
                clipper.clipup()
            # FIXME crash?
            elif PROMPT == 'true':
                filename, ok = QtGui.QInputDialog.getText(None, 'File Name', 'Enter file name:')
                if ok and filename:
                    clipper.clipup(filename)
            else:
                clipper.clipup()

    def on_finished(self, url, path):
        image_viewer.image_path = path
        self.showMessage('Success', 'Upload finished: ' + url)

    def on_show_action(self):
        image_viewer.show_content()


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
    sys.exit(app.exec_())

