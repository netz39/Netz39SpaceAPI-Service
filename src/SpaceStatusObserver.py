import paho.mqtt.client as mqtt

class SpaceStatusObserver:
    def __init__(self, broker, port, topic_status, topic_lastchange, space_api_entry):
        self.broker = broker
        self.port = int(port)
        self.topic_status = topic_status
        self.topic_lastchange = topic_lastchange
        self.space_api_entry = space_api_entry

        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message

    def on_connect(self, client, _userdata, _flags, rc):
        print(f"Connected with result code {rc}")
        for topic in [self.topic_status, self.topic_lastchange]:
            print(f"Subscribing to topic {topic}")
            client.subscribe(topic)

    def on_disconnect(self, client, userdata, rc):
        print(f"Disconnected with result code {rc}")
        if rc != 0:
            print("Unexpected disconnection. Reconnecting...")
            self.client.reconnect()

    def on_message(self, client, userdata, msg):
        print(f"Message received on topic {msg.topic}: {msg.payload.decode()}")
        self.on_message_callback(msg.topic, msg.payload.decode())

    def on_message_callback(self, topic, message):
        if topic == self.topic_status:
            self.space_api_entry.set_is_open(message == "true")
        elif topic == self.topic_lastchange:
            self.space_api_entry.set_lastchange(int(message))

    def start(self):
        self.client.connect(self.broker, self.port, 60)
        self.client.loop_start()

    def stop(self):
        self.client.loop_stop()
        self.client.disconnect()

    def get_space_api_entry(self):
        return self.space_api_entry.data
