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

import tempfile
import os
from ConfigParser import ConfigParser

from PIL import ImageGrab
import win32clipboard as wclip
from PyQt4 import QtCore
from qiniu import Auth
from qiniu import put_file


__cur_path = os.path.abspath(os.path.dirname(__file__))

config = ConfigParser()
config.read(__cur_path + os.sep + 'config.conf')


ACCESS_KEY = config.get('config', 'access_key')
SECRET_KEY = config.get('config', 'secret_key')
BUCKET = config.get('config', 'bucket')
FORMAT = config.get('config', 'format') or '{}'
HOTKEY = config.get('config', 'hotkey')


class ContentNotFitException(Exception):
    pass


class ClipupImageQiniu(QtCore.QObject):

    # must define here, cannot be in any method
    finished = QtCore.pyqtSignal(str)

    def save_clip_to_file(self):
        """
        Save clipboard image to a tempfile

        :return: @str temp file path
        """
        image = ImageGrab.grabclipboard()

        if image:
            fd, path = tempfile.mkstemp(suffix='.jpg')
            f = open(path, 'wb')
            image.save(path, 'JPEG')
            f.close()
            return path
        else:
            raise ContentNotFitException('Clipboard content is not an image.')


    @staticmethod
    def qiniu_init(access_key, secret_key):
        q = Auth(access_key, secret_key)
        return q


    @staticmethod
    def upload_to_qiniu(path, qiniu):
        """
        upload file to qiniu
        :param path: file path
        :param qiniu: qiniu Auth instance
        :return: URL if upload succeed, error info if failed
        """
        bucket_name = BUCKET
        key = os.path.basename(path)
        params = {}
        mime_type = 'image/jpeg'

        token = qiniu.upload_token(bucket_name, key)
        ret, info = put_file(token, key, path, params, mime_type=mime_type, check_crc=True)
        if ret:
            return('http://' + BUCKET + '.qiniudn.com/' + key)
        else:
            return(info)


    def clipup(self):
        temp_path = self.save_clip_to_file()
        q = self.qiniu_init(ACCESS_KEY, SECRET_KEY)
        url = t_url = self.upload_to_qiniu(temp_path, q)
        url = FORMAT.format(url)
        wclip.OpenClipboard()
        wclip.SetClipboardText(str(url), wclip.CF_TEXT)
        wclip.CloseClipboard()

        self.finished.emit(t_url)
        print('Upload finished: ' + t_url)
        return url


# if __name__ == '__main__':

    # icon = 'icon.ico'
    # hover_text = "Clipboard image upload assist"
    #
    # menu_options = (('Upload', None, clipup),)
    #
    # def bye(sysTrayIcon): pass
    #
    # SysTrayIcon(icon, hover_text, menu_options, on_quit=bye, default_menu_index=1)

    # from gui import main
    # main(clipup)

