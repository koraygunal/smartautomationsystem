# -*- coding: utf-8 -*-
"""
Created on Tue Nov  8 08:17:48 2022

Recep2 is the subscriber to the mqtt broker and it will get the information
from the sensor node to save that data in a csv file and then, plot that
information in real time.

There will be as meny csv files as sensor nodes are register by the program.
All the data will be save in a directory called "sensorNodes" in this path:
    C:/Users/{user}/Documents/sensorNodesCSV


@author: Imanol Martín Toral , Koray GÜNAL
"""

from datetime import time,datetime,date,timedelta
from paho.mqtt import client as mqtt_client #Import client library.
import paho.mqtt.publish as publish
from timeloop import Timeloop
from getpass import getuser
from time import sleep
from math import ceil
import pandas as pd
import numpy as np
import queue
import json
import time
import os
import subprocess

#------------------VARIABLES---------------------------------------------------

q=queue.Queue() #We create an empty queue.
client_id=("Usuario") #Client ID
broker_adress="158.227.233.24" #Broker Ip adress
#Port Number is 1883
msg={}
keyboard=""
topic="values/#"
mes2=None
tl = Timeloop()

#------------------FUNCTIONS---------------------------------------------------

#Desc: Establish a connection to an MQTT broker using the Python client.
#Param In: client,userdata,flags,rc.
#Parama Out: 
#Return: The state of the connection qith the MQTT broker.
#Date: 08/11/2022
def on_connect(client,userdata,flags,rc):
    if rc==0:
        global connected_flag
        connected_flag=True #set flag.
        print("Connected successfully=",rc)
    else:
        print("Failed to connect=",rc)

#Desc: Function that recieves the messages from the MQTT broker and enqueued them.
#Param In: client,userdata,message.
#Parama Out: mes2
#Return: mes2
#Date: 08/11/2022
def on_message(client,userdata,message):
    # global message_flag
    global mes2
    mes2=message
    q.put(message)
    print(f"{q.qsize()} messages recieved \n")
    return mes2

#Desc: Extraction of the data inside msg diccionary to variables type "list".
#Param In: Data from msg diccionary.
#Parama Out: 
#Return: the data will be save in a txt file.
#Date: 14/11/2022
def fnSavedata():
    global cDirect
    global content
    global temp
    for data in msg['values']: #message is read and save in data.
        temp=data['TMP']
        hum=data['HUM']
        co2=data['co2']
    cTime=time.strftime('%H:%M') #Current time of the data send to the cotroller.
    
    cDirect=fnDirectories()#Creates the necesary folder to save the data.
    #stValve=Control_28112022.py.ctrValve() #Valve status
    
    stValve=ctrValve(temp)
    
    #define the variables of time:
    fecha=date.today().strftime('%Y%m%d')
    txtFecha=date.today().strftime('%Y/%m/%d')
   
    #Txt document redaction:
    txtFile= (f'{fecha}_'+str(numNodo)+'.txt')
    txtPath=(rf"C:\Users\{user}\Documents\sensorNodesTXT\{numNodo}/"+str(txtFile))
    fieldnames=['Time','TMP[C]','HUM-H[%]','CO2[ppm]','Valve_status'] 
    lnData=[cTime,temp,hum,co2,stValve]
    
    spaces=0
    for content in [fieldnames, lnData]:
        maximun = max(map(len, str(content)))
        spaces = maximun if spaces<maximun else spaces
        spaces+=5

    fieldNames = [f"{col:^{spaces}}" for col in fieldnames]

    body = [] #The result is storage.

    for line in [lnData]:
        row1 = f"{line[0]:^{spaces}}" #Line up the first column to the left.

        #Lines up the rest of the rows to the center.
        row = [row1]+[f"{row:^{spaces}}" for row in line[1:]]
        row[-1] +='\n' #Add a line break in the last data.

        body.append(row) #Add row to the list "body"
    
    
    with open(txtPath, mode='a') as f: #Write every information to a txt file.
        if os.stat(txtPath).st_size == 0:
            #write the headlines:
            f.write('[Nodo_ID]: Nodo '+str(numNodo)+'\n')
            f.write('[Sensores]: '+str(3)+'\n')
            f.write('[Periodo_medida (seg)]: '+str(10)+'\n')
            f.write('[Fecha]: '+str(txtFecha)+'\n')
            f.write('[Intervalo_horario_desde]: '+str(cTime)+'\n')
            f.write('[Intervalo_horario_hasta]: ' +str(cTime[len(cTime)-1])+'\n\n')
                
            f.write("".join(fieldNames)+'\n') #Writes the fieldnames.
            f.writelines("".join(line) for line in body) #writes the first data.
            
        else:
            f.writelines("".join(line) for line in body)
    
