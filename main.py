import sys
import client_do
import qdarkstyle
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
import paho.mqtt.client as mqtt
import pyautogui
import time
from Subscriber import Mqtt_Subscriber
from PySide6.QtCore import QThread, Signal


"""

 # 初始化MQTT
    mqtt_subscriber = Mqtt_Subscriber()
    if not mqtt_subscriber:
        sys.exit(1)

"""



if __name__ == '__main__':
    app = QApplication(sys.argv)
    def get_resource_path(relative_path):
        """获取资源文件的绝对路径"""
        if hasattr(sys, '_MEIPASS'):
            # PyInstaller打包后的临时目录
            return os.path.join(sys._MEIPASS, relative_path)
        # 开发环境
        return os.path.join(os.path.abspath("."), relative_path)

    # 使用动态路径设置图标
    icon_path = get_resource_path("photograph/logo.jpg")
    # 设置应用程序图标
    app.setWindowIcon(QIcon(icon_path))
    app.setStyleSheet(qdarkstyle.load_stylesheet())
    my_ui=client_do.Client_UI()
    my_ui.show()
    app.exec()