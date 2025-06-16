# mqtt_utils.py
import paho.mqtt.client as mqtt
import time
import logging
import pyautogui

from PySide6.QtCore import QObject, Signal, Slot
# MQTT配置
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "gesture/control"
CLIENT_ID = f"Publisher_{int(time.time())}"  # 客户端ID，确保唯一性
# 命令到操作的映射
COMMAND_ACTIONS = {
    "page_up": lambda:pyautogui.press('up'),
    "page_down":lambda:pyautogui.press('down'),
    "zoom_in":lambda:pyautogui.hotkey('ctrl','+'),
    "zoom_out":lambda:pyautogui.hotkey('ctrl','-'),
    "left": lambda: pyautogui.press('left'),
    "right": lambda:pyautogui.press('right')
}

class Mqtt_Subscriber(QObject):
    signal = Signal(str)  # 根据实际需要调整参数类型
    def __init__(self,username=None, password=None, timeout=60):
        # 设置日志
        super().__init__()
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(f"MQTTClient.{CLIENT_ID}")
        self.client = mqtt.Client(client_id=CLIENT_ID, callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
        self.use_new_api = True
        self.broker = MQTT_BROKER
        self.port = MQTT_PORT
        self.topic = MQTT_TOPIC
        self.username = username
        self.password = password
        self.timeout = timeout
        self.connected = False
        self.client.on_message = self.on_message

        # 防止过快连操作
        self.last_action_time = 0
        self.action_interval = 0.5  # 最小操作问隔(秒)

        # 设置回调函数
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect

        # 设置认证
        if username and password:
            self.client.username_pw_set(username, password)

        # 连接MQTT代理
        self.connect()
    def execute_command(command):
        """执行命令对应的操作"""
        if command in COMMAND_ACTIONS:
            try:
                COMMAND_ACTIONS[command]()
                print(f"执行命令: {command}")
            except Exception as e:
                print(f"执行命令时出错: {e}")
        else:
            print(f"未知命令: {command}")
    def start_to_connect(self):
        # 初始化MQTT订阅者
        mqtt_subscriber = Mqtt_Subscriber(
            client_id=CLIENT_ID,
            broker=MQTT_BROKER,
            port=MQTT_PORT,
            topic=MQTT_TOPIC
        )

        # 等待MQTT连接
        print("等待MQTT连接...")
        connect_timeout = 10
        start_time = time.time()
        while not mqtt_subscriber.connected:
            time.sleep(0.5)
            if time.time() - start_time > connect_timeout:
                print("MQTT连接超时!")
                return False

        print(f"成功连接到MQTT代理: {MQTT_BROKER}:{MQTT_PORT}")
        mqtt_subscriber.subscribe(MQTT_TOPIC)
        print(f"已订阅主题: {MQTT_TOPIC}")

        mqtt_subscriber.client.on_message = mqtt_subscriber.on_message
        # 启动MQTT循环
        mqtt_subscriber.client.loop_start()

        return mqtt_subscriber
    def connect(self):
        try:
            self.logger.info(f"尝试连接到MQTT代理: {self.broker}:{self.port}")
            self.client.connect(self.broker, self.port, keepalive=60)
            self.client.subscribe(self.topic)
            self.client.loop_start()

            # 等待连接建立
            retry = 0
            while not self.connected and retry < 10:
                self.logger.debug(f"等待连接建立...({retry + 1}/10)")
                time.sleep(0.5)
                retry += 1

            if self.connected:
                self.logger.info("成功连接到MQTT代理")
            else:
                self.logger.error("连接超时，未能建立连接")

            return self.connected
        except Exception as e:
            self.logger.error(f"连接异常: {e}")
            return False

    def on_disconnect(self, client, userdata, rc):
        self.connected = False
        if rc != 0:
            self.logger.warning(f"意外断开连接，返回码: {rc}")
        else:
            self.logger.info("正常断开连接")

    def on_message(self, client, userdata, msg):
        """MQTT消息回调函数"""
        command = msg.payload.decode('utf-8')
        print(f"收到命令: {command}")
        self.signal.emit(command)
        # 执行命令
        action = COMMAND_ACTIONS.get(command)
        if action:
            try:
                return command
            except Exception as e:
                print(f"执行命令{command}出错: {e}")
        else:
            print(f"未知命令: {command}")


    def on_subscribe(self, client, userdata, mid, granted_qos):
        self.logger.debug(f"订阅成功 (ID: {mid}, QoS: {granted_qos})")


    def on_connect(self, client, userdata, flags, reason_code, properties=None):
        if self.use_new_api:
            if reason_code == 0:
                self.connected = True
                self.logger.info(f"成功连接到MQTT代理")
            else:
                self.connected = False
                self.logger.error(f"连接失败: {reason_code}")
        else:
            rc = reason_code
            if rc == 0:
                self.connected = True
                self.logger.info(f"成功连接到MQTT代理")
            else:
                self.connected = False
                self.logger.error(f"连接失败: {rc}")

    def disconnect(self):
        if self.connected:
            self.client.loop_stop()
            self.client.disconnect()

    def subscribe(self, topic, qos=1):
        if not self.connected:
            self.logger.warning("未连接，无法订阅主题")
            return False
        try:
            result = self.client.subscribe(topic, qos)
            return result[0] == mqtt.MQTT_ERR_SUCCESS
        except Exception as e:
            self.logger.error(f"订阅主题失败: {e}")
            return False

    def set_message_handler(self, handler):
        """自定义消息处理函数"""
        self.client.on_message = handler
    def __del__(self):
        """析构函数，确保在对象销毁时正确清理资源"""
        try:
            if hasattr(self, 'client') and self.client:
                if self.connected:
                    self.logger.info("对象销毁时断开MQTT连接")
                    self.client.loop_stop()
                    self.client.disconnect()
                # 清理客户端引用
                self.client = None
            self.connected = False
            if hasattr(self, 'logger'):
                self.logger.info("MQTT订阅者对象已销毁")
        except Exception as e:
            # 在析构函数中避免抛出异常
            if hasattr(self, 'logger'):
                self.logger.error(f"销毁对象时出错: {e}")