#Desc: Creates the "sensorNodes" directory and the subfolders that will be inside.
#Param In: all
#Parama Out: 
#Return: Creates all the folders, in case not, return an error message.
#Date: 18/11/2022
def fnDirectories():
    global user
    global numNodo
    
    user=getuser() #Search the user of the computer.
    pDirectory=(f"C:/Users/{user}/Documents/") #General path for all users
    try:
        #creates a directory to save the nodes files
        os.makedirs(f"C:/Users/{user}/Documents/sensorNodesTXT", exist_ok=True)
        #print('sensorNodes# save in: %s' % pDirectory)
    except os.path.exist()!=True:
        print("Directory creation in %s fail" % pDirectory)   
    
    #Creates the folder for each sensorNode that exist.
    numNodo=msgTopic[7:9] #Take the number of the node. e.g: values/n1-> n1
    pFoldersTXT=(f"C:/Users/{user}/Documents/sensorNodesTXT/")
    try:
        os.makedirs(f"C:/Users/{user}/Documents/sensorNodesTXT/{numNodo}", exist_ok=True)
        #print(f'{numNodo} save in: %s' % pFolders#)
    except os.path.exist()!=True: 
        print("Folder creation in %s fail" % pFoldersTXT) 

#Desc: Function to extract the information from the message.
#Param In: all
#Parama Out: 
#Return: Data from the message and show it in the command console.
#Date: 21/11/2022
def fnExtractdata(client):
    global msg
    global dCSV
    global msgTopic     

    if q.empty()==True:
        print("Queue of messages is empty")
        time.sleep(5)
    while q.empty()==False:
        mes2=q.get()
        msgTopic=mes2.topic
        decoded_message=str(mes2.payload.decode()) #Decodes the JSON message.
        msg=json.loads(decoded_message)
        print(f"Received `{mes2.payload.decode()}`\n from `{topic}` topic")
        dCSV=fnSavedata()#This data will be use to plot the graphics.
        time.sleep(1)  

#Desc: Create a interval of 10 seconds after the tl.start() where the function
#fnExtractdata is executed.
#Param In: 
#Parama Out: 
#Return: The values from message and the creation of the files and directories
#Date: 23/11/2022
@tl.job(interval=timedelta(seconds=10))
def sample_job_every_10s():
    fnExtractdata(client.on_message)

#Desc: Create a interval of 300 seconds after the tl.start() where the function
#fnExtractdata is executed.
#Param In: 
#Parama Out: 
#Return: The values from message and the creation of the files and directories
#Date: 29/11/2022
@tl.job(interval=timedelta(seconds=300))
def sample_job_every_300s():
    reqPublish()
    
#Desc: This function control the switch of the electro valve.
#Param In: temp
#Parama Out: stValve
#Return: stValve 
#Date: 29/11/2022
def ctrValve(temp):
    global stValve
    if temp >= 22:
        stValve=0
    elif temp <= 18:
        stValve=100
    elif 18<temp<20:
        if stValve==None:
            stValve=0
        else:
            stValve=stValve   
    return stValve

#Desc: Publish the topics "take" and "open/n#".
#Param In: 
#Parama Out: 
#Return: 
#Date: 29/11/2022
# def reqPublish():
#     if stValve==0:
#         publish.single(f"open/{numNodo}",payload=0,hostname="158.227.233.24",port=1883)
#         publish.single('take',payload="take",hostname="158.227.233.24",port=1883)  
#     elif stValve==100:
#         publish.single(f"open/{numNodo}",payload=100,hostname="158.227.233.24",port=1883)
#         publish.single('take',payload="take",hostname="158.227.233.24",port=1883)

#------------------CONECTION TO THE MQTT BROKER--------------------------------

connected_flag=False #create flag in class.
client=mqtt_client.Client(client_id)
client.on_connect=on_connect
client.loop_start()

#First the program will search the broker adress, then in the second loop it 
#will connect to the broker.
#Flags will help us to prevent that the program repeats some cells blocking the 
#loop in the while functions.
print("Connecting to broker ",broker_adress) 
client.connect(broker_adress)

while not connected_flag: #wait in loop.
    print("In wait loop")
    time.sleep(1)
print("in Main Loop")

client.subscribe(topic) #Subscribe to the topic "values/#"

#------------------STORAGE OF THE DATA FROM THE MESSAGE------------------------

client.on_message=on_message #Receaved the messages from topic.
tl.start() #Execute the loop and the fnExtractdata after receiving all messages.

#------------------PUBLISH PROTOCOL--------------------------------------------



#------------------END PROGRAM PROTOCOL----------------------------------------

while True:
    try:
        time.sleep(1)
    except KeyboardInterrupt:
        tl.stop() #Stop tl.start() loop.
        client.loop_stop()    #Stop client loop. 
        client.disconnect()   #Disconnect
        break
