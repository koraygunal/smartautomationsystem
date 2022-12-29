# python 3.6


import time

from paho.mqtt import client as mqtt_client

import pandas as pd



broker = 'test.mosquitto.org'
port = 1883
topic = "imanolandkoray"
client_id = "python2222"
# username = 'mqtt-upv'
# password = 'basque'




def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)

    client.on_connect = on_connect
    client.connect(broker, port)
    return client



def publish(client):
    while True:
        time.sleep(10)
        df = pd.read_csv("20221116N1.csv")
        last = df.iloc[-1]
        lastTemp = last['TMP']
        if lastTemp<26:
            msg = "26"
            client.publish(topic, msg)
            print(f"Send '{msg}' to topic '{topic}'")
        elif last > 28 :
            msg ="26"
            client.publish(topic, msg)
            print(f"Send '{msg}' to topic '{topic}'")
        else:
            print("All value is normal")


        '''result = client.publish(topic, msg)
        # result: [0, 1]
        status = result[0]
        if status == 0:
            print(f"Send `{msg}` to topic `{topic}`")
        else:
            print(f"Failed to send message to topic {topic}")
            msg_count += 1'''


def run():
    client = connect_mqtt()
    client.loop_start()
    publish(client)


if __name__ == '__main__':
    run()
