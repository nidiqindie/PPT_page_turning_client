import paho.mqtt.client as mqtt
import time

# MQTT配置
MQTT_BROKER = "localhost"  # EMQX服务器地址
MQTT_PORT = 1883  # MQTT默认端口
MQTT_TOPIC = "test"  # 订阅的主题
CLIENT_ID = f"Test_Subscriber_{int(time.time())}"  # 客户端ID，确保唯一性


# 连接成功回调
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"已连接到MQTT代理: {MQTT_BROKER}:{MQTT_PORT}")
        # 订阅主题，QoS=0
        client.subscribe(MQTT_TOPIC, qos=0)
        print(f"已订阅主题: {MQTT_TOPIC}")
    else:
        print(f"连接失败，错误码: {rc}")


# 收到消息回调
def on_message(client, userdata, msg):
    print(f"收到消息: 主题={msg.topic}, 载荷={msg.payload.decode('utf-8')}")


# 创建MQTT客户端实例
client = mqtt.Client(client_id=CLIENT_ID)

# 设置回调函数
client.on_connect = on_connect
client.on_message = on_message

# 连接MQTT代理
try:
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    # 启动网络循环（非阻塞模式）
    client.loop_start()

    print("按 Ctrl+C 终止程序")
    while True:
        time.sleep(60)  # 保持主线程运行

except KeyboardInterrupt:
    print("\n程序已停止")
finally:
    # 断开连接
    client.loop_stop()
    client.disconnect()