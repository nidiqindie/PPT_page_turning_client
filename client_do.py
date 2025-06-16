from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox, QWidget
from PySide6.QtUiTools import QUiLoader
import sys
import os  # 添加路径处理
from all_ui.ppt_client_ui import Ui_Form
from script import script
from Focus_Detection import Focus_Detection
from PySide6.QtCore import QMetaObject, Qt
from Subscriber import Mqtt_Subscriber
import time
class Client_UI(QWidget):
    def __init__(self):  # 添加loader参数
        super().__init__()
        #使用ui文件动态创建窗口
        # # 获取UI文件的绝对路径
        # ui_path = os.path.join(os.path.dirname(__file__), "all_ui", "ppt_client.ui")
        # # 加载UI文件
        # self.ui = loader.load(ui_path)
        # if not self.ui:
        #     QMessageBox.critical(None, "错误", "无法加载UI文件")
        #     sys.exit(1)
        # self.setCentralWidget(self.ui)  # 设置中心部件
        # self.setWindowTitle("ppt智能助手客户端")  # 设置窗口标题
        # # self.ui.layout().activate()
        # self.resize(300, 200)  # 设置为设计器中的尺寸

        #############使用py文件创建窗口
        # 使用ui文件导入定义界面类
        self.ui = Ui_Form()
        # 初始化界面
        self.ui.setupUi(self)
        # 基础置顶设置
        self.setWindowFlags(Qt.WindowStaysOnTopHint) # 窗口置顶
        self.ui.Button1.setStyleSheet("""
            QPushButton {
                background: #4CAF50;
                color: white;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover { background: #45a049; }
        """)
        #显示是否启动的label
        self.ui.label1.setStyleSheet("""
                    QLabel {
                        background: #3c3b31;
                        color: white;
                        border-radius: 5px;
                        font-weight: bold;
                    }
                """)
        #显示当前是什么手势
        self.ui.label2.setStyleSheet("""
                         QLabel {
                             background: #3c3b31;
                             color: white;
                             border-radius: 5px;
                             font-weight: bold;
                         }
                     """)
        #显示焦点是否在ppt中
        self.ui.label3.setStyleSheet("""
                         QLabel {
                             background: #3c3b31;
                             color: white;
                             border-radius: 5px;
                             font-weight: bold;
                         }
                     """)
        self.in_ppt = False
        
        self.ui.Button1.clicked.connect(self.start_ppt)
     
        ############
        
        #创建一个脚本对象用于实现对应效果
        self.script = script()
        
        ############创建一个视奸进程用来监控当前焦点进程，焦点是ppt时，则执行脚本
        self.detector = Focus_Detection()
        self.detector.set_interrupt_callback(self.interrupt_callback)#设置中断回调函数
         # 添加需要监听的目标进程（PowerPoint）
        self.detector.add_interrupt_target("POWERPNT.EXE")  # PowerPoint
        ############
        self.mqtt_client = None
    def interrupt_callback(self,event_type, process_name, window_info):
        """中断事件回调函数示例"""
        if event_type == 'enter':
            print(f"🔴 目前焦点已在powerpoint中！")
            self.ui.label3.setStyleSheet(
                """
                  QLabel {
                        background: #4CAF50;
                        border-radius: 5px;
                    }
                """
                )
            self.in_ppt = True
            self.ui.label3.setText(f"🔴 目前焦点已在powerpoint中！")
        elif event_type == 'exit':
            print(f"🟢 焦点离开 powerpoint！")
            self.ui.label3.setStyleSheet(
                """
                  QLabel {
                        background: #3c3b31;
                        border-radius: 5px;
                    }
                """
                )
            self.in_ppt = False
            self.ui.label3.setText(f"🟢 焦点离开 powerpoint！")
        
    def start_ppt(self):
        """启动PPT监控功能"""
        if not hasattr(self, 'monitoring_started'):
            self.detector.start_monitoring()
            self.monitoring_started = True
           
            self.mqtt_client=Mqtt_Subscriber()
            if not self.mqtt_client:
                self.ui.label1.setText("程序启动失败！初始化MQTT失败！")
                return False
            # 等待MQTT连接
            print("等待MQTT连接...")
            connect_timeout = 10
            start_time = time.time()
            while not self.mqtt_client.connected:
                time.sleep(0.5)
                if time.time() - start_time > connect_timeout:
                    self.ui.label1.setText("程序启动失败！连接超时！") # 连接超时
                    return False

            print(f"成功连接到MQTT代理: {self.mqtt_client.broker}:{self.mqtt_client.port}")
            self.mqtt_client.subscribe(self.mqtt_client.topic)
            print(f"已订阅主题: {self.mqtt_client.topic}")
            self.mqtt_client.client.on_message = self.mqtt_client.on_message
            self.mqtt_client.client.loop_start()
            self.ui.label1.setText("程序已启动！")
            self.ui.label1.setStyleSheet(
                """
                  QLabel {
                        background: #4CAF50;
                        border-radius: 5px;
                    }
                """
                )
            self.ui.label2.setText("🟢 程序已启动！正在检测手势中")
            self.ui.label3.setText("🎈 程序已启动！等待焦点移动至ppt窗口")
            self.ui.label2.setStyleSheet("""
                  QLabel {
                        background: #4CAF50;
                        border-radius: 5px;
                    }
                """)
            self.mqtt_client.signal.connect(self.gesture_callback)
        else:
            self.ui.label1.setText("程序已在运行中")
    def gesture_callback(self, event_type):
        if self.in_ppt:
            match event_type:
                #向上翻
                case "0":
                    self.script.up_sliding()
                    self.ui.label2.setText(f"🟢 向上翻页！")
                #向下翻
                case "1":
                    self.script.down_sliding()
                    self.ui.label2.setText(f"🟢 向下翻页！")
                #放大一点
                case "2":
                    self.script.zoom_in()
                    self.ui.label2.setText(f"🟢 放大！")
                #缩小一点
                case "3":
                    self.script.zoom_out()
                    self.ui.label2.setText(f"🟢 缩小！")
                case "4":    
                    self.script.Left_sliding()
                    self.ui.label2.setText(f"🟢 左键")
                case "5":
                    self.script.Right_sliding()
                    self.ui.label2.setText(f"🟢 右键")
            
    def closeEvent(self, event):
        """程序关闭时的清理工作"""
        try:
            # 停止焦点检测监控
            if hasattr(self, 'detector') and self.detector:
                print("🔄 正在停止焦点监控...")
                self.detector.stop_monitoring()
                print("✅ 焦点监控已停止")
            
            # 清理其他资源
            if hasattr(self, 'script'):
                del self.script
            if hasattr(self, 'mqtt_client') and self.mqtt_client:
                print("🔄 正在断开MQTT连接...")
                self.mqtt_client.disconnect()
                print("✅ MQTT连接已断开")
                pass
            print("🔚 程序资源清理完成")
            
        except Exception as e:
            print(f"❌ 清理资源时出错: {e}")
        finally:
            # 接受关闭事件
            event.accept()

# if __name__ == "__main__":
#     #使用ui文件创建的时候
#     # app = QApplication(sys.argv)
#     # loader = QUiLoader()
#     # # 创建Client实例时传入loader
#     # window = Client(loader)
#     # window.show()  # 显示主窗口对象（不是window.ui）
#     # app.exec()
#     print("调试ui客户端");
#     #使用py文件创建的时候
#     app = QApplication(sys.argv)
#     window = Client_UI()
#     window.show()  # 显示主窗口对象（不是window.ui）
#     app.exec()
