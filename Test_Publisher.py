import paho.mqtt.client as mqtt
import time

# MQTT配置
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "test"
CLIENT_ID = f"Test_Publisher_{int(time.time())}"  # 确保唯一性

def on_connect(client, userdata, flags, rc):
    print(f"连接结果: {rc}")
    if rc == 0:
        print("已连接到MQTT代理")
        # 发布测试消息
        client.publish(MQTT_TOPIC, "Test Message", qos=1)
    else:
        print(f"连接失败，错误码: {rc}")

def on_publish(client, userdata, mid):
    print(f"消息已发布，消息ID: {mid}")

client = mqtt.Client(client_id=CLIENT_ID)
client.on_connect = on_connect
client.on_publish = on_publish

client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.loop_start()

try:
    # 保持主线程运行，等待消息发布
    time.sleep(60)
except KeyboardInterrupt:
    print("程序终止")
finally:
    client.loop_stop()
    client.disconnect()