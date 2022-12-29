#If do you have any question about program or code you can send e-mail to me(cc:koraygnal@gmail.com)
import random

from paho.mqtt import client as mqtt_client
import json
import pandas as pd
import csv
import time

broker = '192.168.68.23' #Broker Ip adress
port = 1883  #Port Number
topic = "values/n1"  #Topic

client_id = 'Python-1' #Client ID



def connect_mqtt() -> mqtt_client:    #Thanks to the broker address and port we defined in this block, we connect with mqtt.
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    #client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


def subscribe(client: mqtt_client):  #After the connection , we subscribe the topic
    def on_message(client,userdata, msg):  #We will received message from publisher.
        print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")

        a = msg.payload.decode()

        b=json.loads(a)  #Message format is json so we have to convert this format json to string

        c=json.dumps(b)

        humidity = b["HUM"]  #We identify humidity specificly
        temp= b["TMP"]    #We identify temperature specificly
        for i in temp:
            temp2=i
            for j in humidity:
                humidity2=j  #Köşeli parantezden kurtulmak için
        carbondioxyde = b["CO2"]
        for i in carbondioxyde:
            CO2 = i

        valve = "%100"

        data = pd.read_csv(
            '20221116N1.csv')  # Convert the data's informations to pandas.In this way we can manipulate the datas
        index = len(data.index)  # Identfy long of data
        Node = "Node1"

        zaman = time.strftime(
            '%c')  # Show the current time.When we write data to csv file we can see when the data written to file.

        with open('20221116N1.csv', mode='a') as sensor_readings:  # Write every information to csv file.
            writer = csv.writer(sensor_readings)

            writer.writerow([temp2, humidity2, CO2, valve, zaman, index])







    client.subscribe(topic)     #Run the function of client.subscribe
    client.on_message = on_message #Run the function of client.on_message




def run():      #This part most important part because we want to run program forever till we stop.
    client = connect_mqtt()
    subscribe(client)
    client.loop_forever()



if __name__ == '__main__':
    run()
